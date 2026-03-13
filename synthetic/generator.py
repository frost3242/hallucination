from openai import OpenAI
from config.config import OPENAI_API_KEY
from synthetic.prompts import QA_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

def generate(context):

    prompt = QA_PROMPT.format(context=context)

    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=200,
        temperature=0.3
    )

    return r.choices[0].message.content