# 数据处理工具集

本目录包含VeighNa期货数据下载和查询工具。

## 📁 文件清单

### 数据下载脚本

| 文件 | 功能 | 数据源 | 费用 |
|-----|------|-------|------|
| `download_tqdata.py` | 天勤数据下载 | 天勤TQSDK | ✅ 完全免费 |
| `download_jqdata.py` | 聚宽数据下载 | 聚宽JQData | ⚠️ 有调用次数限制 |
| `download_tushare.py` | Tushare数据下载 | Tushare | ⚠️ 需要积分/付费 |

### 数据查询脚本

| 文件 | 功能 | 方式 |
|-----|------|------|
| `check_tqdata.py` | 数据库查询（VeighNa API） | Python对象 |
| `check_tqdata_sql.py` | 数据库查询（SQL） | SQL查询 |
| `sql_query_interactive.py` | 交互式SQL查询 | 命令行交互 |

### 数据库管理脚本

| 文件 | 功能 |
|-----|------|
| `clear_database.py` | 清理数据库（安全，有确认） |
| `quick_clear_db.py` | 快速清理数据库 |

### 文档

| 文件 | 说明 |
|-----|------|
| `期货品种列表.md` | 64个期货品种详细列表 |
| `README.md` | 本文档 |

---

## 🚀 快速开始

### 1. 下载数据（推荐：天勤免费）

```bash
# 编辑 download_tqdata.py，选择需要的品种
python download_tqdata.py
```

**特点：**
- ✅ 完全免费，无限制
- ✅ 数据质量高
- ✅ 支持64个期货品种
- ⏱️ 下载全部品种约需2-3小时

### 2. 查询数据

**方式A：使用VeighNa API（简单）**
```bash
python check_tqdata.py
```

**方式B：使用SQL查询（灵活）**
```bash
python check_tqdata_sql.py
```

**方式C：交互式SQL（自定义查询）**
```bash
python sql_query_interactive.py
# 然后输入SQL语句或选择快速查询
```

---

## 📖 详细使用指南

### 一、天勤数据下载

#### 步骤1：配置账号
在 `download_tqdata.py` 中设置：
```python
TQDATA_USERNAME = "你的手机号"
TQDATA_PASSWORD = "你的密码"
```

或设置环境变量：
```powershell
$env:TQDATA_USERNAME='13712345678'
$env:TQDATA_PASSWORD='your_password'
```

#### 步骤2：选择品种
```python
FUTURES_SYMBOLS = [
    'rb2505.SHFE',      # 螺纹钢
    'i2505.DCE',        # 铁矿石
    # 注释掉不需要的品种
]
```

完整品种列表请查看：[期货品种列表.md](./期货品种列表.md)

#### 步骤3：运行下载
```bash
python download_tqdata.py
```

---

### 二、数据查询

#### 方法1：Python API查询

**脚本：** `check_tqdata.py`

**功能：**
- 数据库概览（所有合约的数据统计）
- 特定合约查询（显示K线数据）

**示例：**
```python
# 查询rb2505最近365天的数据
check_specific_symbol('rb2505.SHFE', days=365)
```

#### 方法2：SQL查询

**脚本：** `check_tqdata_sql.py`

**功能：**
- SQL语法查询
- 自定义统计
- 数据导出CSV

**示例SQL：**
```sql
-- 查询每日最高价和最低价
SELECT 
    DATE(datetime) as date,
    MAX(high_price) as high,
    MIN(low_price) as low
FROM dbbardata
WHERE symbol='rb2505'
GROUP BY DATE(datetime)
ORDER BY date DESC;
```

#### 方法3：交互式SQL

**脚本：** `sql_query_interactive.py`

**特点：**
- 命令行交互
- 提供快速查询示例
- 实时执行SQL

**使用：**
```bash
python sql_query_interactive.py

SQL> 1                    # 输入数字快速查询
SQL> SELECT * FROM ...    # 或输入自定义SQL
SQL> help                 # 查看帮助
SQL> quit                 # 退出
```

