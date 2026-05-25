# 喜马拉雅资本 · 李录 13F 持仓追踪

[![Update 13F Data](https://github.com/guoziyuan/li-lu-13f/actions/workflows/update.yml/badge.svg)](https://github.com/guoziyuan/li-lu-13f/actions/workflows/update.yml)

自动追踪李录（Li Lu）旗下喜马拉雅资本（Himalaya Capital Management）每季度向 SEC 提交的 13F 持仓报告。

👉 **[在线查看](https://guoziyuan.github.io/li-lu-13f/)**

## 功能

- 📊 当前持仓明细（代码、市值、占比）
- 📈 季度环比变化（股数 + 市值双向对比）
- 📜 历史趋势图（自 2020Q4）
- 🔍 自动生成关键动态分析
- 🔄 支持一键从 SEC 拉取实时数据（海外用户）
- 🤖 GitHub Actions 每周自动更新数据

## 工作原理

```
SEC EDGAR ──→ GitHub Actions (每周) ──→ data.json ──→ GitHub Pages
                  │
                  └── fetch_13f.py  自动发现最新 13F
                      解析 INFOTABLE XML
                      更新 data.json + 自动 commit
```

## 本地运行

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `index.html` | 主页面 |
| `app.js` | 渲染逻辑 + 实时拉取 |
| `data.json` | 持仓数据（由 GitHub Actions 自动更新） |
| `fetch_13f.py` | Python 脚本，从 SEC EDGAR 拉取并解析 13F |
| `.github/workflows/update.yml` | 每周自动运行的 Actions 工作流 |

## 部署到 GitHub Pages

1. Fork 本仓库
2. Settings → Pages → Source: `main` branch, root (`/`)
3. 等待几分钟，访问 `https://你的用户名.github.io/li-lu-13f/`
4. 修改 `.github/workflows/update.yml` 中 GitHub 链接

GitHub Actions 会自动启用，每周一自动更新数据。