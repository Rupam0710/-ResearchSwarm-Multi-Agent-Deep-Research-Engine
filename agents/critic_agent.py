import json
from typing import Any, Dict, List

from core.config import load_project_env
from core.llm_config import powerful_llm


load_project_env()


def _normalize_output(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and validate the critique payload shape."""
    flagged_claims = parsed.get("flagged_claims", [])
    gaps = parsed.get("gaps", [])
    confidence_score = parsed.get("confidence_score", 0)

    if not isinstance(flagged_claims, list):
        flagged_claims = []
    if not isinstance(gaps, list):
        gaps = []

    normalized_flagged_claims: List[str] = [
        str(item).strip() for item in flagged_claims if str(item).strip()
    ]
    normalized_gaps: List[str] = [str(item).strip() for item in gaps if str(item).strip()]

    try:
        normalized_confidence = int(confidence_score)
    except (TypeError, ValueError):
        normalized_confidence = 0

    normalized_confidence = max(0, min(10, normalized_confidence))

    return {
        "flagged_claims": normalized_flagged_claims,
        "gaps": normalized_gaps,
        "confidence_score": normalized_confidence,
    }


def critique_report(report_markdown: str) -> Dict[str, Any]:
    """Critique a markdown research report for unsupported claims and coverage gaps.

    Args:
        report_markdown: A markdown-formatted research report.

    Returns:
        Dict with keys:
        - flagged_claims: list[str]
        - gaps: list[str]
        - confidence_score: int in range 0-10
    """
    if not report_markdown.strip():
        raise ValueError("report_markdown must be a non-empty string")

    prompt = (
        "You are a strict research quality critic. "
        "Analyze the provided markdown report and return a concise structured critique.\n\n"
        "Tasks:\n"
        "1) Identify claims that appear unsupported, weakly supported, or potentially hallucinated.\n"
        "2) Identify important topic gaps that are not covered but should likely be covered.\n"
        "3) Provide a confidence score from 0 to 10 indicating your confidence in this critique.\n\n"
        "Output rules (strict):\n"
        "- Return ONLY valid JSON.\n"
        "- Return a single JSON object with EXACTLY these keys: flagged_claims, gaps, confidence_score.\n"
        "- flagged_claims must be an array of strings.\n"
        "- gaps must be an array of strings.\n"
        "- confidence_score must be an integer from 0 to 10.\n"
        "- No markdown, no code fences, no extra text.\n\n"
        f"Markdown report:\n{report_markdown}"
    )

    response = powerful_llm.invoke(prompt)
    content = (response.content or "").strip()  # type: ignore

    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return _normalize_output(parsed)
    except json.JSONDecodeError:
        pass

    # Best-effort fallback when the model wraps JSON in prose.
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        maybe_json = content[start : end + 1]
        try:
            parsed = json.loads(maybe_json)
            if isinstance(parsed, dict):
                return _normalize_output(parsed)
        except json.JSONDecodeError:
            pass

    return {
        "flagged_claims": [],
        "gaps": ["Unable to parse model critique output."],
        "confidence_score": 0,
    }


if __name__ == "__main__":
    sample_report = """# Research Report

## Executive Summary
AI adoption in enterprise market research grew by 300% year-over-year in every major industry in 2025.
Most Fortune 500 firms now rely entirely on autonomous agents for end-to-end market intelligence.

## Workflow Changes
- Teams are using retrieval-augmented generation with human-in-the-loop reviews.
- Some organizations report improved report turnaround times.

## Risks
- Hallucination remains a challenge in ungrounded workflows.
"""

    try:
        critique = critique_report(sample_report)
        print(json.dumps(critique, indent=2))
    except Exception as exc:
        print(f"Critic test failed: {exc}")