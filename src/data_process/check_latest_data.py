"""
检查数据库中实际最新的交易数据日期
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def get_database_path():
    """获取数据库文件路径"""
    home_path = Path.home()
    db_path = home_path.joinpath(".vntrader", "database.db")
    if not db_path.exists():
        db_path = Path("database.db")
    return str(db_path)


def check_latest_data():
    """检查最新数据日期"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询数据库中所有数据的最新日期
    sql = """
    SELECT 
        MAX(datetime) as latest_date,
        MIN(datetime) as earliest_date
    FROM dbbardata
    """
    
    cursor.execute(sql)
    result = cursor.fetchone()
    
    if result:
        latest_date = result[0]
        earliest_date = result[1]
        
        print("=" * 80)
        print("数据库时间范围统计")
        print("=" * 80)
        print(f"\n最早数据时间: {earliest_date}")
        print(f"最新数据时间: {latest_date}")
        
        # 解析日期
        if latest_date:
            latest_dt = datetime.strptime(latest_date, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            days_ago = (now - latest_dt).days
            
            print(f"\n当前系统时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"数据延迟天数: {days_ago} 天")
            
            if days_ago > 30:
                print(f"\n⚠️  警告：数据已经延迟 {days_ago} 天，建议更新数据！")
            elif days_ago > 7:
                print(f"\n⚠️  提示：数据延迟 {days_ago} 天，可以考虑更新。")
            else:
                print(f"\n✅  数据较新，延迟在 {days_ago} 天以内。")
        
        print("=" * 80)
    
    # 查询每个品种的最新数据日期（显示前10个最旧的）
    sql_by_symbol = """
    SELECT 
        symbol,
        exchange,
        MAX(datetime) as latest_date,
        COUNT(*) as count
    FROM dbbardata
    GROUP BY symbol, exchange
    ORDER BY latest_date ASC
    LIMIT 10
    """
    
    cursor.execute(sql_by_symbol)
    results = cursor.fetchall()
    
    print("\n数据最旧的10个品种（按最新日期排序）:")
    print("-" * 80)
    for i, (symbol, exchange, latest, count) in enumerate(results, 1):
        vt_symbol = f"{symbol}.{exchange}"
        print(f"{i:2d}. {vt_symbol:20s} 最新数据: {latest}  (共{count:,}条)")
    
    print("\n" + "=" * 80)
    
    conn.close()


if __name__ == "__main__":
    check_latest_data()

