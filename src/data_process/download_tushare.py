"""
健壮的期货全量数据下载程序 日线数据 使用tushare接口
"""
from datetime import datetime
import time
import json
import os
import pandas as pd
import tushare as ts
from vnpy.trader.object import BarData, Interval, Exchange
from vnpy.trader.database import get_database

# 从环境变量获取Tushare TOKEN
TOKEN = os.getenv("TUSHARE_TOKEN")
if not TOKEN:
    raise ValueError(
        "未找到 TUSHARE_TOKEN 环境变量！\n"
        "请先设置环境变量：\n"
        "  Windows (PowerShell): $env:TUSHARE_TOKEN='your_token_here'\n"
        "  Windows (CMD): set TUSHARE_TOKEN=your_token_here\n"
        "  Linux/Mac: export TUSHARE_TOKEN='your_token_here'"
    )
ts.set_token(TOKEN)

LOG_FILE = "download_progress.log"
STATE_FILE = "download_state.json"  # 保存进度

def log(message):
    """写日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    msg = f"{timestamp} | {message}"
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

def save_state(completed_symbols):
    """保存已完成的品种列表"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump({"completed": completed_symbols}, f)

def load_state():
    """加载已完成的品种列表"""
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f).get("completed", []))
    except:
        return set()

# 所有品种
ALL_FUTURES = [
    ("螺纹钢", "RB", "SHFE", "20090327"),
    ("热轧卷板", "HC", "SHFE", "20140321"),
    ("铜", "CU", "SHFE", "19950417"),
    ("铝", "AL", "SHFE", "19920513"),
    ("锌", "ZN", "SHFE", "20070326"),
    ("铅", "PB", "SHFE", "20110324"),
    ("锡", "SN", "SHFE", "20151119"),
    ("黄金", "AU", "SHFE", "20080109"),
    ("白银", "AG", "SHFE", "20120510"),
    ("沥青", "BU", "SHFE", "20131009"),
    ("天然橡胶", "RU", "SHFE", "19950516"),
    ("纸浆", "SP", "SHFE", "20181127"),
    ("不锈钢", "SS", "SHFE", "20191225"),
    ("原油", "SC", "INE", "20180326"),
    ("低硫燃料油", "LU", "INE", "20200616"),
    ("豆一", "A", "DCE", "19990104"),
    ("豆粕", "M", "DCE", "20000717"),
    ("豆油", "Y", "DCE", "20060109"),
    ("棕榈油", "P", "DCE", "20071029"),
    ("玉米", "C", "DCE", "20040922"),
    ("玉米淀粉", "CS", "DCE", "20141219"),
    ("鸡蛋", "JD", "DCE", "20131108"),
    ("生猪", "LH", "DCE", "20210108"),
    ("铁矿石", "I", "DCE", "20131018"),
    ("焦炭", "J", "DCE", "20110415"),
    ("焦煤", "JM", "DCE", "20130322"),
    ("聚乙烯", "L", "DCE", "20070731"),
    ("聚氯乙烯", "V", "DCE", "20090525"),
    ("聚丙烯", "PP", "DCE", "20140228"),
    ("乙二醇", "EG", "DCE", "20181210"),
    ("苯乙烯", "EB", "DCE", "20190926"),
    ("棉花", "CF", "CZCE", "20040601"),
    ("白糖", "SR", "CZCE", "20060106"),
    ("PTA", "TA", "CZCE", "20061218"),
    ("菜籽油", "OI", "CZCE", "20070608"),
    ("菜籽粕", "RM", "CZCE", "20121228"),
    ("甲醇", "MA", "CZCE", "20111026"),
    ("玻璃", "FG", "CZCE", "20121203"),
    ("纯碱", "SA", "CZCE", "20191206"),
    ("尿素", "UR", "CZCE", "20190809"),
    ("花生", "PK", "CZCE", "20210201"),
    ("短纤", "PF", "CZCE", "20201016"),
]

def split_date_range(start_date, end_date="20241231", chunk_years=3):
    """分段日期"""
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    ranges = []
    current = start
    while current < end:
        next_year = current.year + chunk_years
        next_date = datetime(next_year, 12, 31)
        if next_date > end:
            next_date = end
        ranges.append((current.strftime("%Y%m%d"), next_date.strftime("%Y%m%d")))
        current = datetime(next_year + 1, 1, 1)
    return ranges

