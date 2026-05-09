import os
import re
import json


TRACE_DIR = "evaluation/traces"

OUTPUT_FILE = "evaluation/parsed_traces.json"


# -----------------------------
# EXTRACT USER MESSAGES
# -----------------------------

def extract_messages(content):

    messages = []

    user_blocks = re.findall(
        r"\*\*User\*\*\s*> (.+?)(?=\n\n|\Z)",
        content,
        re.DOTALL
    )

    for msg in user_blocks:

        messages.append({
            "role": "user",
            "content": msg.strip()
        })

    return messages


# -----------------------------
# EXTRACT EXPECTED ASSESSMENTS
# -----------------------------

def extract_assessments(content):

    assessments = []

    table_rows = re.findall(
        r"\|\s*\d+\s*\|\s*(.*?)\s*\|",
        content
    )

    for row in table_rows:

        name = row.strip()

        if name not in assessments:

            assessments.append(name)

    return assessments


# -----------------------------
# PARSE ALL FILES
# -----------------------------

def parse_all_traces():

    parsed = []

    for file in os.listdir(TRACE_DIR):

        if file.endswith(".md"):

            path = os.path.join(
                TRACE_DIR,
                file
            )

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                content = f.read()

            messages = extract_messages(
                content
            )

            assessments = extract_assessments(
                content
            )

            parsed.append({
                "trace_name": file,
                "messages": messages,
                "expected_assessments": assessments
            })

    return parsed


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    parsed = parse_all_traces()

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            parsed,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nParsed {len(parsed)} traces."
    )

    print(
        f"\nSaved to {OUTPUT_FILE}"
    )