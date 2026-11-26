#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 BOCHK 美元电汇牌价数据接口并解析更新时间与货币数量。

输出：
  WORKDIR/rates.html        接口原始 HTML（调试用）
  WORKDIR/rates_meta.txt    "update_time\tcount" 两行（供后续步骤读取）
校验：必须有更新时间且货币数量 ≥ 10，否则退出码 1（让 workflow 显式失败）。
"""
import io
import os
import re
import sys
import urllib.request

RATES_URL = (
    "https://www.bochk.com/whk/rates/exchangeRatesUSD/"
    "exchangeRatesUSD-input.action?lang=hk"
)


def main():
    workdir = os.environ.get("WORKDIR", ".")
    req = urllib.request.Request(RATES_URL, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Accept-Language": "zh-HK,zh;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")

    with io.open(os.path.join(workdir, "rates.html"), "w", encoding="utf-8") as f:
        f.write(raw)

    m = re.search(r"資料更新於香港時間：\s*([0-9/]+\s+[0-9:]+)", raw)
    update_time = m.group(1).strip() if m else ""

    # 数据行：<td>货币</td><td>卖</td><td>买</td>，货币名以「美元/」「X/美元」为主
    rows = re.findall(
        r"<tr>\s*<td>([^<]+)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>",
        raw, re.S,
    )
    count = 0
    for name, a, b in rows:
        va = re.sub(r"<[^>]+>", "", a)
        vb = re.sub(r"<[^>]+>", "", b)
        va = re.sub(r"\s+", "", va)
        vb = re.sub(r"\s+", "", vb)
        if va and vb:
            count += 1

    with io.open(os.path.join(workdir, "rates_meta.txt"), "w", encoding="utf-8") as f:
        f.write(update_time + "\n")
        f.write(str(count) + "\n")

    print("update_time:", update_time, "| currency_count:", count)
    if not update_time:
        print("ERROR: 未解析到「資料更新於香港時間」", file=sys.stderr)
        sys.exit(1)
    if count < 10:
        print("ERROR: 货币数量异常（<10）", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
