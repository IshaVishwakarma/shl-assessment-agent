from app.services.agent import decide_next_action
from app.services.recommendation import generate_recommendations
from app.services.comparison import compare_assessments
from app.services.llm import generate_llm_response


# -----------------------------
# MAIN CHAT ORCHESTRATOR
# -----------------------------

def process_chat(messages):

    # -------------------------
    # DECISION ENGINE
    # -------------------------

    decision = decide_next_action(messages)

    action = decision["action"]

    context = decision["context"]

    # -------------------------
    # REFUSAL
    # -------------------------

    if action == "refuse":

        return {
            "reply": (
                "I can only assist with "
                "SHL assessment recommendations."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    # -------------------------
    # CLARIFICATION
    # -------------------------

    if action == "clarify":

        return {
            "reply": decision["question"],
            "recommendations": [],
            "end_of_conversation": False
        }

    # -------------------------
    # COMPARISON
    # -------------------------

    if action == "compare":

        latest_user_message = ""

        for msg in reversed(messages):

            if msg["role"] == "user":

                latest_user_message = (
                    msg["content"]
                )

                break

        comparison = compare_assessments(
            latest_user_message
        )

        return {
            "reply": comparison["reply"],
            "recommendations": [],
            "end_of_conversation": False
        }

    # -------------------------
    # REFINEMENT
    # -------------------------

    if action == "refine":

        recommendations = generate_recommendations(
            context
        )

        latest_user_message = ""

        for msg in reversed(messages):

            if msg["role"] == "user":

                latest_user_message = (
                    msg["content"]
                )

                break

        reply = generate_llm_response(
            latest_user_message,
            recommendations
        )

        return {
            "reply": reply,
            "recommendations": recommendations,
            "end_of_conversation": False
        }

    # -------------------------
    # RECOMMENDATIONS
    # -------------------------

    recommendations = generate_recommendations(
        context
    )

    latest_user_message = ""

    for msg in reversed(messages):

        if msg["role"] == "user":

            latest_user_message = (
                msg["content"]
            )

            break

    reply = generate_llm_response(
        latest_user_message,
        recommendations
    )

    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": False
    }