import os
import re
import json
from datetime import datetime
from typing import Dict
from langchain_openai import ChatOpenAI
from tools.tushare_api import find_ts_code_by_name

def _parse_chinese_date(text: str) -> str | None:
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if not m:
        return None
    y, mo, d = m.groups()
    return f"{int(y):04d}{int(mo):02d}{int(d):02d}"

def _fallback_dates(intent: str) -> Dict[str, str | None]:
    parts = re.findall(r"\d{4}年\d{1,2}月\d{1,2}日", intent)
    start = _parse_chinese_date(parts[0]) if len(parts) > 0 else None
    end = _parse_chinese_date(parts[1]) if len(parts) > 1 else None
    return {"start_date": start, "end_date": end}

def _detect_actions(intent: str) -> Dict[str, bool]:
    t = intent.lower()
    plot_kw = ["画图", "折线图", "绘图", "图", "plot", "图表"]
    export_kw = [
        "导出", "保存", "excel", "xlsx", "收集", "下载", "数据集",
        "获取", "获取数据", "拉取", "查询", "数据", "生成文件", "输出", "写入", "保存到",
        "csv", "excel表", "to_excel"
    ]
    only_plot_kw = ["只画图", "仅画图"]
    only_export_kw = ["只导出", "仅导出"]
    no_plot_kw = ["不画图", "无需画图", "不要画图", "不要图"]
    no_export_kw = ["不导出", "无需导出", "不要导出"]

    plot = any(k in intent for k in plot_kw)
    export = any(k in intent for k in export_kw)

    if any(k in intent for k in only_plot_kw):
        plot = True
        export = False
    if any(k in intent for k in only_export_kw):
        export = True
        plot = False

    if any(k in intent for k in no_plot_kw):
        plot = False
    if any(k in intent for k in no_export_kw):
        export = False

    if not plot and not export:
        export = True
    return {"export": export, "plot": plot}

def parse_intent(intent: str) -> Dict[str, str | None]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    stock_name = None
    ts_code = None
    start_date = None
    end_date = None
    api = None
    params = None
    actions = {"export": None, "plot": None}
    m_code = re.search(r"(\d{6})[._](SZ|SH)", intent, re.IGNORECASE)
    if m_code:
        ts_code = f"{m_code.group(1)}.{m_code.group(2).upper()}"
    if api_key:
        try:
            llm = ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=0)
            sys = (
                "你是中文意图解析器，输出严格JSON。字段：stock_name, ts_code, start_date, end_date, api, params, want_export, want_plot。\n"
                "规则：日期格式YYYYMMDD；接口名为知识库中的Tushare接口，如 daily/shibor/gdp 等；params 为调用参数字典。含有‘导出/保存/获取/查询/拉取/数据/Excel/CSV/写入/输出’视为导出；含有‘画图/折线图/图表/plot’视为绘图；含有‘不导出’则want_export=false；含有‘不画图’则want_plot=false；‘只画图’则绘图true导出false；‘只导出’则导出true绘图false；未明确时默认导出true、绘图false。仅输出JSON，不要解释。\n"
                "示例1：导出贵州茅台2023年1月到2月的日线到Excel，不要画图 → {\"stock_name\":\"贵州茅台\",\"ts_code\":null,\"start_date\":\"20230101\",\"end_date\":\"20230201\",\"api\":\"daily\",\"params\":{\"ts_code\":\"600519.SH\",\"start_date\":\"20230101\",\"end_date\":\"20230201\"},\"want_export\":true,\"want_plot\":false}\n"
                "示例2：绘制海康威视2023年3月至4月的收盘价折线图，不导出Excel → {\"stock_name\":\"海康威视\",\"ts_code\":null,\"start_date\":\"20230301\",\"end_date\":\"20230401\",\"api\":\"daily\",\"params\":{\"ts_code\":\"002415.SZ\",\"start_date\":\"20230301\",\"end_date\":\"20230401\"},\"want_export\":false,\"want_plot\":true}\n"
                "示例3：获取SHIBOR隔夜在区间并导出 → {\"stock_name\":null,\"ts_code\":null,\"start_date\":\"20230101\",\"end_date\":\"20230601\",\"api\":\"shibor\",\"params\":{\"start_date\":\"20230101\",\"end_date\":\"20230601\",\"item\":\"ON\"},\"want_export\":true,\"want_plot\":false}"
            )
            msg = [{"role": "system", "content": sys}, {"role": "user", "content": intent}]
            resp = llm.invoke(msg)
            text = resp.content
            j = None
            m = re.search(r"```json\n([\s\S]*?)```", text)
            if m:
                j = m.group(1)
            else:
                m2 = re.search(r"\{[\s\S]*\}", text)
                if m2:
                    j = m2.group(0)
            if j:
                try:
                    data = json.loads(j)
                    stock_name = data.get("stock_name")
                    ts_code = data.get("ts_code")
                    if ts_code and re.match(r"^\d{6}_[A-Z]{2}$", ts_code):
                        ts_code = ts_code.replace("_", ".")
                    start_date = data.get("start_date")
                    end_date = data.get("end_date")
                    api = data.get("api")
                    params = data.get("params")
                    want_export = data.get("want_export")
                    want_plot = data.get("want_plot")
                    if isinstance(want_export, bool):
                        actions["export"] = want_export
                    if isinstance(want_plot, bool):
                        actions["plot"] = want_plot
                except Exception:
                    pass
        except Exception:
            pass
    if not start_date or not end_date:
        d = _fallback_dates(intent)
        start_date = start_date or d["start_date"]
        end_date = end_date or d["end_date"]
    if not ts_code and stock_name:
        try:
            ts_code = find_ts_code_by_name(stock_name)
        except Exception:
            pass
    if not api:
        api = "daily"
    if not params:
        params = {}
    if ts_code and "ts_code" not in params:
        params["ts_code"] = ts_code
    if start_date and "start_date" not in params:
        params["start_date"] = start_date
    if end_date and "end_date" not in params:
        params["end_date"] = end_date
    if actions["export"] is None or actions["plot"] is None:
        fa = _detect_actions(intent)
        if actions["export"] is None:
            actions["export"] = fa["export"]
        if actions["plot"] is None:
            actions["plot"] = fa["plot"]
    return {"stock_name": stock_name, "ts_code": ts_code, "start_date": start_date, "end_date": end_date, "api": api, "params": params, "actions": actions}
