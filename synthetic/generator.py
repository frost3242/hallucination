from openai import OpenAI
from config.config import OPENAI_API_KEY
from synthetic.prompts import QA_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

def generate(context):

    prompt = QA_PROMPT.replace("{context}", context)

    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=800,
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    return r.choices[0].message.content