import json
from typing import Dict, List

from core.config import load_project_env
from core.llm_config import fast_llm


load_project_env()


def extract_insights(
    sub_topic: str, search_results: List[Dict[str, str]]
) -> List[str]:
    """Extract 3-5 key factual insights from search results relevant to a sub-topic.

    Each insight is tagged with its source URL.

    Args:
        sub_topic: The research sub-topic guiding which facts are relevant.
        search_results: List of dicts with keys 'title', 'url', and 'content'.

    Returns:
        List of insight strings in the format "<insight> [Source: <url>]".
    """
    if not search_results:
        return []

    sources_block = "\n\n".join(
        f"SOURCE {i + 1}\nTitle: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
        for i, r in enumerate(search_results)
    )

    prompt = (
        "You are a research analyst. "
        "Given a sub-topic and a set of web search results, extract the 3 to 5 most important "
        "factual insights that are directly relevant to the sub-topic. "
        "Each insight must be a single, concrete, factual sentence. "
        "Each insight must cite its source URL. "
        "Return ONLY a JSON array of strings. "
        "Each string must follow this exact format: \"<insight> [Source: <url>]\". "
        "No markdown, no extra text, no numbering outside the JSON array.\n\n"
        f"Sub-topic: {sub_topic}\n\n"
        f"{sources_block}"
    )

    response = fast_llm.invoke(prompt)
    content = (response.content or "").strip()  # type: ignore

    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    # Fallback: split on newlines and return non-empty lines
    lines = [line.strip("-•[] \t") for line in content.splitlines() if line.strip()]
    return [line for line in lines if line]


if __name__ == "__main__":
    test_sub_topic = "AI agents in enterprise market research"

    test_results = [
        {
            "title": "How AI Agents Are Reshaping Market Research",
            "url": "https://example.com/ai-agents-market-research",
            "content": (
                "AI agents are increasingly being deployed in enterprise market research to automate "
                "data collection, competitive analysis, and trend identification. Companies like "
                "Forrester and Gartner report that over 40% of large enterprises piloted AI-driven "
                "research workflows in 2024, reducing analyst time by up to 60%."
            ),
        },
        {
            "title": "LLMs and Autonomous Research Pipelines",
            "url": "https://example.com/llm-research-pipelines",
            "content": (
                "Large language models such as GPT-4o are being integrated into multi-agent pipelines "
                "that can autonomously gather, synthesize, and summarise industry reports. "
                "These pipelines typically combine a planner agent, web-search agents, and a "
                "reader/synthesis agent to produce structured research outputs."
            ),
        },
        {
            "title": "Challenges of AI in Research Automation",
            "url": "https://example.com/ai-research-challenges",
            "content": (
                "Despite rapid adoption, hallucination rates in LLM-generated research summaries "
                "remain a key concern. A 2025 MIT study found that without grounding on retrieved "
                "sources, error rates in AI-generated market reports can reach 25%."
            ),
        },
    ]

    insights = extract_insights(test_sub_topic, test_results)
    print(f"Extracted {len(insights)} insights:\n")
    for insight in insights:
        print(f"- {insight}")
