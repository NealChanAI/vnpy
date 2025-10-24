"""
使用SQL直接查询天勤TQData数据库中的数据
"""

import sqlite3
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta


def get_database_path():
    """获取数据库文件路径"""
    # VeighNa的数据库默认在用户目录下的.vntrader文件夹
    home_path = Path.home()
    db_path = home_path.joinpath(".vntrader", "database.db")
    
    if not db_path.exists():
        # 尝试当前工作目录
        db_path = Path("database.db")
        if not db_path.exists():
            raise FileNotFoundError(
                f"找不到数据库文件!\n"
                f"尝试的路径: {home_path.joinpath('.vntrader', 'database.db')}\n"
                f"请确认数据库文件位置"
            )
    
    return str(db_path)


def check_database_tables(cursor):
    """查看数据库中的表结构"""
    print("=" * 80)
    print("数据库表结构")
    print("=" * 80)
    
    # 查询所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n数据库中的表: {[t[0] for t in tables]}\n")
    
    # 查看每个表的结构
    for table in tables:
        table_name = table[0]
        print(f"\n表名: {table_name}")
        print("-" * 80)
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]:20s} {col[2]:15s} {'NOT NULL' if col[3] else ''}")


def query_bar_overview_sql(db_path):
    """使用SQL查询K线数据概览"""
    print("\n" + "=" * 80)
    print("K线数据概览 (SQL查询)")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL查询：按合约、交易所、周期分组统计
    sql = """
    SELECT 
        symbol,
        exchange,
        interval,
        COUNT(*) as count,
        MIN(datetime) as start_time,
        MAX(datetime) as end_time
    FROM dbbardata
    GROUP BY symbol, exchange, interval
    ORDER BY symbol, exchange, interval
    """
    
    cursor.execute(sql)
    results = cursor.fetchall()
    
    if not results:
        print("⚠️ 数据库中没有K线数据")
        conn.close()
        return
    
    # 格式化显示
    data_list = []
    for row in results:
        data_list.append({
            '合约代码': f"{row[0]}.{row[1]}",
            '交易所': row[1],
            '周期': row[2],
            '数据量': f"{row[3]:,}",
            '开始时间': row[4],
            '结束时间': row[5]
        })
    
    df = pd.DataFrame(data_list)
    print("\n" + df.to_string(index=False))
    
    # 统计总计
    total_count = sum(row[3] for row in results)
    print("\n" + "=" * 80)
    print(f"总计: {len(results)} 个合约")
    print(f"总数据量: {total_count:,} 条")
    print("=" * 80)
    
    conn.close()


def query_specific_symbol_sql(db_path, symbol, exchange, days=5):
    """使用SQL查询特定合约的数据"""
    print("\n" + "=" * 80)
    print(f"查询合约: {symbol}.{exchange} (最近{days}天)")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # SQL查询
    sql = """
    SELECT 
        datetime,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        turnover,
        open_interest
    FROM dbbardata
    WHERE symbol = ? 
      AND exchange = ?
      AND interval = '1m'
      AND datetime >= ?
    ORDER BY datetime ASC
    """
    
    cursor.execute(sql, (symbol, exchange, start_time.strftime('%Y-%m-%d %H:%M:%S')))
    results = cursor.fetchall()
    
    if not results:
        print(f"⚠️ 没有找到 {symbol}.{exchange} 的数据")
        conn.close()
        return
    
    print(f"\n✅ 找到 {len(results)} 条数据")
    print("-" * 80)
    
    # 显示前10条数据
    print("\n【前10条数据】")
    for i, row in enumerate(results[:10], 1):
        print(f"{i:2d}. {row[0]} | "
              f"开:{row[1]:8.2f} "
              f"高:{row[2]:8.2f} "
              f"低:{row[3]:8.2f} "
              f"收:{row[4]:8.2f} "
              f"量:{row[5]:8.0f}")
    
    if len(results) > 20:
        print("\n... (中间省略) ...\n")
        
        # 显示最后10条数据
        print("【最后10条数据】")
        for i, row in enumerate(results[-10:], len(results)-9):
            print(f"{i:2d}. {row[0]} | "
                  f"开:{row[1]:8.2f} "
                  f"高:{row[2]:8.2f} "
                  f"低:{row[3]:8.2f} "
                  f"收:{row[4]:8.2f} "
                  f"量:{row[5]:8.0f}")
    elif len(results) > 10:
        print("\n【后10条数据】")
        for i, row in enumerate(results[10:], 11):
            print(f"{i:2d}. {row[0]} | "
                  f"开:{row[1]:8.2f} "
                  f"高:{row[2]:8.2f} "
                  f"低:{row[3]:8.2f} "
                  f"收:{row[4]:8.2f} "
                  f"量:{row[5]:8.0f}")
    
    # 统计信息
    print("\n" + "-" * 80)
    print(f"【数据统计】")
    print(f"时间范围: {results[0][0]} 至 {results[-1][0]}")
    print(f"总数据量: {len(results):,} 条")
    print(f"最高价: {max(row[2] for row in results):.2f}")
    print(f"最低价: {min(row[3] for row in results):.2f}")
    print(f"总成交量: {sum(row[5] for row in results):,.0f}")
    
    conn.close()


def query_custom_sql(db_path, sql_query):
    """执行自定义SQL查询"""
    print("\n" + "=" * 80)
    print("自定义SQL查询")
    print("=" * 80)
    print(f"SQL: {sql_query}\n")
    
    conn = sqlite3.connect(db_path)
    
    try:
        df = pd.read_sql_query(sql_query, conn)
        print(df.to_string(index=False))
        print(f"\n返回 {len(df)} 行数据")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()


def export_to_csv(db_path, symbol, exchange, output_file="output.csv"):
    """导出数据到CSV文件"""
    print("\n" + "=" * 80)
    print(f"导出数据: {symbol}.{exchange}")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    
    sql = """
    SELECT 
        datetime,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        turnover,
        open_interest
    FROM dbbardata
    WHERE symbol = ? 
      AND exchange = ?
      AND interval = '1m'
    ORDER BY datetime ASC
    """
    
    try:
        df = pd.read_sql_query(sql, conn, params=(symbol, exchange))
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 成功导出 {len(df)} 条数据到 {output_file}")
    except Exception as e:
        print(f"❌ 导出失败: {e}")
    finally:
        conn.close()


def main():
    """主函数"""
    try:
        # 获取数据库路径
        db_path = get_database_path()
        print(f"数据库路径: {db_path}\n")
        
        # 1. 查看数据库表结构（可选，首次使用时打开）
        conn = sqlite3.connect(db_path)
        check_database_tables(conn.cursor())
        conn.close()
        
        # 2. 查询K线数据概览
        # query_bar_overview_sql(db_path)
        
        # 3. 查询特定合约
        # query_specific_symbol_sql(db_path, 'rb2505', 'SHFE', days=30)
        
        # 4. 自定义SQL查询示例
        # 查询rb2505在2024年的每日最高价和最低价
        custom_sql = """
        SELECT 
            DATE(datetime) as date,
            MAX(high_price) as day_high,
            MIN(low_price) as day_low,
            COUNT(*) as bar_count
        FROM dbbardata
        WHERE symbol = 'rb2505'
          AND exchange = 'SHFE'
          AND datetime >= '2024-01-01'
        GROUP BY DATE(datetime)
        ORDER BY date DESC
        LIMIT 10
        """
        # query_custom_sql(db_path, custom_sql)
        
        # 5. 导出数据到CSV（按需使用）
        # export_to_csv(db_path, 'rb2505', 'SHFE', 'rb2505_data.csv')
        
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()

