import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict

from langgraph.graph import END, START, StateGraph
from rich.console import Console
from rich.panel import Panel

from agents.critic_agent import critique_report
from agents.planner import plan_subtopics
from agents.reader_agent import extract_insights
from agents.search_agent import search_subtopic
from agents.synthesis_agent import synthesize_report


CRITIC_TIMEOUT_SECONDS = 120
SEARCH_TIMEOUT_SECONDS = 30  # Per-subtopic timeout
READER_TIMEOUT_SECONDS = 30  # Per-subtopic timeout


console = Console()

AGENT_STYLES: Dict[str, str] = {
    "planner": "bold cyan",
    "search": "bold blue",
    "reader": "bold magenta",
    "synthesis": "bold green",
    "critic": "bold yellow",
    "orchestrator": "bold white",
}

AGENT_EMOJIS: Dict[str, str] = {
    "planner": "🧠",
    "search": "🔎",
    "reader": "📚",
    "synthesis": "✍️",
    "critic": "🛡️",
    "orchestrator": "🎯",
}


def log_agent(agent: str, message: str) -> None:
    style = AGENT_STYLES.get(agent, "white")
    emoji = AGENT_EMOJIS.get(agent, "•")
    console.print(f"{emoji} [{style}][{agent.capitalize()}][/{style}] {message}")


class OrchestratorState(TypedDict):
    question: str
    sub_topics: List[str]
    search_results: Dict[str, List[Dict[str, str]]]
    insights: Dict[str, List[str]]
    report: str
    critique: Dict[str, Any]
    progress_callback: Optional[Callable[[Dict[str, str]], None]]


class WorkflowSummary(TypedDict):
    sub_topics_count: int
    sources_used: int
    confidence_score: float


def emit_progress(
    state: OrchestratorState,
    agent: str,
    status: str,
    detail: Optional[str] = None,
) -> None:
    callback = state.get("progress_callback")
    if callback is None:
        return

    event = {
        "type": "progress",
        "agent": agent,
        "status": status,
    }
    if detail:
        event["detail"] = detail

    callback(event)


def planner_node(state: OrchestratorState) -> Dict[str, Any]:
    question = state["question"]
    log_agent("planner", f"Planning sub-topics for question: {question}")
    emit_progress(state, "planner", "running", "Planning research scope")

    try:
        sub_topics = plan_subtopics(question)
    except Exception as exc:
        emit_progress(state, "planner", "error", str(exc))
        raise

    log_agent("planner", f"Generated {len(sub_topics)} sub-topics")
    emit_progress(state, "planner", "done", f"Generated {len(sub_topics)} sub-topics")
    return {"sub_topics": sub_topics}


async def search_node(state: OrchestratorState) -> Dict[str, Any]:
    sub_topics = state.get("sub_topics", [])
    log_agent("search", f"Running web search in parallel for {len(sub_topics)} sub-topics")

    async def run_search(sub_topic: str) -> Tuple[str, List[Dict[str, str]]]:
        emit_progress(state, "search", "running", sub_topic)
        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(search_subtopic, sub_topic),
                timeout=SEARCH_TIMEOUT_SECONDS
            )
            log_agent("search", f"{sub_topic} -> {len(results)} results")
            emit_progress(state, "search", "done", sub_topic)
            return sub_topic, results
        except asyncio.TimeoutError:
            log_agent("search", f"{sub_topic} timed out after {SEARCH_TIMEOUT_SECONDS}s")
            emit_progress(state, "search", "error", f"{sub_topic}: timeout after {SEARCH_TIMEOUT_SECONDS}s")
            return sub_topic, []
        except Exception as exc:
            log_agent("search", f"{sub_topic} failed: {exc}")
            emit_progress(state, "search", "error", f"{sub_topic}: {exc}")
            return sub_topic, []

    pairs = await asyncio.gather(*(run_search(sub_topic) for sub_topic in sub_topics))
    search_results = {sub_topic: results for sub_topic, results in pairs}

    log_agent("search", "Completed parallel search stage")
    return {"search_results": search_results}


async def reader_node(state: OrchestratorState) -> Dict[str, Any]:
    search_results = state.get("search_results", {})
    log_agent("reader", f"Extracting insights in parallel for {len(search_results)} result sets")

    async def run_reader(sub_topic: str, results: List[Dict[str, str]]) -> Tuple[str, List[str]]:
        emit_progress(state, "reader", "running", f"{sub_topic} ({len(results)} sources)")
        try:
            extracted = await asyncio.wait_for(
                asyncio.to_thread(extract_insights, sub_topic, results),
                timeout=READER_TIMEOUT_SECONDS
            )
            log_agent("reader", f"{sub_topic} -> {len(extracted)} insights")
            emit_progress(state, "reader", "done", f"{sub_topic} ({len(results)} sources)")
            return sub_topic, extracted
        except asyncio.TimeoutError:
            log_agent("reader", f"{sub_topic} timed out after {READER_TIMEOUT_SECONDS}s")
            emit_progress(state, "reader", "error", f"{sub_topic}: timeout after {READER_TIMEOUT_SECONDS}s")
            return sub_topic, []
        except Exception as exc:
            log_agent("reader", f"{sub_topic} failed: {exc}")
            emit_progress(state, "reader", "error", f"{sub_topic}: {exc}")
            return sub_topic, []

    pairs = await asyncio.gather(
        *(run_reader(sub_topic, results) for sub_topic, results in search_results.items())
    )
    insights = {sub_topic: extracted for sub_topic, extracted in pairs}

    log_agent("reader", "Completed parallel insight extraction stage")
    return {"insights": insights}


