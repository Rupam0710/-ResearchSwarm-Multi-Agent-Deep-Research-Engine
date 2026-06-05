import json
from typing import List

from core.config import load_project_env
from core.llm_config import fast_llm


load_project_env()


def plan_subtopics(question: str) -> List[str]:
    """Break a research question into 4-6 focused sub-topics for parallel research."""
    prompt = (
        "You are a research planner. "
        "Given a research question, produce 4 to 6 focused sub-topics suitable for parallel web research. "
        "Each sub-topic should be specific and non-overlapping. "
        "Return ONLY a JSON array of strings, no markdown, no extra text.\n\n"
        f"Research question: {question}"
    )

    response = fast_llm.invoke(prompt)
    content = (response.content or "").strip() # type: ignore

    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    lines = [line.strip("-• \t") for line in content.splitlines() if line.strip()]
    return [line for line in lines if line]


if __name__ == "__main__":
    test_question = "How will AI agents transform enterprise market research workflows over the next 5 years?"
    subtopics = plan_subtopics(test_question)
    print(subtopics)