def download_segment(symbol, exchange, start_date, end_date, retry_count=0):
    """下载一个时间段 - 带重试和错误处理"""
    try:
        # 构建代码
        if exchange == "CZCE":
            ts_code = f"{symbol}.ZCE"
        else:
            ts_code = f"{symbol}.{exchange[:3].upper()}"
        
        exchange_map = {
            "SHFE": Exchange.SHFE,
            "INE": Exchange.INE,
            "DCE": Exchange.DCE,
            "CZCE": Exchange.CZCE,
        }
        vn_exchange = exchange_map.get(exchange)
        
        # 获取数据
        pro = ts.pro_api()
        df = pro.fut_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            return 0, None
        
        # 转换数据 - 给NULL值设置默认值-9999.99
        bar_list = []
        skipped = 0
        for _, row in df.iterrows():
            try:
                # 处理价格字段：为空则设为-9999.99
                open_price = float(row['open']) if row['open'] and pd.notna(row['open']) else -9999.99
                high_price = float(row['high']) if row['high'] and pd.notna(row['high']) else -9999.99
                low_price = float(row['low']) if row['low'] and pd.notna(row['low']) else -9999.99
                close_price = float(row['close']) if row['close'] and pd.notna(row['close']) else -9999.99
                
                # 处理成交量：为空则设为-9999.99
                volume = float(row['vol']) if row['vol'] and pd.notna(row['vol']) else -9999.99
                
                # 处理持仓量：为空则设为-9999.99
                open_interest = float(row['oi']) if row['oi'] and pd.notna(row['oi']) else -9999.99
                
                bar = BarData(
                    symbol=symbol,
                    exchange=vn_exchange,
                    datetime=datetime.strptime(row['trade_date'], "%Y%m%d"),
                    interval=Interval.DAILY,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume,
                    open_interest=open_interest,
                    gateway_name="TUSHARE",
                )
                bar_list.append(bar)
            except Exception as e:
                skipped += 1
                continue
        
        if not bar_list:
            return 0, f"全部数据无效(跳过{skipped}条)"
        
        # 保存
        database = get_database()
        database.save_bar_data(bar_list)
        
        msg = f"✓ {len(bar_list)}条"
        if skipped > 0:
            msg += f" (跳过{skipped}条)"
        return len(bar_list), msg
        
    except Exception as e:
        error_msg = str(e)
        
        # 处理API频率限制
        if "每分钟最多访问" in error_msg or "频率" in error_msg:
            if retry_count < 3:
                log(f"    ⚠ API限制，等待65秒后重试...")
                time.sleep(65)
                return download_segment(symbol, exchange, start_date, end_date, retry_count + 1)
            else:
                return 0, "API限制(已重试3次)"
        
        # 其他错误
        return 0, f"错误: {error_msg[:50]}"

def download_future(name, symbol, exchange, start_date):
    """下载单个品种完整历史"""
    log(f"\n{'='*50}")
    log(f"{name} ({symbol}.{exchange})")
    
    segments = split_date_range(start_date)
    log(f"共{len(segments)}段，时间{start_date}~20241231")
    
    total_count = 0
    success_segments = 0
    
    for i, (seg_start, seg_end) in enumerate(segments, 1):
        count, msg = download_segment(symbol, exchange, seg_start, seg_end)
        
        if msg:
            log(f"  [{i}/{len(segments)}] {seg_start}~{seg_end} {msg}")
        else:
            log(f"  [{i}/{len(segments)}] {seg_start}~{seg_end} 无数据")
        
        if count > 0:
            total_count += count
            success_segments += 1
        
        # 每段之间等待5秒（避免API限制）
        time.sleep(5)
    
    log(f"完成! 有效数据{total_count}条 (成功{success_segments}/{len(segments)}段)")
    return total_count

def main():
    """主函数"""
    # 初始化日志
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("VeighNa 期货全量数据下载 (健壮版)\n")
        f.write(f"开始时间: {datetime.now()}\n")
        f.write("="*60 + "\n\n")
    
    log("="*60)
    log("下载所有品种历史全量数据 (健壮版)")
    log("="*60)
    log(f"品种数量: {len(ALL_FUTURES)}")
    log(f"改进: 处理NULL值、API限制、断点续传")
    log("="*60)
    
    # 加载进度
    completed = load_state()
    if completed:
        log(f"\n检测到之前的进度，已完成{len(completed)}个品种")
        log(f"将跳过: {', '.join(completed)}")
    
    log("\n开始下载...\n")
    
    start_time = time.time()
    total_downloaded = 0
    success_count = 0
    
    for i, (name, symbol, exchange, start_date) in enumerate(ALL_FUTURES, 1):
        # 跳过已完成的
        symbol_key = f"{symbol}.{exchange}"
        if symbol_key in completed:
            log(f"\n>>> [{i}/{len(ALL_FUTURES)}] {name} - 已完成，跳过")
            continue
        
        log(f"\n>>> [{i}/{len(ALL_FUTURES)}] <<<")
        
        try:
            count = download_future(name, symbol, exchange, start_date)
            total_downloaded += count
            
            if count > 0:
                success_count += 1
                # 标记为已完成
                completed.add(symbol_key)
                save_state(list(completed))
        except KeyboardInterrupt:
            log("\n\n>>> 用户中断 <<<")
            save_state(list(completed))
            return
        except Exception as e:
            log(f"严重错误: {e}")
            continue
        
        # 进度报告
        if i % 5 == 0:
            elapsed = (time.time() - start_time) / 60
            log(f"\n【进度】{i}/{len(ALL_FUTURES)} ({i/len(ALL_FUTURES)*100:.1f}%)")
            log(f"已用{elapsed:.1f}分钟，已下载{total_downloaded}条\n")
    
    elapsed = time.time() - start_time
    log("\n" + "="*60)
    log("全部完成！")
    log("="*60)
    log(f"成功: {success_count}/{len(ALL_FUTURES)}")
    log(f"总数据: {total_downloaded}条")
    log(f"总耗时: {elapsed/60:.1f}分钟")
    log("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"\n致命错误: {e}")

