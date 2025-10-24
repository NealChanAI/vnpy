#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分析每天的数据条数"""

from datetime import datetime, timedelta
from collections import defaultdict
from vnpy.trader.database import get_database
from vnpy.trader.constant import Exchange, Interval

database = get_database()

# 分析螺纹钢数据
symbol = 'rb2505'
exchange = Exchange.SHFE

bars = database.load_bar_data(
    symbol=symbol,
    exchange=exchange,
    interval=Interval.MINUTE,
    start=datetime(2024, 12, 1),
    end=datetime(2024, 12, 31)
)

# 按日期统计
daily_count = defaultdict(int)
for bar in bars:
    date = bar.datetime.date()
    daily_count[date] += 1

print("=" * 60)
print(f"{symbol.upper()} - 每日1分钟数据条数统计")
print("=" * 60)

if daily_count:
    # 按日期排序
    sorted_dates = sorted(daily_count.items())
    
    print(f"\n前10天样本：")
    for i, (date, count) in enumerate(sorted_dates[:10], 1):
        print(f"{i:2d}. {date} : {count:3d} 条")
    
    # 统计
    counts = list(daily_count.values())
    avg_count = sum(counts) / len(counts)
    max_count = max(counts)
    min_count = min(counts)
    
    print(f"\n统计结果：")
    print(f"  总交易日: {len(daily_count)} 天")
    print(f"  平均每天: {avg_count:.0f} 条")
    print(f"  最多: {max_count} 条")
    print(f"  最少: {min_count} 条")
    
    print(f"\n原因分析：")
    print(f"  期货交易时间（以螺纹钢为例）：")
    print(f"  ├─ 白天: 09:00-10:15, 10:30-11:30, 13:30-15:00")
    print(f"  │         (75分钟 + 60分钟 + 90分钟 = 225分钟)")
    print(f"  └─ 夜盘: 21:00-23:00 (120分钟)")
    print(f"  合计约: 345分钟/天")
    print(f"  实际: {avg_count:.0f} 分钟/天 (包含集合竞价等)")

else:
    print("❌ 没有数据")

print("\n" + "=" * 60)

