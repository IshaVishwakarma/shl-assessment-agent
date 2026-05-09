from groq import Groq

from app.core.config import GROQ_API_KEY


client = Groq(
    api_key=GROQ_API_KEY
)


# -----------------------------
# GENERATE NATURAL RESPONSE
# -----------------------------

def generate_llm_response(
    user_query,
    recommendations
):

    recommendation_text = ""

    for rec in recommendations:

        recommendation_text += f"""
Assessment:
{rec['name']}

Type:
{rec['test_type']}

URL:
{rec['url']}

"""
    
    prompt = f"""
You are an SHL assessment recommendation assistant.

User Query:
{user_query}

Recommended Assessments:
{recommendation_text}

STRICT RULES:
- Only discuss the provided assessments
- Do NOT criticize, reject, or exclude any assessment
- Do NOT say an assessment is irrelevant
- Explain why each assessment helps evaluate the candidate
- Keep the tone recruiter-friendly and professional
- Be concise and grounded
- Keep response under 120 words
- Never invent assessments or capabilities
- Focus on strengths of the returned recommendations only

Generate a natural explanation of the recommendations.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    return response.choices[0].message.content