"""
使用FinDataAgent技能完整导出600519.SH在2023-01-01至2023-01-31的日线数据到Excel
包含完整的分析结果和统计信息
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import tushare as ts
from dotenv import load_dotenv
import matplotlib.pyplot as plt

def export_stock_daily_complete():
    """完整的股票日线数据导出功能"""
    
    # 加载环境变量
    load_dotenv()
    token = os.getenv('TUSHARE_TOKEN')
    
    if not token:
        print("未找到Tushare token")
        return False
    
    # 设置token
    ts.set_token(token)
    pro = ts.pro_api()
    
    # 参数设置
    ts_code = "600519.SH"
    stock_name = "贵州茅台"
    start_date = "20230101"
    end_date = "20230131"
    
    print(f"=== FinDataAgent 股票数据导出 ===")
    print(f"股票: {stock_name} ({ts_code})")
    print(f"时间: {start_date} 至 {end_date}")
    print()
    
    try:
        # 1. 获取日线数据
        print("1. 正在获取日线数据...")
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            print("未获取到数据")
            return False
        
        print(f"   成功获取 {len(df)} 条日线数据")
        
        # 2. 获取复权因子（用于前复权计算）
        print("2. 正在获取复权因子...")
        adj_df = pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if not adj_df.empty:
            df = df.merge(adj_df[['trade_date', 'adj_factor']], on='trade_date', how='left')
            df['adj_factor'] = df['adj_factor'].fillna(1)
            print("   复权因子获取成功")
        else:
            df['adj_factor'] = 1.0
            print("   使用默认复权因子")
        
        # 3. 数据预处理
        print("3. 正在处理数据...")
        
        # 转换数据类型
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 计算前复权价格
        for col in ['open', 'high', 'low', 'close', 'pre_close']:
            if col in df.columns:
                df[f'{col}_adj'] = df[col] * df['adj_factor']
        
        # 添加股票名称
        df['stock_name'] = stock_name
        
        # 按日期排序
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        # 4. 计算技术指标
        print("4. 正在计算技术指标...")
        
        # 移动平均线
        df['ma5'] = df['close_adj'].rolling(window=5).mean()
        df['ma10'] = df['close_adj'].rolling(window=10).mean()
        df['ma20'] = df['close_adj'].rolling(window=20).mean()
        
        # 成交量移动平均
        df['vol_ma5'] = df['vol'].rolling(window=5).mean()
        df['vol_ma10'] = df['vol'].rolling(window=10).mean()
        
        # 振幅
        df['amplitude'] = ((df['high'] - df['low']) / df['pre_close'] * 100).round(2)
        
        # 换手率（近似）
        df['turnover_rate'] = (df['vol'] / 1000000 * 100).round(4)  # 假设总股本为100万股
        
        print("   技术指标计算完成")
        
        # 5. 数据统计分析
        print("5. 正在生成统计摘要...")
        
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
        
        # 6. 导出到Excel
        print("6. 正在导出Excel文件...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_filename = f"{ts_code}_{stock_name}_完整日线分析_{start_date}_{end_date}_{timestamp}.xlsx"
        excel_path = f"workspace/exports/{excel_filename}"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            
            # 工作表1: 原始日线数据
            raw_columns = ['trade_date', 'ts_code', 'stock_name', 'open', 'high', 'low', 'close', 
                          'pre_close', 'change', 'pct_chg', 'vol', 'amount']
            df[raw_columns].to_excel(writer, sheet_name='原始数据', index=False)
            
            # 工作表2: 复权数据和技术指标
            adj_columns = ['trade_date', 'close_adj', 'open_adj', 'high_adj', 'low_adj',
                          'ma5', 'ma10', 'ma20', 'vol_ma5', 'vol_ma10', 'amplitude', 'turnover_rate']
            df[adj_columns].to_excel(writer, sheet_name='技术分析', index=False)
            
            # 工作表3: 数据摘要
            summary_data = pd.DataFrame({
                '指标': ['股票代码', '股票名称', '数据日期', '交易天数', 
                       '期初价格', '期末价格', '期间涨跌', '涨跌幅(%)',
                       '最高价', '最低价', '平均价', '价格区间(%)',
                       '总成交量', '平均成交量', '最大成交量',
                       '总成交额', '平均成交额',
                       '日均波动率(%)', '最大单日涨幅(%)', '最大单日跌幅(%)',
                       '上涨天数', '下跌天数', '平盘天数'],
                '数值': [
                    ts_code, stock_name, f"{df['trade_date'].min().strftime('%Y-%m-%d')} 至 {df['trade_date'].max().strftime('%Y-%m-%d')}", len(df),
                    f"{first_price:.2f}元", f"{latest_price:.2f}元", f"{price_change:+.2f}元", f"{price_change_pct:+.2f}%",
                    f"{max_price:.2f}元", f"{min_price:.2f}元", f"{avg_price:.2f}元", f"{((max_price/min_price-1)*100):.2f}%",
                    f"{total_volume:,.0f}手", f"{avg_volume:,.0f}手", f"{max_volume:,.0f}手",
                    f"{total_amount:,.0f}元", f"{avg_amount:,.0f}元",
                    f"{volatility:.2f}%", f"{max_daily_gain:.2f}%", f"{max_daily_loss:.2f}%",
                    up_days, down_days, flat_days
                ]
            })
            summary_data.to_excel(writer, sheet_name='数据摘要', index=False)
            
            # 工作表4: 价格统计
            price_stats = pd.DataFrame({
                '统计项': ['开盘价', '最高价', '最低价', '收盘价', '涨跌额', '涨跌幅(%)', 
                          '成交量', '成交额', '振幅(%)', '换手率(%)'],
                '平均值': [df['open'].mean(), df['high'].mean(), df['low'].mean(), df['close'].mean(),
                          df['change'].mean(), df['pct_chg'].mean(), df['vol'].mean(), df['amount'].mean(),
                          df['amplitude'].mean(), df['turnover_rate'].mean()],
                '最大值': [df['open'].max(), df['high'].max(), df['low'].max(), df['close'].max(),
                          df['change'].max(), df['pct_chg'].max(), df['vol'].max(), df['amount'].max(),
                          df['amplitude'].max(), df['turnover_rate'].max()],
                '最小值': [df['open'].min(), df['high'].min(), df['low'].min(), df['close'].min(),
                          df['change'].min(), df['pct_chg'].min(), df['vol'].min(), df['amount'].min(),
                          df['amplitude'].min(), df['turnover_rate'].min()],
                '标准差': [df['open'].std(), df['high'].std(), df['low'].std(), df['close'].std(),
                          df['change'].std(), df['pct_chg'].std(), df['vol'].std(), df['amount'].std(),
                          df['amplitude'].std(), df['turnover_rate'].std()]
            })
            
            # 格式化数值
            for col in ['平均值', '最大值', '最小值', '标准差']:
                price_stats[col] = price_stats[col].round(2)
            
            price_stats.to_excel(writer, sheet_name='价格统计', index=False)
        
        print(f"   Excel文件导出成功: {excel_path}")
        print(f"   文件大小: {os.path.getsize(excel_path):,} 字节")
        
        # 7. 生成图表
        print("7. 正在生成图表...")
        
        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 价格走势图
        ax1.plot(df['trade_date'], df['close_adj'], label='前复权收盘价', linewidth=2, color='blue')
        ax1.plot(df['trade_date'], df['ma5'], label='MA5', alpha=0.7, color='orange')
        ax1.plot(df['trade_date'], df['ma10'], label='MA10', alpha=0.7, color='red')
        ax1.set_title(f'{stock_name} 前复权价格走势', fontsize=14, fontweight='bold')
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
        
        # 涨跌幅分布
        ax3.hist(df['pct_chg'], bins=10, alpha=0.7, color='green', edgecolor='black')
        ax3.axvline(df['pct_chg'].mean(), color='red', linestyle='--', label=f'均值: {df["pct_chg"].mean():.2f}%')
        ax3.set_title('日涨跌幅分布', fontsize=14, fontweight='bold')
        ax3.set_xlabel('涨跌幅 (%)', fontsize=12)
        ax3.set_ylabel('频次', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 振幅分析
        ax4.plot(df['trade_date'], df['amplitude'], marker='o', color='purple', label='振幅')
        ax4.set_title('日内振幅变化', fontsize=14, fontweight='bold')
        ax4.set_ylabel('振幅 (%)', fontsize=12)
        ax4.set_xlabel('日期', fontsize=12)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        chart_filename = f"{ts_code}_{stock_name}_图表_{start_date}_{end_date}_{timestamp}.png"
        chart_path = f"workspace/exports/{chart_filename}"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   图表保存成功: {chart_path}")
        print(f"   图表大小: {os.path.getsize(chart_path):,} 字节")
        
        # 8. 输出结果摘要
        print()
        print("=== 导出完成 ===")
        print(f"股票: {stock_name} ({ts_code})")
        print(f"期间: {df['trade_date'].min().strftime('%Y-%m-%d')} 至 {df['trade_date'].max().strftime('%Y-%m-%d')}")
        print(f"交易天数: {len(df)}天")
        print(f"期初价格: {first_price:.2f}元")
        print(f"期末价格: {latest_price:.2f}元")
        print(f"期间涨跌: {price_change:+.2f}元 ({price_change_pct:+.2f}%)")
        print(f"总成交量: {total_volume:,.0f}手")
        print(f"总成交额: {total_amount:,.0f}元")
        print()
        print("生成文件:")
        print(f"1. Excel文件: {excel_filename}")
        print(f"2. 图表文件: {chart_filename}")
        
        return {
            'excel_path': excel_path,
            'chart_path': chart_path,
            'summary': {
                'trading_days': len(df),
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'total_volume': total_volume,
                'total_amount': total_amount
            }
        }
        
    except Exception as e:
        print(f"导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 执行任务
if __name__ == "__main__":
    result = export_stock_daily_complete()
    
    if result:
        print(f"\n任务完成! 所有文件已保存到 workspace/exports/ 目录")
    else:
        print(f"\n任务失败，请检查token权限和网络连接")