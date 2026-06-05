import re
from typing import List, Set, Tuple

from core.config import load_project_env
from core.llm_config import powerful_llm


load_project_env()


def _estimate_tokens(text: str) -> int:
    """Rough estimate of token count. ~1 token per 4 characters on average."""
    return max(1, len(text.strip()) // 4)


def _extract_urls(text: str) -> List[str]:
    """Extract HTTP(S) URLs from text, preserving discovery order."""
    matches = re.findall(r"https?://[^\s)\]>\"']+", text)
    seen: Set[str] = set()
    ordered: List[str] = []

    for url in matches:
        cleaned = url.rstrip(".,;:")
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            ordered.append(cleaned)

    return ordered


def synthesize_report(
    question: str, subtopic_insights: List[Tuple[str, List[str]]]
) -> str:
    """Synthesize sub-topic insights into a structured markdown research report.

    Args:
        question: The original research question.
        subtopic_insights: List of tuples in the form (sub-topic, [insights]).

    Returns:
        A markdown-formatted research report string containing:
        - Executive Summary
        - One section per sub-topic
        - Key Conclusions
        - All source URLs listed at the end
    """
    if not question.strip():
        raise ValueError("question must be a non-empty string")

    if not subtopic_insights:
        return (
            f"# Research Report\n\n"
            f"## Original Question\n{question.strip()}\n\n"
            "## Executive Summary\n"
            "No sub-topic insights were provided, so no synthesis could be produced.\n\n"
            "## Key Conclusions\n"
            "- Insufficient evidence to draw conclusions.\n\n"
            "## Sources\n"
            "No source URLs were provided.\n"
        )

    all_urls: List[str] = []
    seen_urls: Set[str] = set()

    sections_block_parts: List[str] = []
    for idx, (sub_topic, insights) in enumerate(subtopic_insights, start=1):
        cleaned_sub_topic = (sub_topic or "Untitled Sub-topic").strip()
        # Limit to top 3-4 insights per subtopic to reduce token size
        cleaned_insights = [insight.strip() for insight in insights if insight.strip()][:4]

        for insight in cleaned_insights:
            for url in _extract_urls(insight):
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_urls.append(url)

        bullet_block = "\n".join(f"- {insight}" for insight in cleaned_insights) or "- No insights provided"
        sections_block_parts.append(
            f"{cleaned_sub_topic}: {bullet_block}"
        )

    sections_block = "\n".join(sections_block_parts)
    urls_block = "\n".join(f"- {url}" for url in all_urls) or "- No source URLs found"

    # Simplified, token-efficient prompt
    prompt = (
        "Synthesize this research into a markdown report with: ## Executive Summary, "
        "## Sub-topic Analysis (one ### section per subtopic), ## Key Conclusions, ## Sources.\n"
        "Use only provided facts. Return markdown only.\n\n"
        f"Question: {question.strip()}\n\n"
        f"Insights by topic:\n{sections_block}\n\n"
        f"URLs to include in Sources:\n{urls_block}"
    )

    # Estimate tokens and warn if close to limit
    estimated_tokens = _estimate_tokens(prompt)
    if estimated_tokens > 5500:  # Leave buffer for response before hitting 6000 TPM limit
        print(f"⚠️  WARNING: Synthesis prompt estimated at ~{estimated_tokens} tokens (Groq limit: 6000). "
              f"Report may fail. Consider simplifying the question or reducing sub-topics.")

    response = powerful_llm.invoke(prompt)
    report = (response.content or "").strip()  # type: ignore

    if not report:
        report = (
            "## Executive Summary\n"
            "The model did not return a synthesis.\n\n"
            "## Sub-topic Analysis\n"
            "### Unavailable\n"
            "No analysis was generated.\n\n"
            "## Key Conclusions\n"
            "- No conclusions could be generated.\n\n"
            "## Sources\n"
            f"{urls_block}\n"
        )

    # Ensure required URLs are present even if the model omits some.
    missing_urls = [url for url in all_urls if url not in report]
    if missing_urls:
        if "## Sources" in report:
            report = report.rstrip() + "\n" + "\n".join(f"- {url}" for url in missing_urls)
        else:
            report = (
                report.rstrip()
                + "\n\n## Sources\n"
                + "\n".join(f"- {url}" for url in all_urls)
            )

    return report


if __name__ == "__main__":
    test_question = "How will AI agents transform enterprise market research workflows over the next 5 years?"

    test_subtopic_insights: List[Tuple[str, List[str]]] = [
        (
            "Workflow Automation and Productivity",
            [
                "AI agents can automate repetitive research tasks like data collection and first-pass synthesis, reducing analyst manual effort by up to 50% in pilot programs. [Source: https://example.com/automation-productivity]",
                "Organizations report faster turnaround for recurring market-monitoring reports when agent pipelines are integrated with internal knowledge bases. [Source: https://example.com/market-monitoring]",
            ],
        ),
        (
            "Data Quality, Risk, and Governance",
            [
                "Ungrounded model outputs can introduce factual errors, requiring retrieval grounding and human review loops for high-stakes decisions. [Source: https://example.com/grounding-risk]",
                "Leading teams are implementing governance controls such as prompt versioning, source traceability, and audit logs. [Source: https://example.com/ai-governance]",
            ],
        ),
        (
            "Operating Model and Talent Impact",
            [
                "Research roles are shifting toward higher-value interpretation and scenario modeling, while junior tasks become increasingly automated. [Source: https://example.com/talent-shift]",
                "Cross-functional squads combining research, data engineering, and AI operations are becoming a common operating model. [Source: https://example.com/ai-squads]",
            ],
        ),
    ]

    try:
        md_report = synthesize_report(test_question, test_subtopic_insights)
        print(md_report)
    except Exception as exc:
        print(f"Synthesis test failed: {exc}")
