import os
import json
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

def load_knowledge_base() -> str:
    """
    Load all knowledge base schemas and docs into a string for the LLM context.
    Currently loads tushare_schema.json and tool_docs.json.
    """
    paths = [
        os.path.join(ROOT_DIR, "knowledge_base/tushare_schema.json"),
        #os.path.join(ROOT_DIR, "knowledge_base/tool_docs.json")
    ]
    
    knowledge_content = []
    
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Simple formatting for readability
                    filename = os.path.basename(p)
                    knowledge_content.append(f"--- {filename} ---")
                    knowledge_content.append(json.dumps(data, ensure_ascii=False, indent=2))
            except Exception as e:
                # Log error or skip? For now skip
                pass
                
    return "\n\n".join(knowledge_content)

def get_knowledge_context(query: str) -> str:
    """
    Retrieve relevant knowledge based on query.
    For MVP, we just return the full knowledge base as it's small.
    Future: Implement vector search or keyword filtering.
    """
    # TODO: Implement retrieval logic if KB grows
    return load_knowledge_base()
