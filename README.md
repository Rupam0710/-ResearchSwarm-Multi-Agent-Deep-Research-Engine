# ResearchSwarm: Multi-Agent Deep Research Engine

ResearchSwarm is a Python + React system that orchestrates a swarm of specialized AI agents to investigate a question end-to-end.

Instead of one-shot generation, ResearchSwarm splits work across focused stages:
- Planner: breaks a question into sub-topics
- Search: gathers source candidates per sub-topic
- Reader: extracts structured insights from sources
- Synthesis: composes a single report
- Critic: evaluates report quality and confidence

The backend now includes rich, colored console logs for each agent and a final workflow summary banner.

## Architecture (ASCII)

```text
								 +----------------------+
								 |   User Question      |
								 +----------+-----------+
														|
														v
									 +--------+--------+
									 |   Planner 🧠    |
									 +--------+--------+
														|
														v
									 +--------+--------+
									 | Search Agents 🔎 |
									 | (parallel web)   |
									 +--------+--------+
														|
														v
									 +--------+--------+
									 | Reader Agents 📚 |
									 | (parallel parse) |
									 +--------+--------+
														|
														v
									 +--------+--------+
									 | Synthesis ✍️    |
									 +--------+--------+
														|
														v
									 +--------+--------+
									 |  Critic 🛡️      |
									 +--------+--------+
														|
						 +--------------+--------------+
						 | Report + Critique + Summary |
						 +-----------------------------+
```

## Screenshot

Placeholder:

```text
[ Add screenshot here: frontend home + report view ]
```

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
 