---

### 三、数据库管理

#### 清空数据库

**推荐方式：** 使用 `clear_database.py`（安全）

```bash
python clear_database.py
```

**功能：**
- 查看所有表和数据量
- 多种清理选项
- 自动备份
- 二次确认

**快速方式：** 使用 `quick_clear_db.py`（危险）

```bash
python quick_clear_db.py
```

⚠️ 直接执行，无确认，谨慎使用！

---

## 🗄️ 数据库结构

VeighNa使用SQLite数据库，包含4张表：

| 表名 | 功能 | 说明 |
|-----|------|------|
| `dbbardata` | K线数据 | 存储OHLCV等主要数据 |
| `dbbaroverview` | K线概览 | 快速查询统计信息 |
| `dbtickdata` | Tick数据 | 逐笔成交数据（含五档盘口） |
| `dbtickoverview` | Tick概览 | Tick数据统计 |

**数据库位置：**
- Windows: `C:\Users\用户名\.vntrader\database.db`
- Linux/Mac: `~/.vntrader/database.db`

---

## 💡 常见问题

### Q1: 为什么数据查询不到？
**可能原因：**
1. 查询的时间范围不对（数据不是最近几天的）
2. 合约代码错误
3. 数据还没下载

**解决：**
- 先运行 `check_tqdata.py` 查看数据概览
- 调整查询天数：`check_specific_symbol('rb2505.SHFE', days=365)`

### Q2: 下载的数据来自哪里？
数据库**不区分数据源**，所有数据源下载的数据都存在同一个数据库中。

**建议：**
- 只使用一个数据源
- 下载前清空数据库避免混合

### Q3: 合约月份怎么选？
- **主力合约**：通常是成交量最大的合约
- **查询方式**：通过交易所网站或行情软件
- **示例**：2024年10月，螺纹钢主力是rb2505

### Q4: 下载失败怎么办？
**可能原因：**
1. 合约代码错误（检查格式）
2. 合约未上市或已退市（更换月份）
3. 网络问题（重试）
4. 账号权限（检查天勤账号）

### Q5: 如何加速下载？
1. 只下载需要的品种
2. 缩短时间范围（如只下载最近1年）
3. 使用更快的网络
4. 分批下载

---

## 🔧 高级用法

### 导出数据到CSV
```python
# 在 check_tqdata_sql.py 中
export_to_csv(db_path, 'rb2505', 'SHFE', 'rb2505_data.csv')
```

### 自定义统计查询
```python
# 查询价格波动最大的时间段
custom_sql = """
SELECT datetime, 
       (high_price - low_price) as range,
       volume
FROM dbbardata
WHERE symbol='rb2505'
ORDER BY range DESC
LIMIT 10;
"""
query_custom_sql(db_path, custom_sql)
```

### 批量下载历史数据
```python
# 修改时间范围
START_DATE = datetime(2015, 1, 1, tzinfo=DB_TZ)  # 从2015年开始
```

---

## 📚 参考资源

### 数据源文档
- [天勤TQSDK文档](https://doc.shinnytech.com/tqsdk/latest/)
- [聚宽JQData文档](https://www.joinquant.com/help/api/help)
- [Tushare文档](https://tushare.pro/document/2)

### VeighNa文档
- [VeighNa官网](https://www.vnpy.com/)
- [VeighNa文档](https://www.vnpy.com/docs/)

### 交易所官网
- [上期所](http://www.shfe.com.cn/)
- [大商所](http://www.dce.com.cn/)
- [郑商所](http://www.czce.com.cn/)
- [能源中心](http://www.ine.cn/)
- [中金所](http://www.cffex.com.cn/)

---

## 📝 版本历史

- **v1.0** - 初始版本，支持天勤数据下载
- **v1.1** - 添加SQL查询工具
- **v1.2** - 添加64个期货品种（覆盖5大交易所）
- **v1.3** - 添加交互式查询和数据库管理工具

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可

MIT License

