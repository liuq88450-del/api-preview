# 示例代码说明

三份示例，逻辑相同，选你顺手的：

| 文件 | 环境 | 说明 |
|---|---|---|
| `quickstart.py` | Python 3.8+ | 只用标准库，无需 `pip install` |
| `quickstart.js` | Node 18+ | 用内置 `fetch` 和 `crypto`，无需装包 |
| `quickstart.sh` | bash + curl + openssl | 适合快速验证，不适合生产 |

## 怎么用

```bash
# 1. 设置环境变量（把占位换成开通邮件里的值）
export RN_BASE_URL="https://【按正式文档填】"
export RN_APP_ID="app_xxxxx"
export RN_APP_SECRET="【开通时下发】"

# 2. 二要素
python3 quickstart.py two "张*" "110101********1234"

# 3. 三要素（多一个手机号）
python3 quickstart.py three "张*" "110101********1234" "138****5678"
```

## 重要说明

1. **域名、路径、字段名是占位**。`RN_BASE_URL`、`/v1/realname/verify2` 这些按开通文档替换，别直接拿去打生产。
2. **签名规则是示意**。示例用"参数排序 + HMAC-SHA256"，真实规则（是否含空值、是否 URL 编码、时间戳窗口）以正式文档为准。
3. **示例数据是脱敏占位**，直接发会返回参数错误。换成你自己的测试数据，别用真实客户数据。
4. **生产环境不要照抄**：要加超时、重试退避、幂等、日志脱敏，密钥走环境变量或配置中心。

## 跑通后

- 把 `request_id` 写进日志；
- 用 `order_no` 做幂等；
- 余额低于 20% 配告警；
- 看 `docs.html` 第 6 节处理错误码。
