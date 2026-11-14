import argparse
import time
from pathlib import Path

from crew.crew import market_research_crew


def run_market_research(query: str):

    print("\n========================================")
    print(" MULTI-AGENT MARKET RESEARCH SYSTEM")
    print("========================================")

    print(f"\nResearch Topic: {query}")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    report_path = output_dir / "market_research_report.md"

    # Retry temporary API/server failures
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

            with open(report_path, "w", encoding="utf-8") as file:
                file.write(result.raw)

            print("\n========================================")
            print(" RESEARCH COMPLETED SUCCESSFULLY")
            print("========================================")

            print(f"\nReport saved at: {report_path}")

            return result

        except Exception as error:

            error_message = str(error)

            if "503" in error_message or "UNAVAILABLE" in error_message:

                if attempt < max_attempts:
                    wait_time = 20 * attempt

                    print(
                        f"\nGemini server is temporarily busy."
                        f"\nRetrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                else:
                    print(
                        "\nGemini is still unavailable after "
                        "3 attempts."
                    )
                    print(
                        "Please try again later. "
                        "No billing or paid API is required."
                    )
                    return None

            else:
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