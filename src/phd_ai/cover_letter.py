from __future__ import annotations

import json
from pathlib import Path

from phd_ai.cv import extract_cv_evidence
from phd_ai.research import build_llm


def generate_cover_letter(
    cv_path: Path,
    researcher: str,
    research_dossier: dict,
    fit_analysis: dict,
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

    evidence = extract_cv_evidence(cv_path=cv_path, fields=fields, api_key=api_key, model_name=model_name)
    llm = build_llm(api_key, model_name)
    prompt = PromptTemplate(
        template=(
            "You are helping draft a thoughtful PhD application cover letter.\n"
            "Use UK English spelling, grammar, and tone throughout.\n"
            "The target researcher is {researcher}.\n"
            "Use the research dossier, fit analysis, and CV evidence below to write a concise, professional letter "
            "that explicitly connects the applicant's prior research to the researcher's agenda.\n"
            "Avoid generic praise and be specific about overlapping topics, methods, and why the fit is credible.\n\n"
            "Research dossier:\n{research_dossier}\n\n"
            "Fit analysis:\n{fit_analysis}\n\n"
            "CV evidence:\n{text}\n"
        ),
        input_variables=["text", "researcher", "research_dossier", "fit_analysis"],
    )
    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    return chain.run(
        {
            "text": evidence,
            "researcher": researcher,
            "research_dossier": json.dumps(research_dossier, indent=2),
            "fit_analysis": json.dumps(fit_analysis, indent=2),
        }
    )
