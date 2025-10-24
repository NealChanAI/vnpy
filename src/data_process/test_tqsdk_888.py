from tqsdk import TqApi, TqAuth
api = TqApi(auth=TqAuth("13716539053", "Nealchan1001"))
# 获取全部主连合约列表
main_contracts = api.query_quotes(ins_class="CONT")
print(f'len(main_contracts): {len(main_contracts)}  ')
print(main_contracts)  # 输出所有主连合约代码，如 ["KQ.m@SHFE.cu", "KQ.m@DCE.m", ...]
api.close()