import os
import tushare as ts
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from datetime import datetime

load_dotenv()
token = os.getenv('TUSHARE_TOKEN')
ts.set_token(token)
pro = ts.pro_api()

params = {"ts_code": "002415.SZ", "start_date": "20230301", "end_date": "20230401"}
df = pro.daily(**params)

if 'trade_date' in df.columns:
    df = df.sort_values('trade_date', ascending=True)

plot_path = "workspace/exports/002415_SZ_20230301_20230401_20251220_154313.png"

plt.figure(figsize=(12, 6))
plt.plot(df['trade_date'], df['close'], marker='o', linestyle='-', linewidth=2)
plt.title('海康威视收盘价 (2023-03-01 至 2023-04-01)')
plt.xlabel('交易日期')
plt.ylabel('收盘价')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(plot_path, dpi=300)
plt.close()

print(os.path.abspath(plot_path))
