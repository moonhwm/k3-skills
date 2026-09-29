# 星藏家管线资产拓扑（2026-09-28 实测定型）

> 本文只记位置与状态，**永不记录任何密钥明文**。凭据一律从位置文件读出即用。

## 1. X 实例

| 项 | 值 |
|---|---|
| 地址 | <SERVER_IP>（MoonChannelPlasma，华为云 ECS 北京四，8vCPU/32GB，EulerOS） |
| SSH | `ssh -i ~/.ssh/<ssh_key_file> root@<SERVER_IP>` |
| 私钥恢复源 | 沙箱重置丢 `~/.ssh/<ssh_key_file>` → 从 `/mnt/agents/upload/月之游乐场/keys/<ssh_key_file>` 复制并 `chmod 600` |

## 2. 端口地图

| 端口 | 用途 | 备注 |
|---|---|---|
| 22 | sshd | — |
| 8017 | llama-server 判官池 Qwen3-32B | **永不擅杀**（pid 会变，按端口认） |
| 8018 | llama-server 摘要池 Qwen3-4B（`-t 6`） | 本地回退保底，云主用 |
| 8080 | A2A 中继 | — |
| 17391 | 星藏家只读 Knowledge API（protocol 3.1） | `/api/manifest`、`/api/knowledge/catalog`、`/api/knowledge/documents`、`.../{id}/content` 分页 |
| 8188 | ComfyUI | — |
| 13337 | Electron CDP 调试口 | 由启动器带 `--remote-debugging-port` 开启 |
| :99 | Xvfb 显示号 | 判活看 `/tmp/.X11-unix/X99` |

## 3. 实例关键文件

| 路径 | 说明 |
|---|---|
| `/opt/star-owner/` | 应用根（Electron，须 root + `--no-sandbox`） |
| `/opt/star-owner/start-with-keyring.sh` | **唯一合法启动器**（钥匙串三件套+CDP口）；直启 electron 必致 safeStorage 存钥失败 |
| `/opt/star-owner/src/main.js` | 卷首已打 undici headersTimeout 补丁（备份 `main.js.bak-mainjs-20260928`） |
| `/opt/star-owner/src/core/workspace.js` | 已打 `fitNameToBytes` 字节截断补丁（备份 `workspace.js.bak-bytecap-20260928`） |
| `/opt/star-owner/tools/ima-bridge.cjs` | IMA 同步桥（两处补丁，备份 `.bak-idfix-20260928`） |
| `/opt/star-owner/workspace/` | 任务工作区（用户/收藏夹/[BV-...] 任务目录） |
| `/opt/star-owner/workspace/.ima-sync-ledger.json` | 旧台账（主库时代，存档勿动） |
| `/opt/star-owner/workspace/.ima-sync-ledger-playground.json` | **现役游乐场台账** |
| `/root/.<bailian_key_file>` (600) | 百炼礼赠钥（在役） |
| `/root/.bailian_api_key` (600) | 百炼主钥（**401 失效留档**，勿用） |
| `/root/.config/ima/{client_id,api_key}` (600) | IMA 凭据（ima_api.cjs 自动读） |
| `/root/.<ima_kb_name>` / `/root/.ima_kb_main` (600) | 两个 IMA 目标库 ID（**用 `$(cat ...)` 引用，永不回显**） |
| `/var/log/ima-bridge-playground.log` | 桥接守护日志 |
| `/tmp/cdp.py`、`/tmp/ima_fetch.sh` | CDP 驱动器、IMA 原文抓取器（本技能 scripts/ 有正本，可回传） |

## 4. 推理三档（冗余架构）

1. **云主用**：阿里云百炼礼赠池，工作区端点 `https://<workspace_id>.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`（OpenAI 兼容），启用 qwen3.8-flash（主）/ qwen3.7-flash（备）。
2. **本地回退**：8018 摘要池 Qwen3-4B-Instruct-2507-Q4_K_M（`-c 16384 -ngl 0 -t 6`）。
3. **判官池**：8017 Qwen3-32B，永不擅杀。

## 5. 沙箱侧资产

| 路径 | 说明 |
|---|---|
| `/mnt/agents/upload/月之游乐场/keys/<ssh_key_file>` | SSH 私钥恢复源 |
| `/mnt/agents/upload/credentials.env` | 凭据总册（只经 `set -a; . ...; set +a` 入环境，零落盘） |
| `/mnt/agents/output/星藏家-Linux移植裁定与华为云算力方案.md` | 裁定书正本（§1-§十 全程实录） |
