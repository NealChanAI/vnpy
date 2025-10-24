"""
快速清理数据库 - 直接执行SQL
"""

import sqlite3
from pathlib import Path


def get_database_path():
    home_path = Path.home()
    db_path = home_path.joinpath(".vntrader", "database.db")
    if not db_path.exists():
        db_path = Path("database.db")
    return str(db_path)


# 连接数据库
db_path = get_database_path()
print(f"数据库路径: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看所有表
print("\n当前的表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# === 选择以下其中一种操作 ===

# 1. 删除所有表（完全清空数据库）
print("\n正在删除所有表...")
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
    print(f"  ✅ 已删除: {table[0]}")
conn.commit()

# 2. 只清空数据，保留表结构（注释掉上面的代码，使用这个）
# print("\n正在清空所有数据...")
# for table in tables:
#     cursor.execute(f"DELETE FROM {table[0]};")
#     print(f"  ✅ 已清空: {table[0]}")
# conn.commit()

# 3. 只删除K线数据表（注释掉上面的代码，使用这个）
# print("\n正在删除K线数据表...")
# cursor.execute("DROP TABLE IF EXISTS dbbardata;")
# conn.commit()
# print("  ✅ 已删除 dbbardata 表")

# 4. 只清空K线数据（注释掉上面的代码，使用这个）
# print("\n正在清空K线数据...")
# cursor.execute("DELETE FROM dbbardata;")
# conn.commit()
# print("  ✅ 已清空 dbbardata 表的数据")

conn.close()
print("\n✅ 操作完成！")

