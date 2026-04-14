from __future__ import annotations

import argparse
import json
from pathlib import Path

from phd_ai.applicant import (
    DEFAULT_APPLICANT_PROFILE_PATH,
    ensure_applicant_profile,
    load_applicant_profile,
    prompt_for_applicant_profile,
    save_applicant_profile,
)
from phd_ai.config import load_settings
from phd_ai.cover_letter import generate_cover_letter
from phd_ai.cv import extract_cv_evidence, extract_cv_research_fit, extract_cv_skills
from phd_ai.output import build_run_directory, save_json_output, save_text_output
from phd_ai.pipeline import build_application_package, save_application_package
from phd_ai.research import build_research_dossier, extract_research_profile, get_latest_paper_for_researcher


def _resolve_cv_path(cli_value: str | None, default: Path | None) -> Path:
    if cli_value:
        return Path(cli_value).expanduser()
    if default is None:
        raise ValueError("A CV path is required. Set CV_PATH in .env or pass --cv-path.")
    return default


def _resolve_output_dir(cli_value: str | None) -> Path:
    return Path(cli_value).expanduser() if cli_value else Path("outputs") / "applications"


def _resolve_applicant_profile_path(cli_value: str | None, default: Path | None) -> Path | None:
    if cli_value:
        return Path(cli_value).expanduser()
    if default is not None:
        return default
    fallback = DEFAULT_APPLICANT_PROFILE_PATH
    return fallback if fallback.exists() else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PhD AI command line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    research_parser = subparsers.add_parser("research", help="Fetch a researcher's latest paper and summarize it")
    research_parser.add_argument("--researcher", required=True)

    dossier_parser = subparsers.add_parser("dossier", help="Build a multi-paper research dossier for a researcher")
    dossier_parser.add_argument("--researcher", required=True)
    dossier_parser.add_argument("--recent-paper-count", type=int, default=5)
    dossier_parser.add_argument("--notable-paper-count", type=int, default=2)
    dossier_parser.add_argument("--candidate-paper-count", type=int, default=8)

    arxiv_parser = subparsers.add_parser("arxiv-id", help="Fetch the latest arXiv id for a researcher")
    arxiv_parser.add_argument("--researcher", required=True)

    cv_parser = subparsers.add_parser("cv-evidence", help="Extract CV evidence for target fields")
    cv_parser.add_argument("--fields", nargs="+", required=True)
    cv_parser.add_argument("--cv-path")

    cover_parser = subparsers.add_parser("cover-letter", help="Generate a cover letter from the full linked pipeline")
    cover_parser.add_argument("--researcher", required=True)
    cover_parser.add_argument("--cv-path")
    cover_parser.add_argument("--applicant-profile")
    cover_parser.add_argument("--output-dir")

    skills_parser = subparsers.add_parser("cv-skills", help="Extract skills from a CV")
    skills_parser.add_argument("--cv-path")

    profile_parser = subparsers.add_parser("applicant-profile", help="Interactively collect applicant profile details")
    profile_parser.add_argument("--output", default=str(DEFAULT_APPLICANT_PROFILE_PATH))

    fit_parser = subparsers.add_parser("fit", help="Analyze fit between a CV and a researcher's paper dossier")
    fit_parser.add_argument("--researcher", required=True)
    fit_parser.add_argument("--cv-path")

    package_parser = subparsers.add_parser("pipeline", help="Run the full researcher-to-cover-letter pipeline")
    package_parser.add_argument("--researcher", required=True)
    package_parser.add_argument("--cv-path")
    package_parser.add_argument("--applicant-profile")
    package_parser.add_argument("--output-dir")
    package_parser.add_argument("--recent-paper-count", type=int, default=5)
    package_parser.add_argument("--notable-paper-count", type=int, default=2)
    package_parser.add_argument("--candidate-paper-count", type=int, default=8)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()

    if args.command == "research":
        result = extract_research_profile(
            researcher=args.researcher,
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
        )
        print(json.dumps(result, indent=2))
        return

    if args.command == "arxiv-id":
        paper = get_latest_paper_for_researcher(args.researcher)
        print(paper.arxiv_id)
        return

    if args.command == "dossier":
        result = build_research_dossier(
            researcher=args.researcher,
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
            recent_paper_count=args.recent_paper_count,
            notable_paper_count=args.notable_paper_count,
            candidate_paper_count=args.candidate_paper_count,
        )
        print(json.dumps(result, indent=2))
        return

    if args.command == "cv-evidence":
        cv_path = _resolve_cv_path(args.cv_path, settings.cv_path)
        result = extract_cv_evidence(
            cv_path=cv_path,
            fields=args.fields,
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
        )
        print(result)
        return

    if args.command == "cv-skills":
        cv_path = _resolve_cv_path(args.cv_path, settings.cv_path)
        result = extract_cv_skills(
            cv_path=cv_path,
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
        )
        print(json.dumps(result, indent=2))
        return

    if args.command == "applicant-profile":
        profile = prompt_for_applicant_profile()
        output_path = Path(args.output).expanduser()
        save_applicant_profile(profile, output_path)
        print(str(output_path))
        return

    if args.command == "fit":
        cv_path = _resolve_cv_path(args.cv_path, settings.cv_path)
        dossier = build_research_dossier(
            researcher=args.researcher,
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
        )
        result = extract_cv_research_fit(
            cv_path=cv_path,
            research_dossier=dossier,
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
        )
        print(json.dumps(result, indent=2))
        return

    if args.command == "cover-letter":
        cv_path = _resolve_cv_path(args.cv_path, settings.cv_path)
        output_dir = _resolve_output_dir(args.output_dir)
        applicant_profile_path = _resolve_applicant_profile_path(args.applicant_profile, settings.applicant_profile_path)
        applicant_profile, applicant_profile_path = ensure_applicant_profile(applicant_profile_path)
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
            applicant_profile=applicant_profile,
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
        )
        run_dir = build_run_directory(output_dir, args.researcher)
        run_dir.mkdir(parents=True, exist_ok=True)
        save_json_output(applicant_profile, run_dir / "applicant_profile.json")
        save_json_output(dossier, run_dir / "research_dossier.json")
        save_json_output(fit_analysis, run_dir / "fit_analysis.json")
        output_path = save_text_output(result, run_dir / "cover_letter.md")
        print(str(output_path))
        return

    if args.command == "pipeline":
        cv_path = _resolve_cv_path(args.cv_path, settings.cv_path)
        output_dir = _resolve_output_dir(args.output_dir)
        applicant_profile_path = _resolve_applicant_profile_path(args.applicant_profile, settings.applicant_profile_path)
        if applicant_profile_path is None or not applicant_profile_path.exists():
            _, applicant_profile_path = ensure_applicant_profile(applicant_profile_path)
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
        return

    parser.error(f"Unknown command: {args.command}")
