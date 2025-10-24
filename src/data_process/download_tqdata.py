"""
天勤TQData - 期货分钟数据下载到VeighNa数据库
"""

import os
from datetime import datetime
from vnpy.trader.setting import SETTINGS
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.database import get_database, DB_TZ
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest
from vnpy.trader.utility import extract_vt_symbol
# from tqsdk import TqApi, TqAuth


# api = TqApi(auth=TqAuth("13716539053", "Nealchan1001"))

# 1. 天勤账号（从环境变量获取）
TQDATA_USERNAME = os.getenv("TQDATA_USERNAME","13716539053")
TQDATA_PASSWORD = os.getenv("TQDATA_PASSWORD","Nealchan1001")

if not TQDATA_USERNAME or not TQDATA_PASSWORD:
    raise ValueError(
        "未找到天勤账号环境变量！\n"
        "请先设置环境变量：\n"
        "  Windows (PowerShell):\n"
        "    $env:TQDATA_USERNAME='13716539053'\n"
        "    $env:TQDATA_PASSWORD='Nealchan1001'\n"
        "  注册地址: https://www.shinnytech.com/tianqin （完全免费）"
    )

# 2. 要下载的期货品种（2026年合约，数据有效期到2026年初）
FUTURES_SYMBOLS = [
    # ==================== 上海期货交易所（SHFE） ====================
    # 黑色系
    'rb2601.SHFE',      # 螺纹钢 2026年1月
    'hc2601.SHFE',      # 热轧卷板 2026年1月
    'ss2601.SHFE',      # 不锈钢 2026年1月
    'wr2601.SHFE',      # 线材 2026年1月
    
    # 有色金属
    'cu2601.SHFE',      # 铜 2026年1月
    'al2601.SHFE',      # 铝 2026年1月
    'zn2601.SHFE',      # 锌 2026年1月
    'pb2601.SHFE',      # 铅 2026年1月
    'ni2601.SHFE',      # 镍 2026年1月
    'sn2601.SHFE',      # 锡 2026年1月
    
    # 贵金属
    'au2602.SHFE',      # 黄金 2026年2月
    'ag2602.SHFE',      # 白银 2026年2月
    
    # 能源化工
    'fu2601.SHFE',      # 燃料油 2026年1月
    'bu2602.SHFE',      # 石油沥青 2026年2月
    'ru2601.SHFE',      # 天然橡胶 2026年1月
    'sp2601.SHFE',      # 纸浆 2026年1月
    
    # ==================== 大连商品交易所（DCE） ====================
    # 黑色系
    'i2601.DCE',        # 铁矿石 2026年1月
    'j2601.DCE',        # 焦炭 2026年1月
    'jm2601.DCE',       # 焦煤 2026年1月
    
    # 农产品
    'a2601.DCE',        # 豆一 2026年1月
    'b2601.DCE',        # 豆二 2026年1月
    'm2601.DCE',        # 豆粕 2026年1月
    'y2601.DCE',        # 豆油 2026年1月
    'p2601.DCE',        # 棕榈油 2026年1月
    'c2601.DCE',        # 玉米 2026年1月
    'cs2601.DCE',       # 玉米淀粉 2026年1月
    'jd2601.DCE',       # 鸡蛋 2026年1月
    'lh2601.DCE',       # 生猪 2026年1月
    
    # 化工
    'l2601.DCE',        # 聚乙烯（LLDPE）2026年1月
    'v2601.DCE',        # 聚氯乙烯（PVC）2026年1月
    'pp2601.DCE',       # 聚丙烯 2026年1月
    'eg2601.DCE',       # 乙二醇 2026年1月
    'eb2601.DCE',       # 苯乙烯 2026年1月
    'pg2601.DCE',       # 液化石油气 2026年1月
    
    # 建材
    'fb2601.DCE',       # 纤维板 2026年1月
    'bb2601.DCE',       # 胶合板 2026年1月
    
    # ==================== 郑州商品交易所（CZCE） ====================
    # 农产品
    'SR601.CZCE',       # 白糖 2026年1月
    'CF601.CZCE',       # 棉花 2026年1月
    'CY601.CZCE',       # 棉纱 2026年1月
    'AP601.CZCE',       # 苹果 2026年1月
    'CJ601.CZCE',       # 红枣 2026年1月
    'PK601.CZCE',       # 花生 2026年1月
    'RM601.CZCE',       # 菜粕 2026年1月
    'OI601.CZCE',       # 菜油 2026年1月
    
    # 化工
    'TA601.CZCE',       # PTA（精对苯二甲酸）2026年1月
    'MA601.CZCE',       # 甲醇 2026年1月
    'FG601.CZCE',       # 玻璃 2026年1月
    'SA601.CZCE',       # 纯碱 2026年1月
    'UR601.CZCE',       # 尿素 2026年1月
    'PF601.CZCE',       # 短纤 2026年1月
    
    # 能源
    'ZC601.CZCE',       # 动力煤 2026年1月
    
    # 金属
    'SF601.CZCE',       # 硅铁 2026年1月
    'SM601.CZCE',       # 锰硅 2026年1月
    
    # ==================== 上海国际能源交易中心（INE） ====================
    'sc2601.INE',       # 原油 2026年1月
    'nr2601.INE',       # 20号胶 2026年1月
    'lu2601.INE',       # 低硫燃料油 2026年1月
    'bc2601.INE',       # 国际铜 2026年1月
    
    # ==================== 中国金融期货交易所（CFFEX） ====================
    'IF2511.CFFEX',     # 沪深300股指 2025年11月
    'IH2511.CFFEX',     # 上证50股指 2025年11月
    'IC2511.CFFEX',     # 中证500股指 2025年11月
    'IM2511.CFFEX',     # 中证1000股指 2025年11月
    'T2512.CFFEX',      # 10年期国债 2025年12月
    'TF2512.CFFEX',     # 5年期国债 2025年12月
    'TS2512.CFFEX',     # 2年期国债 2025年12月
]

