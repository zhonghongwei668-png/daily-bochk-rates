#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""向钉钉群发送 markdown 消息（内嵌公网图片 URL，群内可点击放大）。

环境变量：
  DINGTALK_WEBHOOK  必填，机器人 webhook（含 access_token）
  DINGTALK_SECRET   可选，加签密钥（SEC 开头）；为空则不加签
  IMAGE_URL         必填，图片公网直链
  UPDATE_TIME       可选，资料更新时间（香港时间）
  SHOT_TIME         可选，截图时间（香港时间）；缺省读 WORKDIR/shot_time.txt
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


def signed_url(webhook, secret):
    if not secret:
        return webhook
    ts = str(round(time.time() * 1000))
    string_to_sign = f"{ts}\n{secret}"
    digest = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(digest))
    sep = "&" if "?" in webhook else "?"
    return f"{webhook}{sep}timestamp={ts}&sign={sign}"


def main():
    webhook = os.environ.get("DINGTALK_WEBHOOK", "").strip()
    secret = os.environ.get("DINGTALK_SECRET", "").strip()
    image_url = os.environ.get("IMAGE_URL", "").strip()
    if not webhook or not image_url:
        print("缺少 DINGTALK_WEBHOOK 或 IMAGE_URL", file=sys.stderr)
        sys.exit(2)

    workdir = os.environ.get("WORKDIR", ".")

    update_time = os.environ.get("UPDATE_TIME", "").strip()
    if not update_time:
        p = os.path.join(workdir, "rates_meta.txt")
        if os.path.exists(p):
            update_time = open(p, encoding="utf-8").read().split("\n")[0].strip()

    shot_time = os.environ.get("SHOT_TIME", "").strip()
    if not shot_time:
        p = os.path.join(workdir, "shot_time.txt")
        if os.path.exists(p):
            shot_time = open(p, encoding="utf-8").read().strip()

    # 关键词过滤（机器人启用加签关键词，需含简体关键词）
    title = "每日汇率|汇率|牌价|美元电汇牌价|中银香港|BOCHK"
    lines = ["### 每日汇率｜中银香港美元电汇牌价"]
    if update_time:
        lines.append(f"> 資料更新於香港時間：{update_time}")
    if shot_time:
        lines.append(f"> 截圖時間（香港時間）：{shot_time}")
    lines.append(f"![每日汇率]({image_url})")
    text = "\n".join(lines)

    body = json.dumps({"msgtype": "markdown", "markdown": {"title": title, "text": text}})
    req = urllib.request.Request(
        signed_url(webhook, secret),
        data=body.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    print("DingTalk response:", result)
    if result.get("errcode") != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