def synthesis_node(state: OrchestratorState) -> Dict[str, Any]:
    question = state["question"]
    insights_map = state.get("insights", {})

    subtopic_insights: List[Tuple[str, List[str]]] = [
        (sub_topic, insights_map.get(sub_topic, []))
        for sub_topic in state.get("sub_topics", [])
    ]

    log_agent("synthesis", f"Building report from {len(subtopic_insights)} sub-topics")
    emit_progress(state, "synthesis", "running", "Synthesizing final report")
    try:
        report = synthesize_report(question, subtopic_insights)
    except Exception as exc:
        emit_progress(state, "synthesis", "error", str(exc))
        raise
    log_agent("synthesis", "Report generation complete")
    emit_progress(state, "synthesis", "done", "Report ready")

    return {"report": report}


async def critic_node(state: OrchestratorState) -> Dict[str, Any]:
    report = state.get("report", "")
    log_agent("critic", "Reviewing synthesized report")
    emit_progress(state, "critic", "running", "Reviewing report quality")
    completed_successfully = False

    if not report.strip():
        critique = {
            "flagged_claims": [],
            "gaps": ["No report available to critique."],
            "confidence_score": 0,
        }
        log_agent("critic", "Skipped critique because report is empty")
        emit_progress(state, "critic", "error", "No report available to critique")
        return {"critique": critique}

    try:
        critique = await asyncio.wait_for(
            asyncio.to_thread(critique_report, report),
            timeout=CRITIC_TIMEOUT_SECONDS,
        )
        completed_successfully = True
    except asyncio.TimeoutError:
        log_agent("critic", f"Timed out after {CRITIC_TIMEOUT_SECONDS}s; returning fallback critique")
        emit_progress(state, "critic", "error", f"Timed out after {CRITIC_TIMEOUT_SECONDS}s")
        critique = {
            "flagged_claims": [],
            "gaps": [],
            "confidence_score": -1,
            "error": "Critic timed out"
        }
    except Exception as exc:
        log_agent("critic", f"Critique failed: {exc}")
        emit_progress(state, "critic", "error", str(exc))
        critique = {
            "flagged_claims": [],
            "gaps": [f"Critic stage failed: {exc}"],
            "confidence_score": 0,
        }

    log_agent("critic", "Critique complete")
    if completed_successfully:
        emit_progress(state, "critic", "done", "Critique complete")
    return {"critique": critique}


def _count_sources(search_results: Dict[str, List[Dict[str, str]]]) -> int:
    urls = {
        str(item.get("url", "")).strip()
        for results in search_results.values()
        for item in results
        if isinstance(item, dict)
    }
    return len({url for url in urls if url})


def _to_confidence_score(critique: Dict[str, Any]) -> float:
    raw = critique.get("confidence_score", 0)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _print_summary_banner(summary: WorkflowSummary) -> None:
    content = (
        f"• Sub-topics: [bold]{summary['sub_topics_count']}[/bold]\n"
        f"• Sources used: [bold]{summary['sources_used']}[/bold]\n"
        f"• Confidence score: [bold]{summary['confidence_score']:.1f}/10[/bold]"
    )
    console.print(Panel.fit(content, title="📌 Research Summary", border_style="bright_green"))


def build_orchestrator_graph():
    graph_builder = StateGraph(OrchestratorState)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("search", search_node)
    graph_builder.add_node("reader", reader_node)
    graph_builder.add_node("synthesis", synthesis_node)
    graph_builder.add_node("critic", critic_node)

    graph_builder.add_edge(START, "planner")
    graph_builder.add_edge("planner", "search")
    graph_builder.add_edge("search", "reader")
    graph_builder.add_edge("reader", "synthesis")
    graph_builder.add_edge("synthesis", "critic")
    graph_builder.add_edge("critic", END)

    return graph_builder.compile()


async def run_research_async(
    question: str,
    progress_callback: Optional[Callable[[Dict[str, str]], None]] = None,
) -> Tuple[str, Dict[str, Any]]:
    log_agent("orchestrator", "Starting research workflow")

    graph = build_orchestrator_graph()
    initial_state: OrchestratorState = {
        "question": question,
        "sub_topics": [],
        "search_results": {},
        "insights": {},
        "report": "",
        "critique": {},
        "progress_callback": progress_callback,
    }

    final_state = await graph.ainvoke(initial_state)

    report = str(final_state.get("report", ""))
    critique = final_state.get("critique", {})
    summary: WorkflowSummary = {
        "sub_topics_count": len(final_state.get("sub_topics", [])),
        "sources_used": _count_sources(final_state.get("search_results", {})),
        "confidence_score": _to_confidence_score(critique if isinstance(critique, dict) else {}),
    }

    log_agent("orchestrator", "Workflow complete")
    _print_summary_banner(summary)
    return report, critique


def run_research(question: str) -> Tuple[str, Dict[str, Any]]:
    return asyncio.run(run_research_async(question))