# ⚠️ 重要提示：
# 1. 上面列出了64个期货品种，下载全部需要较长时间
# 2. 建议首次使用时：
#    - 只选择需要的品种（注释掉不需要的）
#    - 或先下载少量品种测试
# 3. 合约月份说明：
#    - 商品期货通常用2505（2025年5月）
#    - 郑商所用505（不带年份前缀）
#    - 股指期货用2501（季月合约）
#    - 国债期货用2503（季月合约）
# 4. 如果某个合约下载失败，可能是：
#    - 合约代码错误
#    - 合约尚未上市或已退市
#    - 月份选择不对（需要改为实际的主力合约月份）

# 3. 下载时间范围（天勤支持从合约上市以来的全部历史）
START_DATE = datetime(2015, 1, 1, tzinfo=DB_TZ)  # 可以改为更早的日期
END_DATE = datetime.now(tz=DB_TZ)                # 到当前时间

# 4. 数据周期
INTERVAL = Interval.MINUTE  # 1分钟

# ==================== 主程序 ====================

def main():
    """天勤数据下载主流程"""
    
    print("=" * 70)
    print("天勤TQSDK - 期货分钟数据下载（")
    print("=" * 70)
    print(f"\n📋 待下载品种数量: {len(FUTURES_SYMBOLS)} 个")
    print(f"📅 时间范围: {START_DATE.date()} 至 {END_DATE.date()}")
    
    
    # 1. 配置天勤数据服务
    print("\n【步骤1】配置天勤数据服务...")
    SETTINGS["datafeed.name"] = "tqsdk"
    SETTINGS["datafeed.username"] = TQDATA_USERNAME
    SETTINGS["datafeed.password"] = TQDATA_PASSWORD
    
    # 2. 获取数据服务实例
    try:
        datafeed = get_datafeed()
        datafeed.init()
        print("✅ 天勤数据服务连接成功")
    except Exception as e:
        print(f"❌ 天勤连接失败: {e}")
        return
    
    # 3. 获取数据库实例
    print("\n【步骤2】连接数据库...")
    try:
        database = get_database()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 4. 下载数据
    print(f"\n【步骤3】开始下载数据...")
    print(f"时间范围: {START_DATE.date()} 至 {END_DATE.date()}")
    print(f"数据粒度: 1分钟")
    print(f"合约数量: {len(FUTURES_SYMBOLS)}")
    print("=" * 70)
    
    total_bars = 0
    success_count = 0
    
    for i, vt_symbol in enumerate(FUTURES_SYMBOLS, 1):
        print(f"\n[{i}/{len(FUTURES_SYMBOLS)}] {vt_symbol}")
        
        try:
            # 拆分合约代码和交易所
            symbol, exchange = extract_vt_symbol(vt_symbol)
            
            # 创建历史数据请求
            req = HistoryRequest(
                symbol=symbol,
                exchange=exchange,
                start=START_DATE,
                end=END_DATE,
                interval=INTERVAL
            )
            
            # 从天勤数据服务下载
            print(f"  正在下载...")
            bars = datafeed.query_bar_history(req)
            
            if not bars:
                print(f"  ⚠️ 没有数据")
                continue
            
            # 保存到数据库
            database.save_bar_data(bars)
            
            print(f"  ✅ 成功下载: {len(bars)} 条")
            print(f"  💾 已保存到数据库")
            
            total_bars += len(bars)
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 下载失败: {e}")
            continue
    
    # 5. 统计信息
    print("\n" + "=" * 70)
    print("下载完成！")
    print(f"成功: {success_count}/{len(FUTURES_SYMBOLS)}")
    print(f"总数据量: {total_bars:,} 条")
    print("=" * 70)



if __name__ == "__main__":
    main()