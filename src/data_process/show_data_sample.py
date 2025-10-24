#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查看期货数据样本并解释字段含义"""

from datetime import datetime
from vnpy.trader.database import get_database
from vnpy.trader.constant import Exchange, Interval

# 获取数据库
database = get_database()

# 查询螺纹钢数据
bars = database.load_bar_data(
    symbol='rb2505',
    exchange=Exchange.SHFE,
    interval=Interval.MINUTE,
    start=datetime(2024, 12, 1),
    end=datetime(2024, 12, 31)
)

print("=" * 80)
print("期货1分钟数据样本 - 螺纹钢 RB2505")
print("=" * 80)

if bars:
    print(f"\n总数据量: {len(bars)} 条\n")
    print("前10条数据展示:\n")
    
    # 表头
    print(f"{'序号':<4} {'时间':<20} {'开盘':<8} {'最高':<8} {'最低':<8} "
          f"{'收盘':<8} {'成交量':<10} {'成交额':<12}")
    print("-" * 80)
    
    # 展示前10条数据
    for i, bar in enumerate(bars[:10], 1):
        print(f"{i:<4} {str(bar.datetime):<20} {bar.open_price:<8.1f} "
              f"{bar.high_price:<8.1f} {bar.low_price:<8.1f} {bar.close_price:<8.1f} "
              f"{bar.volume:<10.0f} {bar.turnover:<12.0f}")
    
    print("\n" + "=" * 80)
    print("字段详细说明")
    print("=" * 80)
    
    # 取第一条数据做详细说明
    bar = bars[0]
    
    print(f"""
┌─ 基础信息 ─────────────────────────────────────────────────
│
│ symbol         : {bar.symbol}
│ 说明           : 合约代码（小写）
│ 示例           : rb2505 表示螺纹钢2025年5月合约
│
│ exchange       : {bar.exchange.value}
│ 说明           : 交易所代码
│ 可选值         : SHFE(上期所), DCE(大商所), CZCE(郑商所), 
│                 CFFEX(中金所), INE(能源中心)
│
│ datetime       : {bar.datetime}
│ 说明           : K线时间戳（该分钟的开始时间）
│ 格式           : YYYY-MM-DD HH:MM:SS+时区
│ 注意           : 这是K线柱的开始时间，收盘时间为下一分钟
│
│ interval       : {bar.interval.value}
│ 说明           : 数据周期
│ 可选值         : 1m(1分钟), 1h(1小时), d(日线), w(周线)
│
│ gateway_name   : {bar.gateway_name}
│ 说明           : 数据来源标识
│ 示例           : JQDATA表示来自聚宽数据
│
└────────────────────────────────────────────────────────────

┌─ 价格信息（OHLC）──────────────────────────────────────────
│
│ open_price     : {bar.open_price}
│ 说明           : 开盘价 - 该分钟第一笔成交价格
│ 单位           : 元/吨（螺纹钢）
│
│ high_price     : {bar.high_price}
│ 说明           : 最高价 - 该分钟内的最高成交价
│ 用途           : 用于计算ATR、布林带等指标
│
│ low_price      : {bar.low_price}
│ 说明           : 最低价 - 该分钟内的最低成交价
│ 用途           : 用于支撑阻力位分析
│
│ close_price    : {bar.close_price}
│ 说明           : 收盘价 - 该分钟最后一笔成交价格
│ 重要性         : ⭐⭐⭐⭐⭐ 最常用于技术指标计算
│
└────────────────────────────────────────────────────────────

┌─ 成交信息 ─────────────────────────────────────────────────
│
│ volume         : {bar.volume}
│ 说明           : 成交量 - 该分钟的成交手数
│ 单位           : 手（1手 = 10吨，对于螺纹钢）
│ 用途           : 判断市场活跃度、验证价格突破
│ 注意           : 夜盘和开盘初期成交量通常较小
│
│ turnover       : {bar.turnover}
│ 说明           : 成交额 - 该分钟的成交金额
│ 单位           : 元
│ 计算公式       : 约等于 成交价格 × 成交量 × 合约乘数
│ 用途           : 资金流向分析
│
│ open_interest  : {bar.open_interest}
│ 说明           : 持仓量 - 该时刻的未平仓合约数
│ 单位           : 手
│ 重要性         : ⭐⭐⭐ 反映市场参与度
│ 特点           : 持仓量增加 = 新资金入场
│               持仓量减少 = 资金离场
│
└────────────────────────────────────────────────────────────
    """)
    
    print("=" * 80)
    print("重要概念解释")
    print("=" * 80)
    
    print("""
1. 📊 OHLC（Open High Low Close）
   - 技术分析的基础，几乎所有指标都基于这四个价格
   - K线图就是由OHLC绘制而成
   
2. 🔢 成交量 vs 持仓量
   - 成交量：交易活跃度，当天买卖的手数
   - 持仓量：市场深度，未平仓的合约总数
   - 成交量大、持仓量增 → 强势行情
   - 成交量大、持仓量减 → 反转信号
   
3. ⏰ 时间戳注意事项
   - datetime是K线开始时间
   - 例如：09:30:00的K线，包含09:30:00到09:30:59的数据
   - 收盘价是09:30:59的最后成交价
   
4. 🔄 数据更新频率
   - 1分钟K线：每分钟更新一次
   - 实盘时：实时推送
   - 回测时：逐根K线回放
   
5. 💰 价格单位
   - 螺纹钢：元/吨
   - 黄金：元/克
   - 原油：元/桶
   - 不同品种单位不同，需要注意
    """)
    
    print("=" * 80)
    print("实际应用示例")
    print("=" * 80)
    
    print("""
# 1. 计算涨跌幅
change_pct = (close_price - open_price) / open_price * 100

# 2. 判断K线类型
if close_price > open_price:
    print("阳线 - 上涨")
elif close_price < open_price:
    print("阴线 - 下跌")
else:
    print("十字星 - 震荡")

# 3. 计算振幅
amplitude = (high_price - low_price) / open_price * 100

# 4. 判断成交活跃度
if volume > avg_volume * 2:
    print("放量突破")
    """)
    
    print("\n" + "=" * 80)

else:
    print("❌ 没有找到数据")

