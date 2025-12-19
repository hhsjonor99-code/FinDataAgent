#  完成次项目的最小实践，即完成一个最小实践


#  需要完成的功能：
    1.core模块
    2.knowlege_base模块中的tushare_schema.json填充所需的知识条目
    3.tools模块中的tushare_api完成对应的封装，code_executor.py需要能够运行temp_scripts下的python脚本


# 假设用户输入：“我希望获取2023年1月1日至2023年12月31日的平安银行的股票收盘价数据“，完成对应工作流，在workspace/exports下生成对应的xlsx文件

    测试脚本为min_test.py,假设“我希望获取2023年1月1日至2023年12月31日的平安银行的股票收盘价数据“作为Agent的输入，完成对应工作流

#  为完成最小实践，所需要的tushare的接口函数示例如下

    pro = ts.pro_api()
    df = pro.daily(ts_code='000001.SZ', start_date='20180701', end_date='20180718')

  

