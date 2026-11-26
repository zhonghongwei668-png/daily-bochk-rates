#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成合成页 composite.html：仿浏览器 chrome（标签页+地址栏）+ 真实页面截图 + 底部红色时间条。

输入：WORKDIR/page_raw.png（Chrome 无头直截 BOCHK 真实页面的产物）
输出：WORKDIR/composite.html 与 WORKDIR/shot_time.txt（香港时间，精确到分）
"""
import io
import os
import datetime


def hkt_now():
    """香港时间（UTC+8），避免依赖运行机系统时区（GitHub runner 为 UTC）。"""
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))


def main():
    workdir = os.environ.get("WORKDIR", ".")
    shot_time = hkt_now().strftime("%Y-%m-%d %H:%M")
    # 页面原始尺寸
    W, H = 1400, 1560

    html = u"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #dde3ea; font-family: "Noto Sans CJK TC","Noto Sans TC","PingFang TC","Microsoft JhengHei","Segoe UI",sans-serif; width: {W}px; }}
  .chrome {{ background: #dee1e6; padding-top: 6px; }}
  .tabs {{ display: flex; align-items: flex-end; padding: 0 10px; height: 34px; }}
  .tab {{
    background: #fff; border-radius: 8px 8px 0 0; padding: 7px 16px; font-size: 12.5px;
    color: #333; display: flex; align-items: center; gap: 7px; width: 300px;
    box-shadow: 0 -1px 3px rgba(0,0,0,.08);
  }}
  .favicon {{ width: 14px; height: 14px; border-radius: 3px; background: #b5121b; color:#fff;
    font-size: 9px; display:flex; align-items:center; justify-content:center; }}
  .winbtns {{ margin-left: auto; display: flex; gap: 12px; color: #555; font-size: 12px; padding-bottom: 8px; }}
  .navbar {{ background: #fff; padding: 7px 10px; display: flex; align-items: center; gap: 9px; }}
  .navbtns {{ display: flex; gap: 6px; color: #5f6368; font-size: 15px; }}
  .navbtns span {{ width: 26px; text-align: center; }}
  .urlbar {{
    flex: 1; background: #f1f3f4; border-radius: 16px; padding: 7px 14px; font-size: 13px;
    color: #202124; display: flex; align-items: center; gap: 8px; font-family: Consolas, monospace;
  }}
  .lock {{ color: #5bb974; font-size: 12px; }}
  .ext {{ color: #5f6368; font-size: 14px; }}
  .page {{ line-height: 0; }}
  .page img {{ width: {W}px; display: block; }}
  .stamp {{
    background: #b5121b; color: #fff; padding: 11px 26px 11px 34px; font-size: 17px; font-weight: 700;
    display: flex; justify-content: space-between; align-items: center; letter-spacing: .5px;
  }}
  .stamp .t {{ font-family: Consolas, monospace; font-size: 18px; }}
  .stamp small {{ font-weight: 400; font-size: 12.5px; opacity: .85; }}
</style></head>
<body>
  <div class="chrome">
    <div class="tabs">
      <div class="tab"><span class="favicon">中</span>各類貨幣兌美元電匯牌價 | 投資 | 中國銀行(香港)有限公司</div>
      <div class="winbtns"><span>&#8211;</span><span>&#9633;</span><span>&#10005;</span></div>
    </div>
    <div class="navbar">
      <div class="navbtns"><span>&#8592;</span><span>&#8594;</span><span>&#8635;</span><span>&#8962;</span></div>
      <div class="urlbar"><span class="lock">&#128274;</span>https://www.bochk.com/tc/investment/rates/usdrates.html</div>
      <div class="ext">&#9749;</div>
    </div>
  </div>
  <div class="page"><img src="page_raw.png"></div>
  <div class="stamp">
    <span>截圖時間（香港時間）：<span class="t">{T}</span></span>
    <span>資料來源：中國銀行（香港）官網實時頁面 <small>BOCHK USD Telegraphic Transfer Rates</small></span>
  </div>
</body></html>
""".format(W=W, T=shot_time)

    with io.open(os.path.join(workdir, "composite.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with io.open(os.path.join(workdir, "shot_time.txt"), "w", encoding="utf-8") as f:
        f.write(shot_time)
    print("shot_time:", shot_time)


if __name__ == "__main__":
    main()
