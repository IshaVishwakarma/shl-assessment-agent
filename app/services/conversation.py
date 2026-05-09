import re


# -----------------------------
# ROLE KEYWORDS
# -----------------------------

ROLE_KEYWORDS = [
    "developer",
    "engineer",
    "manager",
    "analyst",
    "sales",
    "designer",
    "leadership",
    "executive",
    "director",
    "cxo",

    # NEW DOMAIN ROLES
    "customer support",
    "customer service",
    "contact center",
    "call center",
    "graduate",
    "trainee",
    "finance",
    "accounting",
    "safety",
    "manufacturing",
    "healthcare"
]


# -----------------------------
# SENIORITY KEYWORDS
# -----------------------------

SENIORITY_KEYWORDS = [
    "entry",
    "junior",
    "mid",
    "senior",
    "lead",
    "manager",
    "director",
    "executive",
    "cxo"
]


# -----------------------------
# PERSONALITY TERMS
# -----------------------------

PERSONALITY_TERMS = [
    "communication",
    "leadership",
    "stakeholder",
    "teamwork",
    "personality",
    "behavior"
]


# -----------------------------
# TECH TERMS
# -----------------------------

TECH_TERMS = [
    "java",
    "python",
    ".net",
    "backend",
    "frontend",
    "react",
    "developer",
    "software",
    "api",
    "spring",
    "docker",
    "aws",
    "sql"
]


# -----------------------------
# DOMAIN ROLE INFERENCE
# -----------------------------

DOMAIN_ROLE_INFERENCE = {

    "customer_service": "customer service",

    "graduate": "graduate trainee",

    "safety": "manufacturing safety",

    "finance": "finance analyst",

    "software_engineering": "developer",

    "leadership": "executive leadership",

    "healthcare": "healthcare support"
}


# -----------------------------
# PURPOSE TERMS
# -----------------------------

SELECTION_TERMS = [
    "selection",
    "hiring",
    "compare candidates",
    "benchmark"
]

DEVELOPMENT_TERMS = [
    "development",
    "developmental",
    "feedback",
    "upskilling",
    "coaching"
]


# -----------------------------
# REFINEMENT TERMS
# -----------------------------

REFINEMENT_TERMS = [
    "also",
    "add",
    "include",
    "actually",
    "along with",
    "replace",
    "remove",
    "drop"
]


# -----------------------------
# ROLE INFERENCE
# -----------------------------

def infer_role_from_text(text):

    text = text.lower()

    # -------------------------
    # CUSTOMER SERVICE
    # -------------------------

    if any(
        word in text
        for word in [
            "customer support",
            "contact center",
            "call center",
            "customer service",
            "retail support"
        ]
    ):

        return "customer service"

    # -------------------------
    # GRADUATE
    # -------------------------

    if any(
        word in text
        for word in [
            "graduate",
            "trainee",
            "campus hiring",
            "entry level"
        ]
    ):

        return "graduate trainee"

    # -------------------------
    # SAFETY
    # -------------------------

    if any(
        word in text
        for word in [
            "safety",
            "manufacturing",
            "workplace safety",
            "dependability"
        ]
    ):

        return "manufacturing safety"

    # -------------------------
    # FINANCE
    # -------------------------

    if any(
        word in text
        for word in [
            "finance",
            "accounting",
            "numerical reasoning",
            "statistics"
        ]
    ):

        return "finance analyst"

    # -------------------------
    # HEALTHCARE
    # -------------------------

    if any(
        word in text
        for word in [
            "hipaa",
            "medical",
            "healthcare"
        ]
    ):

        return "healthcare support"

    return None


# -----------------------------
# EXTRACT CONTEXT
# -----------------------------

def extract_context(messages):

    context = {
        "role": None,
        "seniority": None,
        "needs_personality": False,
        "tech_stack": [],
        "is_refinement": False,
        "purpose": None,
        "leadership_scope": False,
        "completeness_score": 0,
        "ready_for_recommendation": False,
        "query": ""
    }

    # -------------------------
    # PROCESS ALL MESSAGES
    # -------------------------

    for msg in messages:

        text = msg["content"].lower()

        # ---------------------
        # ROLE DETECTION
        # ---------------------

        for role in ROLE_KEYWORDS:

            if role in text:

                context["role"] = role

        # ---------------------
        # DOMAIN ROLE INFERENCE
        # ---------------------

        if not context["role"]:

            inferred_role = (
                infer_role_from_text(text)
            )

            if inferred_role:

                context["role"] = (
                    inferred_role
                )

        # ---------------------
        # SENIORITY
        # ---------------------

        for level in SENIORITY_KEYWORDS:

            if level in text:

                context["seniority"] = level

        # ---------------------
        # PERSONALITY
        # ---------------------

        if any(
            term in text
            for term in PERSONALITY_TERMS
        ):

            context["needs_personality"] = True

        # ---------------------
        # TECH STACK
        # ---------------------

        for term in TECH_TERMS:

            if term in text:

                context["tech_stack"].append(term)

        # ---------------------
        # PURPOSE DETECTION
        # ---------------------

        if any(
            term in text
            for term in SELECTION_TERMS
        ):

            context["purpose"] = "selection"

        if any(
            term in text
            for term in DEVELOPMENT_TERMS
        ):

            context["purpose"] = "development"

        # ---------------------
        # LEADERSHIP SCOPE
        # ---------------------

        if any(
            term in text
            for term in [
                "leadership",
                "executive",
                "director",
                "cxo"
            ]
        ):

            context["leadership_scope"] = True

    # -------------------------
    # REMOVE DUPLICATES
    # -------------------------

    context["tech_stack"] = list(
        set(context["tech_stack"])
    )

    # -------------------------
    # DETECT REFINEMENT
    # -------------------------

    latest_user_message = ""

    for msg in reversed(messages):

        if msg["role"] == "user":

            latest_user_message = (
                msg["content"].lower()
            )

            break

    if any(
        term in latest_user_message
        for term in REFINEMENT_TERMS
    ):

        context["is_refinement"] = True

    # -------------------------
    # COMPLETENESS SCORING
    # -------------------------

    score = 0

    if context["role"]:
        score += 2

    if context["seniority"]:
        score += 2

    if context["purpose"]:
        score += 2

    if context["tech_stack"]:
        score += 2

    if context["needs_personality"]:
        score += 1

    if context["leadership_scope"]:
        score += 1

    context["completeness_score"] = score

    # -------------------------
    # RECOMMENDATION READINESS
    # -------------------------

    if score >= 2:

        context["ready_for_recommendation"] = True

    # -------------------------
    # STRUCTURED QUERY
    # -------------------------

    query_parts = []

    if context["role"]:
        query_parts.append(
            context["role"]
        )

    if context["seniority"]:
        query_parts.append(
            context["seniority"]
        )

    if context["purpose"]:
        query_parts.append(
            context["purpose"]
        )

    if context["tech_stack"]:
        query_parts.extend(
            context["tech_stack"]
        )

    if context["needs_personality"]:

        query_parts.extend([
            "personality",
            "communication",
            "leadership",
            "behavior"
        ])

    context["query"] = " ".join(query_parts)

    return context