import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from phd_ai.applicant import ensure_applicant_profile
from phd_ai.config import load_settings
from phd_ai.pipeline import build_application_package, save_application_package


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the full linked pipeline from researcher name to CV fit analysis and cover letter."
    )
    parser.add_argument("--researcher", default="Ciaran O'Hare")
    parser.add_argument("--cv-path")
    parser.add_argument("--applicant-profile")
    parser.add_argument("--output-dir")
    parser.add_argument("--recent-paper-count", type=int, default=5)
    parser.add_argument("--notable-paper-count", type=int, default=2)
    parser.add_argument("--candidate-paper-count", type=int, default=8)
    args = parser.parse_args()

    settings = load_settings()
    cv_path = Path(args.cv_path).expanduser() if args.cv_path else settings.cv_path
    if cv_path is None:
        raise ValueError("A CV path is required. Set CV_PATH in .env or pass --cv-path.")
    applicant_profile_path = (
        Path(args.applicant_profile).expanduser()
        if args.applicant_profile
        else settings.applicant_profile_path
    )
    if applicant_profile_path is None or not applicant_profile_path.exists():
        _, applicant_profile_path = ensure_applicant_profile(applicant_profile_path)
    output_dir = Path(args.output_dir).expanduser() if args.output_dir else Path("outputs") / "applications"

    result = build_application_package(
        researcher=args.researcher,
        cv_path=cv_path,
        applicant_profile_path=applicant_profile_path,
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
        recent_paper_count=args.recent_paper_count,
        notable_paper_count=args.notable_paper_count,
        candidate_paper_count=args.candidate_paper_count,
    )
    result["saved_paths"] = save_application_package(result, output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
