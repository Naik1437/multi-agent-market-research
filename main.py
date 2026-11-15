import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4
from monitoring.execution_tracker import (
    agent_metrics,
    execution_tracker,
    reset_tracking,
    routing_history,
    task_metrics,
)

from pathlib import Path

from crew.crew import market_research_crew
from crew.financial_parser import analyze_financial_data, build_illustrative_financial_section
from crew.pdf_generator import generate_pdf


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
BENCHMARK_FILE = BASE_DIR / "benchmarks" / "benchmarks.json"

REPORT_PATH = OUTPUT_DIR / "market_research_report.md"
PDF_PATH = OUTPUT_DIR / "market_report.pdf"
FINANCIAL_DATA_PATH = BASE_DIR / "data" / "sample_financial_data.csv"


def replace_financial_section(markdown, financial_result):
    """Use deterministic CSV calculations in the final report instead of generated figures."""
    replacement = build_illustrative_financial_section(financial_result)
    heading = re.search(r"(?m)^##\s+\d+\.\s+Financial Analysis\s*$", markdown)
    if heading:
        next_heading = re.search(r"(?m)^##\s+", markdown[heading.end():])
        end = heading.end() + next_heading.start() if next_heading else len(markdown)
        return markdown[:heading.start()] + replacement + "\n\n" + markdown[end:].lstrip()
    return markdown.rstrip() + "\n\n" + replacement + "\n"


def append_research_sources(markdown, task_outputs):
    """Carry only URLs returned by the market research task into the report."""
    url_pattern = re.compile(r"https?://[^\s<>\]\)\"']+", re.IGNORECASE)
    source_urls = []
    for task_output in task_outputs or []:
        description = str(getattr(task_output, "description", "")).lower()
        if "market topic" not in description or "source url" not in description:
            continue
        raw_output = str(getattr(task_output, "raw", ""))
        for url in url_pattern.findall(raw_output):
            url = url.rstrip(".,;:!?")
            if url and url not in source_urls:
                source_urls.append(url)

    existing_urls = set(url_pattern.findall(markdown))
    missing_urls = [url for url in source_urls if url not in existing_urls]
    if not missing_urls:
        return markdown

    source_lines = "\n".join(f"* <{url}>" for url in missing_urls)
    source_heading = re.compile(
        r"(?im)^(?:#{1,3}\s*)?(?:\*\*)?Sources(?:\s*&\s*References)?(?::\*\*|:)?\s*$"
    ).search(markdown)
    if source_heading:
        insertion = source_heading.end()
        return markdown[:insertion] + "\n\n" + source_lines + markdown[insertion:]

    return markdown.rstrip() + "\n\n## Sources\n\n" + source_lines + "\n"


def report_paths(query):
    """Create stable, query-specific paths without replacing old reports."""
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")[:60]
    slug = slug or "market-research"
    slug = f"{slug}-{hashlib.sha256(query.encode('utf-8')).hexdigest()[:8]}"
    return OUTPUT_DIR / f"{slug}.md", OUTPUT_DIR / f"{slug}.pdf"


def safe_error_message(error):
    """Keep API credentials out of console output and benchmark records."""
    message = f"{type(error).__name__}: {error}"
    for name in ("TAVILY_API_KEY", "GOOGLE_API_KEY", "SERPER_API_KEY", "OPENAI_API_KEY"):
        secret = os.getenv(name)
        if secret:
            message = message.replace(secret, "[REDACTED]")
    return message


def update_benchmarks(query, status, execution_time, report_path,
                      pdf_path, report_generated=False, pdf_generated=False,
                      run_id=None, started_at=None, failure_reason=None):
    """Update execution metrics without overwriting existing benchmark data."""

    try:
        BENCHMARK_FILE.parent.mkdir(parents=True, exist_ok=True)

        if BENCHMARK_FILE.exists():
            data = json.loads(
                BENCHMARK_FILE.read_text(encoding="utf-8")
            )
        else:
            data = {}

        execution = data.setdefault("execution", {})

        execution.update({
            "status": status,
            "query": query,
            "run_id": run_id,
            "started_at_utc": started_at,
            "model": os.getenv("MODEL", "configured Gemini model"),
            "execution_time_seconds": round(execution_time, 2),
            "report_generated": report_generated,
            "markdown_report": report_path.relative_to(BASE_DIR).as_posix(),
            "pdf_report": pdf_path.relative_to(BASE_DIR).as_posix(),
            "pdf_generated": pdf_generated
        })
        data["agent_execution_metrics"] = list(agent_metrics)
        data["task_execution_metrics"] = list(task_metrics)
        data.setdefault("manager", {})
        data["manager"]["observed_task_assignments"] = list(routing_history)
        data["manager"]["verified_routing_history"] = [
            {
                "task": route.get("task"),
                "manager": route.get("manager"),
                "delegated_to": route.get("delegated_to"),
                "status": (
                    "Specialist execution observed"
                    if route.get("specialist_execution_observed")
                    else "Task assignment observed"
                ),
            }
            for route in routing_history
            if route.get("event") == "task_assignment_observed"
        ]
        data["notes"] = [
            note for note in data.get("notes", [])
            if "require additional verification" not in str(note).lower()
            and "execution duration of" not in str(note).lower()
            and "researcher delegation observed" not in str(note).lower()
        ]
        completed_agents = {
            metric.get("agent") for metric in agent_metrics
            if metric.get("status") == "COMPLETED"
        }
        for agent in data.get("agents", []):
            role = agent.get("role")
            agent["execution_verified"] = role in completed_agents or any(
                role and role in name for name in completed_agents
            )
        if failure_reason:
            execution["failure_reason"] = failure_reason
        else:
            execution.pop("failure_reason", None)

        data["output_metrics"] = data.get("output_metrics", {})
        data["output_metrics"]["pdf_validation"] = (
            "PASS" if pdf_generated else "NOT_GENERATED"
        )

        temporary_file = BENCHMARK_FILE.with_suffix(".json.tmp")
        temporary_file.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )
        temporary_file.replace(BENCHMARK_FILE)

        print(f"\nBenchmarks updated: {BENCHMARK_FILE}")

    except Exception as error:
        print(f"\nBenchmark update warning: {error}")


