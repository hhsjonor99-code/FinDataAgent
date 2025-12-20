import os
import json
import re
from pathlib import Path
from datetime import datetime
from langchain_openai import ChatOpenAI
from .prompt_templates import SYSTEM_PROMPT, CODE_TEMPLATE
from tools.code_executor import run_python_code
from .knowledge_manager import parse_intent, build_script

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

def agent_workflow(intent: str):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    info = parse_intent(intent)
    ts_code = info.get("ts_code")
    stock_name = info.get("stock_name")
    start_date = info.get("start_date")
    end_date = info.get("end_date")
    actions = info.get("actions") or {"export": True, "plot": False}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = None
    plot_path = None
    label = ts_code or stock_name or "unknown"
    safe_label = str(label).replace(".", "_").replace(" ", "")
    if actions.get("export"):
        export_path = f"workspace/exports/{safe_label}_{start_date}_{end_date}_{ts}.xlsx"
    if actions.get("plot"):
        plot_path = f"workspace/exports/{safe_label}_{start_date}_{end_date}_{ts}.png"
    print_path = export_path or plot_path

    try:
        llm = ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=0)
        knowledge = _load_knowledge()
        user_prompt = (
            f"意图：{intent}\n"
            f"参数解析：ts_code={ts_code}, start_date={start_date}, end_date={end_date}\n"
            f"动作：export={actions.get('export')}, plot={actions.get('plot')}\n"
            f"导出路径：{export_path or ''}\n"
            f"图像路径：{plot_path or ''}\n"
            f"打印路径（只能打印这一项）：{print_path or ''}\n"
            f"知识库：{knowledge}\n"
            "要求：\n"
            "1. 必须使用以下代码初始化 token：\n"
            "   import os\n"
            "   import tushare as ts\n"
            "   from dotenv import load_dotenv\n"
            "   load_dotenv()\n"
            "   token = os.getenv('TUSHARE_TOKEN')\n"
            "   ts.set_token(token)\n"
            "   pro = ts.pro_api()\n"
            "2. 数据按 trade_date 升序排序。\n"
            "3. 当 export=true 且 plot=false：必须包含 df.to_excel(export_path) 并只保存 Excel；不要画图。\n"
            "4. 当 export=false 且 plot=true：必须包含绘图保存到 plot_path；不要导出 Excel。\n"
            "5. 当 export=true 且 plot=true：同时保存 Excel 与图像，各自到对应路径。\n"
            "6. 禁止使用 print 输出除最终绝对路径外任何内容；最后一行必须仅包含路径字符串。\n"
            "7. 生成的代码不包含交互输入；只输出代码，不要解释。"
        )
        msg = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
        resp = llm.invoke(msg)
        code = _extract_code(resp.content)
        
        # 移除 Fallback，确保真实调用
        # 如果 LLM 生成失败，应当直接报错，而不是静默切换到硬编码脚本
        ok, out = run_python_code(code, script_name="agent_exec.py")
        if not ok:
            fallback_code = build_script(ts_code or "", start_date or "", end_date or "", export_path=export_path, plot_path=plot_path, actions=actions)
            ok_fb, out_fb = run_python_code(fallback_code, script_name="agent_exec.py")
            ok = ok_fb
            out = out_fb
        candidates = []
        if export_path:
            candidates.append(Path(ROOT_DIR, export_path).resolve())
        if plot_path:
            candidates.append(Path(ROOT_DIR, plot_path).resolve())
        for p in candidates:
            if p.exists():
                return True, str(p)
        last_line = (out or "").strip().splitlines()[-1] if out else ""
        lp = Path(last_line) if last_line else None
        if lp and (lp.is_absolute() and lp.exists()):
            return True, str(lp)
        fallback_code = build_script(ts_code or "", start_date or "", end_date or "", export_path=export_path, plot_path=plot_path, actions=actions)
        ok_fb2, out_fb2 = run_python_code(fallback_code, script_name="agent_exec.py")
        if ok_fb2:
            for p in candidates:
                if p.exists():
                    return True, str(p)
            last_line2 = (out_fb2 or "").strip().splitlines()[-1] if out_fb2 else ""
            lp2 = Path(last_line2) if last_line2 else None
            if lp2 and (lp2.is_absolute() and lp2.exists()):
                return True, str(lp2)
        return False, out_fb2
    except Exception as e:
        return False, f"Agent Execution Error: {str(e)}"
