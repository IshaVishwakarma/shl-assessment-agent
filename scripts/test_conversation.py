from app.services.conversation import extract_context


messages = [

    {
        "role": "user",
        "content": "Hiring a Java backend developer"
    },

    {
        "role": "assistant",
        "content": "What seniority level?"
    },

    {
        "role": "user",
        "content": "Mid-level with stakeholder communication"
    }
]


context = extract_context(messages)

print("\nExtracted Context:\n")

print(context)