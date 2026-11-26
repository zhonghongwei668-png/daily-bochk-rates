#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""向钉钉发送「执行失败」告警（带失败 run 链接与重试说明）。

环境变量：
  DINGTALK_WEBHOOK  必填
  DINGTALK_SECRET   可选，加签密钥
  RUN_URL           可选，失败 run 的链接
"""
import os
import sys
import json
import time
import hmac
import base64
import hashlib
import urllib.parse
import urllib.request
import datetime


def signed_url(webhook, secret):
    if not secret:
        return webhook
    ts = str(round(time.time() * 1000))
    string_to_sign = f"{ts}\n{secret}"
    digest = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(digest))
    sep = "&" if "?" in webhook else "?"
    return f"{webhook}{sep}timestamp={ts}&sign={sign}"


def hkt_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))


def main():
    webhook = os.environ.get("DINGTALK_WEBHOOK", "").strip()
    secret = os.environ.get("DINGTALK_SECRET", "").strip()
    run_url = os.environ.get("RUN_URL", "").strip()
    if not webhook:
        print("缺少 DINGTALK_WEBHOOK", file=sys.stderr)
        sys.exit(2)

    hkt = hkt_now().strftime("%Y-%m-%d %H:%M")

    title = "每日汇率|汇率|牌价|执行失败|告警|BOCHK"
    text = "\n".join([
        "### ⚠️ 每日汇率执行失败",
        f"> 香港时间 {hkt} 本次执行未成功，截图未能推送到群",
        "> 将每小时自动重试，直至成功",
    ])
    if run_url:
        text += f"\n[查看失败日志]({run_url})"

    body = json.dumps({"msgtype": "markdown", "markdown": {"title": title, "text": text}})
    req = urllib.request.Request(
        signed_url(webhook, secret),
        data=body.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    print("DingTalk failure alert response:", result)
    if result.get("errcode") != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
