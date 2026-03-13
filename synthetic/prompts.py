QA_PROMPT = """
You are generating synthetic data to evaluate a medical hallucination detection system.

Using ONLY the information provided in the context below, generate three statements about the drug.

Context:
{context}

Create the following:

1. TRUE — a statement that is fully supported by the context.
2. CONTRADICTION — a statement that directly contradicts the TRUE statement.
3. UNCERTAIN — a statement that is ambiguous or not clearly supported by the context.

Rules:
- Do NOT introduce external medical knowledge.
- Use only the information in the context.
- Each statement must be one concise sentence.
- The contradiction must clearly conflict with the true statement.

Return ONLY valid JSON and nothing else.:

{
"true_statement": "...",
"contradiction_statement": "...",
"uncertain_statement": "..."
}
"""