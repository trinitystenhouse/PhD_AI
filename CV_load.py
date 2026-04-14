import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from phd_ai.config import load_settings
from phd_ai.cv import extract_cv_evidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract CV evidence for one or more target fields.")
    parser.add_argument("--fields", nargs="+", required=True)
    parser.add_argument("--cv-path")
    args = parser.parse_args()

    settings = load_settings()
    cv_path = Path(args.cv_path).expanduser() if args.cv_path else settings.cv_path
    if cv_path is None:
        raise ValueError("A CV path is required. Set CV_PATH in .env or pass --cv-path.")

    result = extract_cv_evidence(
        cv_path=cv_path,
        fields=args.fields,
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
    )
    print(result)


if __name__ == "__main__":
    main()
