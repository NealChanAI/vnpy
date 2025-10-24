#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""计算一年的期货数据量"""

print("=" * 70)
print("期货品种 - 一年1分钟数据量计算")
print("=" * 70)

# 基础参数
trading_days_per_year = 240  # 一年约240个交易日

print("\n【一年数据量 = 每天条数 × 年交易日数】\n")

# 不同品种的每天数据条数
futures_types = [
    ("螺纹钢/热卷/铁矿/焦炭/焦煤", 345, "21:00-23:00"),
    ("铜/铝/锌/铅/锡/镍", 465, "21:00-01:00"),
    ("黄金/白银", 555, "21:00-02:30"),
    ("原油", 555, "21:00-02:30"),
    ("橡胶/沥青/纸浆", 345, "21:00-23:00"),
    ("豆类/玉米/棕榈油", 345, "21:00-23:00"),
    ("棉花/白糖/PTA", 345, "21:00-23:00"),
    ("股指期货(IF/IH/IC/IM)", 225, "无夜盘"),
]

for name, bars_per_day, night_session in futures_types:
    yearly_total = bars_per_day * trading_days_per_year
    print(f"{name:30s} | 每天:{bars_per_day:3d}条 | 一年:{yearly_total:7,}条 | 夜盘:{night_session}")

print("\n" + "=" * 70)
print("关键结论：")
print("=" * 70)
print(f"✅ 黑色系品种(螺纹钢等): 一年约 82,800 条")
print(f"✅ 有色金属(铜铝锌等): 一年约 111,600 条")
print(f"✅ 贵金属/能源(金银原油): 一年约 133,200 条")
print(f"✅ 股指期货: 一年约 54,000 条")

print("\n" + "=" * 70)
print("实际应用：")
print("=" * 70)

scenarios = [
    ("回测1个品种1年(螺纹钢)", 82800, 1),
    ("回测5个品种1年(黑色系)", 82800, 5),
    ("回测10个品种1年(全市场)", 100000, 10),  # 平均值
    ("回测1个品种3年(长期策略)", 82800, 3),
]

for scenario, bars_per_year, multiplier in scenarios:
    total = bars_per_year * multiplier
    size_mb = (total * 100) / 1024 / 1024  # 假设每条数据约100字节
    print(f"{scenario:30s} : {total:8,} 条 ≈ {size_mb:.1f} MB")

print("\n" + "=" * 70)
print("你当前的数据情况：")
print("=" * 70)
print(f"已下载: 5个品种 × 6个月 = 222,450 条")
print(f"如果下载满1年: 5个品种 × 1年 ≈ 414,000 条")
print(f"存储空间估算: ≈ 40 MB (数据库压缩后)")
print("=" * 70)

