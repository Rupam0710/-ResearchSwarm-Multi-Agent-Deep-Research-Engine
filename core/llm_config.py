import os

from langchain_groq import ChatGroq

from core.config import load_project_env


load_project_env()


def _require_groq_api_key() -> str:
	api_key = os.getenv("GROQ_API_KEY", "").strip()
	if not api_key:
		raise EnvironmentError(
			"Missing GROQ_API_KEY. Add it to the project .env file or your environment variables."
		)
	return api_key


_groq_api_key = _require_groq_api_key()

# Fast lightweight agents
fast_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=_groq_api_key)

# Heavy reasoning agents
powerful_llm = ChatGroq(
	model="llama-3.3-70b-versatile", temperature=0, api_key=_groq_api_key
)