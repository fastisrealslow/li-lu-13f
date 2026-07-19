# Li Lu 13F Tracker

价值投资者 13F 持仓追踪 + 港美股分拆进展监控。

## 文件分类

### 源数据（手动维护，禁止 CI 覆盖）

| 文件 | 说明 |
|------|------|
| `data.json` | 李录 13F 持仓（含历史） |
| `pabrai_data.json` | 帕布莱 13F |
| `duan.json` | 段永平 13F |
| `tepper.json` | 大卫·泰珀 13F |
| `buffett.json` | 巴菲特 13F |
| `akre.json` | 查克·阿克雷 13F |
| `greenberg.json` | 格林伯格 13F |
| `webb.json` | David Webb 港股持仓 |
| `spinoff.json` | 港股分拆公告（手动 + CI 追加） |
| `spinoff_us.json` | 美股分拆公告（KNOWN_SPINOFFS 手动维护 + CI 追加） |

### 计算结果（CI 自动写入，可安全覆盖）

| 文件 | 来源脚本 |
|------|----------|
| `prices.json` / `prices_*.json` | `fetch_prices_all.py` |
| `hk_holdings.json` / `*_hk.json` | `fetch_webb_holdings.py` / `monitor_hk_disclosures.py` |
| `metadata_cache.json` | `enrich_metadata.py` |
| `alerts_hk_persons.json` | `monitor_hk_disclosures.py` |
| `run_status.json` | `update_status.py` |

### 脚本说明

| 脚本 | 功能 |
|------|------|
| `fetch_13f_all.py` | 从 SEC EDGAR 抓取所有投资者 13F（唯一入口） |
| `fetch_prices_all.py` | 抓取所有投资者股价 + 历史均价（唯一入口） |
| `fetch_spinoff.py` | 港股分拆公告抓取 |
| `fetch_spinoff_us.py` | 美股分拆公告抓取（含 `KNOWN_SPINOFFS` 手动库） |
| `spinoff_price_refresh.py` | 刷新分拆子公司股价 + 母公司公告以来表现 |
| `fetch_webb_holdings.py` | Webb 港股持仓抓取（仅周一） |
| `enrich_metadata.py` | 补充中文名 + 行业（SiliconFlow LLM） |
| `monitor_hk_disclosures.py` | 段永平港股权益披露监控 |
| `update_status.py` | CI 运行状态记录 |

## CI 调度

- **UTC 00:00**（HKT 08:00）— 港股开盘前更新
- **UTC 13:00**（HKT 21:00）— 美股盘中更新

## 常见维护

**新公司改名 / 新 ticker**：在 `fetch_13f_all.py` 的 `TICKER_MAP` 里添加映射。CI 日志会打印 `⚠️ 未识别 ticker` 告警。

**新增美股分拆**：在 `fetch_spinoff_us.py` 的 `KNOWN_SPINOFFS` 列表里手动添加条目，填写 `distributionDate`。

**新增美股分拆已知分拆日期**：在 `spinoff_price_refresh.py` 的 `US_KNOWN_DIST_DATES` 字典里补充。
