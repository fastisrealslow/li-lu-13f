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
| `resolve_unmapped_tickers.py` | 自动解析 `?` 前缀未识别 ticker（CUSIP → 真实 ticker，OpenFIGI API） |
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

**发现新的未识别 ticker/未翻译中文名**（见下方 2026-07-26 第二条记录）：不需要手工处理。CI 会在每次运行时自动调用 `resolve_unmapped_tickers.py`（CUSIP 解析）+ `enrich_metadata.py`（LLM 翻译）。若某个 ticker/公司名长期保持未解析，大概率是已退市/被并购公司，OpenFIGI 和 SEC 都查不到，属预期行为，不需要人工干预。

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

### 2026-07-26（第二条）：CUSIP 自动解析 ticker + LLM 中文名翻译补全

**背景**：用户反馈“很多股票名没有翻译成中文”。诊断发现这其实是两个独立问题叠加：

1. **Ticker 解析层**：`fetch_13f_all.py` 的 `resolve_ticker()` 只能靠手工维护的 `TICKER_MAP`/`TICKER_CLASS_MAP`/`CUSIP_TICKER_MAP` 查表，查不到就 fallback 成 `?公司原名`存入 JSON。`enrich_metadata.py` 又会主动跳过所有 `?` 前缀 ticker（因为模糊的公司名字符串无法可靠地匹配到真实公司，避免引入错误映射）。全量扫描发现 13,961 条历史持仓记录中 59.2% 缺 cnName，其中 99.2% 跟这个 `?` 前缀问题相关。
2. **中文翻译层**（更根本的问题，规模更大）：即使 ticker 解析正确，`enrich_metadata.py` 的 `fetch_yf_info()` 只有命中手写白名单 `MANUAL_CN_NAME`（仅 ~130 个 ticker）才会得到真正中文名，否则就直接用 yfinance 的 `longName`（英文）当作 cnName 存入。实测全量数据发现 8,182 条真实 ticker 记录中，实际是英文 fallback 的有 3,103 条，**比真正翻译成中文的 2,892 条还多**——这才是用户感觉“很多没翻译”的真正根源。

**修复方案**（严格按用户要求——全自动化、优先确定性规则、不确定的不乱填）：

