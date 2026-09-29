# k3-skills

K3 技能库公开分发层——38 件便携 Agent 技能包（.skill = zip，解压即得 SKILL.md 技能定义+references/scripts）。

## 用法

`unzip xxx.skill` → 读 SKILL.md（触发域/规程/脚本用法）。适配支持 Agent Skill 的宿主（Kimi/Claude Code 类）。

## 脱敏声明

- 7 件 `-public` 后缀为**脱敏公开版**：服务器 IP、凭据文件位名、实名已泛化为占位符；恢复真值以机主私藏版为准。
- 全部件过 preflight_scan 脱敏扫描（PASS/REVIEW 人工过目），无私钥值/手机号/身份证/银行卡命中。

## 上架状态（2026-09-29）

### ✅ 脱敏公开版 7 件——已上架（目录形式，GitHub 可直接读）

| 目录 | 内容 | 上架 commit |
|---|---|---|
| `star-owner-ops-public/` | 星藏家总署：Linux 移植裁定书（§一~§十六全文）等 3 件 | `33f6822` |
| `star-owner-pipeline-ops-public/` | Linux 移植管线 7 件（脚本+23 条实证坑+端口地图+IMA API） | `729cbc5` |
| `openpangu-seat-ops-public/` | OpenPangu 常设异族座 2 件（v1.1.1 全档+dryrun 用例） | `729cbc5` |
| `extpool-furnace-ops-public/` | 外池压测炉运维 v1.3.1 四件（组阁闸/线程安全炉体/装机五查） | `5ea3406` |
| `quota-guard-ops-public/` | 额度守护运维三合一 v2.0.0 九件（Q0-Q3 档位机+哈希链账本+每日一语推送） | `6cc8087` |
| `app-input-troubleshooting-public/` | 输入框修复指南 4 件（五层漏斗+三平台细则+案例库） | `2e5b530` |
| `autonomous-advance-ops-public/` | 自主推进运维总控 v1.1.2 四件（退化光谱 L0-L4+六条款+落实幻觉核验） | `64b626b` |

### ⏳ 待上架（等机主 GitHub PAT 到位后 git CLI 推送二进制）

- 31 件原样干净 `.skill` 包（清单同下）
- 7 件 `-public.skill` 包本体（与上面目录同内容的 zip 形态）
- 3D 资源 5 件（GLB/VRM，~110MB）→ 另仓 `k3-3d-assets`

## 上架偏差登记

- **app-input-troubleshooting-public**：源包锻件期丢失换行（四件文件各仅 1–4 行），上架版经排版修复管线重建换行并修复两处表格分隔行的冗余 `|`——**正文内容零改动**（逐件经空白剥离比对验证），仅版式恢复。登记日 2026-09-29。

## 上架清单（38 件）

### 脱敏公开版（7 件，见上表）

### 原样干净件（31 件）
- archive-ops-kit.skill / arxiv-source-sentinel.skill / cn-housing-finder.skill / daily-life-autopilot.skill / diffusion-dynamics-extension_v1.5.1.skill / epsilon-delta-proof-sovereign.skill / fusion-cast-ops.skill / fusion-program-audit.skill / goal-child-ops.skill / home-network-troubleshooter.skill / humanizer-zh.skill / hyper3d-rodin-mcp.skill / intl-case-intf.skill / iteration-convergence-ops.skill / k3-interaction-ops_v1.6.skill / k3-territory-studies.skill / link-bridge-ops.skill / monograph-forge-ops_v1.0.2.skill / monograph-forge-ops_v1.0.3.skill / night-playground-ops.skill / phys-ai-mat-conf-radar.skill / ppp-city-verdict-audit.skill / quant-frontier-lab_v1.1.1.skill / quota-ledger-ops.skill / rumor-chain-verifier.skill / rust-browser-pilot.skill / skill-library-auditor.skill / source-semantics-sentinel.skill / travel-commute-planner.skill / ultra-compress-ops.skill / vision-ocr-pipeline.skill
