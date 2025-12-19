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
