"""
逐行列出所有品种的数据详情
"""

import sqlite3
from pathlib import Path


# 品种名称映射表
SYMBOL_NAMES = {
    # 上海期货交易所 SHFE
    'rb': '螺纹钢', 'hc': '热轧卷板', 'ss': '不锈钢', 'wr': '线材',
    'cu': '铜', 'al': '铝', 'zn': '锌', 'pb': '铅', 'ni': '镍', 'sn': '锡',
    'au': '黄金', 'ag': '白银',
    'fu': '燃料油', 'bu': '石油沥青', 'ru': '天然橡胶', 'sp': '纸浆',
    
    # 大连商品交易所 DCE
    'i': '铁矿石', 'j': '焦炭', 'jm': '焦煤',
    'a': '豆一', 'b': '豆二', 'm': '豆粕', 'y': '豆油', 'p': '棕榈油',
    'c': '玉米', 'cs': '玉米淀粉', 'jd': '鸡蛋', 'lh': '生猪',
    'l': '聚乙烯', 'v': 'PVC', 'pp': '聚丙烯', 'eg': '乙二醇', 'eb': '苯乙烯', 'pg': '液化石油气',
    'fb': '纤维板', 'bb': '胶合板',
    
    # 郑州商品交易所 CZCE
    'SR': '白糖', 'CF': '棉花', 'CY': '棉纱', 'AP': '苹果', 'CJ': '红枣', 'PK': '花生',
    'RM': '菜粕', 'OI': '菜油',
    'TA': 'PTA', 'MA': '甲醇', 'FG': '玻璃', 'SA': '纯碱', 'UR': '尿素', 'PF': '短纤',
    'ZC': '动力煤',
    'SF': '硅铁', 'SM': '锰硅',
    
    # 上海国际能源交易中心 INE
    'sc': '原油', 'nr': '20号胶', 'lu': '低硫燃料油', 'bc': '国际铜',
    
    # 中国金融期货交易所 CFFEX
    'IF': '沪深300股指', 'IH': '上证50股指', 'IC': '中证500股指', 'IM': '中证1000股指',
    'T': '10年期国债', 'TF': '5年期国债', 'TS': '2年期国债',
}

# 交易所名称
EXCHANGE_NAMES = {
    'SHFE': '上期所',
    'DCE': '大商所',
    'CZCE': '郑商所',
    'INE': '能源中心',
    'CFFEX': '中金所',
}


def get_symbol_name(symbol):
    """获取品种中文名称"""
    # 去掉数字部分，提取品种代码
    code = ''.join([c for c in symbol if not c.isdigit()])
    return SYMBOL_NAMES.get(code, '未知品种')


def get_database_path():
    """获取数据库文件路径"""
    home_path = Path.home()
    db_path = home_path.joinpath(".vntrader", "database.db")
    if not db_path.exists():
        db_path = Path("database.db")
    return str(db_path)


def list_all_symbols():
    """逐行列出所有品种"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有品种
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
    
    print("=" * 100)
    print("数据库中所有品种的详细信息")
    print("=" * 100)
    print()
    
    # 逐行打印
    for i, row in enumerate(results, 1):
        symbol, exchange, count, start_date, end_date = row
        vt_symbol = f"{symbol}.{exchange}"
        
        # 获取中文名称和交易所简称
        symbol_name = get_symbol_name(symbol)
        exchange_name = EXCHANGE_NAMES.get(exchange, exchange)
        
        print(f"{i:2d}. {vt_symbol:20s} ({symbol_name:8s} | {exchange_name:6s})  "
              f"数据量: {count:>10,} 条  开始: {start_date}  结束: {end_date}")
    
    # 统计
    total_bars = sum(row[2] for row in results)
    print()
    print("=" * 100)
    print(f"总计: {len(results)} 个品种  |  总数据量: {total_bars:,} 条K线")
    print("=" * 100)
    
    conn.close()


if __name__ == "__main__":
    list_all_symbols()

