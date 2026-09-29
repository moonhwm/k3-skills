---
name: quota-guard-ops
description: "[项目技能] 额度守护运维三合一——事中档位守护（Q0–Q3）×事前/事后额度账本（自评五环）×每日一语语料轮换推送（萧红/尼采/海德格尔→飞书/微信）。触发（满足任一）：①额度信号：quota 耗尽/加油包提示/「额度不足」徽标，或用户说「额度」「加油包」「quota」「还剩多少额度」（含同音变体）；高消耗任务启动前查档。②预算账目：用户给预算办任务（「1-2元额度包办这事」）、要求评估 token 消耗/省钱/降本、任务结项报账。③每日一语：用户说「每日一句」「每日一语」「推送一句到手机」「语料推送」「萧红/尼采/海德格尔 每日」。不触发：领券/POI/通勤/答题领券→daily-life-autopilot。English triggers: quota watch, token budget, cost ledger, daily quote push, credit exhaustion, tiered operation."
metadata:
  version: "2.0.0"
  assistant_aliases: ["kim阁下", "元宝"]
---

# 额度守护运维（quota-guard-ops）v2.0.0 三合一

> **能力自报块**：能力域=管理｜输入型=额度信号/预算约束/推送请求｜输出型=档位+账本+判决+手机推送｜只读性=否（写额度台账/账本 JSONL，只读语料库）｜依赖=python3 标准库（lark-cli 可选）
> **纪律继承声明**：本技能继承 conf 词表统一、红线条款、写类例外、信息充分性条款、全局共同遵守（autonomous-advance-ops 为准）。

## 〇、一技三层（合并不混层）

| 层 | 管什么 | 脚本 |
|---|---|---|
| 层一 事中守护 | 额度信号检测、Q0–Q3 档位、止损交接 | scripts/quota_state.py |
| 层二 事前/事后账本 | 这事花多少（估算）、花到哪（记账）、超了怎么办（策略）、值不值（结项） | scripts/quota_ledger.py |
| 层三 每日一语推送 | 三语料确定性轮换 + 推送手机（飞书/微信） | scripts/daily_quote.py + scripts/push_quote.py |

让渡：生活执行（领券/POI/通勤）全归 daily-life-autopilot；本技能只算账、守档、推一句，不跑腿。
v2.0.0 合并原 quota-ledger-ops（v1.x 单飞技能）全部辖区；每日一语引擎自 output/daily-quote 收编为唯一真源。

## 层一 · 事中守护

**诚实边界**：精确余额不可机读（平台无开放额度 API）。一切档位判定=信号+代理量，conf=estimated。
1. **错误信号**：工具/子代理返回 quota exhausted 类错误 → `signal quota_error`（→Q3）。
2. **加油包提示**：出现「加油包」「额度不足 去升级」徽标 → `signal pack_prompt`（→Q2）——计费窗口开启，继续使用须用户知情同意（单独一句明示，k3 条款1）。
3. **遥测代理量**：连续 3 轮超基线 2 倍 → 建议升 Q1（人工确认）。
4. **用户 UI 上报**：用户粘贴账户页/徽标状态 → 按用户口径 `set` 入档（最高证据级）。

| 档 | 触发 | 动作边界 |
|---|---|---|
| Q0 绿灯 | 默认/复位 | 全栈常态；Swarm 可用；遥测照常 |
| Q1 黄灯 | 遥测连续高耗/用户上报偏紧 | 单线程优先；子代理 ≤2；非必要不派多席表决 |
| Q2 橙灯 | 加油包提示/计费窗口 | **骨架先行**；禁派子代理；加油包消耗须用户知情同意；每轮结束报预估剩余轮次 |
| Q3 红灯 | quota 耗尽错误 | **止损**：不推新任务；成果即刻落盘；交接等重置或用户拍板 |

**铁则**：信号只升不降——降档只能 `set` 显式确认。台账 `/mnt/agents/upload/skill-iteration-registry/额度状态台账.json`。

```bash
python3 scripts/quota_state.py show
python3 scripts/quota_state.py signal <quota_error|pack_prompt|ok>
python3 scripts/quota_state.py set <Q0|Q1|Q2|Q3> <理由>
```

## 层二 · 事前/事后账本（额度自评五环）

**诚实边界**：一切数字=估算（estimated）。官方锚点：额度池全功能共享、按月刷新、赠送额度优先、任务失败不扣费、量纲「简单 PPT≈1-2%／深研≈5-10%」。价目表与免费降级通道见 references/pricing-anchors.md。

