from __future__ import annotations

import json
from pathlib import Path

from phd_ai.research import build_llm


def load_cv(cv_path: Path):
    from langchain.document_loaders import PyPDFLoader

    if not cv_path.exists():
        raise FileNotFoundError(f"CV file not found: {cv_path}")
    loader = PyPDFLoader(str(cv_path))
    return loader.load_and_split()


def extract_cv_evidence(cv_path: Path, fields: list[str], api_key: str, model_name: str) -> str:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate

    llm = build_llm(api_key, model_name)
    prompt = PromptTemplate(
        template=(
            "You are helping tailor a PhD application.\n"
            "Use UK English spelling and phrasing in your response.\n"
            "Read the CV below and identify concrete examples that show strength in these fields: {fields}.\n\n"
            "CV:\n{text}\n\n"
            "Return a concise deduplicated bullet list of the form 'Field: evidence'. "
            "Only include evidence grounded in the CV."
        ),
        input_variables=["text", "fields"],
    )
    documents = load_cv(cv_path)
    cv_text = "\n\n".join(page.page_content for page in documents)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    return chain.run({"text": cv_text, "fields": fields})


def extract_cv_skills(cv_path: Path, api_key: str, model_name: str) -> dict:
    from kor.extraction import create_extraction_chain

    from phd_ai.schemas import build_cv_skills_schema

    llm = build_llm(api_key, model_name)
    documents = load_cv(cv_path)
    combined_text = "\n\n".join(page.page_content for page in documents)
    chain = create_extraction_chain(llm, build_cv_skills_schema())
    return chain.run(combined_text)


def extract_cv_research_fit(cv_path: Path, research_dossier: dict, api_key: str, model_name: str) -> dict:
    from kor.extraction import create_extraction_chain

    from phd_ai.schemas import build_cv_research_fit_schema

    llm = build_llm(api_key, model_name)
    documents = load_cv(cv_path)
    cv_text = "\n\n".join(page.page_content for page in documents)
    research_text = json.dumps(research_dossier, indent=2)
    combined_text = (
        "Research dossier:\n"
        f"{research_text}\n\n"
        "Candidate CV:\n"
        f"{cv_text}"
    )
    chain = create_extraction_chain(llm, build_cv_research_fit_schema())
    return chain.run(combined_text)
