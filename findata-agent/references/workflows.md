# FinDataAgent 工作流参考

## 主工作流程

### 1. 意图解析流程
```python
# 用户输入示例
user_input = "分析贵州茅台近一年的股价趋势并绘制折线图"

# 意图识别关键要素
intent_analysis = {
    "target": "贵州茅台",           # 分析对象
    "ts_code": "600519.SH",        # 股票代码
    "period": "近一年",             # 时间范围
    "analysis_type": "股价趋势",    # 分析类型
    "output_format": "折线图"       # 输出格式
}
```

### 2. 代码生成模板

#### 股票趋势分析模板
```python
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 初始化Tushare
ts.set_token('YOUR_TOKEN')
pro = ts.pro_api()

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 获取数据
def get_stock_data(ts_code, start_date, end_date):
    """获取股票日线数据"""
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    return df.sort_values('trade_date')

# 计算技术指标
def calculate_indicators(df):
    """计算移动平均线和其他技术指标"""
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    return df

# 绘制趋势图
def plot_trend(df, stock_name):
    """绘制股价趋势图"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 价格走势图
    ax1.plot(df['trade_date'], df['close'], label='收盘价', linewidth=2)
    ax1.plot(df['trade_date'], df['ma5'], label='MA5', alpha=0.7)
    ax1.plot(df['trade_date'], df['ma20'], label='MA20', alpha=0.7)
    ax1.plot(df['trade_date'], df['ma60'], label='MA60', alpha=0.7)
    
    ax1.set_title(f'{stock_name} 股价趋势', fontsize=16)
    ax1.set_ylabel('价格 (元)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 成交量图
    ax2.bar(df['trade_date'], df['vol'], alpha=0.6, color='blue')
    ax2.set_title('成交量', fontsize=14)
    ax2.set_ylabel('成交量 (手)', fontsize=12)
    ax2.set_xlabel('日期', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# 主执行函数
def main():
    # 参数设置
    ts_code = "600519.SH"
    stock_name = "贵州茅台"
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    # 获取并处理数据
    df = get_stock_data(ts_code, start_date, end_date)
    df = calculate_indicators(df)
    
    # 绘制图表
    fig = plot_trend(df, stock_name)
    
    # 保存图表
    output_path = f"workspace/exports/{stock_name}_趋势图_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"图表已保存至: {output_path}")
    
    # 导出数据
    data_output = f"workspace/exports/{stock_name}_数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(data_output, index=False)
    print(f"数据已导出至: {data_output}")

if __name__ == "__main__":
    main()
```

#### 财务数据分析模板
```python
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt

def analyze_financial_data(ts_code, start_year, end_year):
    """分析财务数据"""
    pro = ts.pro_api()
    
    # 获取利润表数据
    income_df = pro.income(ts_code=ts_code, 
                           start_date=f"{start_year}1231", 
                           end_date=f"{end_year}1231")
    
    # 获取资产负债表数据
    balance_df = pro.balancesheet(ts_code=ts_code,
                                 start_date=f"{start_year}1231",
                                 end_date=f"{end_year}1231")
    
    # 数据处理和分析
    # ... 具体分析逻辑
    
    return income_df, balance_df
```

### 3. 流式输出处理

#### 流式响应格式
```python
# 流式输出数据结构
stream_response = {
    "type": "thinking",  # thinking, code, result, error
    "content": "正在分析用户需求...",
    "timestamp": "2024-01-14 10:30:00"
}

# 代码生成阶段
code_response = {
    "type": "code",
    "content": "import tushare as ts\n...",
    "language": "python"
}

# 结果展示阶段
result_response = {
    "type": "result",
    "content": {
        "charts": ["path/to/chart.png"],
        "data": ["path/to/data.xlsx"],
        "summary": "分析完成，发现股价呈现上升趋势..."
    }
}
```

## 错误处理工作流

### 1. API调用错误
```python
def handle_api_error(error):
    """处理API调用错误"""
    error_mapping = {
        "积分不足": "请检查Tushare积分余额",
        "频率限制": "API调用频率超限，请稍后重试",
        "参数错误": "请检查股票代码或日期格式",
        "数据不存在": "指定时间范围内无数据"
    }
    
    for key, message in error_mapping.items():
        if key in str(error):
            return message
    
    return f"未知错误: {str(error)}"
```

### 2. 代码执行错误
```python
def safe_code_execution(code, context):
    """安全执行生成的代码"""
    try:
        # 创建安全的执行环境
        exec_globals = {
            "ts": ts,
            "pd": pd,
            "plt": plt,
            "np": np,
            "__builtins__": {}
        }
        
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        
        return {"status": "success", "result": exec_locals}
        
    except SyntaxError as e:
        return {"status": "error", "message": f"代码语法错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"执行错误: {e}"}
```

## 性能优化工作流

### 1. 数据缓存策略
```python
import pickle
import os
from datetime import datetime, timedelta

class DataCache:
    def __init__(self, cache_dir="workspace/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, api_name, params):
        """生成缓存键"""
        param_str = "_".join([f"{k}:{v}" for k, v in sorted(params.items())])
        return f"{api_name}_{param_str}.pkl"
    
    def is_cache_valid(self, cache_file, max_age_hours=24):
        """检查缓存是否有效"""
        if not os.path.exists(cache_file):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - file_time < timedelta(hours=max_age_hours)
    
    def get_data(self, api_name, params):
        """获取缓存数据"""
        cache_key = self.get_cache_key(api_name, params)
        cache_file = os.path.join(self.cache_dir, cache_key)
        
        if self.is_cache_valid(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        return None
    
    def set_data(self, api_name, params, data):
        """设置缓存数据"""
        cache_key = self.get_cache_key(api_name, params)
        cache_file = os.path.join(self.cache_dir, cache_key)
        
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
```

### 2. 异步处理
```python
import asyncio
import concurrent.futures

async def async_data_processing(tasks):
    """异步处理多个数据任务"""
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            loop.run_in_executor(executor, process_task, task)
            for task in tasks
        ]
        
        results = await asyncio.gather(*futures)
    
    return results
```

## 用户交互工作流

### 1. 意图确认机制
```python
def confirm_intent(user_input, parsed_intent):
    """确认解析的用户意图"""
    confirmation = f"""
    我理解您的需求是：
    - 分析对象: {parsed_intent.get('target')}
    - 时间范围: {parsed_intent.get('period')}
    - 输出格式: {parsed_intent.get('output_format')}
    
    是否正确？如需修改请说明。
    """
    return confirmation
```

### 2. 进度反馈
```python
def progress_feedback(stage, total_stages):
    """生成进度反馈"""
    progress_messages = {
        1: "正在解析您的需求...",
        2: "正在生成分析代码...",
        3: "正在获取数据...",
        4: "正在处理数据...",
        5: "正在生成图表...",
        6: "正在保存结果..."
    }
    
    message = progress_messages.get(stage, "处理中...")
    progress = stage / total_stages
    
    return {
        "message": message,
        "progress": progress,
        "stage": stage
    }
```