1. **新增 `resolve_unmapped_tickers.py`**：扫描所有投资者数据文件里 `?` 前缀记录的 CUSIP，调用 [OpenFIGI `/mapping` API](https://www.openfigi.com/api/documentation)（免费、无需 API key）批量解析。验证过的选择规则：优先取 `exchCode=='US' 且 securityType=='Common Stock'` 且候选 ticker 唯一，否则退而求其次取任意 US 交易所记录但仍要求唯一，出现歧义（多个不同 ticker）则不采纳。全量跑一次结果：541 个唯一 CUSIP 中 201 个解析成功（37%），回填 2,118 条历史记录的 ticker。解析结果持久化写入独立的 `resolved_cusip_map.json`（不直接改手写 `CUSIP_TICKER_MAP` 字面量，关注点分离，方便 CI 自动提交），`fetch_13f_all.py` 启动时自动合并进 `CUSIP_TICKER_MAP`。剩余 340 个 CUSIP（约 67%）经根因排查均为已退市/被并购/私有化公司（如二十一世纪福斯、VMware、Sears、CBS 等），OpenFIGI 和 SEC 官方 ticker 表都只追踪当前活跃登记人，无法通过规则解析，不强行猜测。
2. **`enrich_metadata.py` 新增 `translate_names_to_chinese()`**：在每次 yfinance 回填完成后，扫描缓存里所有 `cnName` 不含中文字符的条目，批量交给 SiliconFlow LLM 翻译。**关键安全设计**：要求 LLM 返回 `{"编号": "译文"}` 的 JSON 对象而不是纯数组，按编号回填而不是按数组位置 `zip`——即使 LLM 漏答/乱序部分编号，已经答对的也不会因位置错位而被错误归属到另一个公司。本地用 mock 单元测试验证了正常/漏答/乱序/异常格式 4 种场景都不会产生错误映射。翻译结果同时回写 `metadata_cache.json` 缓存和所有已落盘的数据文件。
3. **CI 集成**：`.github/workflows/update.yml` 新增 `Resolve unmapped tickers via CUSIP` 步骤，放在 `Enrich metadata` 之前执行（先解析 ticker，再让翻译步骤去查真实 ticker 的信息）。两个步骤都是幂等的（已解析过的 CUSIP/已翻译过的名字不会重复请求），每次 CI 运行都会自动处理新出现的未解析记录，无需人工重跑。
4. **删除死代码**：确认 `fetch_13f.py`/`fetch_13f_backup.py`/`fetch_13f_akre_greenberg.py`/`fetch_13f_buffett.py`/`fetch_13f_duan.py`/`fetch_13f_pabrai.py`/`fetch_13f_tepper.py`/`fetch_pabrai_prices.py` 8 个旧脚本均已被 `fetch_13f_all.py` 取代且不被任何地方引用，删除。

**经验教训**：
- 字段名叫 `cnName` 不代表里面真的是中文—— fallback 逻辑可能对 API 返回值原样不动地当成目标语言写入。评估这类字段的真实覆盖率时，要检查字符内容本身（如正则匹配中文字符），不能只看字段是否为空。
- 批量 LLM 翻译/映射任务中，用数组位置 `zip` 对应输入输出存在隐藏风险：一旦 LLM 漏答或乱序，会静默产生错位映射而不报错。要求 LLM 返回带显式编号/key 的结构化格式，按 key 回填而不是按位置回填。
- 免费 API 的限流参数要以官方文档为准，不能凭经验猜测（OpenFIGI 无 key 时实际是每请求最多 10 个 job，不是直觉以为的 25）。
- 能解决的部分用确定性规则自动化解决，解决不了的部分（数据源本身不存在权威映射）应该诚实保留原状，而不是用 LLM 猜测填充——自动化的边界应该是“能确认的都自动确认，不能确认的诚实报告无法自动化”。

### 2026-07-26（第三条）：发现并修复 history.quarters 乱序导致的图表/AI摘要错误

**背景**：本次回归验证截图时意外发现格伦伯格“历史趋势”图表 X 轴年份乱序（2025 后突然出现 2013）。根因排查确认与本次 CUSIP/翻译修复无关（`app.js` 本次唯一改动只涉及状态面板标签），是早已存在的数据序问题，因为认为“图表能看就行”而顺便一并修复。

**根因**：`fetch_13f_all.py` 的 `process_full()`/`process_incremental()` 对 `data["history"]["quarters"]`/`["values"]` 始终用 `.append()` 追加写入，从不排序。当某个投资者先抓近期持仓、后来又补抓了更早的历史 filing（如格伦伯格/Akre 这样 2013 年就开始披露但初次只抓了 2016 年以后的情况），新补抓的早期季度会被追加到数组末尾而不是插入到正确时间位置，导致 `quarters`/`values` 这两个平行数组变成乱序。因为前端 `renderHistoryChart()`、`generateHistoryInsight()`、`renderHistoryMobile()` 都直接按数组原始顺序读取（假设它已经是时间序），乱序不仅让 X 轴标签乱，连折线走势本身都是错的（连接了乱序的数据点），且 AI 摘要文案会彻底错误（修复前实测会说“从 2026 Q1 到 2016 Q1”这种时间倒流的话术）。

**修复**：
1. `fetch_13f_all.py` 新增 `_sort_history_in_place()`，在 `save_data()` 写盘前自动按季度时间顺序重排 `quarters`/`values`（`holdings` 是以季度字符串为 key 的字典，不受数组顺序影响，无需调整）。已正确的数据无副作用（直接 `return`）。
2. `app.js` 的 `renderHistoryChart()` 同步加了一层前端防御性重排（不依赖后端数据必然已排序，即使旧数据文件没重跑抓取也能正确显示）。
3. 写一次性脚本对现有数据文件回填修复，发现并修正了两个受影响文件：`greenberg.json`、`akre.json`（其他投资者文件本来就是时间序，无需改动）。修复后验证：重跑脚本确认幂等（第二次 0 个文件需改动），`holdings` 字典 key 集合与排序后 `quarters` 集合一致。
4. 视觉验证：修复后格伦伯格历史趋势图表 X 轴从 2013 到 2026 按序排列，折线走势变得连贯合理（之前乱序时折线有非理性锯齿状跳变），AI 摘要文案变为正确的“从 2013 Q2 到 2026 Q1，规模增长 87%”。

**经验教训**：
- 对既有回归验证时发现的“无关”问题不要直接忽略——先确认是否是本次改动引入的回归（看 `git diff` 涉及文件），如果确认不是回归而是早已存在的 bug，应该向用户报告并征求处理意见，而不是默许推迟。
- 分批/增量抓取的历史数据，只用 `.append()` 而不排序，在抓取顺序与时间顺序不一致时（先近期后回填早期）会静默产生乱序数组，不会报错但下游消费方会静默得到错误结果。写盘前显式排序比依赖抓取顺序更稳健。
- 同一个根因同时在后端（数据写盘）和前端（渲染读取）修复两道防线更稳健——后端修复让数据文件本身规范，前端修复让已经存在的旧数据文件（还没重跑抓取脚本）也能正确显示。
