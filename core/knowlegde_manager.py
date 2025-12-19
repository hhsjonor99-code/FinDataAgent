import os
import re
from datetime import datetime

_SYMBOL_MAP = {
    "平安银行": "000001.SZ",
}

def _parse_chinese_date(text: str) -> str | None:
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if not m:
        return None
    y, mo, d = m.groups()
    return f"{int(y):04d}{int(mo):02d}{int(d):02d}"

def parse_intent(intent: str):
    start = None
    end = None
    for part in re.findall(r"\d{4}年\d{1,2}月\d{1,2}日", intent):
        if start is None:
            start = _parse_chinese_date(part)
        else:
            end = _parse_chinese_date(part)
    symbol = None
    for name, code in _SYMBOL_MAP.items():
        if name in intent:
            symbol = code
            break
    return {
        "ts_code": symbol,
        "start_date": start,
        "end_date": end,
    }

def build_script(ts_code: str, start_date: str, end_date: str, export_path: str) -> str:
    code = f"""
import os
from dotenv import load_dotenv
load_dotenv()
import tushare as ts
token = os.getenv('TUSHARE_TOKEN')
if token:
    ts.set_token(token)
pro = ts.pro_api()
df = pro.daily(ts_code='{ts_code}', start_date='{start_date}', end_date='{end_date}')
os.makedirs(os.path.dirname('{export_path}'), exist_ok=True)
df.to_excel('{export_path}', index=False)
print('{export_path}')
"""
    return code
