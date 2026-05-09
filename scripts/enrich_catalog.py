import json


# -----------------------------
# LOAD NORMALIZED CATALOG
# -----------------------------

with open("db/catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)


# -----------------------------
# ROLE SEMANTICS
# -----------------------------

ROLE_SEMANTICS = {

    "developer": [
        "software engineer",
        "backend",
        "frontend",
        "full stack",
        "programming",
        "coding",
        "api",
        "microservices"
    ],

    "manager": [
        "leadership",
        "stakeholder management",
        "team management",
        "decision making",
        "communication"
    ],

    "sales": [
        "sales",
        "negotiation",
        "business development",
        "client interaction",
        "customer relationship"
    ],

    "analyst": [
        "analysis",
        "critical thinking",
        "reasoning",
        "problem solving",
        "data interpretation"
    ]
}


# -----------------------------
# CATEGORY SEMANTICS
# -----------------------------

CATEGORY_INFERENCE = {

    "Personality & Behavior": [
        "personality",
        "behavior",
        "leadership",
        "communication",
        "teamwork",
        "stakeholder management"
    ],

    "Ability & Aptitude": [
        "cognitive",
        "aptitude",
        "reasoning",
        "problem solving",
        "logical thinking"
    ],

    "Knowledge & Skills": [
        "technical skills",
        "software engineering",
        "programming",
        "coding"
    ],

    "Competencies": [
        "leadership",
        "decision making",
        "communication",
        "collaboration"
    ]
}


# -----------------------------
# TECHNOLOGY STACKS
# -----------------------------

TECH_STACKS = {

    ".net": [
        ".net",
        "wcf",
        "soa",
        "c#"
    ],

    "java": [
        "java",
        "spring",
        "j2ee"
    ],

    "frontend": [
        "javascript",
        "react",
        "angular",
        "frontend"
    ],

    "database": [
        "sql",
        "database",
        "mysql",
        "postgresql"
    ]
}


# -----------------------------
# PROCESS EACH ASSESSMENT
# -----------------------------

for item in catalog:

    search_text = item["search_text"].lower()

    enriched_keywords = []

    # -------------------------
    # CATEGORY ENRICHMENT
    # -------------------------

    for category, keywords in CATEGORY_INFERENCE.items():

        if category.lower() in search_text:

            enriched_keywords.extend(keywords)

    # -------------------------
    # ROLE INFERENCE
    # -------------------------

    if any(
        keyword in search_text
        for keyword in [
            "developer",
            "programming",
            "software",
            "coding",
            "api"
        ]
    ):

        enriched_keywords.extend(
            ROLE_SEMANTICS["developer"]
        )

    if any(
        keyword in search_text
        for keyword in [
            "manager",
            "leadership",
            "supervisor"
        ]
    ):

        enriched_keywords.extend(
            ROLE_SEMANTICS["manager"]
        )

    if any(
        keyword in search_text
        for keyword in [
            "sales",
            "client",
            "customer"
        ]
    ):

        enriched_keywords.extend(
            ROLE_SEMANTICS["sales"]
        )

    if any(
        keyword in search_text
        for keyword in [
            "analysis",
            "reasoning",
            "critical thinking"
        ]
    ):

        enriched_keywords.extend(
            ROLE_SEMANTICS["analyst"]
        )

    # -------------------------
    # TECHNOLOGY ENRICHMENT
    # -------------------------

    detected_tech = []

    for stack_name, stack_keywords in TECH_STACKS.items():

        if any(
            keyword in search_text
            for keyword in stack_keywords
        ):

            detected_tech.append(stack_name)

            enriched_keywords.extend(stack_keywords)

    # -------------------------
    # REMOVE DUPLICATES
    # -------------------------

    enriched_keywords = sorted(
        list(set(enriched_keywords))
    )

    # -------------------------
    # FINAL RETRIEVAL TEXT
    # -------------------------

    retrieval_text = f"""
    {item['search_text']}

    {' '.join(enriched_keywords)}

    {' '.join(detected_tech)}
    """

    item["enriched_keywords"] = enriched_keywords

    item["detected_tech"] = detected_tech

    item["retrieval_text"] = retrieval_text.strip()


# -----------------------------
# SAVE ENRICHED CATALOG
# -----------------------------

with open(
    "db/catalog_enriched.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        catalog,
        f,
        indent=2,
        ensure_ascii=False
    )


print("\nEnrichment complete.")
print(f"Processed records: {len(catalog)}")

print("\nSample enriched item:\n")
print(json.dumps(catalog[0], indent=2)[:5000])

print("\nSaved enriched catalog.")