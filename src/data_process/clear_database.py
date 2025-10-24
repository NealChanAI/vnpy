"""
清理天勤数据库 - 删除表或清空数据
⚠️ 危险操作，请谨慎使用！
"""

import sqlite3
from pathlib import Path
import os


def get_database_path():
    """获取数据库文件路径"""
    home_path = Path.home()
    db_path = home_path.joinpath(".vntrader", "database.db")
    
    if not db_path.exists():
        db_path = Path("database.db")
        if not db_path.exists():
            raise FileNotFoundError("找不到数据库文件!")
    
    return str(db_path)


def backup_database(db_path):
    """备份数据库"""
    from datetime import datetime
    import shutil
    
    backup_path = db_path.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(db_path, backup_path)
    print(f"✅ 数据库已备份到: {backup_path}")
    return backup_path


def show_tables(db_path):
    """显示所有表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n当前数据库中的表:")
    print("-" * 50)
    for i, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
        count = cursor.fetchone()[0]
        print(f"{i}. {table[0]:20s} ({count:,} 条数据)")
    
    conn.close()
    return [t[0] for t in tables]


def clear_table_data(db_path, table_name):
    """清空表数据（保留表结构）"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DELETE FROM {table_name};")
        conn.commit()
        print(f"✅ 已清空表 {table_name} 的所有数据")
    except Exception as e:
        print(f"❌ 清空失败: {e}")
        conn.rollback()
    finally:
        conn.close()


def drop_table(db_path, table_name):
    """删除表（包括表结构）"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        print(f"✅ 已删除表 {table_name}")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        conn.rollback()
    finally:
        conn.close()


def drop_all_tables(db_path):
    """删除所有表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            print(f"✅ 已删除表: {table_name}")
        
        conn.commit()
        print(f"\n✅ 成功删除 {len(tables)} 个表")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        conn.rollback()
    finally:
        conn.close()


def clear_all_data(db_path):
    """清空所有表的数据（保留表结构）"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name};")
            print(f"✅ 已清空表: {table_name}")
        
        conn.commit()
        print(f"\n✅ 成功清空 {len(tables)} 个表的数据")
    except Exception as e:
        print(f"❌ 清空失败: {e}")
        conn.rollback()
    finally:
        conn.close()


def delete_database_file(db_path):
    """删除整个数据库文件"""
    try:
        os.remove(db_path)
        print(f"✅ 已删除数据库文件: {db_path}")
    except Exception as e:
        print(f"❌ 删除失败: {e}")


def main():
    """主函数"""
    print("=" * 80)
    print("天勤数据库清理工具")
    print("⚠️  危险操作，请谨慎使用！")
    print("=" * 80)
    
    try:
        db_path = get_database_path()
        print(f"\n数据库路径: {db_path}")
        
        # 显示当前表
        tables = show_tables(db_path)
        
        if not tables:
            print("\n数据库中没有表")
            return
        
        print("\n" + "=" * 80)
        print("请选择操作:")
        print("=" * 80)
        print("1. 清空所有表的数据（保留表结构）")
        print("2. 删除所有表（包括表结构）")
        print("3. 删除指定的表")
        print("4. 清空指定表的数据")
        print("5. 删除整个数据库文件")
        print("0. 退出")
        print("=" * 80)
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == "0":
            print("已取消操作")
            return
        
        # 二次确认
        print("\n⚠️  警告: 此操作不可恢复！")
        confirm = input("是否要先备份数据库? (y/n): ").strip().lower()
        
        if confirm == 'y':
            backup_database(db_path)
        
        final_confirm = input("\n确认执行此操作? 输入 'YES' 确认: ").strip()
        
        if final_confirm != 'YES':
            print("已取消操作")
            return
        
        print("\n开始执行...")
        print("-" * 80)
        
        if choice == "1":
            clear_all_data(db_path)
            
        elif choice == "2":
            drop_all_tables(db_path)
            
        elif choice == "3":
            table_name = input("\n请输入要删除的表名: ").strip()
            if table_name in tables:
                drop_table(db_path, table_name)
            else:
                print(f"❌ 表 {table_name} 不存在")
                
        elif choice == "4":
            table_name = input("\n请输入要清空的表名: ").strip()
            if table_name in tables:
                clear_table_data(db_path, table_name)
            else:
                print(f"❌ 表 {table_name} 不存在")
                
        elif choice == "5":
            delete_database_file(db_path)
            
        else:
            print("❌ 无效的选项")
        
        print("-" * 80)
        print("操作完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()

