from __future__ import annotations

import json
from pathlib import Path

from phd_ai.cover_letter import generate_cover_letter
from phd_ai.cv import extract_cv_research_fit, extract_cv_skills
from phd_ai.output import build_run_directory, save_json_output, save_text_output
from phd_ai.research import build_research_dossier


def build_application_package(
    researcher: str,
    cv_path: Path,
    api_key: str,
    model_name: str,
    recent_paper_count: int = 3,
    notable_paper_count: int = 2,
    candidate_paper_count: int = 8,
) -> dict:
    research_dossier = build_research_dossier(
        researcher=researcher,
        api_key=api_key,
        model_name=model_name,
        recent_paper_count=recent_paper_count,
        notable_paper_count=notable_paper_count,
        candidate_paper_count=candidate_paper_count,
    )

    cv_skills = extract_cv_skills(
        cv_path=cv_path,
        api_key=api_key,
        model_name=model_name,
    )

    fit_analysis = extract_cv_research_fit(
        cv_path=cv_path,
        research_dossier=research_dossier,
        api_key=api_key,
        model_name=model_name,
    )

    cover_letter = generate_cover_letter(
        cv_path=cv_path,
        researcher=researcher,
        research_dossier=research_dossier,
        fit_analysis=fit_analysis,
        api_key=api_key,
        model_name=model_name,
    )

    return {
        "researcher": researcher,
        "research_dossier": research_dossier,
        "cv_skills": cv_skills,
        "fit_analysis": fit_analysis,
        "cover_letter": cover_letter,
    }


def format_application_package(package: dict) -> str:
    return json.dumps(package, indent=2)


def save_cover_letter_from_package(package: dict, output_dir: Path) -> Path:
    researcher = package["researcher"]
    cover_letter = package["cover_letter"]
    output_path = output_dir / "cover_letter.md"
    return save_text_output(cover_letter, output_path)


def _as_bullets(value) -> list[str]:
    if isinstance(value, list):
        bullets: list[str] = []
        for item in value:
            if isinstance(item, str):
                bullets.append(item)
            elif isinstance(item, dict):
                for inner_value in item.values():
                    if isinstance(inner_value, str):
                        bullets.append(inner_value)
            else:
                bullets.append(str(item))
        return bullets
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def build_research_summary_markdown(package: dict, saved_paths: dict) -> str:
    dossier = package.get("research_dossier", {})
    fit_analysis = package.get("fit_analysis", {})
    profile = dossier.get("profile", {})
    profile_items = profile.get("researcher_profile", []) if isinstance(profile, dict) else []

    core_topics: list[str] = []
    methods: list[str] = []
    open_directions: list[str] = []
    for item in profile_items:
        if not isinstance(item, dict):
            continue
        core_topics.extend(_as_bullets(item.get("core_topics")))
        methods.extend(_as_bullets(item.get("methods")))
        open_directions.extend(_as_bullets(item.get("open_directions")))

    fit_items = fit_analysis.get("cv_fit", []) if isinstance(fit_analysis, dict) else []
    matching_topics: list[str] = []
    matching_methods: list[str] = []
    selling_points: list[str] = []
    for item in fit_items:
        if not isinstance(item, dict):
            continue
        matching_topics.extend(_as_bullets(item.get("matching_topics")))
        matching_methods.extend(_as_bullets(item.get("matching_methods")))
        selling_points.extend(_as_bullets(item.get("selling_points")))

    recent_papers = dossier.get("recent_papers", [])
    notable_papers = dossier.get("notable_papers", [])

    lines = [
        f"# Application Summary: {package['researcher']}",
        "",
        "## Saved Artefacts",
        f"- Research dossier: `{saved_paths['research_dossier']}`",
        f"- CV skills: `{saved_paths['cv_skills']}`",
        f"- Fit analysis: `{saved_paths['fit_analysis']}`",
        f"- Cover letter: `{saved_paths['cover_letter']}`",
        f"- Full package: `{saved_paths['application_package']}`",
        "",
        "## Recent Papers",
    ]

    for paper in recent_papers:
        lines.extend(
            [
                f"- `{paper.get('arxiv_id', '')}` {paper.get('title', '')} ({paper.get('published', '')})",
                f"  Abstract: {paper.get('abstract', '')}",
            ]
        )

    lines.extend(["", "## Notable Papers"])
    for paper in notable_papers:
        lines.extend(
            [
                f"- `{paper.get('arxiv_id', '')}` {paper.get('title', '')} ({paper.get('published', '')})",
                f"  Abstract: {paper.get('abstract', '')}",
            ]
        )

    if dossier.get("notable_selection_reasoning"):
        lines.extend(["", "## Why These Papers Look Notable", dossier["notable_selection_reasoning"]])

    lines.extend(["", "## Inferred Research Themes"])
    if core_topics:
        lines.extend([f"- {item}" for item in core_topics])
    if methods:
        lines.extend(["", "## Inferred Methods"])
        lines.extend([f"- {item}" for item in methods])
    if open_directions:
        lines.extend(["", "## Possible Directions"])
        lines.extend([f"- {item}" for item in open_directions])

    lines.extend(["", "## Common Interests and Fit"])
    if matching_topics:
        lines.extend([f"- Shared topics: {item}" for item in matching_topics])
    if matching_methods:
        lines.extend([f"- Shared methods: {item}" for item in matching_methods])
    if selling_points:
        lines.extend([f"- Selling point: {item}" for item in selling_points])

    if not matching_topics and not matching_methods and not selling_points:
        lines.append("- See `fit_analysis.json` for the extracted alignment details.")

    return "\n".join(lines) + "\n"


def save_application_package(package: dict, output_dir: Path) -> dict:
    run_dir = build_run_directory(output_dir, package["researcher"])
    run_dir.mkdir(parents=True, exist_ok=True)

    research_dossier_path = save_json_output(package["research_dossier"], run_dir / "research_dossier.json")
    cv_skills_path = save_json_output(package["cv_skills"], run_dir / "cv_skills.json")
    fit_analysis_path = save_json_output(package["fit_analysis"], run_dir / "fit_analysis.json")
    cover_letter_path = save_text_output(package["cover_letter"], run_dir / "cover_letter.md")
    package_path = save_json_output(package, run_dir / "application_package.json")

    saved_paths = {
        "run_dir": str(run_dir),
        "research_dossier": str(research_dossier_path),
        "cv_skills": str(cv_skills_path),
        "fit_analysis": str(fit_analysis_path),
        "cover_letter": str(cover_letter_path),
        "application_package": str(package_path),
    }
    research_summary_path = save_text_output(
        build_research_summary_markdown(package, saved_paths),
        run_dir / "research_summary.md",
    )
    saved_paths["research_summary"] = str(research_summary_path)

    summary_lines = [
        f"Researcher: {package['researcher']}",
        "",
        "Saved artefacts:",
        f"- Research dossier: {saved_paths['research_dossier']}",
        f"- CV skills: {saved_paths['cv_skills']}",
        f"- Fit analysis: {saved_paths['fit_analysis']}",
        f"- Research summary: {saved_paths['research_summary']}",
        f"- Cover letter: {saved_paths['cover_letter']}",
        f"- Full package: {saved_paths['application_package']}",
    ]
    save_text_output("\n".join(summary_lines), run_dir / "README.md")

    return saved_paths
