from dotenv import load_dotenv
load_dotenv()
from core.agent_engine import run_min_workflow

def main():
    print(">>> Test 1: 获取数据 (Excel)")
    intent = "我希望获取2023年1月1日至2023年1月31日的平安银行的股票收盘价数据"
    ok, out = run_min_workflow(intent)
    if ok:
        print(f"Success: {out}")
    else:
        print(f"Failed: {out}")

    print("\n>>> Test 2: 获取数据并画图 (扩展性测试)")
    # 这个测试依赖于 knowledge_base 中存在 plot_line_chart 的定义
    intent_plot = "获取平安银行2023年1月1日到2023年3月1日的收盘价并画出折线图"
    ok, out = run_min_workflow(intent_plot)
    if ok:
        print(f"Success: {out}")
    else:
        print(f"Failed: {out}")

if __name__ == "__main__":
    main()
