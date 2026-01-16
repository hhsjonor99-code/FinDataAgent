"""
导出600519.SH在2023-01-01至2023-01-31的日线数据到Excel
使用FinDataAgent的数据处理功能
"""

import pandas as pd
import numpy as np
import tushare as ts
from datetime import datetime
import os

# 设置工作目录
WORKSPACE_DIR = "workspace"
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "exports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def export_stock_daily_to_excel():
    """导出股票日线数据到Excel"""
    
    print("开始导出600519.SH日线数据...")
    
    # 检查是否有Tushare token
    try:
        # 尝试从.env文件获取token
        import os
        from dotenv import load_dotenv
        
        # 加载.env文件
        load_dotenv()
        tushare_token = os.getenv('TUSHARE_TOKEN')
        
        if not tushare_token:
            print("警告: 未设置TUSHARE_TOKEN环境变量")
            print("请确保在.env文件中配置了有效的Tushare token")
            return False
        
        # 设置token
        ts.set_token(tushare_token)
        pro = ts.pro_api()
        
        print("Tushare API初始化成功")
        
    except Exception as e:
        print(f"Tushare初始化失败: {e}")
        return False
    
    # 参数设置
    ts_code = "600519.SH"
    stock_name = "贵州茅台"
    start_date = "20230101"
    end_date = "20230131"
    
    print(f"获取数据: {stock_name} ({ts_code})")
    print(f"时间范围: {start_date} 至 {end_date}")
    
    try:
        # 获取日线数据
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            print(f"未获取到数据: {ts_code} {start_date} - {end_date}")
            return False
        
        print(f"成功获取 {len(df)} 条日线数据")
        
        # 数据预处理
        # 转换日期格式
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        
        # 转换数值类型
        numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 按日期排序
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        # 添加股票名称
        df['stock_name'] = stock_name
        
        # 重新排列列顺序
        columns_order = ['trade_date', 'ts_code', 'stock_name', 'open', 'high', 'low', 'close', 
                         'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        
        # 只保留存在的列
        available_columns = [col for col in columns_order if col in df.columns]
        df = df[available_columns]
        
        # 显示数据概览
        print("\n=== 数据概览 ===")
        print(f"数据条数: {len(df)}")
        print(f"日期范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")
        print(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f} 元")
        print(f"平均成交量: {df['vol'].mean():.0f} 手")
        
        print("\n前5条数据:")
        print(df.head())
        
        # 导出到Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_filename = f"{ts_code}_{stock_name}_日线_{start_date}_{end_date}_{timestamp}.xlsx"
        excel_path = os.path.join(OUTPUT_DIR, excel_filename)
        
        # 使用ExcelWriter导出
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # 主数据表
            df.to_excel(writer, sheet_name='日线数据', index=False)
            
            # 创建统计摘要
            summary_data = pd.DataFrame({
                '指标': ['股票代码', '股票名称', '数据条数', '开始日期', '结束日期', 
                       '最高价', '最低价', '收盘价(最后)', '平均成交量', '总成交额'],
                '数值': [ts_code, stock_name, len(df), df['trade_date'].min().strftime('%Y-%m-%d'),
                       df['trade_date'].max().strftime('%Y-%m-%d'), f"{df['high'].max():.2f}元",
                       f"{df['low'].min():.2f}元", f"{df['close'].iloc[-1]:.2f}元",
                       f"{df['vol'].mean():.0f}手", f"{df['amount'].sum():.0f}元"]
            })
            summary_data.to_excel(writer, sheet_name='数据摘要', index=False)
            
            # 创建价格统计表
            price_stats = pd.DataFrame({
                '统计项': ['开盘价', '最高价', '最低价', '收盘价', '涨跌额', '涨跌幅(%)', '成交量', '成交额'],
                '平均值': [df['open'].mean(), df['high'].mean(), df['low'].mean(), df['close'].mean(),
                          df['change'].mean(), df['pct_chg'].mean(), df['vol'].mean(), df['amount'].mean()],
                '最大值': [df['open'].max(), df['high'].max(), df['low'].max(), df['close'].max(),
                          df['change'].max(), df['pct_chg'].max(), df['vol'].max(), df['amount'].max()],
                '最小值': [df['open'].min(), df['high'].min(), df['low'].min(), df['close'].min(),
                          df['change'].min(), df['pct_chg'].min(), df['vol'].min(), df['amount'].min()],
                '标准差': [df['open'].std(), df['high'].std(), df['low'].std(), df['close'].std(),
                          df['change'].std(), df['pct_chg'].std(), df['vol'].std(), df['amount'].std()]
            })
            
            # 格式化数值
            for col in ['平均值', '最大值', '最小值', '标准差']:
                price_stats[col] = price_stats[col].round(2)
            
            price_stats.to_excel(writer, sheet_name='价格统计', index=False)
        
        print(f"\n数据导出成功!")
        print(f"文件路径: {excel_path}")
        print(f"文件大小: {os.path.getsize(excel_path)} 字节")
        
        # 验证导出文件
        try:
            # 读取导出的文件验证
            verify_df = pd.read_excel(excel_path, sheet_name='日线数据')
            print(f"\n文件验证成功，包含 {len(verify_df)} 条数据")
        except Exception as e:
            print(f"⚠️ 文件验证失败: {e}")
        
        return excel_path
        
    except Exception as e:
        print(f"数据导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 执行导出任务
if __name__ == "__main__":
    result = export_stock_daily_to_excel()
    
    if result:
        print(f"\n任务完成! Excel文件已生成: {result}")
    else:
        print("\n任务失败，请检查配置和网络连接")