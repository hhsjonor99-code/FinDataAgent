"""
FinDataAgent 代码执行器
提供安全的代码执行环境和依赖注入
"""

import sys
import os
import traceback
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess
import tempfile
import shutil

class SafeCodeExecutor:
    """安全代码执行器"""
    
    def __init__(self, workspace_dir="workspace"):
        """初始化执行器"""
        self.workspace_dir = workspace_dir
        self.temp_dir = os.path.join(workspace_dir, "temp_scripts")
        self.output_dir = os.path.join(workspace_dir, "exports")
        
        # 创建工作目录
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置执行环境
        self.setup_environment()
    
    def setup_environment(self):
        """设置执行环境"""
        # 配置matplotlib
        plt.switch_backend('Agg')  # 使用非交互式后端
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.figsize'] = (12, 8)
        
        # 设置pandas显示选项
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)
    
    def inject_dependencies(self, code, tushare_token=None):
        """
        注入必要的依赖和配置
        
        Args:
            code: 用户代码
            tushare_token: Tushare token
        
        Returns:
            str: 注入依赖后的完整代码
        """
        # 依赖注入模板
        dependency_template = f'''
# FinDataAgent 自动注入的依赖
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import sys

# 添加工作目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tushare配置
try:
    import tushare as ts
    if "{tushare_token}" and "{tushare_token}" != "None":
        ts.set_token("{tushare_token}")
        pro = ts.pro_api()
    print("Tushare初始化成功")
except Exception as e:
    print(f"Tushare初始化失败: {{e}}")

# Matplotlib配置
plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 8)

# 工作目录配置
WORKSPACE_DIR = "{self.workspace_dir}"
OUTPUT_DIR = "{self.output_dir}"
TEMP_DIR = "{self.temp_dir}"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

print("依赖注入完成")
print(f"工作目录: {{WORKSPACE_DIR}}")
print(f"输出目录: {{OUTPUT_DIR}}")

# 用户代码开始
'''
        
        return dependency_template + code
    
    def execute_code(self, code, tushare_token=None, timeout=120):
        """
        执行用户代码
        
        Args:
            code: 要执行的Python代码
            tushare_token: Tushare API token
            timeout: 执行超时时间（秒）
        
        Returns:
            dict: 执行结果
        """
        result = {
            'success': False,
            'output': '',
            'error': '',
            'files_created': [],
            'execution_time': 0
        }
        
        start_time = datetime.now()
        
        try:
            # 注入依赖
            full_code = self.inject_dependencies(code, tushare_token)
            
            # 创建临时脚本文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_filename = f"temp_script_{timestamp}.py"
            script_path = os.path.join(self.temp_dir, script_filename)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(full_code)
            
            # 执行代码
            try:
                # 使用subprocess执行，更安全
                process = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.workspace_dir
                )
                
                result['output'] = process.stdout
                result['error'] = process.stderr
                result['success'] = process.returncode == 0
                
            except subprocess.TimeoutExpired:
                result['error'] = f"代码执行超时（{timeout}秒）"
                result['success'] = False
            
            # 检查生成的文件
            result['files_created'] = self.get_created_files(start_time)
            
            # 清理临时文件
            try:
                os.remove(script_path)
            except:
                pass
            
        except Exception as e:
            result['error'] = f"执行器错误: {str(e)}\n{traceback.format_exc()}"
            result['success'] = False
        
        finally:
            result['execution_time'] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def execute_code_direct(self, code, tushare_token=None):
        """
        直接执行代码（不使用subprocess）
        
        Args:
            code: 要执行的Python代码
            tushare_token: Tushare API token
        
        Returns:
            dict: 执行结果
        """
        result = {
            'success': False,
            'output': '',
            'error': '',
            'files_created': [],
            'execution_time': 0
        }
        
        start_time = datetime.now()
        
        try:
            # 注入依赖
            full_code = self.inject_dependencies(code, tushare_token)
            
            # 准备执行环境
            exec_globals = {
                'pd': pd,
                'np': np,
                'plt': plt,
                'datetime': datetime,
                'timedelta': timedelta,
                'os': os,
                'sys': sys,
                'WORKSPACE_DIR': self.workspace_dir,
                'OUTPUT_DIR': self.output_dir,
                'TEMP_DIR': self.temp_dir,
                '__builtins__': __builtins__
            }
            
            # 如果有Tushare token，添加tushare
            if tushare_token:
                try:
                    import tushare as ts
                    ts.set_token(tushare_token)
                    exec_globals['ts'] = ts
                    exec_globals['pro'] = ts.pro_api()
                except Exception as e:
                    result['error'] = f"Tushare初始化失败: {e}"
                    return result
            
            exec_locals = {}
            
            # 重定向输出
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                try:
                    exec(full_code, exec_globals, exec_locals)
                    result['success'] = True
                except Exception as e:
                    result['error'] = f"代码执行错误: {str(e)}\n{traceback.format_exc()}"
            
            result['output'] = stdout_capture.getvalue()
            if not result['error']:
                result['error'] = stderr_capture.getvalue()
            
            # 检查生成的文件
            result['files_created'] = self.get_created_files(start_time)
            
        except Exception as e:
            result['error'] = f"执行器错误: {str(e)}\n{traceback.format_exc()}"
        
        finally:
            result['execution_time'] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def get_created_files(self, since_time):
        """获取指定时间后创建的文件"""
        created_files = []
        
        try:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time >= since_time:
                        rel_path = os.path.relpath(file_path, self.workspace_dir)
                        created_files.append({
                            'path': rel_path,
                            'full_path': file_path,
                            'size': os.path.getsize(file_path),
                            'created_time': file_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        except Exception as e:
            print(f"获取文件列表失败: {e}")
        
        return created_files
    
    def validate_code(self, code):
        """
        验证代码安全性
        
        Args:
            code: 要验证的代码
        
        Returns:
            tuple: (is_safe, warnings)
        """
        warnings = []
        is_safe = True
        
        # 危险操作列表
        dangerous_operations = [
            'os.system', 'subprocess.call', 'subprocess.run',
            'eval(', 'exec(', 'compile(',
            '__import__', 'open(', 'file(',
            'input(', 'raw_input(',
            'socket.', 'urllib.', 'requests.',
            'shutil.rmtree', 'os.remove', 'os.unlink'
        ]
        
        # 检查危险操作
        for op in dangerous_operations:
            if op in code:
                warnings.append(f"检测到潜在危险操作: {op}")
                is_safe = False
        
        # 检查文件操作
        file_operations = ['open(', 'with open', 'pd.read_', 'pd.to_']
        for op in file_operations:
            if op in code:
                warnings.append(f"检测到文件操作: {op}")
        
        return is_safe, warnings
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
                print("临时文件清理完成")
        except Exception as e:
            print(f"清理临时文件失败: {e}")

# 示例使用
def demo_code_execution():
    """演示代码执行"""
    executor = SafeCodeExecutor()
    
    # 示例代码
    test_code = '''
# 测试代码
import pandas as pd
import numpy as np
from datetime import datetime

print("开始执行测试代码")

# 创建测试数据
dates = pd.date_range('2023-01-01', periods=10)
data = pd.DataFrame({
    'date': dates,
    'value': np.random.randn(10).cumsum() + 100
})

print("测试数据:")
print(data)

# 保存数据
output_file = os.path.join(OUTPUT_DIR, "test_data.xlsx")
data.to_excel(output_file, index=False)
print(f"数据已保存至: {output_file}")

# 创建简单图表
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(data['date'], data['value'], marker='o')
plt.title('测试图表')
plt.xlabel('日期')
plt.ylabel('数值')
plt.grid(True)
plt.xticks(rotation=45)

chart_file = os.path.join(OUTPUT_DIR, "test_chart.png")
plt.tight_layout()
plt.savefig(chart_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"图表已保存至: {chart_file}")
print("测试代码执行完成")
'''
    
    # 执行代码
    result = executor.execute_code_direct(test_code)
    
    print("执行结果:")
    print(f"成功: {result['success']}")
    print(f"执行时间: {result['execution_time']:.2f}秒")
    print(f"输出: {result['output']}")
    if result['error']:
        print(f"错误: {result['error']}")
    print(f"生成文件: {len(result['files_created'])}")
    
    for file_info in result['files_created']:
        print(f"  - {file_info['path']} ({file_info['size']} bytes)")

if __name__ == "__main__":
    demo_code_execution()