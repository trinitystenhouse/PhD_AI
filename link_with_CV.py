import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from phd_ai.config import load_settings
from phd_ai.cv import extract_cv_skills


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract high-level skills and fields from a CV.")
    parser.add_argument("--cv-path")
    args = parser.parse_args()

    settings = load_settings()
    cv_path = Path(args.cv_path).expanduser() if args.cv_path else settings.cv_path
    if cv_path is None:
        raise ValueError("A CV path is required. Set CV_PATH in .env or pass --cv-path.")

    result = extract_cv_skills(
        cv_path=cv_path,
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
