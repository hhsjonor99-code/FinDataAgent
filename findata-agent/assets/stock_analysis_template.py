"""
FinDataAgent 股票分析模板
提供常用的股票分析代码模板
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts
from datetime import datetime, timedelta
import os

def stock_analysis_template(ts_code, stock_name, period_days=365):
    """
    股票分析模板
    
    Args:
        ts_code: 股票代码 (如: 600519.SH)
        stock_name: 股票名称
        period_days: 分析周期天数
    """
    
    # 1. 数据获取
    print(f"正在获取 {stock_name} ({ts_code}) 的数据...")
    
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y%m%d')
    
    try:
        # 获取日线数据
        df = ts.pro_api().daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            print(f"未获取到 {stock_name} 的数据")
            return
        
        # 数据处理
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date')
        
        # 转换数据类型
        for col in ['open', 'high', 'low', 'close', 'vol']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"成功获取 {len(df)} 天的数据")
        
    except Exception as e:
        print(f"数据获取失败: {e}")
        return
    
    # 2. 技术指标计算
    print("正在计算技术指标...")
    
    # 移动平均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # 布林带
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    # 3. 数据分析
    print("正在进行数据分析...")
    
    # 基本统计
    latest_price = df['close'].iloc[-1]
    price_change = df['close'].iloc[-1] - df['close'].iloc[0]
    price_change_pct = (price_change / df['close'].iloc[0]) * 100
    
    max_price = df['high'].max()
    min_price = df['low'].min()
    avg_volume = df['vol'].mean()
    
    # 技术分析
    current_rsi = df['rsi'].iloc[-1]
    current_macd = df['macd'].iloc[-1]
    
    # 趋势分析
    ma_trend = "上升" if df['ma20'].iloc[-1] > df['ma20'].iloc[-5] else "下降"
    price_vs_ma20 = "上方" if latest_price > df['ma20'].iloc[-1] else "下方"
    
    print(f"""
    === {stock_name} 分析结果 ===
    最新价格: {latest_price:.2f}元
    期间涨跌: {price_change:+.2f}元 ({price_change_pct:+.2f}%)
    最高价: {max_price:.2f}元
    最低价: {min_price:.2f}元
    平均成交量: {avg_volume:.0f}手
    
    技术指标:
    RSI(14): {current_rsi:.2f}
    MACD: {current_macd:+.4f}
    MA20趋势: {ma_trend}
    当前价格vs MA20: {price_vs_ma20}
    """)
    
    # 4. 图表生成
    print("正在生成图表...")
    
    # 设置图表样式
    plt.style.use('seaborn-v0_8')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建复合图表
    fig = plt.figure(figsize=(16, 12))
    
    # 价格和移动平均线
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(df['trade_date'], df['close'], label='收盘价', linewidth=2, color='blue')
    ax1.plot(df['trade_date'], df['ma5'], label='MA5', alpha=0.7)
    ax1.plot(df['trade_date'], df['ma20'], label='MA20', alpha=0.7)
    ax1.plot(df['trade_date'], df['ma60'], label='MA60', alpha=0.7)
    ax1.fill_between(df['trade_date'], df['bb_upper'], df['bb_lower'], alpha=0.1, color='gray', label='布林带')
    
    ax1.set_title(f'{stock_name} 价格走势与技术指标', fontsize=16, fontweight='bold')
    ax1.set_ylabel('价格 (元)', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 成交量
    ax2 = plt.subplot(3, 1, 2)
    ax2.bar(df['trade_date'], df['vol'], alpha=0.6, color='lightblue')
    ax2.plot(df['trade_date'], df['vol'].rolling(window=20).mean(), color='red', label='成交量MA20')
    ax2.set_title('成交量', fontsize=14)
    ax2.set_ylabel('成交量 (手)', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # RSI和MACD
    ax3 = plt.subplot(3, 1, 3)
    ax3.plot(df['trade_date'], df['rsi'], label='RSI(14)', color='purple')
    ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='超买线')
    ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='超卖线')
    
    # 创建第二个y轴用于MACD
    ax3_twin = ax3.twinx()
    ax3_twin.plot(df['trade_date'], df['macd'], label='MACD', color='orange', alpha=0.7)
    ax3_twin.plot(df['trade_date'], df['macd_signal'], label='MACD信号', color='red', alpha=0.7)
    
    ax3.set_title('RSI 和 MACD', fontsize=14)
    ax3.set_ylabel('RSI', fontsize=12, color='purple')
    ax3_twin.set_ylabel('MACD', fontsize=12, color='orange')
    ax3.legend(loc='upper left')
    ax3_twin.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chart_filename = f"{stock_name}_技术分析_{timestamp}.png"
    chart_path = os.path.join(OUTPUT_DIR, chart_filename)
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"图表已保存至: {chart_path}")
    
    # 5. 数据导出
    print("正在导出数据...")
    
    # 选择要导出的列
    export_columns = [
        'trade_date', 'open', 'high', 'low', 'close', 'vol',
        'ma5', 'ma10', 'ma20', 'ma60', 'rsi', 'macd', 'macd_signal'
    ]
    
    export_data = df[export_columns].copy()
    
    # 导出Excel
    excel_filename = f"{stock_name}_分析数据_{timestamp}.xlsx"
    excel_path = os.path.join(OUTPUT_DIR, excel_filename)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 原始数据
        export_data.to_excel(writer, sheet_name='技术指标', index=False)
        
        # 统计摘要
        summary_data = pd.DataFrame({
            '指标': ['最新价格', '期间涨跌', '涨跌幅', '最高价', '最低价', '平均成交量', 'RSI', 'MACD'],
            '数值': [latest_price, price_change, price_change_pct, max_price, min_price, avg_volume, current_rsi, current_macd]
        })
        summary_data.to_excel(writer, sheet_name='分析摘要', index=False)
    
    print(f"数据已导出至: {excel_path}")
    
    print(f"\n{stock_name} 分析完成！")
    print(f"生成文件:")
    print(f"  - 图表: {chart_filename}")
    print(f"  - 数据: {excel_filename}")
    
    return {
        'data': export_data,
        'chart_path': chart_path,
        'excel_path': excel_path,
        'summary': {
            'latest_price': latest_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'max_price': max_price,
            'min_price': min_price,
            'current_rsi': current_rsi,
            'current_macd': current_macd
        }
    }

# 使用示例
if __name__ == "__main__":
    # 注意：需要先设置Tushare token
    # ts.set_token('your_token_here')
    
    # 分析贵州茅台
    result = stock_analysis_template("600519.SH", "贵州茅台", 365)
    
    if result:
        print("分析成功完成！")
    else:
        print("分析失败，请检查参数和网络连接。")