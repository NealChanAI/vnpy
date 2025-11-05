import backtrader as bt
import pandas as pd
import tushare as ts  # 需提前安装：pip install tushare
import os
import numpy as np

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


class MACDBottomDeviationStrategy(bt.Strategy):
    params = (
        ('macd1', 12),    # MACD 短期EMA周期
        ('macd2', 26),    # MACD 长期EMA周期
        ('macdsig', 9),   # MACD 信号线周期
        ('dev_threshold', 0.05),  # 底背离价格差值阈值（5%）
        ('zero_range', 0.05),     # 回零轴允许波动区间（±0.05）
        ('vol_multiplier', 1.3),  # 成交量放大倍数（1.3倍均值）
    )

    def __init__(self):
        # 初始化MACD指标
        self.macd = bt.indicators.MACD(
            self.data,
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig
        )
        self.dif = self.macd.macd
        self.dea = self.macd.signal
        self.macd_hist = self.dif - self.dea  # 正确计算MACD柱

        # 辅助指标：20日均线（趋势过滤）、成交量均值
        self.ma20 = bt.indicators.SimpleMovingAverage(self.data, period=20)
        self.vol_mean = bt.indicators.SimpleMovingAverage(self.data.volume, period=5)

        # 状态变量：记录底背离、上零轴状态
        self.bottom_deviation = False
        self.cross_up_zero = False

    def next(self):
        # 1. 判断底背离（股价新低，DIF未新低，且股价跌幅达标）
        if (len(self.data) > 2 and
            self.data.low[0] < self.data.low[-1] < self.data.low[-2]  # 股价创2期新低
            and self.dif[0] > self.dif[-1] > self.dif[-2]  # DIF创2期新高（底背离）
            and (self.data.low[-2] - self.data.low[0]) / self.data.low[-2] > self.p.dev_threshold):  # 跌幅达标
            self.bottom_deviation = True

        # 2. 底背离后，DIF上穿零轴（趋势确认）
        if self.bottom_deviation and self.dif[-1] < 0 and self.dif[0] > 0:
            self.cross_up_zero = True

        # 3. 上零轴后，DIF回零轴企稳（买入信号）
        if (self.cross_up_zero
            and abs(self.dif[0]) < self.p.zero_range  # DIF在零轴附近
            and self.data.close[0] > self.ma20[0]  # 股价在20日均线上（趋势过滤）
            and self.data.volume[0] > self.vol_mean[0] * self.p.vol_multiplier  # 成交量放大
            and not self.position):  # 无持仓
            self.buy(size=100)  # 买入（可调整仓位, A股最小单位100）

        # 4. 止损：跌破回零轴低点下方1%
        if self.position:
            stop_loss_price = self.data.low[0] * 0.99  # 以回零轴当日低点为基准
            if self.data.close[0] < stop_loss_price:
                self.sell(size=self.position.size)
                self.bottom_deviation = False  # 重置状态
                self.cross_up_zero = False

        # 5. 止盈：MACD顶背离 或 DIF下穿零轴
        if self.position:
            # 顶背离判断（股价新高，DIF未新高）
            top_dev = (len(self.data) > 2 and
                       self.data.high[0] > self.data.high[-1] > self.data.high[-2]
                       and self.dif[0] < self.dif[-1] < self.dif[-2])
            # DIF下穿零轴
            cross_down_zero = self.dif[-1] > 0 and self.dif[0] < 0
            if top_dev or cross_down_zero:
                self.sell(size=self.position.size)
                self.bottom_deviation = False
                self.cross_up_zero = False

# 数据获取（以贵州茅台600519为例，可替换为其他股票）
def get_stock_data(ts_code, start_date, end_date):
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df = df.sort_values('trade_date')  # 按日期排序
    print(f'sort之后\n {df.head(10)}')
    # 转换为Backtrader所需格式（日期索引，列名对应open/high/low/close/volume）
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'}, inplace=True)
    # Tushare的vol单位是手，backtrader需要股数
    df['Volume'] = df['Volume'] * 100
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    # df = df.iloc[::-1] # Tushare数据是降序的，需要反转为升序
    print(f'iloc之后\n {df.head(10)}')
    return bt.feeds.PandasData(dataname=df)

if __name__ == '__main__':
    # 回测设置
    cerebro = bt.Cerebro()

    # 添加股票数据（2018-2023年数据，可调整时间范围）
    data = get_stock_data(ts_code='600519.SH', start_date='20180101', end_date='20231231')
    cerebro.adddata(data)
    # 添加策略
    cerebro.addstrategy(MACDBottomDeviationStrategy)
    # 初始资金
    INIT_CASH = 100000
    cerebro.broker.setcash(INIT_CASH)
    # 添加佣金
    cerebro.broker.addcommissioninfo(AShareCommission())
    # 运行回测
    print('初始资金：%.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('回测结束资金：%.2f' % cerebro.broker.getvalue())
    print(f'累计收益：{(cerebro.broker.getvalue() - INIT_CASH) / INIT_CASH * 100:.2f}%')
    # 绘制回测曲线
    # cerebro.plot()