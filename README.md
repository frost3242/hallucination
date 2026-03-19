# Medical Hallucination Detection & Verification System

This intelligent pipeline is engineered to act as an enforcement layer for medical AI systems. Instead of making impossible promises about catching every error, this autonomous architecture algorithmically **maximizes detection performance on an evolving hard-case distribution**.

By utilizing a closed-domain RAG (Retrieval-Augmented Generation) approach, it enforces **Strict Extractive Logic** against unstructured text. If a Generated Hypothesis cannot be strictly verified against the scraped FDA text block, it is instantly mathematically graded as a 1.0 (100%) hallucination risk.

## End-to-End System Architecture

1. **Autonomous Ingestion (`run_pipeline.py`)**  
   The system constantly crawls new FDA drug labels and untapped medical web APIs, turning massive HTML blocks into clean, deduplicated `evidence_sentence` splits via `spaCy`.
2. **Dynamic Active Learning (`active_learning.py` + `generator.py`)**  
   For every new document scraped, a lightweight LLM drafts 3 synthetic test cases (True, Contradiction, and Unverified/Neutral assertions). These tests are committed directly to `golden_data.json` so the test suite becomes permanently harder to beat every day.
3. **Strict Validation Pipeline (`evaluate_pipeline.py`)**  
   Built on heavy transformer models like `DeBERTa-v3`, the system grades the LLM's assertions explicitly against the provided context blocks. Any unverified claim ("Neutral") incurs an immediate 100% risk penalty.
4. **Agentic Optimizer Daemon (`autoresearch.py`)**  
   Running endlessly in the background, this AI researcher queries the `golden_data.json` baseline and prompts `GPT-4o` to dynamically tweak the mathematical threshold weights in `config.py` until the highest possible detection score is safely committed to GitHub.

## Project Structure

```bash
hallucination project/
├── config/              # Central metrics thresholds adjusted by the Autoresearch agent
├── evaluation/          # Dynamic test suite (golden_data.json) & metric scoring
├── hallucination/       # Core OCI, PLI, and Semantic Detectors enforcing standard NLI
├── ingestion/           # API and Web Scraper modules 
├── pipeline/            # run_pipeline.py linking the disparate ETL and AI processes
├── processing/          # Normalization and Deduplication Logic
├── synthetic/           # GPT-4o-mini data generator for active learning
├── training/            # Autoresearch Loop (The optimizer daemon)
└── workflows/           # Agentic guidelines for interacting with the AI Agent
```

## Running the Architecture

To start the data extraction and test-generation pipeline:
```bash
python pipeline/run_pipeline.py
```

To run the background optimizer loop daemon:
```bash
python training/autoresearch.py
```
