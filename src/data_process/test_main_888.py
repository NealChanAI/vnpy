"""
测试888主力连续合约是否可用
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datetime import datetime, timedelta
from vnpy.trader.setting import SETTINGS
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest


def test_main_888():
    """测试888主力连续合约"""
    
    # 配置天勤
    TQDATA_USERNAME = "13716539053"
    TQDATA_PASSWORD = "Nealchan1001"
    
    SETTINGS["datafeed.name"] = "tqsdk"
    SETTINGS["datafeed.username"] = TQDATA_USERNAME
    SETTINGS["datafeed.password"] = TQDATA_PASSWORD
    
    datafeed = get_datafeed()
    
    # 测试几个主连合约
    test_cases = [
        ("rb888", Exchange.SHFE, "螺纹钢主连"),
        ("cu888", Exchange.SHFE, "铜主连"),
        ("IF888", Exchange.CFFEX, "沪深300主连"),
        ("i888", Exchange.DCE, "铁矿石主连"),
        ("MA888", Exchange.CZCE, "甲醇主连"),
    ]
    
    print("\n" + "=" * 80)
    print("测试 888 主力连续合约")
    print("=" * 80)
    
    # 查询最近30天
    end = datetime.now()
    start = end - timedelta(days=30)
    
    for symbol, exchange, name in test_cases:
        vt_symbol = f"{symbol}.{exchange.value}"
        print(f"\n📊 正在测试: {vt_symbol} ({name})")
        print(f"   查询范围: {start.date()} 至 {end.date()}")
        
        try:
            req = HistoryRequest(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.MINUTE,
                start=start,
                end=end
            )
            
            # 只查询前10条数据测试
            bars = datafeed.query_bar_history(req, 10)
            
            if bars:
                print(f"   ✅ 成功! 获取到 {len(bars)} 条数据")
                print(f"   📅 数据时间范围:")
                print(f"      开始: {bars[0].datetime}")
                print(f"      结束: {bars[-1].datetime}")
                print(f"   💰 最新价格: 开 {bars[-1].open_price:.2f} | "
                      f"高 {bars[-1].high_price:.2f} | "
                      f"低 {bars[-1].low_price:.2f} | "
                      f"收 {bars[-1].close_price:.2f}")
            else:
                print(f"   ❌ 无数据")
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    test_main_888()

