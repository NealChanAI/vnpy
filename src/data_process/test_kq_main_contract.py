"""
测试天勤主连合约格式 KQ.m@交易所.品种
"""

import os
from datetime import datetime, timedelta
from vnpy.trader.setting import SETTINGS
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest


# 配置天勤
TQDATA_USERNAME = "13716539053"
TQDATA_PASSWORD = "Nealchan1001"

SETTINGS["datafeed.name"] = "tqsdk"
SETTINGS["datafeed.username"] = TQDATA_USERNAME
SETTINGS["datafeed.password"] = TQDATA_PASSWORD

datafeed = get_datafeed()
datafeed.init()

print("\n" + "=" * 80)
print("测试天勤主连合约格式: KQ.m@交易所.品种")
print("=" * 80)

# 测试不同的主连格式
test_cases = [
    # 格式1: KQ.m@交易所.品种 (天勤文档中的格式)
    ("KQ.m@SHFE.rb", Exchange.SHFE, "螺纹钢主连(KQ格式)"),
    ("KQ.m@SHFE.cu", Exchange.SHFE, "铜主连(KQ格式)"),
    ("KQ.m@DCE.m", Exchange.DCE, "豆粕主连(KQ格式)"),
    
    # 格式2: 直接用交易所.品种主连
    ("CONT@SHFE.rb", Exchange.SHFE, "螺纹钢主连(CONT格式)"),
    
    # 格式3: 尝试m@格式
    ("m@SHFE.rb", Exchange.SHFE, "螺纹钢主连(m@格式)"),
]

# 查询最近10天
end = datetime.now()
start = end - timedelta(days=10)

print(f"\n查询时间范围: {start.date()} 至 {end.date()}\n")

for symbol, exchange, name in test_cases:
    print(f"📊 测试: {symbol} ({name})")
    
    try:
        req = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.MINUTE,
            start=start,
            end=end
        )
        
        bars = datafeed.query_bar_history(req, 10)
        
        if bars:
            print(f"   ✅ 成功! 获取 {len(bars)} 条数据")
            print(f"   📅 最新时间: {bars[-1].datetime}")
            print(f"   💰 最新价格: {bars[-1].close_price:.2f}")
        else:
            print(f"   ⚠️  没有数据")
            
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    print()

print("=" * 80)
print("测试完成！")
print("\n💡 如果KQ.m@格式可用，我们就用这个格式下载主连合约数据")
print("=" * 80)

