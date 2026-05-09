from app.services.conversation import extract_context


# -----------------------------
# OFF-TOPIC TERMS
# -----------------------------

OFF_TOPIC_TERMS = [
    "salary",
    "legal",
    "law",
    "lawsuit",
    "tax",
    "politics",
    "fire employee",
    "termination",
    "visa",
    "immigration"
]


# -----------------------------
# COMPARISON TERMS
# -----------------------------

COMPARISON_TERMS = [
    "compare",
    "difference",
    "vs",
    "versus"
]


# -----------------------------
# DECISION ENGINE
# -----------------------------

def decide_next_action(messages):

    # -------------------------
    # RAW USER MESSAGE
    # -------------------------

    latest_user_message = ""

    for msg in reversed(messages):

        if msg["role"] == "user":

            latest_user_message = (
                msg["content"].lower()
            )

            break

    # -------------------------
    # CONTEXT EXTRACTION
    # -------------------------

    context = extract_context(messages)

    # -------------------------
    # OFF-TOPIC DETECTION
    # -------------------------

    if any(
        term in latest_user_message
        for term in OFF_TOPIC_TERMS
    ):

        return {
            "action": "refuse",
            "reason": "off_topic",
            "context": context
        }

    # -------------------------
    # COMPARISON DETECTION
    # -------------------------

    if any(
        term in latest_user_message
        for term in COMPARISON_TERMS
    ):

        return {
            "action": "compare",
            "context": context
        }

    # -------------------------
    # REFINEMENT DETECTION
    # -------------------------

    if context["is_refinement"]:

        return {
            "action": "refine",
            "context": context
        }

    # -------------------------
    # CLARIFICATION LOGIC
    # -------------------------

    if not context["role"]:

        return {
            "action": "clarify",
            "question": (
                "What role are you hiring for?"
            ),
            "context": context
        }

    # -------------------------
    # RECOMMENDATION READY
    # -------------------------

    return {
        "action": "recommend",
        "context": context
    }