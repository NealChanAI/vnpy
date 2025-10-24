"""
测试下载888主力连续合约 - 基于download_tqdata.py
"""

import os
from datetime import datetime
from vnpy.trader.setting import SETTINGS
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.database import get_database, DB_TZ
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest
from vnpy.trader.utility import extract_vt_symbol


# 天勤账号
TQDATA_USERNAME = os.getenv("TQDATA_USERNAME","13716539053")
TQDATA_PASSWORD = os.getenv("TQDATA_PASSWORD","Nealchan1001")

# 配置天勤数据源
SETTINGS["datafeed.name"] = "tqsdk"
SETTINGS["datafeed.username"] = TQDATA_USERNAME
SETTINGS["datafeed.password"] = TQDATA_PASSWORD

# 获取数据接口和数据库
datafeed = get_datafeed()
database = get_database()


# 测试主连合约列表（只测试5个）
TEST_SYMBOLS = [
    'rb888.SHFE',    # 螺纹钢主连
    'cu888.SHFE',    # 铜主连
    'IF888.CFFEX',   # 沪深300主连
    'i888.DCE',      # 铁矿石主连
    'MA888.CZCE',    # 甲醇主连
]


def test_query_888():
    """测试查询888主连合约"""
    
    print("\n" + "=" * 100)
    print("测试 888 主力连续合约查询")
    print("=" * 100)
    print()
    
    # 查询最近30天数据
    end = datetime.now()
    start = datetime(2025, 10, 1)  # 从10月1日开始
    
    for vt_symbol in TEST_SYMBOLS:
        symbol, exchange = extract_vt_symbol(vt_symbol)
        exchange_enum = Exchange(exchange)
        
        print(f"📊 测试: {vt_symbol}")
        print(f"   查询时间: {start.date()} 至 {end.date()}")
        
        try:
            # 创建请求
            req = HistoryRequest(
                symbol=symbol,
                exchange=exchange_enum,
                interval=Interval.MINUTE,
                start=start,
                end=end
            )
            
            # 查询数据（限制前20条）
            bars = datafeed.query_bar_history(req, 20)
            
            if bars:
                print(f"   ✅ 成功! 获取 {len(bars)} 条数据")
                print(f"   📅 第一条: {bars[0].datetime} | 价格: {bars[0].close_price:.2f}")
                print(f"   📅 最后条: {bars[-1].datetime} | 价格: {bars[-1].close_price:.2f}")
            else:
                print(f"   ⚠️  没有数据")
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
        
        print()
    
    print("=" * 100)
    print("测试完成！")
    print("\n💡 如果888主连可用，我们就可以用它替换具体月份合约，")
    print("   这样数据会自动跟随主力合约，永远保持最新！")
    print("=" * 100)


if __name__ == "__main__":
    test_query_888()

