#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""计算聚宽试用账号每天可下载的数据量"""

print("=" * 70)
print("聚宽试用账号 - 每日下载限制分析")
print("=" * 70)

# 实际测试数据
total_calls = 1_000_000  # 总调用次数
calls_before = 993_424   # 下载前剩余
calls_after = 770_974    # 下载后剩余
varieties_downloaded = 5  # 下载的品种数
months_downloaded = 6     # 下载的月份数

# 计算消耗
used_calls = calls_before - calls_after
calls_per_variety = used_calls / varieties_downloaded
calls_per_month = used_calls / (varieties_downloaded * months_downloaded)

print("\n【实际下载统计】")
print(f"下载前剩余: {calls_before:,} 次")
print(f"下载后剩余: {calls_after:,} 次")
print(f"本次消耗: {used_calls:,} 次")
print(f"下载品种: {varieties_downloaded} 个品种 × {months_downloaded} 个月")
print(f"每个品种消耗: {calls_per_variety:,.0f} 次 (6个月数据)")
print(f"每个品种每月: {calls_per_month:,.0f} 次")

print("\n" + "=" * 70)
print("【基于100万次调用额度计算】")
print("=" * 70)

scenarios = [
    (1, "1个月", 1),
    (3, "3个月", 3),
    (6, "6个月", 6),
    (12, "1年", 12),
]

print("\n如果下载不同时长的数据:")
for i, (months, desc, factor) in enumerate(scenarios, 1):
    calls_per_variety_time = calls_per_month * months
    max_varieties = total_calls / calls_per_variety_time
    total_bars = max_varieties * 345 * 20 * months  # 345条/天 * 20天/月
    
    print(f"\n{i}. {desc}数据:")
    print(f"   每品种消耗: {calls_per_variety_time:,.0f} 次")
    print(f"   可下载品种: {max_varieties:.0f} 个")
    print(f"   总数据量: {total_bars:,.0f} 条")

print("\n" + "=" * 70)
print("【推荐方案】")
print("=" * 70)

# 计算不同策略的推荐方案
print("\n根据你的策略类型选择下载方案:\n")

strategies = [
    ("日内高频策略", 1, "下载更多品种，时间短一些"),
    ("日内波段策略", 3, "平衡品种数量和时间长度"),
    ("短期趋势策略", 6, "当前方案刚好合适"),
    ("中长期策略", 12, "减少品种数，获取更长历史"),
]

for strategy, months, suggestion in strategies:
    max_varieties = total_calls / (calls_per_month * months)
    print(f"✓ {strategy:12s} ({months:2d}个月) : 最多 {max_varieties:3.0f} 个品种 - {suggestion}")

print("\n" + "=" * 70)
print("【实际建议】")
print("=" * 70)

# 黑色系组合
print("\n推荐下载组合（示例）:\n")

combinations = [
    ("黑色系全覆盖", ["RB", "HC", "I", "J", "JM"], "6个月", 5),
    ("有色金属", ["CU", "AL", "ZN", "PB", "NI"], "6个月", 5),
    ("化工能源", ["RU", "BU", "SC", "TA", "MA"], "6个月", 5),
    ("农产品", ["A", "M", "Y", "C", "CF"], "6个月", 5),
    ("多品种轮换", ["RB", "CU", "I", "AU", "M", "C", "SC", "TA", "A", "SR"], "3个月", 10),
    ("单品种深度", ["RB"], "1年", 1),
]

for name, symbols, period, count in combinations:
    calls_needed = calls_per_variety if "6个月" in period else (
        calls_per_variety * 2 if "1年" in period else calls_per_variety / 2
    )
    total_calls_needed = calls_needed * count
    can_download = "✅" if total_calls_needed <= total_calls else "❌"
    
    print(f"{can_download} {name:15s} : {count:2d}个品种 × {period} ≈ {total_calls_needed/10000:.0f}万次调用")

print("\n" + "=" * 70)
print("结论：")
print("=" * 70)
print("✅ 一天100万次调用完全够用！")
print("✅ 可以下载 20+ 个品种的6个月数据")
print("✅ 或下载 5-10 个品种的1年数据")
print("✅ 建议：先下载核心品种，测试策略后再扩展")
print("=" * 70)

