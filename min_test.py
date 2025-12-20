from dotenv import load_dotenv
load_dotenv()
from core.agent_engine import agent_workflow

def main():

    """
    print(">>> Test 1: 获取数据 (Excel)")
    intent = "我希望获取2023年1月1日至2023年1月31日的平安银行的股票收盘价数据"
    ok, out = agent_workflow(intent)
    if ok:
        print(f"Success: {out}")
    else:
        print(f"Failed: {out}")


    print("\n>>> Test 2: 获取数据并画图 (扩展性测试)")
    # 这个测试依赖于 knowledge_base 中存在 plot_line_chart 的定义
    intent_plot = "获取平安银行2023年1月1日到2023年3月1日的收盘价并画出折线图"
    ok, out = agent_workflow(intent_plot)
    if ok:
         print(f"Success: {out}")
    else:
        print(f"Failed: {out}")
    """

    """
    print(">>> Test 1: 获取数据 (Excel)")
    intent = "我希望获取2023年1月1日至2023年1月31日的贵州茅台的股票收盘价数据"
    ok, out = agent_workflow(intent)
    if ok:
        print(f"Success: {out}")
    else:
        print(f"Failed: {out}")

    print("\n>>> Test 2: 仅导出(不画图)")
    intent2 = "导出600519.SH在2023年01月01日至2023年01月31日的日线到Excel"
    ok2, out2 = agent_workflow(intent2)
    if ok2:
        print(f"Success: {out2}")
    else:
        print(f"Failed: {out2}")

    print("\n>>> Test 3: 仅画图(不导出)")
    intent3 = "绘制海康威视2023年03月01日至2023年04月01日的收盘价折线图"
    ok3, out3 = agent_workflow(intent3)
    if ok3:
        print(f"Success: {out3}")
    else:
        print(f"Failed: {out3}")

    print("\n>>> Test 4: 同时导出与画图")
    intent4 = "获取平安银行2023年01月01日至2023年03月01日的日线并导出Excel，同时画折线图"
    ok4, out4 = agent_workflow(intent4)
    if ok4:
        print(f"Success: {out4}")
    else:
        print(f"Failed: {out4}")

    print("\n>>> Test 5: 模糊名称默认导出")
    intent5 = "获取茅台2023年01月01日至2023年01月31日的日线"
    ok5, out5 = agent_workflow(intent5)
    if ok5:
        print(f"Success: {out5}")
    else:
        print(f"Failed: {out5}")
    """
    print("\n>>> Test 6: 仅描述获取数据")
    intent6 = "获取数据：平安银行2023年01月01日至2023年01月31日的日线"
    ok6, out6 = agent_workflow(intent6)
    if ok6:
        print(f"Success: {out6}")
    else:
        print(f"Failed: {out6}")

if __name__ == "__main__":
    main()
