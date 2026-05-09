import json
import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from app.services.orchestrator import process_chat


# -----------------------------
# LOAD PARSED TRACES
# -----------------------------

PARSED_TRACE_FILE = (
    "evaluation/parsed_traces.json"
)


# -----------------------------
# NORMALIZE NAMES
# -----------------------------

def normalize_name(name):

    return (
        name.lower()
        .replace("&", "and")
        .replace("-", " ")
        .strip()
    )


# -----------------------------
# RECALL@K
# -----------------------------

def compute_recall(
    expected,
    predicted
):

    expected = set(
        normalize_name(x)
        for x in expected
    )

    predicted = set(
        normalize_name(x)
        for x in predicted
    )

    matches = expected.intersection(
        predicted
    )

    if len(expected) == 0:
        return 0

    return len(matches) / len(expected)


# -----------------------------
# RUN EVALUATION
# -----------------------------

def evaluate():

    # -------------------------
    # LOAD TRACES
    # -------------------------

    with open(
        PARSED_TRACE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        traces = json.load(f)

    recalls = []

    # -------------------------
    # PROCESS EACH TRACE
    # -------------------------

    for trace in traces:

        print("\n====================")
        print(trace["trace_name"])
        print("====================")

        # ---------------------
        # RUN AGENT
        # ---------------------

        response = process_chat(
            trace["messages"]
        )

        # ---------------------
        # PREDICTED RESULTS
        # ---------------------

        predicted = [
            rec["name"]
            for rec in response[
                "recommendations"
            ]
        ]

        # ---------------------
        # EXPECTED RESULTS
        # ---------------------

        expected = trace[
            "expected_assessments"
        ]

        # ---------------------
        # COMPUTE RECALL
        # ---------------------

        recall = compute_recall(
            expected,
            predicted
        )

        recalls.append(recall)

        # ---------------------
        # PRINT RESULTS
        # ---------------------

        print("\nExpected:")
        print(expected)

        print("\nPredicted:")
        print(predicted)

        print(f"\nRecall@5: {recall:.2f}")

    # -------------------------
    # FINAL METRICS
    # -------------------------

    if len(recalls) == 0:

        print("\nNo traces found.")
        return

    avg_recall = (
        sum(recalls) / len(recalls)
    )

    print("\n====================")
    print("FINAL METRICS")
    print("====================")

    print(
        f"\nAverage Recall@5: "
        f"{avg_recall:.2f}"
    )


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    evaluate()