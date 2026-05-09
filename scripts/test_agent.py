from app.services.agent import decide_next_action


# -----------------------------
# TEST CASES
# -----------------------------

cases = [

    [
        {
            "role": "user",
            "content": "I need an assessment"
        }
    ],

    [
        {
            "role": "user",
            "content": "Hiring a Java backend developer"
        }
    ],

    [
        {
            "role": "user",
            "content": "Compare OPQ and GSA"
        }
    ],

    [
        {
            "role": "user",
            "content": "Give hiring law advice"
        }
    ]
]


# -----------------------------
# RUN TESTS
# -----------------------------

for i, messages in enumerate(cases):

    result = decide_next_action(messages)

    print(f"\nCASE {i+1}")
    print(result)