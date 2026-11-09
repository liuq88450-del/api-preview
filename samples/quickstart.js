#!/usr/bin/env node
/**
 * 实名核验 API 快速开始（Node 18+，内置 fetch / crypto）
 *
 * 用法：
 *   export RN_BASE_URL="https://【按正式文档填】"
 *   export RN_APP_ID="app_xxxxx"
 *   export RN_APP_SECRET="【开通时下发】"
 *
 *   node quickstart.js two   "张*" "110101********1234"
 *   node quickstart.js three "张*" "110101********1234" "138****5678"
 *
 * 注意：域名、字段名、签名规则以正式文档为准；示例数据均为脱敏占位。
 */

const crypto = require("node:crypto");

const BASE_URL = (process.env.RN_BASE_URL || "").replace(/\/+$/, "");
const APP_ID = process.env.RN_APP_ID || "";
const APP_SECRET = process.env.RN_APP_SECRET || "";

// 【待确认】路径以正式文档为准
const PATH_TWO = "/v1/realname/verify2";
const PATH_THREE = "/v1/realname/verify3";

function buildSign(params) {
  const raw = Object.keys(params)
    .filter((k) => k !== "sign" && params[k] !== "" && params[k] != null)
    .sort()
    .map((k) => `${k}=${params[k]}`)
    .join("&");
  return crypto.createHmac("sha256", APP_SECRET).update(raw, "utf8").digest("hex");
}

function buildPayload(name, idcard, mobile) {
  const payload = {
    app_id: APP_ID,
    order_no: `quickstart-${Math.floor(Date.now() / 1000)}`,
    name,
    idcard,
    timestamp: String(Math.floor(Date.now() / 1000)),
    nonce: crypto.randomBytes(8).toString("hex"),
  };
  if (mobile) payload.mobile = mobile;
  payload.sign = buildSign(payload);
  return payload;
}

async function post(path, payload) {
  const res = await fetch(BASE_URL + path, {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(10000),
  });
  console.log(`HTTP ${res.status}`);
  console.log(await res.text());
}

async function main() {
  const missing = Object.entries({
    RN_BASE_URL: BASE_URL,
    RN_APP_ID: APP_ID,
    RN_APP_SECRET: APP_SECRET,
  }).filter(([, v]) => !v).map(([k]) => k);

  if (missing.length) {
    console.error("缺少环境变量：" + missing.join(", "));
    console.error("先按 quickstart.html 第 1 步设置，再运行。");
    process.exit(1);
  }

  const [product, name, idcard, mobile] = process.argv.slice(2);
  if (!product || !name || !idcard) {
    console.error("用法：node quickstart.js two|three 姓名 身份证 [手机号]");
    process.exit(1);
  }

  if (product === "two") {
    await post(PATH_TWO, buildPayload(name, idcard));
  } else if (product === "three") {
    if (!mobile) {
      console.error("三要素需要手机号。");
      process.exit(1);
    }
    await post(PATH_THREE, buildPayload(name, idcard, mobile));
  } else {
    console.error("第一个参数只能是 two 或 three");
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("请求失败：" + err.message);
  process.exit(1);
});
