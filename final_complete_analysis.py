"""
基于已获取的真实Tushare数据完成600519.SH完整分析
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt

def complete_analysis_from_real_data():
    """基于真实Tushare数据完成完整分析"""
    
    # 读取已获取的真实数据
    real_data_file = "workspace/exports/600519.SH_tushare_real_20230101_20230131_20260115_000506.xlsx"
    
    if not os.path.exists(real_data_file):
        print("找不到真实数据文件")
        return False
    
    print("=== 基于真实数据的FinDataAgent完整分析 ===")
    
    # 1. 读取真实数据
    print("1. 读取真实Tushare数据...")
    df = pd.read_excel(real_data_file)
    print(f"   成功读取 {len(df)} 条真实数据")
    
    # 2. 数据预处理
    print("2. 数据预处理...")
    
    # 转换数据类型
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 添加股票名称
    df['stock_name'] = "贵州茅台"
    
    # 按日期排序
    df = df.sort_values('trade_date').reset_index(drop=True)
    print("   数据预处理完成")
    
    # 3. 计算技术指标
    print("3. 计算技术指标...")
    
    # 移动平均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10, min_periods=1).mean()
    
    # 成交量移动平均
    df['vol_ma5'] = df['vol'].rolling(window=5).mean()
    df['vol_ma10'] = df['vol'].rolling(window=10, min_periods=1).mean()
    
    # 振幅
    df['amplitude'] = ((df['high'] - df['low']) / df['pre_close'] * 100).round(2)
    
    # 累计涨跌幅
    df['cumulative_return'] = ((df['close'] / df['close'].iloc[0]) - 1) * 100
    
    print("   技术指标计算完成")
    
    # 4. 数据统计分析
    print("4. 生成统计摘要...")
    
    # 基本统计
    latest_price = df['close'].iloc[-1]
    first_price = df['close'].iloc[0]
    price_change = latest_price - first_price
    price_change_pct = (price_change / first_price) * 100
    
    max_price = df['high'].max()
    min_price = df['low'].min()
    avg_price = df['close'].mean()
    
    total_volume = df['vol'].sum()
    avg_volume = df['vol'].mean()
    max_volume = df['vol'].max()
    
    total_amount = df['amount'].sum()
    avg_amount = df['amount'].mean()
    
    # 波动性分析
    daily_returns = df['pct_chg']
    volatility = daily_returns.std()
    max_daily_gain = daily_returns.max()
    max_daily_loss = daily_returns.min()
    
    # 涨跌统计
    up_days = len(df[df['pct_chg'] > 0])
    down_days = len(df[df['pct_chg'] < 0])
    flat_days = len(df[df['pct_chg'] == 0])
    
    print("   统计分析完成")
    
    # 5. 导出到完整的Excel文件
    print("5. 导出完整分析Excel...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_filename = f"600519.SH_贵州茅台_完整分析_20230101_20230131_{timestamp}.xlsx"
    excel_path = f"workspace/exports/{excel_filename}"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        
        # 工作表1: 完整数据
        complete_columns = ['trade_date', 'ts_code', 'stock_name', 'open', 'high', 'low', 'close', 
                           'pre_close', 'change', 'pct_chg', 'vol', 'amount', 'ma5', 'ma10', 
                           'vol_ma5', 'vol_ma10', 'amplitude', 'cumulative_return']
        
        # 确保所有列都存在
        available_columns = [col for col in complete_columns if col in df.columns]
        df[available_columns].to_excel(writer, sheet_name='完整数据', index=False)
        
        # 工作表2: 数据摘要
        summary_data = pd.DataFrame({
            '指标': ['股票代码', '股票名称', '数据日期', '交易天数', 
                   '期初价格', '期末价格', '期间涨跌', '涨跌幅(%)',
                   '最高价', '最低价', '平均价', '价格区间(%)',
                   '总成交量', '平均成交量', '最大成交量',
                   '总成交额', '平均成交额',
                   '日均波动率(%)', '最大单日涨幅(%)', '最大单日跌幅(%)',
                   '上涨天数', '下跌天数', '平盘天数', '上涨概率(%)'],
            '数值': [
                '600519.SH', '贵州茅台', f"{df['trade_date'].min().strftime('%Y-%m-%d')} 至 {df['trade_date'].max().strftime('%Y-%m-%d')}", len(df),
                f"{first_price:.2f}元", f"{latest_price:.2f}元", f"{price_change:+.2f}元", f"{price_change_pct:+.2f}%",
                f"{max_price:.2f}元", f"{min_price:.2f}元", f"{avg_price:.2f}元", f"{((max_price/min_price-1)*100):.2f}%",
                f"{total_volume:,.0f}手", f"{avg_volume:,.0f}手", f"{max_volume:,.0f}手",
                f"{total_amount:,.0f}元", f"{avg_amount:,.0f}元",
                f"{volatility:.2f}%", f"{max_daily_gain:.2f}%", f"{max_daily_loss:.2f}%",
                up_days, down_days, flat_days, f"{(up_days/len(df)*100):.1f}%"
            ]
        })
        summary_data.to_excel(writer, sheet_name='数据摘要', index=False)
        
        # 工作表3: 详细统计
        detailed_stats = pd.DataFrame({
            '统计项': ['开盘价', '最高价', '最低价', '收盘价', '涨跌额', '涨跌幅(%)', 
                      '成交量', '成交额', '振幅(%)', '累计收益率(%)'],
            '平均值': [df['open'].mean(), df['high'].mean(), df['low'].mean(), df['close'].mean(),
                      df['change'].mean(), df['pct_chg'].mean(), df['vol'].mean(), df['amount'].mean(),
                      df['amplitude'].mean(), df['cumulative_return'].mean()],
            '最大值': [df['open'].max(), df['high'].max(), df['low'].max(), df['close'].max(),
                      df['change'].max(), df['pct_chg'].max(), df['vol'].max(), df['amount'].max(),
                      df['amplitude'].max(), df['cumulative_return'].max()],
            '最小值': [df['open'].min(), df['high'].min(), df['low'].min(), df['close'].min(),
                      df['change'].min(), df['pct_chg'].min(), df['vol'].min(), df['amount'].min(),
                      df['amplitude'].min(), df['cumulative_return'].min()],
            '标准差': [df['open'].std(), df['high'].std(), df['low'].std(), df['close'].std(),
                      df['change'].std(), df['pct_chg'].std(), df['vol'].std(), df['amount'].std(),
                      df['amplitude'].std(), df['cumulative_return'].std()]
        })
        
        # 格式化数值
        for col in ['平均值', '最大值', '最小值', '标准差']:
            detailed_stats[col] = detailed_stats[col].round(2)
        
        detailed_stats.to_excel(writer, sheet_name='详细统计', index=False)
    
    print(f"   Excel导出成功: {excel_path}")
    print(f"   文件大小: {os.path.getsize(excel_path):,} 字节")
    
    # 6. 生成图表
    print("6. 生成分析图表...")
    
    # 设置matplotlib中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建综合图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 价格走势图
    ax1.plot(df['trade_date'], df['close'], label='收盘价', linewidth=2, color='blue', marker='o')
    ax1.plot(df['trade_date'], df['ma5'], label='MA5', alpha=0.7, color='orange')
    ax1.plot(df['trade_date'], df['ma10'], label='MA10', alpha=0.7, color='red')
    ax1.set_title('贵州茅台 2023年1月价格走势', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 (元)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 成交量图
    ax2.bar(df['trade_date'], df['vol'], alpha=0.6, color='lightblue', label='成交量')
    ax2.plot(df['trade_date'], df['vol_ma5'], label='成交量MA5', color='red', linewidth=2)
    ax2.set_title('成交量走势', fontsize=14, fontweight='bold')
    ax2.set_ylabel('成交量 (手)', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 累计收益率
    ax3.plot(df['trade_date'], df['cumulative_return'], label='累计收益率', linewidth=2, color='green', marker='o')
    ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax3.fill_between(df['trade_date'], df['cumulative_return'], 0, alpha=0.3, color='green')
    ax3.set_title('累计收益率走势', fontsize=14, fontweight='bold')
    ax3.set_ylabel('收益率 (%)', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 涨跌幅分布
    colors = ['red' if x > 0 else 'green' if x < 0 else 'gray' for x in df['pct_chg']]
    ax4.bar(range(len(df)), df['pct_chg'], color=colors, alpha=0.7)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax4.set_title('每日涨跌幅', fontsize=14, fontweight='bold')
    ax4.set_ylabel('涨跌幅 (%)', fontsize=12)
    ax4.set_xlabel('交易日序号', fontsize=12)
    ax4.grid(True, alpha=0.3)
    
    # 设置x轴标签
    for ax in [ax1, ax2, ax3]:
        for label in ax.get_xticklabels():
            label.set_rotation(45)
    
    plt.tight_layout()
    
    # 保存图表
    chart_filename = f"600519.SH_贵州茅台_分析图表_20230101_20230131_{timestamp}.png"
    chart_path = f"workspace/exports/{chart_filename}"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   图表生成成功: {chart_path}")
    print(f"   图表大小: {os.path.getsize(chart_path):,} 字节")
    
    # 7. 输出完整报告
    print()
    print("=== 完整分析报告 ===")
    print(f"股票代码: 600519.SH (贵州茅台)")
    print(f"分析期间: {df['trade_date'].min().strftime('%Y-%m-%d')} 至 {df['trade_date'].max().strftime('%Y-%m-%d')}")
    print(f"交易天数: {len(df)}天")
    print()
    print("价格表现:")
    print(f"  期初价格: {first_price:.2f}元")
    print(f"  期末价格: {latest_price:.2f}元")
    print(f"  期间涨跌: {price_change:+.2f}元 ({price_change_pct:+.2f}%)")
    print(f"  最高价格: {max_price:.2f}元")
    print(f"  最低价格: {min_price:.2f}元")
    print(f"  价格区间: {((max_price/min_price-1)*100):.2f}%")
    print()
    print("成交情况:")
    print(f"  总成交量: {total_volume:,.0f}手")
    print(f"  平均成交量: {avg_volume:,.0f}手")
    print(f"  最大成交量: {max_volume:,.0f}手")
    print(f"  总成交额: {total_amount:,.0f}元")
    print()
    print("波动性分析:")
    print(f"  日均波动率: {volatility:.2f}%")
    print(f"  最大单日涨幅: {max_daily_gain:.2f}%")
    print(f"  最大单日跌幅: {max_daily_loss:.2f}%")
    print()
    print("涨跌统计:")
    print(f"  上涨天数: {up_days}天 ({up_days/len(df)*100:.1f}%)")
    print(f"  下跌天数: {down_days}天 ({down_days/len(df)*100:.1f}%)")
    print(f"  平盘天数: {flat_days}天 ({flat_days/len(df)*100:.1f}%)")
    print()
    print("生成文件:")
    print(f"1. Excel分析报告: {excel_filename}")
    print(f"2. 图表文件: {chart_filename}")
    print(f"3. 原始数据文件: 600519.SH_tushare_real_20230101_20230131_20260115_000506.xlsx")
    
    return {
        'excel_path': excel_path,
        'chart_path': chart_path,
        'summary': {
            'trading_days': len(df),
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'total_volume': total_volume,
            'total_amount': total_amount,
            'up_days': up_days,
            'down_days': down_days,
            'volatility': volatility
        }
    }

# 执行完整分析
if __name__ == "__main__":
    result = complete_analysis_from_real_data()
    
    if result:
        print(f"\n✅ 任务完成! 基于真实Tushare数据的完整分析已保存到 workspace/exports/ 目录")
    else:
        print(f"\n❌ 任务失败")