import os
import sys
import subprocess
import re
from openai import OpenAI

# Required to load configs for baseline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import OPENAI_API_KEY
from evaluation.evaluate_pipeline import evaluate_current_system

client = OpenAI(api_key=OPENAI_API_KEY)

CONFIG_FILE = "config/config.py"

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def run_git_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return None

def autoresearch_loop(max_iterations=5):
    """
    Autonomous loop that attempts to hyper-optimize config weights 
    using an LLM agent without human intervention.
    """
    print("Starting Autoresearch Loop...")
    
    # Ensure we are in a clean state
    run_git_command("git checkout -b autoresearch-tuning || git checkout autoresearch-tuning")
    
    best_score = evaluate_current_system()
    print(f"Baseline Score: {best_score:.4f}")

    for i in range(max_iterations):
        print(f"\n--- Iteration {i+1}/{max_iterations} ---")
        
        current_config = read_file(CONFIG_FILE)
        
        prompt = f"""
        You are an autonomous AI research scientist optimizing a hallucination detection system.
        The current evaluation score (accuracy) is: {best_score:.4f}

        Here is the current configuration file `config/config.py`:
        ```python
        {current_config}
        ```
        Your goal is to adjust the hallucination risk weights (OCI_WEIGHT, PLI_WEIGHT, RELEVANCE_WEIGHT) 
        and the HIGH_RISK_THRESHOLD to achieve a higher score. Remember that weights should ideally sum to 1.0. 
        Output the ENTIRE modified `config.py` file inside a single python markdown block. 
        Do not add any explanations, only output the updated code block.
        """
        
        print("Consulting LLM for new configuration...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            new_config_text = response.choices[0].message.content
            
            # Extract python code block
            match = re.search(r"```python\n(.*?)```", new_config_text, re.DOTALL)
            if match:
                new_config = match.group(1).strip()
            else:
                new_config = new_config_text.replace("```python", "").replace("```", "").strip()
                
            # Overwrite config
            write_file(CONFIG_FILE, new_config)
            
            # Re-evaluate
            try:
                # Reload the evaluate module to pick up the newly written config
                # As this runs in a continuous script process, 
                # we actually need to spawn a subprocess to ensure clean module import
                eval_script = "python -c \"import sys; sys.path.append(r'.'); from evaluation.evaluate_pipeline import evaluate_current_system; print(evaluate_current_system())\""
                eval_out = subprocess.run(eval_script, shell=True, capture_output=True, text=True, check=True)
                new_score = float(eval_out.stdout.strip())
                print(f"New Score: {new_score:.4f}")
                
                if new_score > best_score:
                    print("✅ Score improved! Committing changes.")
                    best_score = new_score
                    run_git_command(f"git add {CONFIG_FILE}")
                    run_git_command(f'git commit -m "Agent optimized config to score {best_score:.4f}"')
                else:
                    print("❌ Score did not improve. Reverting changes.")
                    run_git_command(f"git checkout -- {CONFIG_FILE}")
                    
            except Exception as eval_err:
                print(f"Evaluation crashed with new config: {eval_err}. Reverting.")
                run_git_command(f"git checkout -- {CONFIG_FILE}")
                
        except Exception as api_err:
            print(f"LLM generation failed: {api_err}")
            
    print(f"\nLoop completed. Best achieved score: {best_score:.4f}")

if __name__ == "__main__":
    autoresearch_loop()
