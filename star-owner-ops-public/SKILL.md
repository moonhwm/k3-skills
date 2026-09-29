---
name: star-owner-ops
description: >
  星藏家总署——星藏家生态「所有链路+Linux移植正史」的单一事实源与恢复点（链路图+移植裁定书一体整合）：X 实例、外置燃烧判官链、IMA 并入链、
  Tushare 数据仓链、技能锻造链、凭据链、沙箱重置恢复链七链真值总表与开工卡。
  触发（满足任一）：①用户说「全链路」「所有链路」「链路图」「星链」「star chain」「恢复链」或等价表述；
  ②沙箱重置后需恢复全生态工作状态时（本件即恢复 SOP）；③新会话/新席需一次拿全
  端点/路径/凭据位/脚本/台账位真值时；④任一链环节点变更（新席位/新端点/新脚本版本）需登记回写时。
  覆盖：七链真值表（链路由/端点/凭据位/台账位/事故档）、沙箱重置恢复七步、跨会话开工卡、
  链路变更登记纪律。不覆盖：各链本体技能的内部规程（burn_judges 用法归 extpool-furnace-ops、
  判官档案归 openpangu-seat-ops、ima_push 五步链归其脚本注释——本件引用不复制）。
  中文名：星藏家总署。English triggers: star chain map, all-chains recovery, chain registry, sandbox reset recovery SOP.
metadata:
  version: "1.0.0"
---

# 星藏家总署（star-owner-ops）

> 本件=原 star-chain-ops v1.0.1（七链图，KEEP/clear 收敛件）改名整合版：新增 references/x-port-ruling.md 移植裁定书全文（正史），地图与正史一包全收。

> 立法锚：**「链不在图上即不存在；图上的每个字都要能被一条命令验证。」**
> 本件是**恢复点**：沙箱可灭、上下文可压缩、记忆可漂移——本件不漂移。一切正本以 X 端与 /mnt/agents/output 为准。

## §0 定位与边界

- **三件套结构**：SKILL.md=总图与开工卡；references/chain-map.md=七链真值详表；references/x-port-ruling.md=星藏家 Linux 移植裁定书全文（正史：装机/组阁/收敛/事故档）
- 本件只管**链与链之间的真值**：端点、路径、凭据位、台账位、版本位、事故档。各链本体的内部规程归各本体技能（引用不复制）。
- 诚实边界：图上条目必须可机验——每条附验证命令；验证不过即标 STALE，禁凭记忆补全。

## §1 七链总图（每链一句话+验证锚）

| # | 链 | 路由 | 验证锚 |
|---|---|---|---|
| 1 | X 实例链 | 沙箱→SSH（<ssh_key_file>）→root@<SERVER_IP>（华为云北京四 8vCPU/32GB） | `ssh ... 'hostname'` |
| 2 | 燃烧判官链 | judge_routes.json 组阁（≥3 异族）→burn_judges.py 评审→fusion_cast.py 裁定→burn-ledger.jsonl | `python3 /opt/star-owner/tools/panel_check.py`（exit 0；脚本在 X 端 tools/，缺失即降级=人工核 judge_routes.json 族数≥3） |
| 3 | IMA 并入链 | 任意文件→ima_push.cjs 五步链→IMA 游乐场库 | `node tools/ima_push.cjs --file <f>`（回 ok:true） |
| 4 | Tushare 数据仓链 | token→tushare_forge.py→SQLite 仓 | `python3 tools/tushare_forge.py status` |
| 5 | 技能锻造链 | forge→rubric9 评审→cast→package→包体终验→output→IMA→写回队列 | `unzip -p <pkg> ...SKILL.md \| grep version` |
| 6 | 凭据链 | X:/root/.*_key\|token（600）；沙箱:credentials.env 入环境变量 | `ls -la /root/.<maas_key_file>`（600） |
| 7 | 重置恢复链 | upload 钥匙存档→~/.ssh→正本回捞（§3 七步） | 本件 §3 |

详表（端点真值/凭据位/台账位/事故档/模型花名册）见 [references/chain-map.md](references/chain-map.md)——**改链先改图，图是唯一事实源**。

## §2 开工卡（新会话/重置后第一件事）

