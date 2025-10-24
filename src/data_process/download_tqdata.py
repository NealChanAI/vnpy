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

# 2. 要下载的期货品种（VeighNa格式：symbol.EXCHANGE）
FUTURES_SYMBOLS = [
    # ==================== 上海期货交易所（SHFE） ====================
    # 黑色系
    'rb2505.SHFE',      # 螺纹钢
    'hc2505.SHFE',      # 热轧卷板
    'ss2505.SHFE',      # 不锈钢
    'wr2505.SHFE',      # 线材
    
    # 有色金属
    'cu2505.SHFE',      # 铜
    'al2505.SHFE',      # 铝
    'zn2505.SHFE',      # 锌
    'pb2505.SHFE',      # 铅
    'ni2505.SHFE',      # 镍
    'sn2505.SHFE',      # 锡
    
    # 贵金属
    'au2506.SHFE',      # 黄金
    'ag2506.SHFE',      # 白银
    
    # 能源化工
    'fu2505.SHFE',      # 燃料油
    'bu2506.SHFE',      # 石油沥青
    'ru2505.SHFE',      # 天然橡胶
    'sp2505.SHFE',      # 纸浆
    
    # ==================== 大连商品交易所（DCE） ====================
    # 黑色系
    'i2505.DCE',        # 铁矿石
    'j2505.DCE',        # 焦炭
    'jm2505.DCE',       # 焦煤
    
    # 农产品
    'a2505.DCE',        # 豆一
    'b2505.DCE',        # 豆二
    'm2505.DCE',        # 豆粕
    'y2505.DCE',        # 豆油
    'p2505.DCE',        # 棕榈油
    'c2505.DCE',        # 玉米
    'cs2505.DCE',       # 玉米淀粉
    'jd2505.DCE',       # 鸡蛋
    'lh2505.DCE',       # 生猪
    
    # 化工
    'l2505.DCE',        # 聚乙烯（LLDPE）
    'v2505.DCE',        # 聚氯乙烯（PVC）
    'pp2505.DCE',       # 聚丙烯
    'eg2505.DCE',       # 乙二醇
    'eb2505.DCE',       # 苯乙烯
    'pg2505.DCE',       # 液化石油气
    
    # 建材
    'fb2505.DCE',       # 纤维板
    'bb2505.DCE',       # 胶合板
    
    # ==================== 郑州商品交易所（CZCE） ====================
    # 农产品
    'SR505.CZCE',       # 白糖
    'CF505.CZCE',       # 棉花
    'CY505.CZCE',       # 棉纱
    'AP505.CZCE',       # 苹果
    'CJ505.CZCE',       # 红枣
    'PK505.CZCE',       # 花生
    'RM505.CZCE',       # 菜粕
    'OI505.CZCE',       # 菜油
    
    # 化工
    'TA505.CZCE',       # PTA（精对苯二甲酸）
    'MA505.CZCE',       # 甲醇
    'FG505.CZCE',       # 玻璃
    'SA505.CZCE',       # 纯碱
    'UR505.CZCE',       # 尿素
    'PF505.CZCE',       # 短纤
    
    # 能源
    'ZC505.CZCE',       # 动力煤
    
    # 金属
    'SF505.CZCE',       # 硅铁
    'SM505.CZCE',       # 锰硅
    
    # ==================== 上海国际能源交易中心（INE） ====================
    'sc2505.INE',       # 原油
    'nr2505.INE',       # 20号胶
    'lu2505.INE',       # 低硫燃料油
    'bc2505.INE',       # 国际铜
    
    # ==================== 中国金融期货交易所（CFFEX） ====================
    'IF2501.CFFEX',     # 沪深300股指期货
    'IH2501.CFFEX',     # 上证50股指期货
    'IC2501.CFFEX',     # 中证500股指期货
    'IM2501.CFFEX',     # 中证1000股指期货
    'T2503.CFFEX',      # 10年期国债期货
    'TF2503.CFFEX',     # 5年期国债期货
    'TS2503.CFFEX',     # 2年期国债期货
]

# ⚠️ 重要提示：
# 1. 上面列出了64个期货品种，下载全部需要较长时间（可能数小时）
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