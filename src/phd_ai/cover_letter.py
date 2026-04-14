from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from phd_ai.cv import extract_cv_evidence
from phd_ai.research import build_llm


def generate_cover_letter(
    cv_path: Path,
    researcher: str,
    research_dossier: dict,
    fit_analysis: dict,
    applicant_profile: dict,
    api_key: str,
    model_name: str,
) -> str:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate

    profile = research_dossier.get("profile", {})
    fields = []
    for item in profile.get("researcher_profile", []) if isinstance(profile, dict) else []:
        if isinstance(item, dict):
            if item.get("core_topics"):
                fields.append(item["core_topics"])
            if item.get("methods"):
                fields.append(item["methods"])

    if not fields:
        fields = ["research fit"]

    english_variant = (applicant_profile.get("english_variant") or "UK").upper()
    english_instruction = (
        "Use UK English spelling, grammar, and tone throughout."
        if english_variant == "UK"
        else "Use American English spelling, grammar, and tone throughout."
    )

    evidence = extract_cv_evidence(cv_path=cv_path, fields=fields, api_key=api_key, model_name=model_name)
    llm = build_llm(api_key, model_name)
    prompt = PromptTemplate(
        template=(
            "You are helping draft a thoughtful PhD application cover letter.\n"
            "{english_instruction}\n"
            "The target researcher is {researcher}.\n"
            "Today's date is {today}.\n"
            "Applicant profile:\n{applicant_profile}\n\n"
            "Use the research dossier, fit analysis, and CV evidence below to write a concise, professional letter "
            "that explicitly connects the applicant's prior research to the researcher's agenda.\n"
            "Use any reliable public-profile context included in the dossier to make the letter better informed, "
            "but do not invent facts.\n"
            "Include a proper cover-letter structure with sender details when they are available in the applicant profile.\n"
            "Avoid generic praise and be specific about overlapping topics, methods, and why the fit is credible.\n\n"
            "Research dossier:\n{research_dossier}\n\n"
            "Fit analysis:\n{fit_analysis}\n\n"
            "CV evidence:\n{text}\n"
        ),
        input_variables=["text", "researcher", "research_dossier", "fit_analysis", "applicant_profile", "today", "english_instruction"],
    )
    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    return chain.run(
        {
            "text": evidence,
            "researcher": researcher,
            "research_dossier": json.dumps(research_dossier, indent=2),
            "fit_analysis": json.dumps(fit_analysis, indent=2),
            "applicant_profile": json.dumps(applicant_profile, indent=2),
            "today": date.today().isoformat(),
            "english_instruction": english_instruction,
        }
    )
