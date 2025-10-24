"""
检查天勤TQData数据库中的数据
"""

from datetime import datetime, timedelta
from vnpy.trader.database import get_database, DB_TZ
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.utility import extract_vt_symbol
import pandas as pd


def check_database_overview():
    """查询数据库概览"""
    print("=" * 80)
    print("天勤数据库 - 数据概览")
    print("=" * 80)
    
    # 连接数据库
    try:
        database = get_database()
        print("✅ 数据库连接成功\n")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 获取K线数据概览
    print("【K线数据概览】")
    print("-" * 80)
    bar_overviews = database.get_bar_overview()
    
    if not bar_overviews:
        print("⚠️ 数据库中没有K线数据")
        return
    
    # 整理数据
    data_list = []
    for overview in bar_overviews:
        data_list.append({
            '合约代码': f"{overview.symbol}.{overview.exchange.value}",
            '交易所': overview.exchange.value,
            '周期': overview.interval.value,
            '数据量': f"{overview.count:,}",
            '开始时间': overview.start.strftime('%Y-%m-%d %H:%M:%S') if overview.start else 'N/A',
            '结束时间': overview.end.strftime('%Y-%m-%d %H:%M:%S') if overview.end else 'N/A',
        })
    
    # 显示数据表格
    df = pd.DataFrame(data_list)
    print(df.to_string(index=False))
    
    print("\n" + "=" * 80)
    print(f"总计: {len(bar_overviews)} 个合约")
    print(f"总数据量: {sum(o.count for o in bar_overviews):,} 条")
    print("=" * 80)


def check_specific_symbol(vt_symbol: str, days: int = 5):
    """查询特定合约的最新数据
    
    参数:
        vt_symbol: 合约代码，如 'rb2505.SHFE'
        days: 查询最近几天的数据，默认5天
    """
    print("\n" + "=" * 80)
    print(f"查询合约: {vt_symbol} (最近{days}天)")
    print("=" * 80)
    
    try:
        # 连接数据库
        database = get_database()
        
        # 解析合约代码
        symbol, exchange = extract_vt_symbol(vt_symbol)
        
        # 计算时间范围
        end = datetime.now(tz=DB_TZ)
        start = end - timedelta(days=days)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查询数据
        bars = database.load_bar_data(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.MINUTE,
            start=start,
            end=end
        )
        
        if not bars:
            print(f"⚠️ 没有找到 {vt_symbol} 的数据")
            return
        
        print(f"\n✅ 找到 {len(bars)} 条数据")
        print("-" * 80)
        
        # 显示前10条数据
        print("\n【前10条数据】")
        for i, bar in enumerate(bars[:10], 1):
            print(f"{i:2d}. {bar.datetime} | "
                  f"开:{bar.open_price:8.2f} "
                  f"高:{bar.high_price:8.2f} "
                  f"低:{bar.low_price:8.2f} "
                  f"收:{bar.close_price:8.2f} "
                  f"量:{bar.volume:8.0f}")
        
        if len(bars) > 20:
            print("\n... (中间省略) ...\n")
            
            # 显示最后10条数据
            print("【最后10条数据】")
            for i, bar in enumerate(bars[-10:], len(bars)-9):
                print(f"{i:2d}. {bar.datetime} | "
                      f"开:{bar.open_price:8.2f} "
                      f"高:{bar.high_price:8.2f} "
                      f"低:{bar.low_price:8.2f} "
                      f"收:{bar.close_price:8.2f} "
                      f"量:{bar.volume:8.0f}")
        elif len(bars) > 10:
            print("\n【后10条数据】")
            for i, bar in enumerate(bars[10:], 11):
                print(f"{i:2d}. {bar.datetime} | "
                      f"开:{bar.open_price:8.2f} "
                      f"高:{bar.high_price:8.2f} "
                      f"低:{bar.low_price:8.2f} "
                      f"收:{bar.close_price:8.2f} "
                      f"量:{bar.volume:8.0f}")
        
        # 统计信息
        print("\n" + "-" * 80)
        print(f"【数据统计】")
        print(f"时间范围: {bars[0].datetime} 至 {bars[-1].datetime}")
        print(f"总数据量: {len(bars):,} 条")
        print(f"最高价: {max(bar.high_price for bar in bars):.2f}")
        print(f"最低价: {min(bar.low_price for bar in bars):.2f}")
        print(f"总成交量: {sum(bar.volume for bar in bars):,.0f}")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")


def main():
    """主函数"""
    # 1. 查询数据库概览
    check_database_overview()
    
    # 2. 查询特定合约（根据下载的合约修改）
    print("\n")
    check_specific_symbol('rb2505.SHFE', days=365)  # 螺纹钢2505，最近365天
    
    # 可以添加更多合约查询
    # check_specific_symbol('hc2505.SHFE', days=30)  # 热卷2505
    # check_specific_symbol('i2505.DCE', days=30)    # 铁矿石2505


if __name__ == "__main__":
    main()
