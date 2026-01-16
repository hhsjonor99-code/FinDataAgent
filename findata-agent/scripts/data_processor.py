"""
FinDataAgent 数据处理脚本
提供常用的数据处理和分析功能
"""

import pandas as pd
import numpy as np
import tushare as ts
from datetime import datetime, timedelta
import os

class TushareDataProcessor:
    """Tushare数据处理器"""
    
    def __init__(self, token=None):
        """初始化处理器"""
        if token:
            ts.set_token(token)
        self.pro = ts.pro_api()
    
    def get_stock_daily(self, ts_code, start_date, end_date, adj='qfq'):
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adj: 复权类型 (qfq前复权, hfq后复权, None不复权)
        
        Returns:
            DataFrame: 处理后的股票数据
        """
        try:
            # 获取基础数据
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if df.empty:
                print(f"未获取到数据: {ts_code} {start_date} - {end_date}")
                return pd.DataFrame()
            
            # 获取复权因子
            if adj:
                adj_df = self.pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
                if not adj_df.empty:
                    df = df.merge(adj_df[['trade_date', 'adj_factor']], on='trade_date', how='left')
                    df['adj_factor'] = df['adj_factor'].fillna(1)
            
            # 数据类型转换
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'vol', 'amount']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 复权处理
            if adj == 'qfq' and 'adj_factor' in df.columns:
                # 前复权
                for col in ['open', 'high', 'low', 'close', 'pre_close']:
                    if col in df.columns:
                        df[col] = df[col] * df['adj_factor']
            elif adj == 'hfq' and 'adj_factor' in df.columns:
                # 后复权
                latest_factor = df['adj_factor'].iloc[-1]
                for col in ['open', 'high', 'low', 'close', 'pre_close']:
                    if col in df.columns:
                        df[col] = df[col] / df['adj_factor'] * latest_factor
            
            # 排序
            df = df.sort_values('trade_date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df):
        """
        计算技术指标
        
        Args:
            df: 股票数据DataFrame
        
        Returns:
            DataFrame: 包含技术指标的DataFrame
        """
        if df.empty or 'close' not in df.columns:
            return df
        
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
        
        # 成交量移动平均
        if 'vol' in df.columns:
            df['vol_ma5'] = df['vol'].rolling(window=5).mean()
            df['vol_ma20'] = df['vol'].rolling(window=20).mean()
        
        return df
    
    def get_financial_data(self, ts_code, start_date, end_date, report_type='annual'):
        """
        获取财务数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            report_type: 报告类型 (annual年报, quarter季报)
        
        Returns:
            dict: 包含各类财务数据的字典
        """
        financial_data = {}
        
        try:
            # 利润表
            income_df = self.pro.income(ts_code=ts_code, 
                                       start_date=start_date, 
                                       end_date=end_date)
            if not income_df.empty:
                financial_data['income'] = income_df
            
            # 资产负债表
            balance_df = self.pro.balancesheet(ts_code=ts_code,
                                              start_date=start_date,
                                              end_date=end_date)
            if not balance_df.empty:
                financial_data['balance'] = balance_df
            
            # 现金流量表
            cashflow_df = self.pro.cashflow(ts_code=ts_code,
                                           start_date=start_date,
                                           end_date=end_date)
            if not cashflow_df.empty:
                financial_data['cashflow'] = cashflow_df
            
            # 财务指标
            fina_indicator_df = self.pro.fina_indicator(ts_code=ts_code,
                                                      start_date=start_date,
                                                      end_date=end_date)
            if not fina_indicator_df.empty:
                financial_data['indicator'] = fina_indicator_df
            
            return financial_data
            
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return {}
    
    def get_economic_data(self, indicator_name, start_date, end_date):
        """
        获取经济数据
        
        Args:
            indicator_name: 指标名称
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            DataFrame: 经济数据
        """
        try:
            if indicator_name == 'GDP':
                df = self.pro.gdp_quarter(start_period=start_date.replace('-', ''), 
                                         end_period=end_date.replace('-', ''))
            elif indicator_name == 'CPI':
                df = self.pro.cpi(start_date=start_date.replace('-', ''), 
                                 end_date=end_date.replace('-', ''))
            elif indicator_name == 'PMI':
                df = self.pro.pmi(start_date=start_date.replace('-', ''), 
                                 end_date=end_date.replace('-', ''))
            else:
                print(f"不支持的经济指标: {indicator_name}")
                return pd.DataFrame()
            
            return df
            
        except Exception as e:
            print(f"获取经济数据失败: {e}")
            return pd.DataFrame()

class DataExporter:
    """数据导出器"""
    
    def __init__(self, output_dir="workspace/exports"):
        """初始化导出器"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_excel(self, data, filename=None, sheet_name="Sheet1"):
        """
        导出数据到Excel
        
        Args:
            data: 要导出的数据 (DataFrame或dict)
            filename: 文件名
            sheet_name: 工作表名
        
        Returns:
            str: 导出文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data_export_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            if isinstance(data, dict):
                # 多个工作表
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    for key, df in data.items():
                        if isinstance(df, pd.DataFrame) and not df.empty:
                            df.to_excel(writer, sheet_name=key, index=False)
            else:
                # 单个工作表
                data.to_excel(filepath, sheet_name=sheet_name, index=False)
            
            print(f"数据已导出至: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"导出Excel失败: {e}")
            return None
    
    def export_to_csv(self, df, filename=None):
        """
        导出数据到CSV
        
        Args:
            df: 要导出的DataFrame
            filename: 文件名
        
        Returns:
            str: 导出文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data_export_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"数据已导出至: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return None

