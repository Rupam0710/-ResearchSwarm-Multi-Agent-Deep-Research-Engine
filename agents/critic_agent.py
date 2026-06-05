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

    normalized_confidence = max(-1, min(10, normalized_confidence))

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
        - confidence_score: int in range 0-10 (or -1 on parse failure)
    """
    if not report_markdown.strip():
        raise ValueError("report_markdown must be a non-empty string")

    prompt = (
        "You are a research quality critic. Analyze the report below and return "
        "ONLY a valid JSON object with exactly these keys:\n"
        '- "flagged_claims": list of strings (claims that seem unsupported or hallucinated)\n'
        '- "gaps": list of strings (important topics not covered)\n'
        '- "confidence_score": integer between 0 and 10 rating the QUALITY OF THE REPORT '
        "based on these criteria:\n"
        "    0-3: Poor — many unsupported claims, major gaps, weak sources\n"
        "    4-6: Average — some gaps, mixed source quality\n"
        "    7-8: Good — mostly supported, minor gaps\n"
        "    9-10: Excellent — well sourced, comprehensive, no major gaps\n\n"
        "Return ONLY the JSON. No explanation. No markdown. No backticks.\n\n"
        f"Report to analyze:\n{report_markdown}"
    )

    response = powerful_llm.invoke(prompt)
    raw_content = (response.content or "").strip()  # type: ignore

    print(f"[critic_agent] Raw LLM output:\n{raw_content}\n")

    # Strip markdown code fences if the model wrapped the JSON
    content = raw_content
    if content.startswith("```"):
        content = content.split("```", 2)[-1] if content.count("```") >= 2 else content
        # Remove leading language tag (e.g. "json\n")
        if "\n" in content:
            first_line, rest = content.split("\n", 1)
            if first_line.strip().isalpha():
                content = rest
        content = content.rstrip("`").strip()

    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            result = _normalize_output(parsed)
            print(f"[critic_agent] Parsed confidence_score: {result['confidence_score']}")
            return result
    except json.JSONDecodeError:
        pass

    # Best-effort fallback: extract outermost {...} from the raw response
    start = raw_content.find("{")
    end = raw_content.rfind("}")
    if start != -1 and end != -1 and end > start:
        maybe_json = raw_content[start : end + 1]
        try:
            parsed = json.loads(maybe_json)
            if isinstance(parsed, dict):
                result = _normalize_output(parsed)
                print(f"[critic_agent] Parsed confidence_score (fallback): {result['confidence_score']}")
                return result
        except json.JSONDecodeError:
            pass

    print(f"[critic_agent] ERROR: Failed to parse LLM output. Raw response was:\n{raw_content}")
    return {
        "flagged_claims": ["Critic parse error"],
        "gaps": [],
        "confidence_score": -1,
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