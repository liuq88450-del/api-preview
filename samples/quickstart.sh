#!/usr/bin/env bash
# 实名核验 API 快速开始（curl + openssl）
#
# 用法：
#   export RN_BASE_URL="https://【按正式文档填】"
#   export RN_APP_ID="app_xxxxx"
#   export RN_APP_SECRET="【开通时下发】"
#
#   bash quickstart.sh two   "张*" "110101********1234"
#   bash quickstart.sh three "张*" "110101********1234" "138****5678"
#
# 注意：域名、字段名、签名规则以正式文档为准；示例数据均为脱敏占位。

set -euo pipefail

: "${RN_BASE_URL:?请先 export RN_BASE_URL}"
: "${RN_APP_ID:?请先 export RN_APP_ID}"
: "${RN_APP_SECRET:?请先 export RN_APP_SECRET}"

PRODUCT="${1:-}"
NAME="${2:-}"
IDCARD="${3:-}"
MOBILE="${4:-}"

if [[ -z "$PRODUCT" || -z "$NAME" || -z "$IDCARD" ]]; then
  echo "用法：bash quickstart.sh two|three 姓名 身份证 [手机号]"
  exit 1
fi

TS="$(date +%s)"
NONCE="$(openssl rand -hex 8)"
ORDER_NO="quickstart-${TS}"

# 签名示意：参数按 key 排序拼接，HMAC-SHA256。规则以正式文档为准。
SIGN_BASE="app_id=${RN_APP_ID}&idcard=${IDCARD}&name=${NAME}&nonce=${NONCE}&order_no=${ORDER_NO}&timestamp=${TS}"
SIGN="$(printf '%s' "$SIGN_BASE" | openssl dgst -sha256 -hmac "$RN_APP_SECRET" | awk '{print $NF}')"

if [[ "$PRODUCT" == "two" ]]; then
  PATH_API="/v1/realname/verify2"
  BODY=$(printf '{"app_id":"%s","order_no":"%s","name":"%s","idcard":"%s","timestamp":"%s","nonce":"%s","sign":"%s"}' \
    "$RN_APP_ID" "$ORDER_NO" "$NAME" "$IDCARD" "$TS" "$NONCE" "$SIGN")
elif [[ "$PRODUCT" == "three" ]]; then
  if [[ -z "$MOBILE" ]]; then
    echo "三要素需要手机号。"
    exit 1
  fi
  PATH_API="/v1/realname/verify3"
  # 三要素的待签串包含 mobile
  SIGN_BASE="app_id=${RN_APP_ID}&idcard=${IDCARD}&mobile=${MOBILE}&name=${NAME}&nonce=${NONCE}&order_no=${ORDER_NO}&timestamp=${TS}"
  SIGN="$(printf '%s' "$SIGN_BASE" | openssl dgst -sha256 -hmac "$RN_APP_SECRET" | awk '{print $NF}')"
  BODY=$(printf '{"app_id":"%s","order_no":"%s","name":"%s","idcard":"%s","mobile":"%s","timestamp":"%s","nonce":"%s","sign":"%s"}' \
    "$RN_APP_ID" "$ORDER_NO" "$NAME" "$IDCARD" "$MOBILE" "$TS" "$NONCE" "$SIGN")
else
  echo "第一个参数只能是 two 或 three"
  exit 1
fi

echo "POST ${RN_BASE_URL}${PATH_API}"
curl -sS -X POST "${RN_BASE_URL}${PATH_API}" \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d "$BODY" \
  --max-time 10 \
  -w '\nHTTP %{http_code}\n'
