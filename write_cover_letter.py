import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from phd_ai.config import load_settings
from phd_ai.cv import extract_cv_research_fit
from phd_ai.cover_letter import generate_cover_letter
from phd_ai.output import build_cover_letter_path, save_text_output
from phd_ai.research import build_research_dossier


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a tailored PhD application cover letter from a research dossier.")
    parser.add_argument("--researcher", required=True)
    parser.add_argument("--cv-path")
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    settings = load_settings()
    cv_path = Path(args.cv_path).expanduser() if args.cv_path else settings.cv_path
    if cv_path is None:
        raise ValueError("A CV path is required. Set CV_PATH in .env or pass --cv-path.")
    output_dir = Path(args.output_dir).expanduser() if args.output_dir else Path("outputs") / "cover_letters"

    dossier = build_research_dossier(
        researcher=args.researcher,
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
    )
    fit_analysis = extract_cv_research_fit(
        cv_path=cv_path,
        research_dossier=dossier,
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
    )
    result = generate_cover_letter(
        cv_path=cv_path,
        researcher=args.researcher,
        research_dossier=dossier,
        fit_analysis=fit_analysis,
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
    )
    output_path = build_cover_letter_path(output_dir=output_dir, researcher=args.researcher)
    save_text_output(result, output_path)
    print(output_path)


if __name__ == "__main__":
    main()
