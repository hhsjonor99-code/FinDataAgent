import os
import subprocess
import sys
from datetime import datetime
from typing import Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
TEMP_DIR = os.path.join(ROOT_DIR, "workspace", "temp_scripts")

def run_python_code(code_str: str, script_name: str | None = None) -> Tuple[bool, str]:
    os.makedirs(TEMP_DIR, exist_ok=True)
    if not script_name:
        script_name = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    script_path = os.path.join(TEMP_DIR, script_name)
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code_str)

    cmd = [sys.executable, script_path]
    try:
        proc = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, timeout=300)
        if proc.returncode == 0:
            return True, proc.stdout.strip()
        else:
            return False, (proc.stdout + "\n" + proc.stderr).strip()
    except Exception as e:
        return False, str(e)

def run_python_file(script_path: str) -> Tuple[bool, str]:
    if not os.path.isabs(script_path):
        script_path = os.path.join(ROOT_DIR, script_path)
    cmd = [sys.executable, script_path]
    try:
        proc = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, timeout=300)
        if proc.returncode == 0:
            return True, proc.stdout.strip()
        else:
            return False, (proc.stdout + "\n" + proc.stderr).strip()
    except Exception as e:
        return False, str(e)
