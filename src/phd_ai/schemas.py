def build_research_schema():
    from kor.nodes import Object, Text

    return Object(
        id="abstract",
        description="The abstract of a research paper.",
        attributes=[
            Text(
                id="concepts",
                description="A list of key physics or mathematical concepts discussed by the paper.",
            ),
            Text(
                id="fields",
                description="A list of research fields that best capture the paper.",
            ),
        ],
        examples=[
            (
                "Effective field theories of dark energy are constrained by gravitational wave observations.",
                [
                    {"concepts": ["Effective field theory", "Dark energy", "Gravitational waves"]},
                    {"fields": ["Cosmology", "Theoretical physics"]},
                ],
            ),
            (
                "String compactifications require fluxes and no-boundary solutions can explain their origin.",
                [
                    {"concepts": ["String compactification", "Fluxes", "No-boundary solutions"]},
                    {"fields": ["String theory", "Cosmology"]},
                ],
            ),
        ],
    )


def build_researcher_profile_schema():
    from kor.nodes import Object, Text

    return Object(
        id="researcher_profile",
        description="A synthesized profile of a researcher's agenda based on several papers.",
        attributes=[
            Text(
                id="core_topics",
                description="A list of the researcher's recurring core topics and subject areas.",
            ),
            Text(
                id="methods",
                description="A list of methods, techniques, or styles of investigation common in their work.",
            ),
            Text(
                id="open_directions",
                description="A list of future directions, unsolved problems, or opportunities implied by the papers.",
            ),
        ],
        examples=[
            (
                "Across these papers the author studies dark matter phenomenology, direct detection, axions, and experimental signatures, often combining theoretical modeling with sensitivity forecasts.",
                [
                    {"core_topics": ["Dark matter", "Axions", "Direct detection"]},
                    {"methods": ["Phenomenology", "Sensitivity forecasting", "Theoretical modeling"]},
                    {"open_directions": ["Experimental discovery opportunities", "Model discrimination"]},
                ],
            )
        ],
    )


def build_cv_skills_schema():
    from kor.nodes import Object, Text

    return Object(
        id="cv",
        description="A CV containing research, technical, and interpersonal experience.",
        attributes=[
            Text(
                id="concepts",
                description="A list of key concepts, methods, or competencies shown in the CV.",
            ),
            Text(
                id="fields",
                description="A list of fields or skill areas the CV demonstrates.",
            ),
        ],
        examples=[
            (
                "Simulating the initial state of the universe and computing star formation properties.",
                [
                    {"concepts": ["Simulation", "Star formation"]},
                    {"fields": ["Computational physics", "Astrophysics"]},
                ],
            ),
            (
                "Managing a student union, representing members, and drafting policy.",
                [
                    {"concepts": ["Management", "Leadership", "Policy writing"]},
                    {"fields": ["Management", "Leadership", "Policy"]},
                ],
            ),
        ],
    )


def build_cv_research_fit_schema():
    from kor.nodes import Object, Text

    return Object(
        id="cv_fit",
        description="How a CV aligns with a target research profile.",
        attributes=[
            Text(
                id="matching_topics",
                description="A list of research topics shared between the CV and the target research profile.",
            ),
            Text(
                id="matching_methods",
                description="A list of methods or technical approaches that align well.",
            ),
            Text(
                id="selling_points",
                description="A list of concise selling points that make the applicant a compelling fit.",
            ),
        ],
        examples=[
            (
                "The CV shows simulation-heavy astrophysics work and machine learning for physics, which aligns with the group's computational modeling and data-analysis style.",
                [
                    {"matching_topics": ["Astrophysics", "Particle physics"]},
                    {"matching_methods": ["Simulation", "Machine learning", "Data analysis"]},
                    {"selling_points": ["Strong quantitative background", "Relevant computational toolkit"]},
                ],
            )
        ],
    )
