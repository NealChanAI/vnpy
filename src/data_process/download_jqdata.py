#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聚宽JQData - 期货分钟数据下载到VeighNa数据库
试用账号时间限制：2024-07-16 至 2025-07-23（当前时间的三个月前）
每天下载量限制：100万条
"""

from datetime import datetime, timedelta
import os
from jqdatasdk import *
import pandas as pd
from tqdm import tqdm

from vnpy.trader.object import BarData, Interval, Exchange
from vnpy.trader.database import get_database
from vnpy.trader.constant import Exchange as VnExchange

# ==================== 配置区 ====================

# 1. JQData账号（从环境变量获取）
JQDATA_USERNAME = os.getenv("JQDATA_USERNAME")
JQDATA_PASSWORD = os.getenv("JQDATA_PASSWORD")

if not JQDATA_USERNAME or not JQDATA_PASSWORD:
    raise ValueError(
        "未找到聚宽账号环境变量！\n"
        "请先设置环境变量：\n"
    )

# 2. 要下载的期货品种（聚宽代码）
FUTURES_SYMBOLS = [
    'RB2505.XSGE',   # 螺纹钢2505
    'HC2505.XSGE',   # 热卷2505
    'I2505.XDCE',    # 铁矿石2505
    'J2505.XDCE',    # 焦炭2505
    'JM2505.XDCE',   # 焦煤2505
    # 可以继续添加...
]

# 3. 下载时间范围（试用账号限制：2024-07-16 至 2025-07-23）
START_DATE = '2024-07-16'  # 试用账号最早日期
END_DATE = '2025-01-24'     # 当前日期，不超过2025-07-23

# 4. 数据粒度
FREQUENCY = '1m'  # 1分钟，可选：1m, 5m, 15m, 30m, 60m, 1d

# ==================== 交易所映射 ====================

EXCHANGE_MAP = {
    'XSGE': Exchange.SHFE,   # 上期所
    'XDCE': Exchange.DCE,    # 大商所
    'XZCE': Exchange.CZCE,   # 郑商所
    'CCFX': Exchange.CFFEX,  # 中金所
    'XINE': Exchange.INE,    # 能源中心
}

# ==================== 核心函数 ====================

def jq_to_vn_symbol(jq_symbol):
    """
    将聚宽合约代码转换为VeighNa格式
    
    例如：RB2505.XSGE -> (rb2505, Exchange.SHFE)
    """
    symbol, exchange_str = jq_symbol.split('.')
    
    # 聚宽代码是大写，VeighNa通常用小写
    vn_symbol = symbol.lower()
    
    # 转换交易所
    vn_exchange = EXCHANGE_MAP.get(exchange_str)
    if not vn_exchange:
        raise ValueError(f"未知的交易所: {exchange_str}")
    
    return vn_symbol, vn_exchange


def download_jqdata_bars(jq_symbol, start_date, end_date, frequency='1m'):
    """
    从聚宽下载K线数据
    
    返回：pandas DataFrame
    """
    print(f"  正在下载 {jq_symbol} 从 {start_date} 到 {end_date}...")
    
    try:
        df = get_price(
            jq_symbol,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            fields=['open', 'high', 'low', 'close', 'volume', 'money'],
            skip_paused=False,
            fq='none'  # 期货不需要复权
        )
        
        if df is not None and not df.empty:
            print(f"  ✅ 成功下载 {len(df)} 条数据")
            return df
        else:
            print(f"  ⚠️ 没有数据")
            return None
            
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return None


def convert_to_vn_bars(df, jq_symbol, frequency='1m'):
    """
    将聚宽DataFrame转换为VeighNa的BarData对象列表
    """
    if df is None or df.empty:
        return []
    
    # 解析合约代码
    vn_symbol, vn_exchange = jq_to_vn_symbol(jq_symbol)
    
    # 确定时间周期
    interval_map = {
        '1m': Interval.MINUTE,
        '5m': Interval.MINUTE,
        '15m': Interval.MINUTE,
        '30m': Interval.MINUTE,
        '60m': Interval.HOUR,
        '1d': Interval.DAILY,
    }
    interval = interval_map.get(frequency, Interval.MINUTE)
    
    # 转换数据
    bar_list = []
    for timestamp, row in df.iterrows():
        bar = BarData(
            symbol=vn_symbol,
            exchange=vn_exchange,
            datetime=timestamp.to_pydatetime(),
            interval=interval,
            volume=float(row['volume']),
            turnover=float(row['money']),
            open_price=float(row['open']),
            high_price=float(row['high']),
            low_price=float(row['low']),
            close_price=float(row['close']),
            gateway_name="JQDATA"
        )
        bar_list.append(bar)
    
    return bar_list


def save_to_database(bar_list):
    """
    保存数据到VeighNa数据库
    """
    if not bar_list:
        return 0
    
    database = get_database()
    result = database.save_bar_data(bar_list)
    return len(bar_list)


# ==================== 主程序 ====================

def main():
    """主下载流程"""
    
    print("=" * 60)
    print("聚宽JQData - 期货分钟数据下载")
    print("=" * 60)
    
    # 1. 登录认证
    print("\n【步骤1】登录聚宽...")
    try:
        auth(JQDATA_USERNAME, JQDATA_PASSWORD)
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return
    
    # 2. 查询配额
    count = get_query_count()
    print(f"📊 今日剩余调用次数: {count}")
    
    if count['spare'] < len(FUTURES_SYMBOLS) * 2:
        print("⚠️ 警告：剩余调用次数可能不足！")
    
    # 3. 获取数据库实例
    print("\n【步骤2】连接数据库...")
    try:
        database = get_database()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 4. 逐个下载合约数据
    print(f"\n【步骤3】开始下载数据...")
    print(f"时间范围: {START_DATE} 至 {END_DATE}")
    print(f"数据粒度: {FREQUENCY}")
    print(f"合约数量: {len(FUTURES_SYMBOLS)}")
    print("=" * 60)
    
    total_bars = 0
    success_count = 0
    
    for i, jq_symbol in enumerate(FUTURES_SYMBOLS, 1):
        print(f"\n[{i}/{len(FUTURES_SYMBOLS)}] {jq_symbol}")
        
        try:
            # 下载数据
            df = download_jqdata_bars(jq_symbol, START_DATE, END_DATE, FREQUENCY)
            
            if df is None or df.empty:
                continue
            
            # 转换格式
            bar_list = convert_to_vn_bars(df, jq_symbol, FREQUENCY)
            
            # 保存到数据库
            saved_count = save_to_database(bar_list)
            print(f"  💾 已保存到数据库: {saved_count} 条")
            
            total_bars += saved_count
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            continue
    
    # 5. 统计信息
    print("\n" + "=" * 60)
    print("下载完成！")
    print("=" * 60)
    print(f"成功: {success_count}/{len(FUTURES_SYMBOLS)}")
    print(f"总数据量: {total_bars} 条")
    
    # 6. 查询剩余配额
    count_after = get_query_count()
    print(f"剩余调用次数: {count_after['spare']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

