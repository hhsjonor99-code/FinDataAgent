"""
FinDataAgent 经济数据分析模板
提供宏观经济数据分析的代码模板
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts
from datetime import datetime, timedelta
import os

def economic_analysis_template(indicator_name, start_period, end_period):
    """
    经济数据分析模板
    
    Args:
        indicator_name: 指标名称 (GDP, CPI, PMI等)
        start_period: 开始期间 (格式: 20180101)
        end_period: 结束期间 (格式: 20231231)
    """
    
    print(f"正在获取 {indicator_name} 数据...")
    
    try:
        pro = ts.pro_api()
        
        # 根据指标类型获取数据
        if indicator_name.upper() == 'GDP':
            df = pro.gdp_quarter(start_period=start_period, end_period=end_period)
            data_type = '季度'
            value_col = 'gdp'
            date_col = 'quarter'
            
        elif indicator_name.upper() == 'CPI':
            df = pro.cpi(start_date=start_period, end_date=end_period)
            data_type = '月度'
            value_col = 'cpi'
            date_col = 'date'
            
        elif indicator_name.upper() == 'PMI':
            df = pro.pmi(start_date=start_period, end_date=end_period)
            data_type = '月度'
            value_col = 'pmi'
            date_col = 'date'
            
        else:
            print(f"不支持的经济指标: {indicator_name}")
            return None
        
        if df.empty:
            print(f"未获取到 {indicator_name} 的数据")
            return None
        
        print(f"成功获取 {len(df)} 个{data_type}的数据点")
        
    except Exception as e:
        print(f"数据获取失败: {e}")
        return None
    
    # 数据预处理
    print("正在处理数据...")
    
    # 转换日期格式
    if date_col == 'quarter':
        # 季度数据转换
        df['date'] = df['quarter'].apply(lambda x: f"{x[:4]}-{str(int(x[4:])*3-2):02d}-01")
        df['date'] = pd.to_datetime(df['date'])
    else:
        df['date'] = pd.to_datetime(df[date_col])
    
    # 排序
    df = df.sort_values('date').reset_index(drop=True)
    
    # 转换数值类型
    for col in df.columns:
        if col not in ['date', 'quarter', 'date'] and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 2. 数据分析
    print("正在进行数据分析...")
    
    # 基本统计
    latest_value = df[value_col].iloc[-1]
    first_value = df[value_col].iloc[0]
    total_change = latest_value - first_value
    total_change_pct = (total_change / first_value) * 100
    
    max_value = df[value_col].max()
    min_value = df[value_col].min()
    avg_value = df[value_col].mean()
    
    # 趋势分析
    # 计算移动平均
    df['ma3'] = df[value_col].rolling(window=3, min_periods=1).mean()
    df['ma6'] = df[value_col].rolling(window=6, min_periods=1).mean()
    
    # 同比/环比增长
    if 'yoy' in df.columns:
        df['growth_yoy'] = df['yoy']
        latest_growth_yoy = df['yoy'].iloc[-1]
    else:
        # 计算同比增长
        if data_type == '季度':
            df['growth_yoy'] = df[value_col].pct_change(periods=4) * 100
        else:
            df['growth_yoy'] = df[value_col].pct_change(periods=12) * 100
        latest_growth_yoy = df['growth_yoy'].iloc[-1] if not pd.isna(df['growth_yoy'].iloc[-1]) else 0
    
    # 环比增长
    if 'mom' in df.columns:
        df['growth_mom'] = df['mom']
        latest_growth_mom = df['mom'].iloc[-1]
    else:
        df['growth_mom'] = df[value_col].pct_change() * 100
        latest_growth_mom = df['growth_mom'].iloc[-1] if not pd.isna(df['growth_mom'].iloc[-1]) else 0
    
    print(f"""
    === {indicator_name} 分析结果 ===
    最新数值: {latest_value:.2f}
    期间变化: {total_change:+.2f} ({total_change_pct:+.2f}%)
    最高值: {max_value:.2f}
    最低值: {min_value:.2f}
    平均值: {avg_value:.2f}
    
    增长情况:
    同比增长: {latest_growth_yoy:+.2f}%
    环比增长: {latest_growth_mom:+.2f}%
    """)
    
    # 3. 图表生成
    print("正在生成图表...")
    
    # 设置图表样式
    plt.style.use('seaborn-v0_8')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建复合图表
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # 主指标图表
    ax1 = axes[0]
    ax1.plot(df['date'], df[value_col], label=indicator_name, linewidth=3, color='blue')
    ax1.plot(df['date'], df['ma3'], label='3期移动平均', alpha=0.7, color='orange')
    ax1.plot(df['date'], df['ma6'], label='6期移动平均', alpha=0.7, color='red')
    
    ax1.set_title(f'{indicator_name} 走势图', fontsize=16, fontweight='bold')
    ax1.set_ylabel('数值', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 添加数值标注
    for i, (date, value) in enumerate(zip(df['date'], df[value_col])):
        if i % max(1, len(df) // 10) == 0:  # 每10个点标注一次
            ax1.annotate(f'{value:.1f}', (date, value), 
                        textcoords="offset points", xytext=(0,10), ha='center')
    
    # 增长率图表
    ax2 = axes[1]
    ax2.plot(df['date'], df['growth_yoy'], label='同比增长', linewidth=2, color='green')
    ax2.plot(df['date'], df['growth_mom'], label='环比增长', linewidth=2, color='purple')
    
    # 添加零线
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    ax2.set_title(f'{indicator_name} 增长率', fontsize=14)
    ax2.set_ylabel('增长率 (%)', fontsize=12)
    ax2.set_xlabel('日期', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chart_filename = f"{indicator_name}_经济分析_{timestamp}.png"
    chart_path = os.path.join(OUTPUT_DIR, chart_filename)
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"图表已保存至: {chart_path}")
    
    # 4. 数据导出
    print("正在导出数据...")
    
    # 选择要导出的列
    export_columns = ['date', value_col, 'ma3', 'ma6', 'growth_yoy', 'growth_mom']
    
    # 添加原始数据中的其他有用列
    for col in df.columns:
        if col not in export_columns and col not in ['quarter', date_col]:
            export_columns.append(col)
    
    export_data = df[export_columns].copy()
    
    # 导出Excel
    excel_filename = f"{indicator_name}_经济数据_{timestamp}.xlsx"
    excel_path = os.path.join(OUTPUT_DIR, excel_filename)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 处理后的数据
        export_data.to_excel(writer, sheet_name='分析数据', index=False)
        
        # 统计摘要
        summary_data = pd.DataFrame({
            '指标': ['最新数值', '期间变化', '变化百分比', '最高值', '最低值', '平均值', '同比增长', '环比增长'],
            '数值': [latest_value, total_change, total_change_pct, max_value, min_value, avg_value, 
                    latest_growth_yoy, latest_growth_mom]
        })
        summary_data.to_excel(writer, sheet_name='分析摘要', index=False)
        
        # 原始数据
        if not df.empty:
            df.to_excel(writer, sheet_name='原始数据', index=False)
    
    print(f"数据已导出至: {excel_path}")
    
    print(f"\n{indicator_name} 经济分析完成！")
    print(f"生成文件:")
    print(f"  - 图表: {chart_filename}")
    print(f"  - 数据: {excel_filename}")
    
    return {
        'data': export_data,
        'chart_path': chart_path,
        'excel_path': excel_path,
        'summary': {
            'latest_value': latest_value,
            'total_change': total_change,
            'total_change_pct': total_change_pct,
            'max_value': max_value,
            'min_value': min_value,
            'latest_growth_yoy': latest_growth_yoy,
            'latest_growth_mom': latest_growth_mom
        }
    }

def multi_indicator_comparison(indicators, start_period, end_period):
    """
    多指标对比分析模板
    
    Args:
        indicators: 指标列表 (如: ['GDP', 'CPI', 'PMI'])
        start_period: 开始期间
        end_period: 结束期间
    """
    
    print(f"正在进行多指标对比分析...")
    
    all_data = {}
    
    for indicator in indicators:
        print(f"获取 {indicator} 数据...")
        result = economic_analysis_template(indicator, start_period, end_period)
        if result:
            all_data[indicator] = result['data']
    
    if len(all_data) < 2:
        print("需要至少2个有效指标进行对比")
        return None
    
    # 创建对比图表
    print("正在生成对比图表...")
    
    fig, axes = plt.subplots(len(all_data), 1, figsize=(14, 8 * len(all_data)))
    
    if len(all_data) == 1:
        axes = [axes]
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (indicator, data) in enumerate(all_data.items()):
        ax = axes[i]
        color = colors[i % len(colors)]
        
        # 标准化数据用于对比 (0-100范围)
        if 'value' in data.columns or len(data.columns) > 1:
            value_col = data.columns[1]  # 假设第二列是数值列
            normalized_values = ((data[value_col] - data[value_col].min()) / 
                               (data[value_col].max() - data[value_col].min()) * 100)
            
            ax.plot(data['date'], normalized_values, label=f'{indicator} (标准化)', 
                   linewidth=2, color=color)
            ax.plot(data['date'], data[value_col], label=f'{indicator} (原始值)', 
                   alpha=0.5, linestyle='--', color=color)
        
        ax.set_title(f'{indicator} 趋势', fontsize=14, fontweight='bold')
        ax.set_ylabel('数值', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('日期', fontsize=12)
    
    plt.tight_layout()
    
    # 保存对比图表
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    indicators_str = '_vs_'.join(indicators)
    chart_filename = f"多指标对比_{indicators_str}_{timestamp}.png"
    chart_path = os.path.join(OUTPUT_DIR, chart_filename)
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"对比图表已保存至: {chart_path}")
    
    return {
        'chart_path': chart_path,
        'data': all_data
    }

# 使用示例
if __name__ == "__main__":
    # 注意：需要先设置Tushare token
    # ts.set_token('your_token_here')
    
    # 单个指标分析
    result = economic_analysis_template("GDP", "20180101", "20231231")
    
    if result:
        print("经济指标分析成功完成！")
    
    # 多指标对比分析
    # comparison_result = multi_indicator_comparison(['GDP', 'CPI'], "20180101", "20231231")