1. **恢复 SSH**（§3 第①步）→ `ssh root@<SERVER_IP> 'echo ok'`；
2. **读图**：本件 + chain-map.md，按验证锚逐链抽检（≤5 条命令）；
3. **对账**：burn-ledger 尾行 ts、tushare status、judge_routes 版本——三数即生态心跳；
4. **续作**：沿存任务以「裁定书」（本件 references/x-port-ruling.md 即全文；沙箱正本 /mnt/agents/output/星藏家-Linux移植裁定与华为云算力方案.md，§十六止）与 IMA 库为正本，**禁凭对话记忆续写**。

## §3 沙箱重置恢复七步（第 7 次重置实证定版）

1. `mkdir -p ~/.ssh && cp "/mnt/agents/upload/月之游乐场/keys/<ssh_key_file>" ~/.ssh/ && chmod 600 ~/.ssh/<ssh_key_file>`；
2. 验证：`ssh -i ~/.ssh/<ssh_key_file> -o StrictHostKeyChecking=no root@<SERVER_IP> 'echo ok'`；**SSH 失败三诊断**——权限错：重查 `chmod 600`+比对指纹 `ssh-keygen -lf ~/.ssh/<ssh_key_file>`；网络不通：`ping -c2 <SERVER_IP>` 或换网络；IP 变更：以华为云控制台实况为准并即改图（§4）；
3. 工具正本在 X（/opt/star-owner/tools/），沙箱侧工作件一律 `scp` 回捞——带空格/中文路径安全模板：`scp -i ~/.ssh/<ssh_key_file> "root@<SERVER_IP>:/opt/star-owner/tools/xxx" ./`；**不在沙箱重建**（防版本分叉）；scp 失败→先做②步三诊断，路径不存在→以 X 端 `ls` 实况为准，禁凭记忆猜路径；
4. /tmp 全失属正常（验证 `ls /tmp` 应仅余当轮件）——/tmp 只是当轮暂存，凡有价值的件必须已在 X 或 output（未落即丢，如实报损）；
5. 技能包正本在 /mnt/agents/output/（包体标记终验后方为正）；
6. 凭据零落盘铁律不动：沙箱侧只经 `set -a; . /mnt/agents/upload/credentials.env; set +a`；
7. 重置事件登记裁定书（计数+波及面）——本会话线已登记至第 7 次。

## §4 链路变更登记（改链纪律）

- 新席位/新端点/新凭据/脚本版本递增/台账换址 → **当轮**改 chain-map.md 对应行+验证锚实测+版本注释；
- 图与实不符时以实测为准修图，禁以图为准强改实（图是描述不是命令）；
- 每轮收尾自检：本件所述路径 `ls` 抽检 ≥3 处，悬空即修。
- **chain-map.md 漂移降级**：references/chain-map.md 随 .skill 包同行（包体终验必含）；若漂移或缺失，以 X 端 /tmp/star-owner-ops-v*.md 正本回捞重建并重打包终验，禁凭记忆补写真值。

## §5 反模式黑名单

| # | 反模式 | 替代 |
|---|---|---|
| 1 | 凭对话记忆续写链路状态 | 开工卡对账三数，以 X/output 正本为准 |
| 2 | 沙箱 /tmp 当正本用 | /tmp 仅暂存，正本先上 X 再谈交付 |
| 3 | 图上写「应该可以」 | 每条附验证锚；未验标 STALE |
| 4 | 改实不改图（图实分叉） | 当轮双改；图是唯一事实源 |
| 5 | 技能包未验包体即交付 | `unzip -p \| grep` 标记终验（v1.0.1 偏擦案） |
| 6 | `--single` 评审只喂 SKILL.md，references 不在判官视野→误判「资源缺失」 | 评审输入拼入 references 全文（本件 R1 实证） |

## §6 诚实边界

1. 本件是恢复点不是备份——数据本体在 X 与 output，本件只存「怎么找回来」；
2. 凭据值永不上图（只记凭据位与权限位）；credentials.env 结构占位示例（值永不落图）：`MAAS_API_KEY=***`、`BAILIAN_GIFT_KEY=***`、`TUSHARE_TOKEN=***`；
3. 端点真值有时效——图上标注核验日，超 30 天复验；
4. 判官链裁定永远归 fusion_cast.py 重算，本件不裁定任何事。

## 联挂

extpool-furnace-ops（链2 本体）｜openpangu-seat-ops（判官档案）｜fusion-cast-ops（裁定）｜link-bridge-ops（链接纪律）｜autonomous-advance-protocol（总纲）｜k3-channel-ops（总线链，本图未收）
