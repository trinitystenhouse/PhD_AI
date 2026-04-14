# PhD AI

`PhD AI` is a small research-assistant project for tailoring PhD applications.

It can:

- take a researcher's name as the only required research input
- read at least five recent papers and infer a smaller set of notable, representative papers
- synthesise the researcher's core topics, methods, and directions
- read a candidate CV from PDF
- analyse the fit between the candidate's research background and the target research agenda
- draft a tailored cover letter that explicitly links the two

## Project Structure

```text
.
├── main.py
├── scraper.py
├── CV_load.py
├── write_cover_letter.py
├── link_with_CV.py
├── src/phd_ai/
│   ├── cli.py
│   ├── config.py
│   ├── cover_letter.py
│   ├── cv.py
│   ├── research.py
│   └── schemas.py
├── pyproject.toml
└── environment.yml
```

The root scripts are lightweight compatibility entry points. The actual application logic lives in `src/phd_ai/`.

## Setup

1. Create an environment from `environment.yml`.
2. Copy `.env.example` to `.env`.
3. Set:
   - `OPENAI_API_KEY`
   - `CV_PATH`
4. Install the project in editable mode:

```bash
pip install -e .
```

5. Optionally create an applicant profile for letter headers and language preference:

```bash
python collect_applicant_info.py
```

## Usage

Run the full linked pipeline:

```bash
python main.py --researcher "Ciaran O'Hare"
```

If you want to explicitly point at an applicant profile:

```bash
python main.py --researcher "Ciaran O'Hare" --applicant-profile ./applicant_profile.json
```

This saves a full run folder into `outputs/applications/`, for example:

```text
outputs/applications/20260414-153012_ciaran-ohare/
├── README.md
├── application_package.json
├── applicant_profile.json
├── cover_letter.md
├── cv_skills.json
├── fit_analysis.json
├── public_information.json
├── research_summary.md
└── research_dossier.json
```

Extract CV evidence for fields:

```bash
python CV_load.py --fields Cosmology "Machine Learning"
```

Generate only the cover letter stage:

```bash
python write_cover_letter.py --researcher "Andrew Tolley"
```

Extract skills from a CV:

```bash
python link_with_CV.py
```

You can also use the unified CLI:

```bash
phd-ai pipeline --researcher "Ciaran O'Hare"
phd-ai dossier --researcher "Ciaran O'Hare"
phd-ai research --researcher "Ciaran O'Hare"
phd-ai cv-evidence --fields Cosmology "Machine Learning"
phd-ai fit --researcher "Andrew Tolley"
phd-ai cover-letter --researcher "Andrew Tolley"
phd-ai cv-skills
```

To choose a different directory for saved outputs:

```bash
python main.py --researcher "Ciaran O'Hare" --output-dir ./letters
phd-ai cover-letter --researcher "Andrew Tolley" --output-dir ./letters
```

The main workflow is now `main.py` or `phd-ai pipeline`, both of which:

1. fetch at least five recent arXiv papers for the named researcher,
2. Google-search `"<name> researcher"` for further public context,
3. infer a small set of notable/representative papers,
4. synthesise a researcher profile,
5. read your CV,
6. analyse topic and method overlap,
7. generate a linked cover letter.

The generated writing is instructed to use UK English.
You can override that by setting `UK` or `US` when you create the applicant profile.

## Notes

- `wandb` logging is optional and disabled by default unless you configure it yourself.
- The codebase is still intentionally lightweight; it is organised as a prototype application rather than a production service.
