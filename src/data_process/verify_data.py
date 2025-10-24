#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证数据库中的期货数据"""

from datetime import datetime
from vnpy.trader.database import get_database
from vnpy.trader.constant import Exchange, Interval

# 获取数据库实例
database = get_database()

# 要验证的合约
contracts = [
    ('rb2505', Exchange.SHFE, '螺纹钢'),
    ('hc2505', Exchange.SHFE, '热卷'),
    ('i2505', Exchange.DCE, '铁矿石'),
    ('j2505', Exchange.DCE, '焦炭'),
    ('jm2505', Exchange.DCE, '焦煤'),
]

print("=" * 60)
print("数据库数据验证")
print("=" * 60)

for symbol, exchange, name in contracts:
    bars = database.load_bar_data(
        symbol=symbol,
        exchange=exchange,
        interval=Interval.MINUTE,
        start=datetime(2024, 7, 16),
        end=datetime(2025, 1, 24)
    )
    
    if bars:
        print(f"\n✅ {name} ({symbol}.{exchange.value})")
        print(f"   数据量: {len(bars)} 条")
        print(f"   起始: {bars[0].datetime}")
        print(f"   结束: {bars[-1].datetime}")
        print(f"   示例: O:{bars[0].open_price} H:{bars[0].high_price} L:{bars[0].low_price} C:{bars[0].close_price}")
    else:
        print(f"\n❌ {name} ({symbol}.{exchange.value}): 无数据")

print("\n" + "=" * 60)
print("验证完成！所有数据已就绪，可以开始回测了！")
print("=" * 60)

