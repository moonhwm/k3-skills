# 星链全图·真值详表（chain-map）

核验日：2026-09-29（端点真值超 30 天须复验）。凭据值永不入图——只记**凭据位**与**权限位**。

## 链1 X 实例

| 项 | 真值 |
|---|---|
| 主机 | root@<SERVER_IP>（华为云北京四，8vCPU/32GB） |
| 私钥（沙箱侧） | ~/.ssh/<ssh_key_file>；**恢复源** /mnt/agents/upload/月之游乐场/keys/<ssh_key_file>（chmod 600） |
| 常设位 | /opt/star-owner/tools/、/opt/star-owner/workspace/{burns,tushare}/ |
| 正本纪律 | X 与 /mnt/agents/output 为准；沙箱 /tmp 仅当轮暂存；沙箱重置 7 次实证零损失 |
| 验证 | `ssh -i ~/.ssh/<ssh_key_file> root@<SERVER_IP> 'hostname && ls /opt/star-owner/tools/'` |

## 链2 外置燃烧判官链

| 项 | 真值 |
|---|---|
| 名册 | /opt/star-owner/tools/judge_routes.json v1.1.0（4 族 active：maas-pangu / maas-glm / maas-deepseek / bailian-gift(qwen)；kimi 席在册不计族数） |
| 组阁闸 | panel_check.py exit 0；组阁律：除 Kimi 外 ≥3 异质族、各走不同路由、名册随件、不足即降级 |
| 炉具 | burn_judges.py v1.3.1：`--single`/`--old` 双模式、`--rubric9`（九维）、`--context <file>`（paired 锚定） |
| 裁定 | fusion_cast.py cast --verdicts v.jsonl --version x.y.z --prev …（判官票独立重算；slight 连两轮→HL-4 出链） |
| 台账 | /opt/star-owner/workspace/burns/burn-ledger.jsonl（含 burn_failed/burn_empty 失败窑） |
| 华为云 MaaS 端点 | https://api.modelarts-maas.com/v2/chat/completions（OpenAI 兼容亦可用 /openai/v1）；凭据位 /root/.<maas_key_file>（600） |
| MaaS 思维补丁 | 请求体 JSON 字段 `"thinking":{"type":"disabled"}`（实证 reasoning_tokens=0）；**glm-5.3 拒此字段→HTTP 400 ModelArts.81001，fallback glm-5.2** |
| 百炼礼赠池端点 | https://<workspace_id>.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions（**/compatible-mode 前缀必带**）；凭据位 /root/.<bailian_key_file>（600）；qwen3.8-flash 主 / qwen3.7-flash 备；思维补丁 `enable_thinking:false` |
| 路由打折在案 | pangu/glm/deepseek 三族同经 MaaS 网关=路由集中度已登记；破法=GLM/DeepSeek 直端点凭据（未入场，占位） |
| 验证 | `ssh ... 'cd /opt/star-owner && python3 tools/panel_check.py && tail -2 workspace/burns/burn-ledger.jsonl'` |

## 链3 IMA 并入链

| 项 | 真值 |
|---|---|
| 推送器 | /opt/node22/bin/node /opt/star-owner/tools/ima_push.cjs --file <路径> [--title 名] |
| 五步链 | preflight→重名检查→create_media→COS→add_knowledge；KB 名取 /root/.<ima_kb_name>（600） |
| UX 纪律 | 面向用户只回 {ok,file_name,file_size,ts}；永不暴露 knowledge_base_id/media_id/folder_id/签名 URL |
| 验证 | `node /opt/star-owner/tools/ima_push.cjs --file <小文件>` 回 ok:true |

## 链4 Tushare 数据仓链

| 项 | 真值 |
|---|---|
| 工具 | /opt/star-owner/tools/tushare_forge.py v1.0.0（纯标准库 POST api.waditu.com；子命令 probe / pull-daily --days N / status） |
| 凭据位 | /root/.<your_tushare_key>（600）；≥2000 积分档实测 |
| 仓 | /opt/star-owner/workspace/tushare/tushare.sqlite（daily 表 PK(ts_code,trade_date)）；台账 tushare-ledger.jsonl |
| 首拉实证 | 55,454 行 / 5,554 代码 / 20260820→20260902（10 交易日，0.4s 间隔+重试×3） |
| 口径 | 积分=门槛+频率配额，非消耗品；燃烧=配额转持久数据资产 |
| 验证 | `ssh ... 'python3 /opt/star-owner/tools/tushare_forge.py status'` |

## 链5 技能锻造链

| 站 | 真值 |
|---|---|
| 锻造 | 工作目录 /tmp/<skill-name>/（SKILL.md + references/） |
| 评审 | burn_judges.py --single --rubric9 [--context]（全席 ≥3 异族）→ verdicts.jsonl |
| 裁定 | fusion_cast.py cast（票重算；抓包→delta 修→复评→收敛） |
| 打包 | package_skill.py <dir> **<外置输出目录>**（防自包含病） |
| 终验 | `unzip -p <pkg> <path>/SKILL.md \| grep <版本标记>`——**不过不交付**（v1.0.1 名实偏擦案入制） |
| 交付 | /mnt/agents/output/<name>.skill + 裁定记录 .md；双推 IMA |
| 写回队列 | 安装位只读时：登记队列+明示用户未装入（furnace v1.3.1 / 座件 v1.1.1 等在队） |

## 链6 凭据链

| 凭据位（X，均 600） | 用途 |
|---|---|
| /root/.<maas_key_file> | 华为云 MaaS 12 模型 |
| /root/.<bailian_key_file> | 百炼礼赠池 qwen |
| /root/.<your_tushare_key> | Tushare |
| /root/.<ima_kb_name> | IMA KB 名 |

沙箱侧：仅 `set -a; . /mnt/agents/upload/credentials.env; set +a` 入环境变量；零落盘零回显；装机五查=新池/新凭据/新端点入场前置闸（归 extpool-furnace-ops §1.5）。

## 链7 重置恢复链

即 SKILL.md §3 七步。事故档：沙箱重置 ×7（私钥与 /tmp 全失，均恢复零损失）；glm-5.3 81001（fallback 成窑）；名实偏擦案（包体终验入制）；fusion_cast 票缺位（票在 X 未渡回→scp 后裁定）。

## 对账三数（生态心跳）

1. `tail -1 /opt/star-owner/workspace/burns/burn-ledger.jsonl` 的 ts；
2. `tushare_forge.py status` 的行数与末交易日；
3. `grep version /opt/star-owner/tools/judge_routes.json`。
