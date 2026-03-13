from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
import os
import sys

# Ensure base directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import OPENAI_API_KEY

# Load semantic model once
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

# OpenAI client (API key from config)
client = OpenAI(api_key=OPENAI_API_KEY)


def semantic_relevance(premise, hypothesis):
    """
    Measures semantic similarity between premise and hypothesis.
    Low similarity → higher hallucination risk.
    """

    premise = premise[:400]
    hypothesis = hypothesis[:400]

    emb1 = semantic_model.encode(premise, convert_to_tensor=True)
    emb2 = semantic_model.encode(hypothesis, convert_to_tensor=True)

    similarity = util.cos_sim(emb1, emb2).item()

    relevance_risk = 1 - similarity
    relevance_risk = max(0, min(1, relevance_risk))

    return {
        "similarity": round(similarity, 3),
        "relevance_risk": round(relevance_risk, 3)
    }


def self_consistency_score(question):
    """
    Generates multiple answers and measures consistency between them.
    High disagreement → hallucination risk.
    """

    answers = []

    # Generate multiple answers
    for _ in range(3):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": question}],
            temperature=0.7
        )

        answers.append(response.choices[0].message.content)

    # Encode all answers once
    embeddings = semantic_model.encode(answers, convert_to_tensor=True)

    sims = []

    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            sim = util.cos_sim(embeddings[i], embeddings[j]).item()
            sims.append(sim)

    avg_sim = sum(sims) / len(sims)

    consistency_risk = 1 - avg_sim
    consistency_risk = max(0, min(1, consistency_risk))

    return {
        "answers": answers,
        "consistency_risk": round(consistency_risk, 3)
    }