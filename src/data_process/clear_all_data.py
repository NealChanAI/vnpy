"""
清空数据库中的所有期货数据
"""

import sqlite3
from pathlib import Path


def get_database_path():
    """获取数据库文件路径"""
    home_path = Path.home()
    db_path = home_path.joinpath(".vntrader", "database.db")
    if not db_path.exists():
        db_path = Path("database.db")
    return str(db_path)


def clear_all_data():
    """清空所有表数据"""
    db_path = get_database_path()
    
    print("\n" + "=" * 80)
    print("清空VeighNa数据库")
    print("=" * 80)
    print(f"\n数据库路径: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取当前数据统计
    tables = ['dbbardata', 'dbbaroverview', 'dbtickdata', 'dbtickoverview']
    
    print("\n当前数据统计:")
    print("-" * 80)
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:20s}: {count:>10,} 条记录")
        except:
            print(f"  {table:20s}: 表不存在")
    
    print("\n⚠️  警告: 即将删除所有数据！")
    confirm = input("\n确认清空所有表吗？(输入 yes 确认): ")
    
    if confirm.lower() != 'yes':
        print("\n❌ 操作已取消")
        conn.close()
        return
    
    # 清空所有表
    print("\n正在清空数据...")
    print("-" * 80)
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"✅ {table:20s} 已清空")
        except Exception as e:
            print(f"⚠️  {table:20s} 清空失败: {e}")
    
    conn.commit()
    
    # 验证清空结果
    print("\n清空后数据统计:")
    print("-" * 80)
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:20s}: {count:>10,} 条记录")
        except:
            pass
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ 数据库清空完成！")
    print("=" * 80)


if __name__ == "__main__":
    clear_all_data()