1. **预算解析**：元/额度池%/token 三口径互转（默认锚=DeepSeek V4-Flash 谷时价，env QUOTA_RATE_IN/OUT 可覆盖）。
2. **任务定档**：T1 浅（数万-十几万 token）/T2 中（十几万-几十万）/T3 深（几十万-数百万）→ 给 **够/紧/不够** 判决，不够给免费通道分流。
3. **逐阶段记账**：
```bash
python3 scripts/quota_ledger.py init <任务名> --budget 1.5 --unit cny
python3 scripts/quota_ledger.py log <任务名> <阶段名> --in 40000 --out 6000
python3 scripts/quota_ledger.py status|report <任务名>
```
账本落 `/mnt/agents/temp/quota_ledger/<任务名>.jsonl`（禁 /tmp），行级哈希链防篡改。
4. **超限三级**：50% 提示／80% 降档或请示（二选一明示）／100% 止损结项+交接层一（Q 档只升不降，本层不复位）。
5. **结项报告**：账本汇总+三省吾身+**文学化落款**（三语料规范见 references/voices.md：萧红 FTS 实引首选，尼采拟箴言标「拟」，海德格尔缺藏禁伪引）。

## 层三 · 每日一语推送

**语料纪律**（references/voices.md 全文为准）：
- 萧红——FTS5 实引（xh_corpus.db，13,044 段），凡引号必带档号 `doc#para(year)`；
- 尼采——epub 实时提取真实句，译本混杂 → 作者标「尼采（拟）」、tentative=true；
- 海德格尔——云侧缺藏在册，禁伪引；显式点播只出缺藏标记，不入默认轮换。

**轮换**：按日期序数在 萧红 ↔ 尼采 间确定性交替；同日同结果可复现。关键词环≥3 字（trigram 词元限制），全部经实库验证。

**推送通道**（开通步骤与凭证纪律见 references/push-channels.md）：
lark 飞书机器人直推（首选，bot 身份，目标存 scripts/lark-target.json）> FEISHU_BOT_WEBHOOK > WECOM_BOT_WEBHOOK > SERVERCHAN_SENDKEY。
**lark 通道一次绑定永久免授权**：2026-09-24 已完成应用注册（App cli_aa3f9a00ed38dcea）+ 用户授权，目标用户 open_id/chat_id 在 scripts/lark-target.json；appSecret 由 lark-cli 本地配置保管，备份于 /mnt/agents/upload/lark-cli-config-backup/——沙箱重建后 `cp -r /mnt/agents/upload/lark-cli-config-backup/. ~/.lark-cli/` 即恢复，**不得再让用户扫码**。
**红线：永不自动化个人微信账号**（itchat/wxauto/wxpy 类通道禁用，永不添加）；微信侧只走 Server酱/企业微信机器人官方网关。
凭证零明文：脚本一律 env 读取（grep|cut 注入），状态查询永不回显钥值。

```bash
python3 scripts/daily_quote.py today [--date D] [--voice xiaohong|nietzsche|heidegger] [--outdir DIR]
python3 scripts/push_quote.py channels          # 通道配置状态（不报钥值）
python3 scripts/push_quote.py send --dry-run    # 组报文预演
python3 scripts/push_quote.py send [--channel lark|feishu|wecom|serverchan|all]
```

**授权边界**：单次实推以用户当次明示为凭；定时推送（cron 每日）须用户另行批准——**2026-09-24 主理人已明示批准每日自动推送**（原话「给我写进技能，你自动能触发」），cron 任务以本记录为凭；如用户要求停推，移除 cron 即恢复手动。

## 不逃逸高性能运作（全层有效）

1. **目的轮优先**：高档位下写动作优先给目的层，治理动作合批。
2. **便宜通道优先**：能搜索就不爬取；能既有台账就不重拉；已核验事实不重核。
3. **合批降耗**：同类查询合并单次调用；多席表决降 Q1+ 后才启用。
4. **逃逸三问照常**：省额度不等于省纪律——红线条款全档有效，Q3 也不豁免；账本字段一律脚本生成，禁人肉补全（ESC-004 同款）。

## 与既有立法关系

k3-interaction-ops quota 止损条款（条款1）> 本技能一切推进义务；本技能是其检测、分档、记账与推送的操作化，不修改条款本体。计时器任务台账联动：cron 日检含额度信号检查（Q2+ 时当日告警入推送候选，受每日≤3 与安静时段约束）。