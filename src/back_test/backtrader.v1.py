# -*- coding: utf-8 -*-
# ===============================================================
#
#    @Create Author : 
#    @Create Time   : 2025-11-04
#    @Description   : 回测脚本1
#
# ===============================================================
import backtrader as bt
import pandas as pd
import tushare as ts  # 需提前安装：pip install tushare
import os

# 配置Tushare接口（需注册获取token：https://tushare.pro/）
TOKEN = os.getenv("TUSHARE_TOKEN")
ts.set_token(TOKEN)
pro = ts.pro_api()

# A股佣金与印花税（仅卖出收取）
class AShareCommission(bt.CommInfoBase):
    params = dict(
        commission=0.0002,   # 佣金（双边）
        stamp_duty=0.001,    # 印花税（单边，仅卖出）
        percabs=True,        # 按比例收费
        stocklike=True       # 股票模式
    )

    def _getcommission(self, size, price, pseudoexec):
        # 佣金按买卖双边收取
        comm = abs(size) * price * self.p.commission
        # 印花税仅在卖出时收取（size < 0）
        if size < 0:
            comm += abs(size) * price * self.p.stamp_duty
        return comm

# 策略类定义
class Break30Retrace5Strategy(bt.Strategy):
    params = (
        ('ma5_period', 5),    # 5日均线周期
        ('ma30_period', 30),  # 30日均线周期
        ('retrace_range', 0.01),  # 回踩容忍幅度（1%）
        ('stop_loss', 0.03),  # 止损比例（3%）
        ('take_profit', 0.1), # 止盈比例（10%）
        ('max_pos_ratio', 0.2), # 单只股票最大仓位比例
    )

    def __init__(self):
        # 初始化均线指标
        self.ma5 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.p.ma5_period)
        self.ma30 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.p.ma30_period)
        # 辅助指标：30日均线趋势（是否向上）
        self.ma30_trend = self.ma30 > bt.indicators.SimpleMovingAverage(self.ma30, period=5)
        # 记录入场价和止损价
        self.entry_price = 0.0
        self.stop_loss_price = 0.0

    def next(self):
        # 无持仓时，寻找入场信号
        if not self.getposition(self.datas[0]).size:
            # 1. 先满足突破30日均线条件（前一交易日未破，当前交易日突破）
            break_30 = (self.datas[0].close[-1] <= self.ma30[-1]) and (self.datas[0].close[0] > self.ma30[0])
            if break_30:
                # 2. 突破后回踩5日均线（收盘价在5日均线±1%内，或最低价触及5日均线）
                retrace_ma5 = (abs(self.datas[0].close[0] - self.ma5[0]) / self.ma5[0] <= self.p.retrace_range) or \
                              (self.datas[0].low[0] <= self.ma5[0] * (1 + self.p.retrace_range))
                # 3. 30日均线保持向上趋势
                if retrace_ma5 and self.ma30_trend[0]:
                    # 计算可买入仓位（总资金×最大仓位比例÷当前股价）
                    target_size = (self.broker.getvalue() * self.p.max_pos_ratio) // self.datas[0].close[0]
                    if target_size > 0:
                        self.buy(size=target_size)
                        self.entry_price = self.datas[0].close[0]
                        self.stop_loss_price = self.datas[0].low[0] * (1 - self.p.stop_loss)  # 按入场日最低价止损
        # 有持仓时，执行止盈止损
        else:
            # 止盈：盈利达到10%
            take_profit = self.datas[0].close[0] >= self.entry_price * (1 + self.p.take_profit)
            # 止损：跌破止损价，或30日均线拐头向下+跌破5日均线
            stop_loss = (self.datas[0].close[0] < self.stop_loss_price) or \
                        (not self.ma30_trend[0] and self.datas[0].close[0] < self.ma5[0])
            if take_profit or stop_loss:
                self.sell(size=self.getposition(self.datas[0]).size)  # 清仓出场

# 数据获取（以贵州茅台600519为例，可替换为其他股票）
def get_stock_data(ts_code, start_date, end_date):
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df = df.sort_values('trade_date')  # 按日期排序
    # 转换为Backtrader所需格式（日期索引，列名对应open/high/low/close/volume）
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'}, inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    return bt.feeds.PandasData(dataname=df)

# 回测执行
if __name__ == '__main__':
    # 初始化回测引擎
    cerebro = bt.Cerebro()
    # 添加策略
    cerebro.addstrategy(Break30Retrace5Strategy)
    # 添加股票数据（2018-2023年数据，可调整时间范围）
    stock_data = get_stock_data(ts_code='600519.SH', start_date='20180101', end_date='20231231')
    cerebro.adddata(stock_data)
    # 初始资金设置（10万元）
    cerebro.broker.setcash(100000.0)
    # 交易成本设置（A股：佣金0.02%，印花税0.1%仅卖出时收取）
    cerebro.broker.addcommissioninfo(AShareCommission())
    # 显示初始资金
    print(f'初始资金：{cerebro.broker.getvalue():.2f} 元')
    # 运行回测
    cerebro.run()
    # 显示回测结果
    print(f'回测结束资金：{cerebro.broker.getvalue():.2f} 元')
    print(f'累计收益：{(cerebro.broker.getvalue() - 100000) / 100000 * 100:.2f}%')
    # 绘制回测图表（K线、均线、买卖信号）
    cerebro.plot(style='candle')