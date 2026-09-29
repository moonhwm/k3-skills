# 手机推送通道开通指引（每日一语层）

四通道按优先级排：lark 飞书机器人直推 > 飞书机器人 webhook > 企业微信机器人 webhook > Server酱。
**红线：永不自动化个人微信账号**——itchat/wxauto/wxpy/PC 协议类一律禁用；微信侧只走下列官方/第三方推送网关。

## 通道一览

| 通道 | 到达端 | 费用 | 配置物 | 适合 |
|---|---|---|---|---|
| lark 飞书机器人直推 | 飞书 App 私聊 | 免费 | scripts/lark-target.json（已绑定） | 默认通道；bot 身份一次授权永久免再扫码 |
| 飞书自定义机器人 webhook | 飞书群 | 免费 | `FEISHU_BOT_WEBHOOK` | 只想推进群；无需鉴权 |
| 企业微信群机器人 webhook | 企业微信 App（可转发到微信） | 免费 | `WECOM_BOT_WEBHOOK` | 有企业微信；群里机器人即开即用 |
| Server酱 Turbo | 个人微信（公众号「Server酱·Turbo」内到达） | 免费版 5 条/天 | `SERVERCHAN_SENDKEY` | 只有个人微信；零开发 |

## lark 直推通道（已开通，维护规程）

**绑定状态（2026-09-24）**：应用 cli_aa3f9a00ed38dcea（bot ready）+ 用户 机主 已授权；目标 open_id/chat_id 存 scripts/lark-target.json（标识符非密钥，可入包）。
**免授权原理**：推送用 bot 身份（appId+appSecret），不依赖用户 token；用户授权仅一次性用于发现 open_id。
**沙箱重建恢复**（关键）：lark-cli 配置在沙箱本地 ~/.lark-cli，重建即丢。已备份至 `/mnt/agents/upload/lark-cli-config-backup/`：
```bash
cp -r /mnt/agents/upload/lark-cli-config-backup/. ~/.lark-cli/ && lark-cli auth status   # bot ready 即恢复
```
**禁止事项**：配置丢失时先恢复备份，**不得直接 `config init --new` 再让用户扫码**；备份恢复失败才允许重走授权流。
**发送**：`python3 scripts/push_quote.py send --channel lark`（脚本内自动取 lark-target.json）。

### 2. 飞书自定义机器人（群 webhook）
飞书群 → 设置 → 群机器人 → 添加「自定义机器人」→ 复制 webhook URL。
```bash
export FEISHU_BOT_WEBHOOK=$(grep '^FEISHU_BOT_WEBHOOK=' /mnt/agents/upload/credentials.env | cut -d= -f2-)
```

### 3. 企业微信群机器人
企业微信群 → 右上角 → 群机器人 → 添加 → 复制 webhook（形如 `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...`）。
```bash
export WECOM_BOT_WEBHOOK=$(grep '^WECOM_BOT_WEBHOOK=' /mnt/agents/upload/credentials.env | cut -d= -f2-)
```

### 4. Server酱 Turbo（推到个人微信）
微信扫码登录 https://sct.ftqq.com → 复制 SendKey；关注其公众号后消息在微信内到达。
```bash
export SERVERCHAN_SENDKEY=$(grep '^SERVERCHAN_SENDKEY=' /mnt/agents/upload/credentials.env | cut -d= -f2-)
```

## 凭证纪律

- 三枚 webhook/SendKey 均属凭证：写入 `/mnt/agents/upload/credentials.env`（单行 KEY=VALUE）+ 凭证链登记（fp_sha256_12，**零明文**）。
- 脚本一律 env 读取；技能包、git、提示词中永不出现钥值。
- `push_quote.py channels` 只报「已配置/缺」，永不回显钥值。

## 定时推送

每日 08:00：`push_quote.py send --channel lark`（lark 直推，零授权）。
**2026-09-24 主理人已批准自动触发**（原话「给我写进技能，你自动能触发」），cron 由平台定时任务承载；停推=用户一句话，移除 cron 即恢复手动。