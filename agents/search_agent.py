import os
from typing import Dict, List

from tavily import TavilyClient
from core.config import load_project_env


load_project_env()


def search_subtopic(sub_topic: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web for a sub-topic using Tavily and return normalized results."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found. Add it to your .env file.")

    client = TavilyClient(api_key=api_key)
    response = client.search(query=sub_topic, max_results=min(max_results, 5))

    results: List[Dict[str, str]] = []
    for item in response.get("results", []):
        results.append(
            {
                "title": str(item.get("title", "")),
                "url": str(item.get("url", "")),
                "content": str(item.get("content", "")),
            }
        )

    return results[:5]


if __name__ == "__main__":
    test_sub_topic = "AI agents in enterprise market research"

    try:
        output = search_subtopic(test_sub_topic)
        print(f"Found {len(output)} results")
        for idx, result in enumerate(output, start=1):
            print(f"\n{idx}. {result['title']}")
            print(result["url"])
            print(result["content"])
    except Exception as exc:
        print(f"Search test failed: {exc}")