def validate_ts_code(ts_code):
    """验证股票代码格式"""
    import re
    pattern = r'^\d{6}\.(SH|SZ)$'
    return bool(re.match(pattern, ts_code))

def validate_date_format(date_str):
    """验证日期格式"""
    try:
        pd.to_datetime(date_str, format='%Y%m%d')
        return True
    except:
        try:
            pd.to_datetime(date_str, format='%Y-%m-%d')
            return True
        except:
            return False

def get_date_range(period_str):
    """
    根据时期字符串获取日期范围
    
    Args:
        period_str: 时期字符串，如"近一年"、"最近30天"等
    
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = datetime.now()
    
    if '年' in period_str:
        years = int(period_str.split('近')[1].split('年')[0]) if '近' in period_str else 1
        start_date = end_date - timedelta(days=years * 365)
    elif '月' in period_str:
        months = int(period_str.split('近')[1].split('月')[0]) if '近' in period_str else 1
        start_date = end_date - timedelta(days=months * 30)
    elif '周' in period_str:
        weeks = int(period_str.split('近')[1].split('周')[0]) if '近' in period_str else 1
        start_date = end_date - timedelta(weeks=weeks * 7)
    elif '天' in period_str:
        days = int(period_str.split('近')[1].split('天')[0]) if '近' in period_str else 30
        start_date = end_date - timedelta(days=days)
    else:
        # 默认返回近一年
        start_date = end_date - timedelta(days=365)
    
    return (start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))

# 示例使用
def demo_data_processing():
    """演示数据处理功能"""
    # 注意：需要设置有效的Tushare token
    processor = TushareDataProcessor()
    
    # 获取股票数据
    df = processor.get_stock_daily('000001.SZ', '20230101', '20231231')
    
    if not df.empty:
        # 计算技术指标
        df = processor.calculate_technical_indicators(df)
        
        # 导出数据
        exporter = DataExporter()
        exporter.export_to_excel(df, 'demo_stock_data.xlsx')
        
        print("数据处理演示完成")
        return df
    else:
        print("未获取到数据")
        return None

if __name__ == "__main__":
    demo_data_processing()