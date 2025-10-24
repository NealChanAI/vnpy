# 聚宽JQData数据下载指南

## 📋 前置准备

### 1. 安装JQData SDK

```bash
pip install jqdatasdk
```

### 2. 验证账号

运行测试脚本：
```bash
python src/data_process/jqdata_test
```

---

## 🚀 快速开始

### 方法1：使用现成脚本（推荐）

```bash
python src/data_process/download_jqdata.py
```

### 方法2：自定义下载

编辑 `download_jqdata.py` 配置区：

```python
# 1. 修改账号（已配置好）
JQDATA_USERNAME = '你的手机号'
JQDATA_PASSWORD = '你的密码'

# 2. 修改要下载的合约
FUTURES_SYMBOLS = [
    'RB2505.XSGE',   # 螺纹钢
    'HC2505.XSGE',   # 热卷
    # 添加更多...
]

# 3. 修改时间范围
START_DATE = '2024-01-01'
END_DATE = '2024-12-31'

# 4. 修改数据粒度
FREQUENCY = '1m'  # 1分钟
```

---

## 📊 聚宽合约代码格式

### 期货合约代码规则

```
格式：品种代码 + 年月 + . + 交易所代码

示例：
- RB2505.XSGE   # 螺纹钢2025年5月，上期所
- I2505.XDCE    # 铁矿石2025年5月，大商所
- CF2505.XZCE   # 棉花2025年5月，郑商所
- IF2505.CCFX   # 沪深300股指2025年5月，中金所
```

### 交易所代码

| 聚宽代码 | 交易所 | VeighNa代码 |
|---------|--------|------------|
| XSGE | 上海期货交易所 | SHFE |
| XDCE | 大连商品交易所 | DCE |
| XZCE | 郑州商品交易所 | CZCE |
| CCFX | 中国金融期货交易所 | CFFEX |
| XINE | 上海国际能源交易中心 | INE |

---

## 🎯 如何查找合约代码

### 方法1：使用聚宽API

```python
from jqdatasdk import *
auth('手机号', '密码')

# 获取所有期货合约
futures = get_all_securities(types=['futures'])
print(futures)

# 筛选螺纹钢
rb = futures[futures.index.str.startswith('RB')]
print(rb)
```

### 方法2：访问聚宽文档

访问：[聚宽期货数据文档](https://www.joinquant.com/help/api/doc?name=JQDatadoc&id=10261)

---

## ⚙️ 数据粒度选项

```python
'1m'   # 1分钟（推荐用于日内策略）
'5m'   # 5分钟
'15m'  # 15分钟
'30m'  # 30分钟
'60m'  # 60分钟（1小时）
'1d'   # 日线
```

---

## 📈 下载后验证数据

```python
from vnpy.trader.database import get_database
from vnpy.trader.constant import Exchange, Interval
from datetime import datetime

database = get_database()

# 查询数据
bars = database.load_bar_data(
    symbol='rb2505',
    exchange=Exchange.SHFE,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

print(f"数据量: {len(bars)}")
print(f"第一条: {bars[0]}")
print(f"最后一条: {bars[-1]}")
```

---

## ⚠️ 注意事项

### 1. 试用账号限制

- **每日调用次数有限**（通常500-1000次）
- 每次调用返回数据量有限制
- 超限后需等待第二天

### 2. 数据时间范围

- 试用账号可能限制历史数据深度
- 建议分批下载，避免超时

### 3. 费用说明

- 试用期免费
- 正式版约 **2000-3000元/年**
- 官网：https://www.joinquant.com

---

## 🔧 常见问题

### Q1: 提示"认证失败"？

检查账号密码是否正确，确认试用已开通。

### Q2: 提示"调用次数不足"？

等待第二天重置，或购买正式版。

### Q3: 下载的数据是否准确？

聚宽数据质量较高，适合回测使用。

### Q4: 如何下载主力连续合约？

聚宽用数字888表示主力，例如：
```python
'RB888.XSGE'   # 螺纹钢主力连续
'I888.XDCE'    # 铁矿石主力连续
```

---

## 📚 相关资源

- [聚宽官网](https://www.joinquant.com)
- [聚宽API文档](https://www.joinquant.com/help/api/doc?name=JQDatadoc)
- [VeighNa文档](https://www.vnpy.com/docs/)

---

## 💡 推荐工作流程

```
1. 先用测试脚本验证账号 ✅
   → python src/data_process/jqdata_test

2. 修改下载脚本配置 ✅
   → 编辑 download_jqdata.py

3. 小范围测试下载 ✅
   → 先下载1-2个合约，1个月数据

4. 验证数据正确性 ✅
   → 检查数据库中的数据

5. 批量下载全部数据 ✅
   → 运行完整下载脚本
```

