---
name: star-owner-pipeline-ops
description: >-
  星藏家（Star-Owner）B站收藏夹→云 LLM 整理→IMA 知识库全链管线的运维与灾后恢复总件。触发（满足任一）：①用户说「星藏家」「star-owner」「X 实例」「SERVER_IP」「百炼整理」「ima-bridge」「IMA 同步」「游乐场库同步」或等价表述（含语音变体，不纠正用户、映射意图）；②应用重启/崩溃/沙箱重置后需要恢复管线时；③CDP 驱动 Electron、safeStorage/钥匙串、ENAMETOOLONG、供应商配置、队列失败重跑等故障处置时；④要把知识文档同步进 IMA 或在 IMA 检索学习时；⑤「以防万一」级别的管线重建。不覆盖：Tripo 3D 生成与绑骨（归 tripo-avatar-ops）、凭据内容本身（永不入技能，只记位置）、B站账号运营。中文名：星藏家管线运维总署。English triggers — star-owner pipeline, X instance recovery, bailian provider ops, ima-bridge daemon, CDP electron driving, headless keyring chain, ENAMETOOLONG byte-cap patch.
---

# 星藏家管线运维总署

链路：**B站收藏夹 → 星藏家（X 实例 Electron）→ faster-whisper 本地 ASR → 阿里云百炼云 LLM 整理 → 知识文档 → ima-bridge → IMA「月之暗面的游乐场ima」**。

## §0 红线（先读再动手）

1. 凭据零明文：只从位置文件读出即用（`/root/.<bailian_key_file>`、`~/.config/ima/`、`/root/.ima_kb_*`），masked display，永不回显、永不入对话/文件/技能。
2. 判官池（8017 Qwen3-32B）永不擅杀；GPU 被占只协调不越权。
3. 写类动作逐次须批准；无法实装当轮诚实声明；禁编造数据。
4. IMA OpenAPI **无删除端点**——删文件只能机主客户端手动，永不承诺自动清理。
5. 面向用户永不暴露 knowledge_base_id / media_id / folder_id / 签名 URL。

## §1 资产速览

实例、端口、文件、模型三档、沙箱侧恢复源——查 [references/topology.md](references/topology.md)。名字对不上号时先读它，勿凭记忆猜路径。

## §2 灾后恢复序列（沙箱重置/会话断点后的标准动作）

按序执行，每步验证再进下一步：

1. **私钥**：`cp /mnt/agents/upload/月之游乐场/keys/<ssh_key_file> ~/.ssh/ && chmod 600 ~/.ssh/<ssh_key_file>`，`ssh ... 'echo OK'` 验证。
2. **实例侧进程盘点**：8017/8018 llama-server、17391 Knowledge API、Electron（`[e]lectron . --no-sandbox`）、ima-bridge 守护（`ima-bridg[e].cjs`）逐项 `pgrep`。
3. **应用不在**：`nohup /opt/star-owner/start-with-keyring.sh > /var/log/star-owner.log 2>&1 &`（调用会挂住，下次调用验证 CDP `curl -s 127.0.0.1:13337/json/list`）。
4. **桥接守护不在**：`cd /opt/star-owner && nohup env IMA_TARGET_KB_ID="$(cat /root/.<ima_kb_name>)" IMA_BRIDGE_LEDGER=/opt/star-owner/workspace/.ima-sync-ledger-playground.json /opt/node22/bin/node tools/ima-bridge.cjs --daemon 120 >> /var/log/ima-bridge-playground.log 2>&1 &`，验证首轮日志「跳过 N ≥0、失败 0」。
5. **会话续跑**：CDP 进「Agent 视频总结工作流」→ 点会话 → 若「已停止」点「重新开始接单」（中断任务自动回滚，勿手动清工作区）。
6. **沙箱侧工具丢失**：本技能 scripts/ 三件（cdp.py / ima_fetch.sh / start-with-keyring.sh）scp 回实例对应位置。

## §3 五管线操作要点

### 3.1 应用运行栈
启动唯一入口 `start-with-keyring.sh`（scripts/ 有正本）。UI 驱动一律走 CDP（scripts/cdp.py：`eval/click/shot`）；X11 仅处置钥匙串弹窗。停止应用用精确模式 `pkill -f "[e]lectron . --no-sandbox"`，杀与起分两次 SSH 调用，重启后必验桥接守护。

### 3.2 百炼云供应商（LLM 主用）
工作区端点 + 礼赠钥（`/root/.<bailian_key_file>`），模型 qwen3.8-flash 主 / qwen3.7-flash 备。新增/改供应商必须应用已解锁钥匙串（见 pitfalls 第 14 条）。主钥（`/root/.bailian_api_key`）401 失效留档勿用。烧后回填 tokens 台账。

### 3.3 本地回退与判官池
8018 摘要池为云挂时的回退；8017 判官池永不擅杀。切换供应商=CDP 进「AI 模型配置」改会话绑定，不动进程。

### 3.4 ima-bridge 同步
命令见 §2 第 4 步。排障先查日志 `tail /var/log/ima-bridge-playground.log`：「新同步 0、跳过 N」=健康；「失败」按 pitfalls 第 18 条对号。改代码先 `.bak`。目标库变更=换 `IMA_TARGET_KB_ID` + 新台账路径重启。

### 3.5 ENAMETOOLONG 字节补丁
已打在实例 `workspace.js`（`fitNameToBytes`，245 字节帽，`]` 边界落刀）。应用升级覆盖文件后须重打——补丁逻辑与单测口径见 pitfalls 第 17 条。

## §4 IMA 检索与学习

端点表与纪律见 [references/ima-api.md](references/ima-api.md)。快查：`search_knowledge` 单词逐个试；读原文用 scripts/ima_fetch.sh（签名链不外泄）。检索游乐场库建模/拓扑/Tripo 知识时同此。

## §5 故障对号入座

一切报错先翻 [references/pitfalls.md](references/pitfalls.md)（23 条实证坑，按 ①进程与 SSH ②应用与 CDP ③凭据与钥匙串 ④补丁与协议 ⑤B站与网络 分组）。坑单没有的再实录补入——本文件是活的。

## §6 全程实录

裁定书正本 `/mnt/agents/output/星藏家-Linux移植裁定与华为云算力方案.md`（§1-§十：P0 部署、P1 云转向、归口游乐场、补丁实录、燃烧台账）。重大变更续写裁定书，并在本技能 pitfalls 补坑。
