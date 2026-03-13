---
description: Run the autonomous optimization loop for the hallucination detection pipeline
---

This workflow is designed to be executed by an autonomous coding agent (like OpenClaw or OpenHands) to drive the continuous improvement of the hallucination detectors.

1. Activate your python environment.
```bash
# If using a virtual environment:
# source venv/bin/activate
```

2. Make sure you are on a fresh branch for research.
// turbo
```bash
git checkout -b autoresearch-tuning || git checkout autoresearch-tuning
```

3. Run the evaluation script once to establish the baseline and verify that all dependencies are installed and the detectors are loading properly without syntax errors.
// turbo
```bash
cd "c:\Users\Yash\Desktop\hallucination project"
python evaluation/evaluate_pipeline.py
```

4. Start the autonomous loop.
// turbo
```bash
python training/autoresearch.py
```

5. Monitor the output.
Wait for the loop to complete. The script is configured to evaluate the changes, commit on success, and revert on failure.
If the script crashes due to bad LLM Python syntax generation in `config/config.py`, manually checkout the last working config (`git checkout -- config/config.py`) and optionally restart the `autoresearch.py` process.

6. Report Back
Once the autoresearch loop finishes its iterations (or you stop it manually after observing significant improvement), summarize the baseline score vs. the new optimal score to the user.
