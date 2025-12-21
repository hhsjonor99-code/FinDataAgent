import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.agent_engine import agent_workflow_streaming

def stream_agent(intent: str):
    return agent_workflow_streaming(intent)
