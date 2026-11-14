import argparse
import json
import os
import time
from pathlib import Path

from crew.crew import market_research_crew
from crew.pdf_generator import generate_pdf


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
BENCHMARK_FILE = BASE_DIR / "benchmarks" / "benchmarks.json"

REPORT_PATH = OUTPUT_DIR / "market_research_report.md"
PDF_PATH = OUTPUT_DIR / "market_research_report.pdf"


def update_benchmarks(query, status, execution_time, pdf_generated=False):
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
            "model": os.getenv("MODEL", "configured Gemini model"),
            "execution_time_seconds": round(execution_time, 2),
            "report_generated": REPORT_PATH.exists(),
            "markdown_report": str(REPORT_PATH.relative_to(BASE_DIR)),
            "pdf_report": str(PDF_PATH.relative_to(BASE_DIR)),
            "pdf_generated": pdf_generated
        })

        data["output_metrics"] = data.get("output_metrics", {})
        data["output_metrics"]["pdf_validation"] = (
            "PASS" if pdf_generated else "NOT_GENERATED"
        )

        BENCHMARK_FILE.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

        print(f"\nBenchmarks updated: {BENCHMARK_FILE}")

    except Exception as error:
        print(f"\nBenchmark update warning: {error}")


def run_market_research(query):

    start_time = time.perf_counter()

    print("\n========================================")
    print(" MULTI-AGENT MARKET RESEARCH SYSTEM")
    print("========================================")

    print(f"\nResearch Topic: {query}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:
            print(
                f"\nStarting hierarchical execution "
                f"(Attempt {attempt}/{max_attempts})..."
            )

            result = market_research_crew.kickoff(
                inputs={"query": query}
            )

            REPORT_PATH.write_text(
                result.raw,
                encoding="utf-8"
            )

            print("\nMarkdown report generated successfully.")

            print("\nStarting professional PDF generation...")

            generate_pdf()

            execution_time = time.perf_counter() - start_time

            update_benchmarks(
                query=query,
                status="SUCCESS",
                execution_time=execution_time,
                pdf_generated=PDF_PATH.exists()
            )

            print("\n========================================")
            print(" RESEARCH COMPLETED SUCCESSFULLY")
            print("========================================")

            print(f"\nMarkdown: {REPORT_PATH}")
            print(f"PDF     : {PDF_PATH}")
            print(f"Time    : {execution_time:.2f} seconds")

            return result

        except Exception as error:

            error_message = str(error)

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

                status = (
                    "PARTIAL_SUCCESS"
                    if REPORT_PATH.exists()
                    else "FAILED"
                )

                update_benchmarks(
                    query=query,
                    status=status,
                    execution_time=execution_time,
                    pdf_generated=PDF_PATH.exists()
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

    run_market_research(args.query)