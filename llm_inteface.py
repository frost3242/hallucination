from openai import OpenAI
from config import LLM_MODEL, OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(prompt):

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content