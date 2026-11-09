#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实名核验 API 快速开始（Python 3.8+，无第三方依赖）

用法：
    export RN_BASE_URL="https://【按正式文档填】"
    export RN_APP_ID="app_xxxxx"
    export RN_APP_SECRET="【开通时下发】"

    python3 quickstart.py two   "张*" "110101********1234"
    python3 quickstart.py three "张*" "110101********1234" "138****5678"

注意：
- 域名、字段名、签名规则以开通时下发的正式文档为准，本文件里的写法是结构示意。
- 示例数据均为脱敏占位，换成你自己的测试数据再跑。
"""

import hashlib
import hmac
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request

BASE_URL = os.environ.get("RN_BASE_URL", "").rstrip("/")
APP_ID = os.environ.get("RN_APP_ID", "")
APP_SECRET = os.environ.get("RN_APP_SECRET", "")

# 【待确认】路径以正式文档为准
PATH_TWO = "/v1/realname/verify2"
PATH_THREE = "/v1/realname/verify3"


def build_sign(params: dict, secret: str) -> str:
    """签名示意：参数排序拼接 + HMAC-SHA256。规则以正式文档为准。"""
    items = sorted((k, str(v)) for k, v in params.items()
                   if k != "sign" and str(v) != "")
    raw = "&".join(f"{k}={v}" for k, v in items)
    return hmac.new(secret.encode("utf-8"), raw.encode("utf-8"),
                    hashlib.sha256).hexdigest()


def build_payload(name: str, idcard: str, mobile: str = None) -> dict:
    payload = {
        "app_id": APP_ID,
        "order_no": f"quickstart-{int(time.time())}",
        "name": name,
        "idcard": idcard,
        "timestamp": str(int(time.time())),
        "nonce": uuid.uuid4().hex[:16],
    }
    if mobile:
        payload["mobile"] = mobile
    payload["sign"] = build_sign(payload, APP_SECRET)
    return payload


def post(path: str, payload: dict) -> None:
    url = BASE_URL + path
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", "replace")
            print(f"HTTP {resp.status}")
            print(body)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}")
        print(e.read().decode("utf-8", "replace"))
    except urllib.error.URLError as e:
        print(f"网络错误：{e.reason}")
        print("检查 RN_BASE_URL 是否正确、服务器是否能出网。")


def main() -> int:
    missing = [k for k, v in {
        "RN_BASE_URL": BASE_URL,
        "RN_APP_ID": APP_ID,
        "RN_APP_SECRET": APP_SECRET,
    }.items() if not v]
    if missing:
        print("缺少环境变量：" + ", ".join(missing))
        print("先按 quickstart.html 第 1 步设置，再运行。")
        return 1

    if len(sys.argv) < 4:
        print(__doc__)
        return 1

    product = sys.argv[1].lower()
    name, idcard = sys.argv[2], sys.argv[3]
    mobile = sys.argv[4] if len(sys.argv) > 4 else None

    if product == "two":
        payload = build_payload(name, idcard)
        post(PATH_TWO, payload)
    elif product == "three":
        if not mobile:
            print("三要素需要手机号：python3 quickstart.py three 姓名 身份证 手机号")
            return 1
        payload = build_payload(name, idcard, mobile)
        post(PATH_THREE, payload)
    else:
        print("第一个参数只能是 two 或 three")
        return 1

    # 提示：真实返回里 request_id 要落日志，排障和账单争议都靠它
    return 0


if __name__ == "__main__":
    sys.exit(main())
