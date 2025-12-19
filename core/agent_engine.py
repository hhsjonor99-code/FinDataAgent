import os
import json
import re
from langchain_openai import ChatOpenAI
from .prompt_templates import SYSTEM_PROMPT, CODE_TEMPLATE
from tools.code_executor import run_python_code
from .knowlegde_manager import parse_intent, build_script

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

def _load_knowledge() -> str:
    paths = [
        os.path.join(ROOT_DIR, "knowledge_base/tushare_schema.json"),
        os.path.join(ROOT_DIR, "knowledge_base/tool_docs.json")
    ]
    payload = {}
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                try:
                    payload[os.path.basename(p)] = json.load(f)
                except Exception:
                    payload[os.path.basename(p)] = f.read()
    return json.dumps(payload, ensure_ascii=False)

def _extract_code(text: str) -> str:
    m = re.search(r"```python\n([\s\S]*?)```", text)
    if m:
        return m.group(1)
    m2 = re.search(r"```\n([\s\S]*?)```", text)
    if m2:
        return m2.group(1)
    return text

def run_min_workflow(intent: str):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    info = parse_intent(intent)
    ts_code = info.get("ts_code")
    start_date = info.get("start_date")
    end_date = info.get("end_date")
    # 简单的后缀判断，辅助LLM决策，但最终由LLM决定
    ext = ".png" if "图" in intent else ".xlsx"
    export_path = f"workspace/exports/{ts_code}_{start_date}_{end_date}{ext}"

    try:
        llm = ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=0)
        knowledge = _load_knowledge()
        user_prompt = (
            f"意图：{intent}\n"
            f"参数解析：ts_code={ts_code}, start_date={start_date}, end_date={end_date}\n"
            f"建议导出路径：{export_path}\n"
            f"知识库：{knowledge}\n"
            "要求：\n"
            "1. 必须使用以下代码初始化 token（不要用 'your_token_here'）：\n"
            "   import os\n"
            "   import tushare as ts\n"
            "   from dotenv import load_dotenv\n"
            "   load_dotenv()\n"
            "   token = os.getenv('TUSHARE_TOKEN')\n"
            "   ts.set_token(token)\n"
            "   pro = ts.pro_api()\n"
            "2. 严格生成可直接运行的 Python 代码。\n"
            "3. 代码应完成数据获取及后续处理（如保存Excel或画图）。\n"
            "4. 必须且只能 print 最终生成文件的绝对路径。\n"
            "5. 只输出代码，不要解释。"
        )
        msg = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
        resp = llm.invoke(msg)
        code = _extract_code(resp.content)
        
        # 移除 Fallback，确保真实调用
        # 如果 LLM 生成失败，应当直接报错，而不是静默切换到硬编码脚本
        ok, out = run_python_code(code, script_name="agent_exec.py")
        return ok, out
    except Exception as e:
        return False, f"Agent Execution Error: {str(e)}"
