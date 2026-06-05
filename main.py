import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

from core.orchestrator import run_research
from core.config import get_missing_env_vars, load_project_env


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ResearchSwarm",
        description="Run the ResearchSwarm multi-agent research pipeline.",
    )
    parser.add_argument(
        "question",
        type=str,
        help="Research question to investigate.",
    )
    return parser


def _validate_api_keys() -> None:
    required_keys = ["GROQ_API_KEY", "TAVILY_API_KEY"]
    missing_keys = get_missing_env_vars(required_keys)

    if missing_keys:
        missing = ", ".join(missing_keys)
        raise EnvironmentError(
            f"Missing required API keys: {missing}. "
            "Set them in your environment or .env file."
        )


def _save_report(report_markdown: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_markdown, encoding="utf-8")


def _print_critique(critique: Dict[str, Any]) -> None:
    flagged_claims_raw = critique.get("flagged_claims", [])
    flagged_claims: List[str] = (
        [str(item) for item in flagged_claims_raw]
        if isinstance(flagged_claims_raw, list)
        else []
    )
    confidence_score = critique.get("confidence_score", "N/A")

    print("\n[4/4] Critic output")
    print(f"Confidence score: {confidence_score}")
    print("Flagged claims:")

    if not flagged_claims:
        print("- None")
        return

    for idx, claim in enumerate(flagged_claims, start=1):
        print(f"{idx}. {claim}")


def main() -> int:
    load_project_env()
    load_dotenv()
    parser = _build_parser()
    args = parser.parse_args()
    question = args.question.strip()

    if not question:
        print("Research question cannot be empty.", file=sys.stderr)
        return 1

    print("[1/4] Validating configuration")
    try:
        _validate_api_keys()
    except EnvironmentError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    print("[2/4] Running swarm")
    try:
        report, critique = run_research(question)
    except Exception as exc:
        print(f"Research workflow failed: {exc}", file=sys.stderr)
        return 1

    output_path = Path("output") / "report.md"
    print(f"[3/4] Saving report to {output_path}")
    try:
        _save_report(report, output_path)
    except OSError as exc:
        print(f"Failed to write report: {exc}", file=sys.stderr)
        return 1

    _print_critique(critique)
    print(f"\nReport saved successfully: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
