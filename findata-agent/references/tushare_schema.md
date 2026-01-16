# Tushare Pro 接口参考

## 核心接口概览

### 股票行情接口

#### 日线行情
```python
# 基础日线数据
ts.daily(ts_code='600519.SH', start_date='20230101', end_date='20231231')

# 复权因子
ts.adj_factor(ts_code='600519.SH', start_date='20230101', end_date='20231231')

# 日线行情（含复权）
ts.daily_basic(ts_code='600519.SH', start_date='20230101', end_date='20231231')
```

**关键字段：**
- `ts_code` - 股票代码（格式：000001.SZ）
- `trade_date` - 交易日期
- `open` - 开盘价
- `high` - 最高价
- `low` - 最低价
- `close` - 收盘价
- `vol` - 成交量
- `amount` - 成交额

#### 周线/月线
```python
# 周线数据
ts.weekly(ts_code='600519.SH', start_date='20230101', end_date='20231231')

# 月线数据
ts.monthly(ts_code='600519.SH', start_date='20230101', end_date='20231231')
```

### K线数据
```python
# 获取K线数据（OHLC）
pro.kline(ts_code='600519.SH', start_date='20230101', end_date='20231231', kline='D')
```

**K线类型：**
- `D` - 日线
- `W` - 周线
- `M` - 月线

### 财务数据接口

#### 资产负债表
```python
# 资产负债表
pro.balancesheet(ts_code='600519.SH', start_date='20230101', end_date='20231231')
```

**关键字段：**
- `total_assets` - 资产总计
- `total_liab` - 负债合计
- `total_hldr_eqy_exc_min_int` - 股东权益合计

#### 利润表
```python
# 利润表
pro.income(ts_code='600519.SH', start_date='20230101', end_date='20231231')
```

**关键字段：**
- `revenue` - 营业收入
- `n_income` - 净利润
- `gross_profit` - 营业利润

#### 现金流量表
```python
# 现金流量表
pro.cashflow(ts_code='600519.SH', start_date='20230101', end_date='20231231')
```

### 经济指标接口

#### GDP数据
```python
# GDP季度数据
pro.gdp_quarter(start_period='20180101', end_period='20231231')
```

**关键字段：**
- `quarter` - 季度
- `gdp` - GDP绝对值
- `gdp_yoy` - GDP同比增长
- `gdp_qoq` - GDP环比增长

#### CPI数据
```python
# CPI月度数据
pro.cpi(start_date='20230101', end_date='20231231')
```

#### PMI数据
```python
# 制造业PMI
pro.pmi(start_date='20230101', end_date='20231231')
```

### 行业数据接口

#### 行业概念
```python
# 获取行业分类
pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

# 概念板块
pro.concept(limit=100)
```

#### 行业行情
```python
# 行业日线行情
pro.index_daily(ts_code='000001.SH', start_date='20230101', end_date='20231231')
```

## 常用查询模式

### 股票基础信息
```python
# 获取股票基本信息
pro.stock_basic(exchange='', list_status='L', 
                fields='ts_code,symbol,name,area,industry,market,list_date')
```

### 实时行情
```python
# 实时行情（需要Level-2权限）
pro.realtime(ts_code='600519.SH')
```

### 历史数据分页
```python
# 分页获取大量数据
df_list = []
offset = 0
limit = 5000

while True:
    df = pro.daily(ts_code='600519.SH', 
                   start_date='20200101', 
                   end_date='20231231',
                   limit=limit, 
                   offset=offset)
    if df.empty:
        break
    df_list.append(df)
    offset += limit

result_df = pd.concat(df_list, ignore_index=True)
```

## 数据处理最佳实践

### 数据清洗
```python
# 处理缺失值
df = df.dropna()

# 转换数据类型
df['trade_date'] = pd.to_datetime(df['trade_date'])
df['close'] = df['close'].astype(float)

# 排序
df = df.sort_values('trade_date')
```

### 复权处理
```python
# 前复权
df['adj_close'] = df['close'] * df['adj_factor']

# 后复权
df['adj_close'] = df['close'] / df['adj_factor'].iloc[-1]
```

### 技术指标计算
```python
# 移动平均线
df['ma5'] = df['close'].rolling(window=5).mean()
df['ma20'] = df['close'].rolling(window=20).mean()

# RSI指标
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['rsi'] = calculate_rsi(df['close'])
```

## 错误处理

### API限制处理
```python
import time
import random

def safe_api_call(func, *args, **kwargs):
    max_retries = 3
    for i in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if i < max_retries - 1:
                wait_time = random.uniform(1, 3)
                time.sleep(wait_time)
            else:
                raise e
```

### 数据验证
```python
# 验证股票代码格式
import re

def validate_ts_code(ts_code):
    pattern = r'^\d{6}\.(SH|SZ)$'
    return bool(re.match(pattern, ts_code))

# 验证日期格式
def validate_date(date_str):
    try:
        pd.to_datetime(date_str, format='%Y%m%d')
        return True
    except:
        return False
```

## 常见问题

### Q: 如何获取所有股票列表？
A: 使用`pro.stock_basic()`接口，设置`list_status='L'`获取在途交易股票。

### Q: 数据更新时间？
A: 日线数据通常在交易日当晚8-9点更新，财务数据按季度更新。

### Q: API调用频率限制？
A: 普通用户每分钟200次，积分用户根据等级提升频率限制。

### Q: 如何处理停牌数据？
A: 停牌股票在日线数据中不会出现，需要单独查询停牌信息。