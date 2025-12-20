import os
import tushare as ts
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
token = os.getenv('TUSHARE_TOKEN')
ts.set_token(token)
pro = ts.pro_api()

ts_code = '000001.SZ'
start_date = '20230101'
end_date = '20230131'
export_path = 'workspace/exports/平安银行_20230101_20230131_20251220_122648.xlsx'

df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
df = df.sort_values('trade_date', ascending=True)
df.to_excel(export_path, index=False)

print(os.path.abspath(export_path))
