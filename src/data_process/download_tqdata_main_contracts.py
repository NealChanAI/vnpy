"""
使用天勤SDK原生API下载主力连续合约数据
数据将保存到VeighNa数据库，合约格式使用 KQ.m@ 主连
"""

import os
from datetime import datetime
import pandas as pd
from tqsdk import TqApi, TqAuth
from tqsdk.tools import DataDownloader
from vnpy.trader.database import get_database, DB_TZ
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData


# 天勤账号
TQDATA_USERNAME = "13716539053"
TQDATA_PASSWORD = "Nealchan1001"

# 主力连续合约列表（使用天勤的 KQ.m@ 格式）
MAIN_CONTRACTS = {
    # 上海期货交易所 SHFE (16个)
    # 'SHFE': ['rb', 'hc', 'ss', 'wr', 'cu', 'al', 'zn', 'pb', 'ni', 'sn',
    #          'au', 'ag', 'fu', 'bu', 'ru', 'sp'],
    
    # # 大连商品交易所 DCE (22个)
    # 'DCE': ['i', 'j', 'jm', 'a', 'b', 'm', 'y', 'p', 'c', 'cs', 'jd', 'lh',
    #         'l', 'v', 'pp', 'eg', 'eb', 'pg', 'fb', 'bb'],
    
    # # 郑州商品交易所 CZCE (16个)
    # 'CZCE': ['SR', 'CF', 'CY', 'AP', 'CJ', 'PK', 'RM', 'OI',
    #          'TA', 'MA', 'FG', 'SA', 'UR', 'PF', 'SF', 'SM', 'ZC'],
    
    # 上海国际能源交易中心 INE (4个)
    'INE': ['sc', 'nr', 'lu', 'bc'],
    
    # 中国金融期货交易所 CFFEX (7个)
    # 'CFFEX': ['IF', 'IH', 'IC', 'IM', 'T', 'TF', 'TS'],
}

# 品种中文名称
SYMBOL_NAMES = {
    'rb': '螺纹钢', 'hc': '热轧卷板', 'ss': '不锈钢', 'wr': '线材',
    'cu': '铜', 'al': '铝', 'zn': '锌', 'pb': '铅', 'ni': '镍', 'sn': '锡',
    'au': '黄金', 'ag': '白银',
    'fu': '燃料油', 'bu': '石油沥青', 'ru': '天然橡胶', 'sp': '纸浆',
    'i': '铁矿石', 'j': '焦炭', 'jm': '焦煤',
    'a': '豆一', 'b': '豆二', 'm': '豆粕', 'y': '豆油', 'p': '棕榈油',
    'c': '玉米', 'cs': '玉米淀粉', 'jd': '鸡蛋', 'lh': '生猪',
    'l': '聚乙烯', 'v': 'PVC', 'pp': '聚丙烯', 'eg': '乙二醇', 'eb': '苯乙烯', 'pg': '液化石油气',
    'fb': '纤维板', 'bb': '胶合板',
    'SR': '白糖', 'CF': '棉花', 'CY': '棉纱', 'AP': '苹果', 'CJ': '红枣', 'PK': '花生',
    'RM': '菜粕', 'OI': '菜油',
    'TA': 'PTA', 'MA': '甲醇', 'FG': '玻璃', 'SA': '纯碱', 'UR': '尿素', 'PF': '短纤',
    'ZC': '动力煤', 'SF': '硅铁', 'SM': '锰硅',
    'sc': '原油', 'nr': '20号胶', 'lu': '低硫燃料油', 'bc': '国际铜',
    'IF': '沪深300股指', 'IH': '上证50股指', 'IC': '中证500股指', 'IM': '中证1000股指',
    'T': '10年期国债', 'TF': '5年期国债', 'TS': '2年期国债',
}

# 数据下载参数
START_DATE = datetime(2015, 1, 1)  # 从2015年开始（实际能下载多少取决于合约上市时间）
END_DATE = datetime.now()          # 到当前时间


