"""
FinDataAgent 图表配置脚本
自动配置matplotlib中文字体和样式
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import os

def setup_matplotlib():
    """配置matplotlib环境"""
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置图表样式
    plt.style.use('seaborn-v0_8')
    
    # 设置默认图表大小
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['figure.dpi'] = 100
    
    # 设置网格
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    return True

def create_stock_chart(df, title="股票价格走势", save_path=None):
    """
    创建股票价格图表
    
    Args:
        df: 包含股票数据的DataFrame，需包含trade_date, close, vol等列
        title: 图表标题
        save_path: 保存路径，如不指定则不保存
    
    Returns:
        fig: matplotlib图表对象
    """
    setup_matplotlib()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 价格走势图
    ax1.plot(df['trade_date'], df['close'], label='收盘价', linewidth=2, color='blue')
    
    # 如果有移动平均线，也绘制出来
    if 'ma5' in df.columns:
        ax1.plot(df['trade_date'], df['ma5'], label='MA5', alpha=0.7, color='orange')
    if 'ma20' in df.columns:
        ax1.plot(df['trade_date'], df['ma20'], label='MA20', alpha=0.7, color='red')
    if 'ma60' in df.columns:
        ax1.plot(df['trade_date'], df['ma60'], label='MA60', alpha=0.7, color='green')
    
    ax1.set_title(title, fontsize=16, fontweight='bold')
    ax1.set_ylabel('价格 (元)', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 成交量图
    ax2.bar(df['trade_date'], df['vol'], alpha=0.6, color='lightblue')
    ax2.set_title('成交量', fontsize=14)
    ax2.set_ylabel('成交量 (手)', fontsize=12)
    ax2.set_xlabel('日期', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {save_path}")
    
    return fig

def create_candlestick_chart(df, title="K线图", save_path=None):
    """
    创建K线图
    
    Args:
        df: 包含OHLC数据的DataFrame
        title: 图表标题
        save_path: 保存路径
    
    Returns:
        fig: matplotlib图表对象
    """
    setup_matplotlib()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 绘制K线
    for i, row in df.iterrows():
        color = 'red' if row['close'] >= row['open'] else 'green'
        
        # 绘制实体
        ax.bar(row['trade_date'], row['close'] - row['open'], 
               bottom=row['open'], width=0.6, color=color, alpha=0.8)
        
        # 绘制影线
        ax.plot([row['trade_date'], row['trade_date']], 
               [row['low'], row['high']], 
               color=color, linewidth=1)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_ylabel('价格 (元)', fontsize=12)
    ax.set_xlabel('日期', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"K线图已保存至: {save_path}")
    
    return fig

def create_financial_chart(df, metrics, title="财务指标分析", save_path=None):
    """
    创建财务指标图表
    
    Args:
        df: 财务数据DataFrame
        metrics: 要绘制的指标列表
        title: 图表标题
        save_path: 保存路径
    
    Returns:
        fig: matplotlib图表对象
    """
    setup_matplotlib()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for metric in metrics:
        if metric in df.columns:
            ax.plot(df['trade_date'], df[metric], label=metric, linewidth=2, marker='o')
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_ylabel('金额 (元)', fontsize=12)
    ax.set_xlabel('日期', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"财务图表已保存至: {save_path}")
    
    return fig

def create_comparison_chart(data_dict, title="数据对比分析", save_path=None):
    """
    创建对比图表
    
    Args:
        data_dict: 数据字典，格式为 {'label': df}
        title: 图表标题
        save_path: 保存路径
    
    Returns:
        fig: matplotlib图表对象
    """
    setup_matplotlib()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (label, df) in enumerate(data_dict.items()):
        color = colors[i % len(colors)]
        ax.plot(df['trade_date'], df['close'], 
               label=label, linewidth=2, color=color)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_ylabel('价格 (元)', fontsize=12)
    ax.set_xlabel('日期', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"对比图表已保存至: {save_path}")
    
    return fig

def auto_generate_filename(prefix, suffix="png"):
    """自动生成文件名"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{suffix}"

def get_default_output_path(filename):
    """获取默认输出路径"""
    output_dir = "workspace/exports"
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)

# 示例使用函数
def demo_chart():
    """演示图表创建"""
    # 创建示例数据
    dates = pd.date_range('2023-01-01', periods=100)
    prices = np.random.randn(100).cumsum() + 100
    volumes = np.random.randint(1000, 10000, 100)
    
    df = pd.DataFrame({
        'trade_date': dates,
        'close': prices,
        'vol': volumes,
        'ma5': pd.Series(prices).rolling(5).mean(),
        'ma20': pd.Series(prices).rolling(20).mean()
    })
    
    # 创建图表
    fig = create_stock_chart(df, "演示股票图表")
    plt.show()
    
    return fig

if __name__ == "__main__":
    demo_chart()