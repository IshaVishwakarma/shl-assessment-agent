from app.services.retrieval import hybrid_search


# -----------------------------
# DUAL RETRIEVAL
# -----------------------------

def generate_recommendations(context):

    technical_query_parts = []

    personality_query_parts = []

    # -------------------------
    # TECHNICAL QUERY
    # -------------------------

    if context["role"]:
        technical_query_parts.append(
            context["role"]
        )

    if context["tech_stack"]:
        technical_query_parts.extend(
            context["tech_stack"]
        )

    technical_query = " ".join(
        technical_query_parts
    )

    # -------------------------
    # PERSONALITY QUERY
    # -------------------------

    if context["needs_personality"]:

        personality_query = (
            technical_query +
            " personality leadership "
            "communication teamwork behavior"
        )

    else:

        personality_query = technical_query

    # -------------------------
    # RUN RETRIEVALS
    # -------------------------

    technical_results = hybrid_search(
        technical_query,
        top_k=10
    )

    personality_results = hybrid_search(
        personality_query,
        top_k=10
    )

    final_results = []

    seen = set()

    # -------------------------
    # ADD TECHNICAL FIRST
    # -------------------------

    for result in technical_results:

        metadata = result["metadata"]

        test_type = metadata[
            "test_types"
        ].lower()

        if (
            "knowledge" in test_type
            or "skills" in test_type
            or "simulation" in test_type
        ):

            if metadata["name"] not in seen:

                final_results.append({
                    "name": metadata["name"],
                    "url": metadata["url"],
                    "test_type": metadata["test_types"]
                })

                seen.add(metadata["name"])

        if len(final_results) >= 3:
            break

    # -------------------------
    # ADD PERSONALITY RESULTS
    # -------------------------

    if context["needs_personality"]:

        for result in personality_results:

            metadata = result["metadata"]

            test_type = metadata[
                "test_types"
            ].lower()

            if (
                "personality" in test_type
                or "competencies" in test_type
            ):

                if metadata["name"] not in seen:

                    final_results.append({
                        "name": metadata["name"],
                        "url": metadata["url"],
                        "test_type": metadata["test_types"]
                    })

                    seen.add(metadata["name"])

            if len(final_results) >= 5:
                break

    # -------------------------
    # FALLBACK FILLING
    # -------------------------

    if len(final_results) < 5:

        combined = (
            technical_results +
            personality_results
        )

        for result in combined:

            metadata = result["metadata"]

            if metadata["name"] not in seen:

                final_results.append({
                    "name": metadata["name"],
                    "url": metadata["url"],
                    "test_type": metadata["test_types"]
                })

                seen.add(metadata["name"])

            if len(final_results) >= 5:
                break

    return final_results[:5]