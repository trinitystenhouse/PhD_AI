import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from phd_ai.applicant import DEFAULT_APPLICANT_PROFILE_PATH, prompt_for_applicant_profile, save_applicant_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactively collect applicant details for cover letter generation.")
    parser.add_argument("--output", default=str(DEFAULT_APPLICANT_PROFILE_PATH))
    args = parser.parse_args()

    profile = prompt_for_applicant_profile()
    output_path = Path(args.output).expanduser()
    save_applicant_profile(profile, output_path)
    print(output_path)


if __name__ == "__main__":
    main()
