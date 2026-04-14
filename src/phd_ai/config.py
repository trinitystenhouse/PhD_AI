from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    cv_path: Path | None = None
    wandb_disabled: bool = True


def _read_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_settings(env_path: str | Path = ".env") -> Settings:
    _read_dotenv(Path(env_path))

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required. Add it to your environment or .env file.")

    cv_path_env = os.getenv("CV_PATH", "").strip()
    cv_path = Path(cv_path_env).expanduser() if cv_path_env else None

    wandb_disabled = os.getenv("WANDB_DISABLED", "true").lower() in {"1", "true", "yes"}

    return Settings(
        openai_api_key=api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        cv_path=cv_path,
        wandb_disabled=wandb_disabled,
    )

