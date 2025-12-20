import os
from typing import Optional

def _load_token_from_env() -> Optional[str]:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    return os.getenv("TUSHARE_TOKEN")

def _ensure_tushare_initialized():
    import tushare as ts
    token = _load_token_from_env()
    if token:
        ts.set_token(token)
    return ts.pro_api()

def get_daily(ts_code: str, start_date: str, end_date: str):
    pro = _ensure_tushare_initialized()
    return pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

def export_to_excel(df, save_path: str):
    import pandas as pd
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_excel(save_path, index=False)

def find_ts_code_by_name(name: str) -> Optional[str]:
    pro = _ensure_tushare_initialized()
    df = pro.stock_basic()
    try:
        m = df[df['name'] == name]
        if not m.empty:
            return str(m.iloc[0]['ts_code'])
        m2 = df[df['name'].str.contains(name, na=False)]
        if not m2.empty:
            return str(m2.iloc[0]['ts_code'])
    except Exception:
        return None
    return None