def download_main_contract(api, database, symbol_code, exchange_str):
    """
    下载单个主力连续合约数据
    
    Args:
        api: TqApi实例
        database: VeighNa数据库实例
        symbol_code: 品种代码（如 rb, cu, MA）
        exchange_str: 交易所代码（如 SHFE, DCE）
    """
    # 构造天勤主连合约代码
    tq_symbol = f"KQ.m@{exchange_str}.{symbol_code}"
    
    # 用于保存到VeighNa数据库的symbol（保留主连标识）
    vn_symbol = f"{symbol_code}_MAIN"  # 如 rb_MAIN
    
    symbol_name = SYMBOL_NAMES.get(symbol_code, symbol_code)
    
    print(f"\n{'='*80}")
    print(f"正在下载: {tq_symbol} ({symbol_name}主连)")
    print(f"保存为: {vn_symbol}.{exchange_str}")
    print(f"{'='*80}")
    
    try:
        # 使用DataDownloader下载完整历史数据
        print(f"⏳ 正在从天勤下载完整历史数据...")
        print(f"   时间范围: {START_DATE.date()} 至 {END_DATE.date()}")
        
        # 创建临时CSV文件
        import tempfile
        temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        temp_csv_path = temp_csv.name
        temp_csv.close()
        
        # 使用DataDownloader下载数据到CSV
        downloader = DataDownloader(api, symbol_list=[tq_symbol], dur_sec=60,
                                   start_dt=START_DATE, end_dt=END_DATE,
                                   csv_file_name=temp_csv_path)
        
        # 等待下载完成
        while not downloader.is_finished():
            api.wait_update()
            # 显示下载进度（get_progress返回的是百分比数值，不需要再乘100）
            progress = downloader.get_progress()
            if progress > 0:
                print(f"\r   下载进度: {progress:.1f}%", end='', flush=True)
        
        print(f"\n   ✅ 下载完成")
        
        # 读取CSV文件
        print(f"📖 正在读取数据文件...")
        klines = pd.read_csv(temp_csv_path)
        
        if klines is None or len(klines) == 0:
            print(f"⚠️  CSV文件为空")
            os.remove(temp_csv_path)
            return False
        
        print(f"✅ 成功读取 {len(klines):,} 条记录")
        print(f"   CSV列名: {list(klines.columns)}")
        print(f"   前3条数据预览:")
        print(klines.head(3))
        
        # 删除临时文件
        os.remove(temp_csv_path)
        
        # 转换为VeighNa的BarData格式
        print(f"🔄 正在转换数据格式...")
        bars = []
        exchange = Exchange(exchange_str)
        
        for idx, row in klines.iterrows():
            # 跳过无效数据
            if pd.isna(row.get('close')) or row.get('close', 0) == 0:
                continue
            
            # CSV格式的datetime是字符串，需要转换
            try:
                # 解析datetime字符串
                dt = pd.to_datetime(row['datetime'])
                
                # 转换为Python原生datetime（非pandas Timestamp）
                if hasattr(dt, 'to_pydatetime'):
                    dt = dt.to_pydatetime()
                
                # 转换为带时区的datetime
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=DB_TZ)
                else:
                    dt = dt.astimezone(DB_TZ)
            except Exception as e:
                print(f"  ⚠️  跳过无效时间数据: {row.get('datetime', 'N/A')} - {e}")
                continue
            
            bar = BarData(
                symbol=vn_symbol,
                exchange=exchange,
                datetime=dt,
                interval=Interval.MINUTE,
                volume=float(row.get('volume', 0)),
                turnover=0,  # 天勤K线没有成交额
                open_interest=float(row.get('close_oi', 0)),
                open_price=float(row.get('open', 0)),
                high_price=float(row.get('high', 0)),
                low_price=float(row.get('low', 0)),
                close_price=float(row.get('close', 0)),
                gateway_name="TQSDK"
            )
            bars.append(bar)
        
        if not bars:
            print(f"⚠️  转换后没有有效数据")
            return False
        
        print(f"✅ 转换完成，共 {len(bars)} 条有效数据")
        print(f"📅 时间范围: {bars[0].datetime} 至 {bars[-1].datetime}")
        
        # 保存到VeighNa数据库
        print(f"💾 正在保存到数据库...")
        database.save_bar_data(bars)
        
        print(f"✅ 保存成功!")
        return True
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主程序"""
    print("\n" + "="*100)
    print(" "*35 + "天勤主力连续合约数据下载")
    print("="*100)
    print()
    print("📌 重要说明:")
    print("   1. 使用天勤SDK原生API，支持 KQ.m@ 主连合约格式")
    print("   2. 主连合约会自动跟随主力合约，数据永不过期")
    print("   3. 数据保存到VeighNa数据库，symbol格式为: 品种_MAIN（如 rb_MAIN）")
    print("   4. 数据从2015年开始下载")
    print()
    
    total_symbols = sum(len(v) for v in MAIN_CONTRACTS.values())
    print(f"   共计 {total_symbols} 个品种")
    print()
    print("="*100)
    
    # 初始化天勤API
    print("\n🔌 正在连接天勤...")
    api = TqApi(auth=TqAuth(TQDATA_USERNAME, TQDATA_PASSWORD))
    print("✅ 天勤连接成功")
    
    # 获取VeighNa数据库
    print("🔌 正在连接数据库...")
    database = get_database()
    print("✅ 数据库连接成功")
    
    # 开始下载
    success_count = 0
    failed_list = []
    start_time = datetime.now()
    
    print("\n" + "="*100)
    print("开始下载数据...")
    print("="*100)
    
    for exchange_str, symbols in MAIN_CONTRACTS.items():
        print(f"\n\n{'#'*100}")
        print(f"# 交易所: {exchange_str} ({len(symbols)}个品种)")
        print(f"{'#'*100}")
        
        for symbol_code in symbols:
            success = download_main_contract(api, database, symbol_code, exchange_str)
            if success:
                success_count += 1
            else:
                failed_list.append(f"{symbol_code}_MAIN.{exchange_str}")
    
    # 关闭API
    api.close()
    
    # 统计信息
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n\n" + "="*100)
    print(" "*40 + "下载完成!")
    print("="*100)
    print(f"\n✅ 成功: {success_count} 个品种")
    print(f"❌ 失败: {len(failed_list)} 个品种")
    print(f"⏱️  耗时: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
    
    if failed_list:
        print(f"\n失败的品种:")
        for vt_symbol in failed_list:
            print(f"   - {vt_symbol}")
    
    print("\n💡 查看下载结果:")
    print("   python src/data_process/list_all_symbols.py")
    print("\n" + "="*100)


if __name__ == "__main__":
    main()

