import os
import subprocess
import sys
from datetime import datetime
from typing import Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
TEMP_DIR = os.path.join(ROOT_DIR, "workspace", "temp_scripts")

DEFAULT_PREAMBLE = """
import os
import sys
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Tushare
token = os.getenv('TUSHARE_TOKEN')
if token:
    ts.set_token(token)
    pro = ts.pro_api()
else:
    print("Warning: TUSHARE_TOKEN not found in environment variables.")
    pro = None

# Ensure workspace directories exist
os.makedirs('workspace/exports', exist_ok=True)
os.makedirs('workspace/temp_scripts', exist_ok=True)

# Helper to print last file path clearly for the Agent to pick up
def print_output_path(path):
    print(f"OUTPUT_PATH:{os.path.abspath(path)}")

"""

def run_python_code(code_str: str, script_name: str | None = None, preamble: str = DEFAULT_PREAMBLE) -> Tuple[bool, str]:
    """
    Executes Python code string in a subprocess.
    Injects preamble before the code.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Clean up old scripts (optional, maybe keep them for debug)
    # for name in os.listdir(TEMP_DIR):
    #     p = os.path.join(TEMP_DIR, name)
    #     try:
    #         if os.path.isfile(p):
    #             os.remove(p)
    #     except Exception:
    #         pass
            
    if not script_name:
        script_name = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    script_path = os.path.join(TEMP_DIR, script_name)
    
    full_code = preamble + "\n" + code_str
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(full_code)

    cmd = [sys.executable, script_path]
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR + os.pathsep + env.get("PYTHONPATH", "")
    
    try:
        # Increased timeout for data fetching
        proc = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, timeout=600, env=env)
        if proc.returncode == 0:
            return True, proc.stdout.strip()
        else:
            return False, (proc.stdout + "\n" + proc.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, "Execution timed out after 600 seconds."
    except Exception as e:
        return False, str(e)

def run_python_file(script_path: str) -> Tuple[bool, str]:
    if not os.path.isabs(script_path):
        script_path = os.path.join(ROOT_DIR, script_path)
    cmd = [sys.executable, script_path]
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR + os.pathsep + env.get("PYTHONPATH", "")
    try:
        proc = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, timeout=600, env=env)
        if proc.returncode == 0:
            return True, proc.stdout.strip()
        else:
            return False, (proc.stdout + "\n" + proc.stderr).strip()
    except Exception as e:
        return False, str(e)
