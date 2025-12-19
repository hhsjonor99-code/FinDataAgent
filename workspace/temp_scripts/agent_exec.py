import os
import tushare as ts
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import pandas as pd

# 初始化token
load_dotenv()
token = os.getenv('TUSHARE_TOKEN')
ts.set_token(token)
pro = ts.pro_api()

# 获取数据
df = pro.daily(ts_code='000001.SZ', start_date='20230101', end_date='20230301')

# 确保数据按日期排序
df = df.sort_values('trade_date')

# 绘制折线图
plt.figure(figsize=(12, 6))
plt.plot(df['trade_date'], df['close'], marker='o', linestyle='-', linewidth=2)
plt.title('平安银行收盘价 (2023-01-01 至 2023-03-01)')
plt.xlabel('交易日期')
plt.ylabel('收盘价')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# 保存图表
save_path = 'workspace/exports/000001.SZ_20230101_20230301.png'
plt.savefig(save_path, dpi=300)
plt.close()

# 打印最终文件路径
print(os.path.abspath(save_path))
