"""
测试下载主力连续合约数据
"""

import os
from datetime import datetime, timedelta
from vnpy.trader.setting import SETTINGS
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest


def test_main_contracts():
    """测试不同的主连合约格式"""
    
    # 配置天勤账号
    TQDATA_USERNAME = os.getenv("TQDATA_USERNAME", "13716539053")
    TQDATA_PASSWORD = os.getenv("TQDATA_PASSWORD", "Nealchan1001")
    
    SETTINGS["datafeed.name"] = "tqsdk"
    SETTINGS["datafeed.username"] = TQDATA_USERNAME
    SETTINGS["datafeed.password"] = TQDATA_PASSWORD
    
    # 初始化天勤数据接口
    datafeed = get_datafeed()
    
    # 测试不同的主连格式
    test_symbols = [
        # 格式1：888（主力连续）
        ("rb888", Exchange.SHFE, "螺纹钢主连"),
        ("cu888", Exchange.SHFE, "铜主连"),
        ("au888", Exchange.SHFE, "黄金主连"),
        
        # 格式2：000（指数连续）
        ("rb000", Exchange.SHFE, "螺纹钢指数"),
        
        # 格式3：99（近月连续）
        ("rb99", Exchange.SHFE, "螺纹钢近月"),
        
        # 股指主连
        ("IF888", Exchange.CFFEX, "沪深300主连"),
        ("IC888", Exchange.CFFEX, "中证500主连"),
        
        # 大商所主连
        ("i888", Exchange.DCE, "铁矿石主连"),
        ("m888", Exchange.DCE, "豆粕主连"),
        
        # 郑商所主连
        ("MA888", Exchange.CZCE, "甲醇主连"),
        ("TA888", Exchange.CZCE, "PTA主连"),
        
        # 能源中心主连
        ("sc888", Exchange.INE, "原油主连"),
    ]
    
    print("=" * 100)
    print("测试主力连续合约数据可用性")
    print("=" * 100)
    print()
    
    # 设置查询时间范围（查询最近30天）
    end = datetime.now()
    start = end - timedelta(days=30)
    
    successful = []
    failed = []
    
    for symbol, exchange, name in test_symbols:
        print(f"正在测试: {symbol}.{exchange.value:8s} ({name})...", end=" ")
        
        try:
            # 创建历史数据请求
            req = HistoryRequest(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.MINUTE,
                start=start,
                end=end
            )
            
            # 查询数据（限制前10条测试）
            bars = datafeed.query_bar_history(req, 10)
            
            if bars:
                print(f"✅ 成功! 获取到 {len(bars)} 条数据")
                print(f"   最新时间: {bars[-1].datetime}")
                successful.append((symbol, exchange, name, len(bars), bars[-1].datetime))
            else:
                print("❌ 无数据")
                failed.append((symbol, exchange, name, "无数据"))
                
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            failed.append((symbol, exchange, name, str(e)))
    
    # 汇总结果
    print("\n" + "=" * 100)
    print(f"测试完成！成功: {len(successful)} 个  失败: {len(failed)} 个")
    print("=" * 100)
    
    if successful:
        print("\n✅ 可用的主连合约格式:")
        print("-" * 100)
        for symbol, exchange, name, count, latest_time in successful:
            print(f"   {symbol}.{exchange.value:8s} ({name:12s}) - 数据最新到: {latest_time}")
    
    if failed:
        print("\n❌ 不可用的格式:")
        print("-" * 100)
        for symbol, exchange, name, error in failed:
            print(f"   {symbol}.{exchange.value:8s} ({name:12s}) - {error}")
    
    print("\n" + "=" * 100)
    print("💡 建议：使用成功的格式来下载主力连续合约数据")
    print("=" * 100)


if __name__ == "__main__":
    test_main_contracts()

