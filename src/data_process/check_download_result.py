"""
检查下载结果 - 对比预期品种和实际数据库中的品种
"""

import sqlite3
from pathlib import Path

# 预期下载的品种列表
FUTURES_SYMBOLS = [
    # SHFE
    'rb2505.SHFE', 'hc2505.SHFE', 'ss2505.SHFE', 'wr2505.SHFE',
    'cu2505.SHFE', 'al2505.SHFE', 'zn2505.SHFE', 'pb2505.SHFE', 'ni2505.SHFE', 'sn2505.SHFE',
    'au2506.SHFE', 'ag2506.SHFE',
    'fu2505.SHFE', 'bu2506.SHFE', 'ru2505.SHFE', 'sp2505.SHFE',
    # DCE
    'i2505.DCE', 'j2505.DCE', 'jm2505.DCE',
    'a2505.DCE', 'b2505.DCE', 'm2505.DCE', 'y2505.DCE', 'p2505.DCE', 'c2505.DCE', 'cs2505.DCE', 'jd2505.DCE', 'lh2505.DCE',
    'l2505.DCE', 'v2505.DCE', 'pp2505.DCE', 'eg2505.DCE', 'eb2505.DCE', 'pg2505.DCE',
    'fb2505.DCE', 'bb2501.DCE',
    # CZCE
    'SR505.CZCE', 'CF505.CZCE', 'CY505.CZCE', 'AP505.CZCE', 'CJ505.CZCE', 'PK505.CZCE', 'RM505.CZCE', 'OI505.CZCE',
    'TA505.CZCE', 'MA505.CZCE', 'FG505.CZCE', 'SA505.CZCE', 'UR505.CZCE', 'PF505.CZCE',
    # 'ZC501.CZCE',  # 动力煤 - 已移除（无可用数据）
    'SF505.CZCE', 'SM505.CZCE',
    # INE
    'sc2505.INE', 'nr2505.INE', 'lu2505.INE', 'bc2505.INE',
    # CFFEX
    'IF2501.CFFEX', 'IH2501.CFFEX', 'IC2501.CFFEX', 'IM2501.CFFEX',
    'T2503.CFFEX', 'TF2503.CFFEX', 'TS2503.CFFEX',
]


def get_database_path():
    """获取数据库文件路径"""
    home_path = Path.home()
    db_path = home_path.joinpath(".vntrader", "database.db")
    if not db_path.exists():
        db_path = Path("database.db")
    return str(db_path)


def check_download_result():
    """检查下载结果"""
    print("=" * 80)
    print("下载结果检查")
    print("=" * 80)
    
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询数据库中的所有品种（包含开始和结束日期）
    sql = """
    SELECT 
        symbol, 
        exchange, 
        COUNT(*) as count,
        MIN(datetime) as start_date,
        MAX(datetime) as end_date
    FROM dbbardata
    GROUP BY symbol, exchange
    ORDER BY exchange, symbol
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    # 构建数据库中的品种集合
    db_symbols = set()
    db_details = {}
    for row in results:
        symbol, exchange, count, start_date, end_date = row
        vt_symbol = f"{symbol}.{exchange}"
        db_symbols.add(vt_symbol)
        db_details[vt_symbol] = {
            'count': count,
            'start': start_date,
            'end': end_date
        }
    
    # 构建预期品种集合
    expected_symbols = set(FUTURES_SYMBOLS)
    
    # 找出成功和失败的品种
    success_symbols = expected_symbols & db_symbols
    failed_symbols = expected_symbols - db_symbols
    extra_symbols = db_symbols - expected_symbols
    
    # 显示结果
    print(f"\n📊 统计:")
    print(f"  预期下载: {len(expected_symbols)} 个品种")
    print(f"  实际成功: {len(success_symbols)} 个品种")
    print(f"  下载失败: {len(failed_symbols)} 个品种")
    if extra_symbols:
        print(f"  额外品种: {len(extra_symbols)} 个品种（数据库中有但不在列表中）")
    
    # 显示失败的品种
    if failed_symbols:
        print("\n" + "=" * 80)
        print("❌ 下载失败的品种:")
        print("=" * 80)
        
        # 按交易所分组
        shfe_failed = sorted([s for s in failed_symbols if 'SHFE' in s])
        dce_failed = sorted([s for s in failed_symbols if 'DCE' in s])
        czce_failed = sorted([s for s in failed_symbols if 'CZCE' in s])
        ine_failed = sorted([s for s in failed_symbols if 'INE' in s])
        cffex_failed = sorted([s for s in failed_symbols if 'CFFEX' in s])
        
        if shfe_failed:
            print(f"\n【上海期货交易所 SHFE】({len(shfe_failed)}个)")
            for symbol in shfe_failed:
                print(f"  ❌ {symbol}")
        
        if dce_failed:
            print(f"\n【大连商品交易所 DCE】({len(dce_failed)}个)")
            for symbol in dce_failed:
                print(f"  ❌ {symbol}")
        
        if czce_failed:
            print(f"\n【郑州商品交易所 CZCE】({len(czce_failed)}个)")
            for symbol in czce_failed:
                print(f"  ❌ {symbol}")
        
        if ine_failed:
            print(f"\n【上海能源中心 INE】({len(ine_failed)}个)")
            for symbol in ine_failed:
                print(f"  ❌ {symbol}")
        
        if cffex_failed:
            print(f"\n【中金所 CFFEX】({len(cffex_failed)}个)")
            for symbol in cffex_failed:
                print(f"  ❌ {symbol}")
    else:
        print("\n✅ 所有品种都下载成功！")
    
    # 显示成功品种的数据量和日期范围
    print("\n" + "=" * 80)
    print("✅ 成功下载的品种（数据量与时间范围）:")
    print("=" * 80)
    
    # 按交易所分组显示
    exchanges = {
        'SHFE': '上海期货交易所',
        'DCE': '大连商品交易所',
        'CZCE': '郑州商品交易所',
        'INE': '上海能源中心',
        'CFFEX': '中金所'
    }
    
    for exchange_code, exchange_name in exchanges.items():
        exchange_symbols = sorted([s for s in success_symbols if exchange_code in s])
        if exchange_symbols:
            print(f"\n【{exchange_name} {exchange_code}】({len(exchange_symbols)}个)")
            print(f"{'品种':<20} {'数据量':>10}    {'开始日期':<20}  {'结束日期':<20}")
            print("-" * 80)
            for symbol in exchange_symbols:
                details = db_details.get(symbol, {})
                count = details.get('count', 0)
                start = details.get('start', 'N/A')
                end = details.get('end', 'N/A')
                print(f"  {symbol:<18} {count:>10,} 条  {start:<20}  {end:<20}")
    
    # 总数据量
    total_bars = sum(d['count'] for d in db_details.values())
    print("\n" + "=" * 80)
    print(f"总数据量: {total_bars:,} 条K线")
    print("=" * 80)
    
    # 如果有额外品种，显示出来
    if extra_symbols:
        print("\n" + "=" * 80)
        print("ℹ️  数据库中的额外品种（不在下载列表中）:")
        print("=" * 80)
        print(f"{'品种':<20} {'数据量':>10}    {'开始日期':<20}  {'结束日期':<20}")
        print("-" * 80)
        for symbol in sorted(extra_symbols):
            details = db_details.get(symbol, {})
            count = details.get('count', 0)
            start = details.get('start', 'N/A')
            end = details.get('end', 'N/A')
            print(f"  {symbol:<18} {count:>10,} 条  {start:<20}  {end:<20}")
    
    conn.close()


if __name__ == "__main__":
    check_download_result()

