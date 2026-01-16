"""
使用FinDataAgent技能直接调用Tushare API导出600519.SH日线数据
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import tushare as ts
from dotenv import load_dotenv

def export_tushare_data():
    """直接使用Tushare API导出数据"""
    
    # 加载环境变量
    load_dotenv()
    token = os.getenv('TUSHARE_TOKEN')
    
    print(f"使用Token: {token[:20]}...")
    
    # 设置token
    ts.set_token(token)
    pro = ts.pro_api()
    
    # 参数设置
    ts_code = "600519.SH"
    start_date = "20230101"
    end_date = "20230131"
    
    print(f"正在获取 {ts_code} {start_date} 到 {end_date} 的日线数据...")
    
    try:
        # 调用日线数据接口
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            print("未获取到数据")
            return None
            
        print(f"成功获取 {len(df)} 条数据")
        print("数据样例:")
        print(df.head())
        
        # 导出到Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"workspace/exports/{ts_code}_tushare_real_{start_date}_{end_date}_{timestamp}.xlsx"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 导出到Excel
        df.to_excel(filename, index=False)
        
        print(f"数据已导出到: {filename}")
        print(f"文件大小: {os.path.getsize(filename)} 字节")
        
        return filename
        
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

if __name__ == "__main__":
    export_tushare_data()