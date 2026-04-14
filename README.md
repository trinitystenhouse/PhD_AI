<<<<<<< HEAD
# PhD_AI
Can generate concepts and fields in research papers, taking input of a researcher's name. Will eventually link to CV, so it will help identify common fields of interest between you and researchers and produce a cover letter/email to them, to help you get started with PhD applications. 

Run 'main.py' after inputting the name of a researcher of your choosing
You may need to change the engineered prompt to specify your area of interest (it is currently 'physics' and 'mathematics' based), and add some examples. 
To add such examples, simply find the abstract of a research paper, paste it, and note the key concepts and fields within it. 

Note: you will need to obtain your own OpenAI API key. This is easy and there are plenty of tutorials on youtube. 
You then need to set up a .env file in your Project folder, and put the key in there.
Run source .env (or similar) in terminal for your Project to link your .env as the source for keys. 
The conda environment for the project is here in the repo, you will also need to configure that.
=======
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

## Usage

Run the full linked pipeline:

```bash
python main.py --researcher "Ciaran O'Hare"
```

This saves a full run folder into `outputs/applications/`, for example:

```text
outputs/applications/20260414-153012_ciaran-ohare/
├── README.md
├── application_package.json
├── cover_letter.md
├── cv_skills.json
├── fit_analysis.json
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
2. infer a small set of notable/representative papers,
3. synthesise a researcher profile,
4. read your CV,
5. analyse topic and method overlap,
6. generate a linked cover letter.

The generated writing is instructed to use UK English.

## Notes

- `wandb` logging is optional and disabled by default unless you configure it yourself.
- The codebase is still intentionally lightweight; it is organised as a prototype application rather than a production service.
>>>>>>> 6ae6139 (pushing things i kept locally for years)
