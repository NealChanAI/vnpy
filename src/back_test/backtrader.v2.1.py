import backtrader as bt
import numpy as np

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
        self.macd_hist = bt.indicators.MACDHisto(
            self.data,
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig
        ).histo

        # 辅助指标：20日均线（趋势过滤）、成交量均值
        self.ma20 = bt.indicators.SimpleMovingAverage(self.data, period=20)
        self.vol_mean = bt.indicators.SimpleMovingAverage(self.data.volume, period=5)

        # 状态变量：记录底背离、上零轴状态
        self.bottom_deviation = False
        self.cross_up_zero = False

    def next(self):
        # 1. 判断底背离（股价新低，DIF未新低，且股价跌幅达标）
        if (self.data.low[0] < self.data.low[-1] < self.data.low[-2]  # 股价创2期新低
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
            self.buy(size=1)  # 买入（可调整仓位）

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
            top_dev = (self.data.high[0] > self.data.high[-1] > self.data.high[-2]
                       and self.dif[0] < self.dif[-1] < self.dif[-2])
            # DIF下穿零轴
            cross_down_zero = self.dif[-1] > 0 and self.dif[0] < 0
            if top_dev or cross_down_zero:
                self.sell(size=self.position.size)
                self.bottom_deviation = False
                self.cross_up_zero = False

if __name__ == '__main__':
    # 回测设置
    cerebro = bt.Cerebro()
    # 加载数据（通过 yfinance 获取后用 PandasData 喂给 Backtrader，规避 Yahoo 解码问题）
    try:
        import yfinance as yf
        import pandas as pd  # noqa: F401 - 仅为确保依赖存在

        df = yf.download(
            '600036.SS',
            start='2018-01-01',
            end='2023-12-31',
            auto_adjust=True,
            progress=False
        )
        if df is None or df.empty:
            raise ValueError('yfinance 返回空数据')

        # 处理可能出现的多级列（单票也可能返回 MultiIndex 列）
        import pandas as _pd  # noqa
        if isinstance(df.columns, _pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns.values]

        # 显式映射列名，确保兼容 PandasData 预期字段
        data = bt.feeds.PandasData(
            dataname=df,
            open='Open', high='High', low='Low', close='Close', volume='Volume', openinterest=-1
        )
        cerebro.adddata(data)
    except Exception as e:
        raise RuntimeError(f"下载数据失败，请改用本地 CSV（GenericCSVData）或你现有的数据接口。错误: {e}")
    # 添加策略
    cerebro.addstrategy(MACDBottomDeviationStrategy)
    # 初始资金
    cerebro.broker.setcash(100000.0)
    # 手续费设置（0.1%佣金，0.1%印花税）
    # cerebro.broker.setcommission(commission=0.001, stamp_duty=0.001)
    cerebro.broker.addcommissioninfo(AShareCommission())
    # 运行回测
    print('初始资金：%.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('回测结束资金：%.2f' % cerebro.broker.getvalue())
    # 绘制回测曲线
    cerebro.plot()