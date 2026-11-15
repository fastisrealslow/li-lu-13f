# ChatGPT MCP（公开只读）

Cloudflare Pages Functions 路由：`https://li-lu-13f.pages.dev/mcp`。

现有 Cloudflare Pages 项目须关联本仓库 master，项目根目录包含 `functions/mcp.js`。Git 集成部署会自动编译 Functions。若此前使用拖放上传，需要改用支持 Functions 的 Git 或 Wrangler 部署。静态输出目录维持现有设置；`_routes.json` 仅让 `/mcp` 使用 Functions。

此接口读取 GitHub Pages 已校验发布的数据，短暂缓存上游响应；不依赖 Cloudflare 静态镜像与 GitHub Pages 同时更新。8 个工具均只读，不接收任意文件路径或网络地址，不使用模型 API、数据库、密钥或付费绑定。资料包含公开的个人持仓；不读取本地原始资料。

部署后在支持自定义 MCP 的 ChatGPT 账号中添加上述地址，认证选择 No authentication。用“列出投资者”“李录最新持仓”“李录 2016 Q4 持仓”验证工具实际被调用。账户管理员可能限制自定义 MCP。

验证命令：`node --test tests/mcp.cjs`。HTTP GET `/mcp` 返回 405 是正常行为；协议使用 POST initialize、tools/list、tools/call。JSON 响应采用无会话 Streamable HTTP，协议版本 2025-06-18。

免费额度来自 Pages Functions / Workers；只有 MCP 路由计入函数调用。运行额度不等同无限免费服务，应在 Cloudflare 面板观察用量及 CPU 限制。
