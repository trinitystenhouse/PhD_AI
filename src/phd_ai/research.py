from __future__ import annotations

from dataclasses import dataclass
import json
import re
from urllib.parse import urlencode


@dataclass(frozen=True)
class ResearchPaper:
    researcher: str
    arxiv_id: str
    title: str
    abstract: str
    published: str
    categories: tuple[str, ...]


def build_llm(api_key: str, model_name: str):
    from langchain.chat_models import ChatOpenAI

    return ChatOpenAI(
        model_name=model_name,
        temperature=0,
        max_tokens=2000,
        openai_api_key=api_key,
    )


def get_latest_paper_for_researcher(researcher: str) -> ResearchPaper:
    return get_recent_papers_for_researcher(researcher, limit=1)[0]


def _normalise_name(value: str) -> str:
    value = value.casefold()
    value = value.replace("’", "'")
    value = re.sub(r"[^a-z0-9\s']", " ", value)
    value = value.replace("'", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _author_matches_researcher(author_name: str, researcher: str) -> bool:
    author_norm = _normalise_name(author_name)
    researcher_norm = _normalise_name(researcher)

    if author_norm == researcher_norm:
        return True

    researcher_tokens = researcher_norm.split()
    author_tokens = author_norm.split()
    if not researcher_tokens or not author_tokens:
        return False

    return all(token in author_tokens for token in researcher_tokens)


def _build_arxiv_search_url(researcher: str, size: int = 50) -> str:
    query = urlencode(
        {
            "query": researcher,
            "searchtype": "all",
            "abstracts": "show",
            "order": "-announced_date_first",
            "size": size,
        }
    )
    return f"https://arxiv.org/search/?{query}"


def _paper_from_result(researcher: str, result) -> ResearchPaper:
    published = getattr(result, "published", None)
    published_str = published.date().isoformat() if published else ""
    categories = tuple(getattr(result, "categories", []) or [])

    return ResearchPaper(
        researcher=researcher,
        arxiv_id=result.get_short_id(),
        title=result.title,
        abstract=result.summary,
        published=published_str,
        categories=categories,
    )


def get_recent_papers_for_researcher(researcher: str, limit: int = 5, search_limit: int = 20) -> list[ResearchPaper]:
    import requests
    from bs4 import BeautifulSoup

    size = max(search_limit, limit, 50)
    url = _build_arxiv_search_url(researcher, size=size)
    response = requests.get(
        url,
        headers={"User-Agent": "PhD-AI/0.1 (+https://arxiv.org)"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.select("li.arxiv-result")
    papers: list[ResearchPaper] = []
    seen_ids: set[str] = set()

    for result in results:
        authors = [author.get_text(" ", strip=True) for author in result.select("p.authors a")]
        if not any(_author_matches_researcher(author_name, researcher) for author_name in authors):
            continue

        abs_link = result.select_one("p.list-title a[href*='/abs/']")
        if abs_link is None:
            continue

        href = abs_link.get("href", "")
        arxiv_id = href.rstrip("/").split("/")[-1].strip()
        if not arxiv_id or arxiv_id in seen_ids:
            continue

        title_el = result.select_one("p.title")
        title = title_el.get_text(" ", strip=True) if title_el else ""

        abstract_el = result.select_one("span.abstract-full")
        abstract = abstract_el.get_text(" ", strip=True) if abstract_el else ""
        abstract = re.sub(r"^\s*Abstract:\s*", "", abstract)
        abstract = re.sub(r"\s*(△ Less|Less)\s*$", "", abstract).strip()

        meta_el = result.select_one("p.is-size-7")
        meta_text = meta_el.get_text(" ", strip=True) if meta_el else ""
        published_match = re.search(r"Submitted\s+(\d{1,2}\s+\w+\s+\d{4})", meta_text)
        published = published_match.group(1) if published_match else ""

        category_tags = [tag.get_text(" ", strip=True) for tag in result.select("span.tag")]

        papers.append(
            ResearchPaper(
                researcher=researcher,
                arxiv_id=arxiv_id,
                title=title,
                abstract=abstract,
                published=published,
                categories=tuple(category_tags),
            )
        )
        seen_ids.add(arxiv_id)

        if len(papers) >= limit:
            break

    if not papers:
        raise ValueError(
            f"No arXiv papers matched '{researcher}' from search results. "
            f"Checked {url}"
        )

    return papers


def ensure_minimum_paper_count(papers: list[ResearchPaper], researcher: str, minimum_count: int = 5) -> list[ResearchPaper]:
    unique_ids = {paper.arxiv_id for paper in papers}
    if len(unique_ids) < minimum_count:
        raise ValueError(
            f"Only found {len(unique_ids)} distinct arXiv papers for '{researcher}'. "
            f"This pipeline requires at least {minimum_count} separate papers to build a reliable profile. "
            f"Try checking https://arxiv.org/search/?query={researcher.replace(' ', '+')}&searchtype=all&abstracts=show&order=-announced_date_first&size=50"
        )
    return papers


def _extract_json_object(text: str) -> dict:
    fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced_match:
        return json.loads(fenced_match.group(1))

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise ValueError("Model response did not contain valid JSON.")


def select_notable_papers(
    researcher: str,
    papers: list[ResearchPaper],
    api_key: str,
    model_name: str,
    notable_paper_count: int = 2,
) -> dict:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate

    llm = build_llm(api_key, model_name)
    prompt = PromptTemplate(
        template=(
            "You are analysing a researcher's papers.\n"
            "Researcher: {researcher}\n\n"
            "Below is a candidate list of papers with ids, titles, dates, and abstracts.\n"
            "Select the {notable_paper_count} papers that seem most representative or notable for understanding this "
            "researcher's agenda. Since citation data is unavailable, infer notability from recurrence of themes, "
            "scope, centrality, and how clearly the papers express the research programme.\n"
            "Write the reasoning in UK English.\n\n"
            "{papers_text}\n\n"
            "Return valid JSON with this exact shape:\n"
            "{{\n"
            '  "selected_ids": ["id1", "id2"],\n'
            '  "reasoning": "short explanation"\n'
            "}}\n"
        ),
        input_variables=["researcher", "papers_text", "notable_paper_count"],
    )
    papers_text = "\n\n".join(
        [
            f"ID: {paper.arxiv_id}\nDate: {paper.published}\nTitle: {paper.title}\nAbstract: {paper.abstract}"
            for paper in papers
        ]
    )
    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    raw = chain.run(
        {
            "researcher": researcher,
            "papers_text": papers_text,
            "notable_paper_count": notable_paper_count,
        }
    )
    parsed = _extract_json_object(raw)
    selected_ids = parsed.get("selected_ids", [])
    selected = [paper for paper in papers if paper.arxiv_id in selected_ids][:notable_paper_count]

    if not selected:
        selected = papers[:notable_paper_count]

    return {
        "papers": [
            {
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "published": paper.published,
                "abstract": paper.abstract,
            }
            for paper in selected
        ],
        "reasoning": parsed.get("reasoning", ""),
    }


def synthesize_researcher_profile(researcher: str, papers: list[ResearchPaper], api_key: str, model_name: str) -> dict:
    from kor.extraction import create_extraction_chain

    from phd_ai.schemas import build_researcher_profile_schema

    llm = build_llm(api_key, model_name)
    combined_text = "\n\n".join(
        [
            f"Title: {paper.title}\nDate: {paper.published}\nAbstract: {paper.abstract}"
            for paper in papers
        ]
    )
    chain = create_extraction_chain(llm, build_researcher_profile_schema())
    extracted = chain.run(combined_text)
    return extracted.get("data", extracted)


def extract_research_profile(researcher: str, api_key: str, model_name: str) -> dict:
    from kor.extraction import create_extraction_chain

    from phd_ai.schemas import build_research_schema

    llm = build_llm(api_key, model_name)
    paper = get_latest_paper_for_researcher(researcher)
    chain = create_extraction_chain(llm, build_research_schema())
    extracted = chain.run(paper.abstract)

    return {
        "researcher": paper.researcher,
        "arxiv_id": paper.arxiv_id,
        "title": paper.title,
        "abstract": paper.abstract,
        "published": paper.published,
        "profile": extracted.get("data", extracted),
    }


def build_research_dossier(
    researcher: str,
    api_key: str,
    model_name: str,
    recent_paper_count: int = 5,
    notable_paper_count: int = 2,
    candidate_paper_count: int = 8,
) -> dict:
    minimum_paper_count = 5
    recent_paper_count = max(recent_paper_count, minimum_paper_count)
    candidate_paper_count = max(candidate_paper_count, minimum_paper_count, recent_paper_count)

    candidate_papers = get_recent_papers_for_researcher(
        researcher=researcher,
        limit=max(recent_paper_count, candidate_paper_count),
        search_limit=max(candidate_paper_count, 20),
    )
    candidate_papers = ensure_minimum_paper_count(
        papers=candidate_papers,
        researcher=researcher,
        minimum_count=minimum_paper_count,
    )
    recent_papers = candidate_papers[:recent_paper_count]
    notable = select_notable_papers(
        researcher=researcher,
        papers=candidate_papers[:candidate_paper_count],
        api_key=api_key,
        model_name=model_name,
        notable_paper_count=notable_paper_count,
    )
    profile = synthesize_researcher_profile(
        researcher=researcher,
        papers=recent_papers + [
            ResearchPaper(
                researcher=researcher,
                arxiv_id=paper["arxiv_id"],
                title=paper["title"],
                abstract=paper["abstract"],
                published=paper.get("published", ""),
                categories=tuple(),
            )
            for paper in notable["papers"]
            if paper["arxiv_id"] not in {recent.arxiv_id for recent in recent_papers}
        ],
        api_key=api_key,
        model_name=model_name,
    )

    return {
        "researcher": researcher,
        "recent_papers": [
            {
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "published": paper.published,
                "abstract": paper.abstract,
            }
            for paper in recent_papers
        ],
        "notable_papers": notable["papers"],
        "notable_selection_reasoning": notable["reasoning"],
        "profile": profile,
    }