def run_market_research(query):

    start_time = time.perf_counter()
    run_id = str(uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    print("\n========================================")
    print(" MULTI-AGENT MARKET RESEARCH SYSTEM")
    print("========================================")

    print(f"\nResearch Topic: {query}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path, pdf_path = report_paths(query)
    report_generated = False
    pdf_generated = False
    reset_tracking(run_id=run_id)

    if not os.getenv("TAVILY_API_KEY"):
        failure_reason = "Missing required API key: TAVILY_API_KEY"
        log_path = BASE_DIR / "benchmarks" / "execution.log.txt"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(
                f"{started_at}: run_id={run_id}, query={query!r}, "
                f"status=FAILED, error={failure_reason}\n"
            )
        update_benchmarks(
            query=query,
            status="FAILED",
            execution_time=time.perf_counter() - start_time,
            report_path=report_path,
            pdf_path=pdf_path,
            run_id=run_id,
            started_at=started_at,
            failure_reason=failure_reason
        )
        print(f"\nResearch execution failed: {failure_reason}")
        return None

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:
            reset_tracking(run_id=run_id)
            print(
                f"\nStarting hierarchical execution "
                f"(Attempt {attempt}/{max_attempts})..."
            )

            result = market_research_crew.kickoff(
                inputs={"query": query}
            )

            financial_result = analyze_financial_data(str(FINANCIAL_DATA_PATH))
            report_markdown = append_research_sources(
                result.raw,
                getattr(result, "tasks_output", []),
            )
            report_markdown = replace_financial_section(report_markdown, financial_result)
            report_path.write_text(
                report_markdown,
                encoding="utf-8"
            )
            report_generated = True

            print("\nMarkdown report generated successfully.")

            print("\nStarting professional PDF generation...")

            generate_pdf(
                input_file=report_path,
                output_file=pdf_path,
                report_title=query
            )
            pdf_generated = True

            execution_time = time.perf_counter() - start_time

            update_benchmarks(
                query=query,
                status="SUCCESS",
                execution_time=execution_time,
                report_path=report_path,
                pdf_path=pdf_path,
                report_generated=report_generated,
                pdf_generated=pdf_generated,
                run_id=run_id,
                started_at=started_at
            )

            print("\n========================================")
            print(" RESEARCH COMPLETED SUCCESSFULLY")
            print("========================================")

            print(f"\nMarkdown: {report_path}")
            print(f"PDF     : {pdf_path}")
            print(f"Time    : {execution_time:.2f} seconds")

            return result

        except Exception as error:

            error_message = safe_error_message(error)

            if (
                ("503" in error_message or "UNAVAILABLE" in error_message)
                and attempt < max_attempts
            ):

                wait_time = 20 * attempt

                print(
                    f"\nGemini server temporarily unavailable."
                    f"\nRetrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                execution_time = time.perf_counter() - start_time

                status = "PARTIAL_SUCCESS" if report_generated else "FAILED"

                update_benchmarks(
                    query=query,
                    status=status,
                    execution_time=execution_time,
                    report_path=report_path,
                    pdf_path=pdf_path,
                    report_generated=report_generated,
                    pdf_generated=pdf_generated,
                    run_id=run_id,
                    started_at=started_at,
                    failure_reason=error_message
                )

                print("\nResearch execution failed:")
                print(error_message)

                return None


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Multi-Agent Market Research & Report Generator"
    )

    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Market research topic"
    )

    args = parser.parse_args()

    result = run_market_research(args.query)
    sys.exit(0 if result is not None else 1)
