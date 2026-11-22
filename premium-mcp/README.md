# 投资研究库 · 批量对比试用

这个独立的 Cloudflare Worker 提供两个只读 MCP 工具：

- `compare_investor_changes` 按一只美股横向对比所有已跟踪的 13F 投资人。附报告期、原始 SEC 申报链接及适用的申报范围。传 `format: "csv"` 导出。
- `export_watchlist_report` 按最多 5 位投资人、12 只股票导出港美股简报。CSV 有中英双语列名，分别列出 SEC 持仓变化、港交所权益原表、分拆公告和各来源的覆盖状态。每页最多 50 条披露；需要继续时按 `structuredContent.nextOffset` 查询。导出只包含有日期和原文的公开监管披露。

CSV 均为 UTF-8 文本，可保存为 `.csv`。账户、支付和自动通知不由此 Worker 保存或发送。

现有公开网站和 `/mcp` 使用原来的发布流程。试用接口读取同一份发布清单和季度比较数据，随公开数据更新。无匹配、没有可比申报、上游不可用都有独立状态。网页有限制的投资人仍按该限制比较。一位投资人的期权、普通股和本金类申报分别列示。

## 试用部署

1. 将此目录作为独立 Worker 项目，以 Cloudflare Secrets 配置 `PREMIUM_MCP_TOKEN`。使用随机生成的至少 32 字符令牌，例如 `openssl rand -hex 32`。令牌建议仅配置在试用调用方或订阅网关的服务器上。
2. 部署后向 Worker 的 `/mcp` 发送 MCP 请求，带 `Authorization: Bearer <token>`。对同一地址用无令牌和错误令牌测试，均应得到 HTTP 401。用正确令牌测试工具发现，以及同一股票的 JSON 和 CSV 结果。
3. 接 MCPize 时，先用测试环境确认网关可以在向原始 Worker 转发时附加服务器保管的固定授权头，并验证未订阅、已订阅、取消后到期三种状态。如果网关无法提供这种转发方式，需要改用该平台的受控托管或单独接入订阅权益校验，再对用户开放。不同地区的收款资质以平台审核为准。

试用令牌只校验调用方身份。订阅、退款、到期和按用户计费由支付或订阅系统处理。收费前用平台测试账号运行：

```sh
python3 premium-mcp/check_release.py --origin 'https://原始付费地址/mcp' --gateway 'https://收费网关地址/mcp'
```

在运行环境中分别设置 `MCPIZE_ACTIVE_TEST_TOKEN` 和 `MCPIZE_INACTIVE_TEST_TOKEN`，使用有效订阅和已到期（或无付费权益）的真实测试凭证。脚本只报告四项验收状态，缺少任一凭证会标为 SKIP 并以失败退出。可再用后台账单确认一次受控调用的额度或计费记录。收费前同时检查 Cloudflare CPU 和请求配额。

本地测试可在仓库根目录运行 `node --test tests/premium_mcp.cjs`。
