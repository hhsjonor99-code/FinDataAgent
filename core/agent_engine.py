import os
import json
import re
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from .prompt_templates import CODE_INTERPRETER_SYSTEM_PROMPT
from tools.code_executor import run_python_code
from .knowledge_manager import get_knowledge_context
from log_tools.logger import get_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

def _extract_code(text: str) -> str:
    """
    提取LLM的回复所生成的Python代码块
    """
    m = re.search(r"```python\n([\s\S]*?)```", text)
    if m:
        return m.group(1)
    m2 = re.search(r"```\n([\s\S]*?)```", text)
    if m2:
        return m2.group(1)
    return text


def agent_workflow(intent: str):
    """
    Main Agent Workflow:
    1. Retrieve Knowledge
    2. Construct Prompt
    3. LLM Think & Code
    4. Execute & Observe
    5. Self-Correction Loop
    """

    """
    从配置文件（.env）中读取LLM的API密钥、基础URL和模型名称
    基础URL与模型名称在配置中没有指定，使用默认值
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    try:
        with open(os.path.join(ROOT_DIR, "config.json"), "r", encoding="utf-8") as f:
            cfg = json.load(f)
            m = cfg.get("llm_model")
            if m:
                model = m
    except Exception:
        pass
    

    
    # Initialize Logger
    log_dir = os.path.join(ROOT_DIR, "core", "agent_log_record")
    os.makedirs(log_dir, exist_ok=True)
    logger = get_logger(log_dir, "agent")
    
    # 1. Retrieve Knowledge
    knowledge = get_knowledge_context(intent)
    
    # 2. Construct System Prompt
    system_prompt = CODE_INTERPRETER_SYSTEM_PROMPT.format(knowledge_base=knowledge)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": intent}
    ]
    
    # Use OpenAI client directly as LangChain seems unstable in this env
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    max_retries = 3
    
    logger.info(f"Starting workflow for intent: {intent}")
    
    for attempt in range(max_retries):
        try:
            # 3. LLM Think & Code
            logger.info(f"Invoking LLM (Attempt {attempt+1})...")
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                temperature=0
            )
            
            content = response.choices[0].message.content
            logger.info(f"LLM Response (Attempt {attempt+1}): {content[:200]}...")
            
            code = _extract_code(content)
            
            # If no code block found, check if it's a refusal or conversational response
            if "```" not in content and len(code) < 50:
                # Assuming non-code response
                logger.info("No code generated, returning content.")
                return True, content
            
            # 4. Execute
            logger.info("Executing code...")
            ok, out = run_python_code(code, script_name=f"agent_exec_{attempt}.py")
            logger.info(f"Execution Result: ok={ok}, out={out[:200]}...")
            
            if ok:
                # Success!
                # Check for output path
                match = re.search(r"OUTPUT_PATH:(.*)", out)
                if match:
                    path = match.group(1).strip()
                    return True, path
                
                # Check if we can find any file in exports matching a pattern if no explicit path?
                # For now, rely on strict OUTPUT_PATH protocol or just return stdout
                return True, out
            else:
                # Failure - Self Correction
                error_msg = f"Execution Failed:\n{out}"
                logger.warning(error_msg)
                
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": f"The code failed to execute. Error:\n{out}\nPlease analyze the error and rewrite the COMPLETE script to fix it."})
                
        except Exception as e:
            logger.error(f"Workflow Exception: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
            
    return False, f"Failed to complete task after {max_retries} attempts."


def agent_workflow_streaming(intent: str):
    """
    Streaming Agent Workflow for UI:
    1. Retrieve Knowledge
    2. Construct Prompt
    3. LLM Think & Code (Streaming)
    4. Execute & Observe
    5. Self-Correction Loop
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    try:
        with open(os.path.join(ROOT_DIR, "config.json"), "r", encoding="utf-8") as f:
            cfg = json.load(f)
            m = cfg.get("llm_model")
            if m:
                model = m
    except Exception:
        pass
    
    log_dir = os.path.join(ROOT_DIR, "core", "agent_log_record")
    os.makedirs(log_dir, exist_ok=True)
    logger = get_logger(log_dir, "agent")
    
    knowledge = get_knowledge_context(intent)
    
    system_prompt = CODE_INTERPRETER_SYSTEM_PROMPT.format(knowledge_base=knowledge)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": intent}
    ]
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    max_retries = 3

    logger.info(f"Starting workflow for intent: {intent}")
    yield json.dumps({"type": "thought", "content": "正在分析您的需求..."}) + "\n"

    for attempt in range(max_retries):
        try:
            logger.info(f"Invoking LLM (Attempt {attempt + 1})...")
            yield json.dumps({"type": "thought", "content": f"第 {attempt + 1} 次尝试思考..."}) + "\n"

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0
            )

            content_buffer = ""
            for chunk in response:
                chunk_content = chunk.choices[0].delta.content
                if chunk_content:
                    content_buffer += chunk_content
                    yield json.dumps({"type": "thought_stream", "content": chunk_content}) + "\n"

            content = content_buffer
            logger.info(f"LLM Response (Attempt {attempt + 1}): {content[:200]}...")

            code = _extract_code(content)

            if "```" not in content and len(code) < 50:
                logger.info("No code generated, returning content.")
                yield json.dumps({"type": "result", "success": True, "data": content}) + "\n"
                return

            logger.info("Executing code...")
            yield json.dumps({"type": "execution", "content": code}) + "\n"
            ok, out = run_python_code(code, script_name=f"agent_exec_{attempt}.py")
            logger.info(f"Execution Result: ok={ok}, out={out[:200]}...")

            if ok:
                match = re.search(r"OUTPUT_PATH:(.*)", out)
                if match:
                    path = match.group(1).strip()
                    result_data = f"任务成功完成，结果已保存至: {path}"
                    yield json.dumps({"type": "result", "success": True, "data": result_data}) + "\n"
                else:
                    result_data = f"任务成功完成。\n{out}"
                    yield json.dumps({"type": "result", "success": True, "data": result_data}) + "\n"
                return
            else:
                error_msg = f"Execution Failed:\n{out}"
                logger.warning(error_msg)
                yield json.dumps({"type": "error", "content": f"代码执行失败: {out[:200]}...\n正在尝试修正错误..."}) + "\n"

                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user",
                                 "content": f"The code failed to execute. Error:\n{out}\nPlease analyze the error and rewrite the COMPLETE script to fix it."})

        except Exception as e:
            logger.error(f"Workflow Exception: {e}")
            import traceback
            traceback.print_exc()
            yield json.dumps({"type": "result", "success": False, "data": str(e)}) + "\n"
            return

    yield json.dumps({"type": "result", "success": False, "data": f"任务在 {max_retries} 次尝试后仍然失败。"}) + "\n"
