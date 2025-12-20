import sys
import os
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent_engine import agent_workflow

def main():
    print("==================================================")
    print("       FinDataAgent - Code Interpreter Mode       ")
    print("==================================================")
    print("Type 'exit' or 'quit' to stop.")
    print("Example: 获取平安银行2023年1月的日线数据并画图")
    print("--------------------------------------------------")

    while True:
        try:
            user_input = input("\nUser> ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit"]:
                print("Bye!")
                break
                
            print(f"\n[Agent] Processing: {user_input}...")
            
            success, result = agent_workflow(user_input)
            
            if success:
                print(f"\n[SUCCESS] Result:\n{result}")
            else:
                print(f"\n[FAILURE] Error:\n{result}")
                
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()
