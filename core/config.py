import os
from pathlib import Path
from typing import Iterable, List

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOTENV_PATH = PROJECT_ROOT / ".env"
DOTENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"


def load_project_env() -> None:
    """Load environment variables from the repository root env file(s)."""
    env_path = DOTENV_PATH if DOTENV_PATH.exists() else DOTENV_EXAMPLE_PATH
    load_dotenv(dotenv_path=env_path, override=False)


def get_missing_env_vars(required_keys: Iterable[str]) -> List[str]:
    """Return required environment variable names that are missing or empty."""
    return [key for key in required_keys if not os.getenv(key)]
