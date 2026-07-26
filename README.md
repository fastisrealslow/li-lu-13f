# Li Lu 13F Tracker

价值投资者 13F 持仓追踪 + 港美股分拆进展监控。

## 投资者配置（单一数据源）

**`investors.json` 是全部 13 位投资者的唯一配置源**（2026-07-26 重构后）。新增/修改投资者只需编辑这一个文件，无需再碰 `app.js`、`fetch_13f_all.py`、`fetch_prices_all.py`、`enrich_metadata.py` 里的任何硬编码列表。

每条投资者配置包含：`id`、`name`/`nameEn`、`cik`（无 13F 义务的投资者为 `null`，如 webb）、`manager`、`people`、`dataFile`、`pricesFile`、`hkFile`（无港股持仓为 `null`）、`market`（US/HK）、`source13F`（是否走 13F 抓取流程）、`consolidate`（是否合并多基金持仓，仅 buffett 为 true）、`inValueScreen`（是否进入价值筛选候选池，仅 webb 为 false）。

详情页面的文字介绍（“关于XX”、投资理念等 prose 内容）仍在 `app.js` 的 `updateInvestorContent()` 里手动维护——这是设计上的取舍，不是遗漏。

## 文件分类

### 源数据（手动维护，禁止 CI 覆盖）

| 文件 | 说明 |
|------|------|
| `investors.json` | **投资者配置单一数据源**，见上 |
| `data.json` | 李录 13F 持仓（含历史） |
| `pabrai_data.json` | 帕布莱 13F |
| `duan.json` | 段永平 13F |
| `tepper.json` | 大卫·泰珀 13F |
| `buffett.json` | 巴菲特 13F |
| `akre.json` | 查克·阿克雷 13F |
| `greenberg.json` | 格林伯格 13F |
| `klarman.json` / `ackman.json` / `abrams.json` / `berkowitz.json` / `hawkins.json` | 塞斯·克拉曼 / 比尔·阿克曼 / 大卫·艾布拉姆斯 / 布鲁斯·伯科威茨 / 梅森·霍金斯 13F（2026-07-26 新增） |
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

**新增投资者**（2026-07-26 重构后）：只需在 `investors.json` 里新加一条配置。若需要页面上的文字介绍，再在 `app.js` 的 `updateInvestorContent()` 里补充 prose。不要再在任何地方添加硬编码的投资者列表。

## 架构决策与 bug 修复记录

### 2026-07-26：investors.json 单一数据源重构

**背景**：新增克拉曼/阿克曼/艾布拉姆斯/伯科威茨/霍金斯 5 位投资者时，因为投资者列表同时硬编码在 4 个文件里（`app.js`、`fetch_13f_all.py`、`fetch_prices_all.py`、`enrich_metadata.py`），每个地方都很容易漏改。因此重构为以 `investors.json` 为单一数据源，四个文件均改为动态读取。

**过程中发现并修复的3个隐藏 bug**（都与硬编码重复/遗漏相关，说明多处硬编码列表本质上无法保证一致性）：

1. **`fetch_prices_all.py` 首次抓取新投资者时 `UnboundLocalError` 崩溃**——导致5位新投资者的 `prices_*.json` 从未生成。修复：确保异常变量（`ex`）在使用前初始化。
2. **`app.js` 的 `loadHKHoldings()` 对无港股持仓的投资者错误 fallback 到李录的港股数据**——根因是 JS 允许同名 `function` 声明并静静覆盖前一个，当时 `app.js` 里存在两个 `renderHKHoldings()` 定义，前面修对的那个其实是死代码，实际生效的是后面未修对的那个。修复：删除重复定义，在真正生效的函数里改为从 `investors.json` 的 `hkFile` 字段读取，`null` 时显示空状态。
3. **`enrich_metadata.py` 的 `data_files`/`FILES` 硬编码列表未包含新投资者**——导致中文名/行业分类不会为新投资者自动补全。修复时附带发现并补上了之前也被遗漏的 `webb_hk.json`。

**另外发现两个错误的硬编码 CIK 值**（不是拼写错误而是指向了完全无关的公司）：`app.js` 的 `INVESTOR_CIK` 字典里 pabrai 显示 `0001474216`（实为 Franchise Portfolio 2, Inc.），akre 显示 `0001499406`（实为 KLP 2010 ANP Mirror Trust B）。均已按 [SEC EDGAR](https://data.sec.gov/submissions/CIK0001549575.json) 校验改为正确值（pabrai=`1549575`，akre=`1112520`），并不再单独硬编码，改为从 `investors.json` 派生。

**经验教训**：
- 若发现“投资者 X 被遗漏在某硬编码列表里”，要 grep 所有类似/同构列表，不能假设只有一处。
- JS 里同名 `function` 声明会被静静覆盖，要 grep 重复函数名，不能假设只存在一份定义。
- 合并硬编码配置时，要对比权威数据源（如 SEC EDGAR）逐个校验，不能只看内部一致性——内部一致不代表数值本身正确。
- CI `✓` 可能误导（容错处理会让失败步骤仍显示成功），要用 `gh run view --log` 看实际日志，不能只看 step 级状态图标。
