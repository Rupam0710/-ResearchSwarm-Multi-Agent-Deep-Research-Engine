# ResearchSwarm: Multi-Agent Deep Research Engine

ResearchSwarm is a Python + React system that orchestrates a swarm of specialized AI agents to investigate a question end-to-end.

Instead of one-shot generation, ResearchSwarm splits work across focused stages:
- Planner: breaks a question into sub-topics
- Search: gathers source candidates per sub-topic
- Reader: extracts structured insights from sources
- Synthesis: composes a single report
- Critic: evaluates report quality and confidence

The backend now includes rich, colored console logs for each agent and a final workflow summary banner.

## Architecture

![ResearchSwarm Architecture](./researchswarm_architecture.svg)
*Multi-agent pipeline: Planner → Search → Reader → Synthesis → Critic.*

## Screenshots

### Home — Launch Interface
![ResearchSwarm Home](./homepage.png)
*Enter your research question and launch the multi-agent swarm.*

### Live Swarm Feed — Agents Running
![Live Agents Swarm Feed](./live-agents swarm feed.png)
*Parallel Search and Reader agents reporting status in real time.*

### Research Report — Page 1
![Summary Page 1](./summary-page-1.png)
*Synthesized markdown report with citations, streamed as soon as Synthesis completes.*

### Research Report — Page 2
![Summary Page 2](./summary-page-2.png)
*Continued report output with conclusions and source references.*

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- API keys in `.env`:
	- `GROQ_API_KEY`
	- `TAVILY_API_KEY`

## Backend Setup

1. Create and activate a virtual environment.
2. Install dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Frontend Setup

```powershell
cd frontend
npm install
```

## Run The Servers

Run backend API from repository root:

```powershell
$env:PYTHONPATH = "."
uvicorn core.api:app --reload
```

Run frontend dev server in a second terminal:

```powershell
cd frontend
npm run dev
```

Default endpoints:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Optional CLI Run

From repository root:

```powershell
python main.py "What are the most promising battery technologies for grid storage in 2030?"
```

Generated report is saved to `output/report.md`.
 