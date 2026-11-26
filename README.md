# 每日汇率（中银香港美元电汇牌价）

每天香港时间 08:30 自动抓取中国银行（香港）「各類貨幣兌美元電匯牌價」，生成真实浏览器窗口截图并推送到钉钉群。

## 架构

```
GitHub Actions (cron 30 0 * * * = 香港 08:30)
  ├─ fetch_rates.py       curl 抓取 BOCHK 静态接口，解析更新时间/货币数（校验）
  ├─ Chrome headless      直截真实页面 page_raw.png (1400×1560)
  ├─ composite.py         合成浏览器 chrome + 红色时间条 → composite.html
  ├─ Chrome headless      截 composite.html → bochk_usd_full.png (1400×1690)
  ├─ gh-pages 部署        图片发布到 github.io（稳定免费、永久可回看）
  └─ send_dingtalk.py     钉钉 markdown 内嵌图片（加签，群内可点击放大）
```

- **数据源**：`https://www.bochk.com/whk/rates/exchangeRatesUSD/exchangeRatesUSD-input.action?lang=hk`（静态 HTML 直出，无登录/API key）
- **图片托管**：GitHub Pages（`https://<owner>.github.io/<repo>/shots/YYYY-MM-DD.png`），非 pixhost 免费图床，长期稳定
- **钉钉**：`msgtype=markdown` 内嵌公网图片 URL（可放大），加签模式，标题带简体关键词通过过滤

## Secrets（仓库 Settings → Secrets and variables → Actions）

| 名称 | 说明 |
|---|---|
| `DINGTALK_WEBHOOK` | 机器人 webhook（`https://oapi.dingtalk.com/robot/send?access_token=...`） |
| `DINGTALK_SECRET` | 加签密钥（`SEC` 开头） |

## 本地运行

```bash
export WORKDIR=$(mktemp -d)
export DINGTALK_WEBHOOK=... DINGTALK_SECRET=...
python3 scripts/fetch_rates.py
"$(command -v google-chrome)" --headless=new --no-sandbox \
  --window-size=1400,1560 --virtual-time-budget=20000 --hide-scrollbars \
  --screenshot="$WORKDIR/page_raw.png" \
  "https://www.bochk.com/tc/investment/rates/usdrates.html"
python3 scripts/composite.py
# 截 composite → bochk_usd_full.png，再设置 IMAGE_URL 后 send_dingtalk.py
```

## 手动触发

仓库 Actions 页 → "Daily BOCHK USD rates shot" → Run workflow（或 `gh workflow run`）。
