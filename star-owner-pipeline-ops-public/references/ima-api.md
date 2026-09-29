# IMA OpenAPI 实战速查（v1.1.10 技能包实证）

## 认证

`/opt/ima-skill/ima_api.cjs <apiPath> <jsonBody>` —— 自动按序读 `IMA_CLIENT_ID`/`IMA_OPENAPI_CLIENTID` 环境变量或 `~/.config/ima/{client_id,api_key}`（600）。返回 `{code, msg, data}`，`code!==0` 即败。

## 端点表（实测）

| 端点 | 用途 | 关键约束 |
|---|---|---|
| `openapi/wiki/v1/search_knowledge_base` | 枚举/搜索知识库 | **limit ≤20**（超限报 code 51） |
| `openapi/wiki/v1/search_knowledge` | 库内检索 | 多词查询可能 0 命中，换单词逐个试 |
| `openapi/wiki/v1/get_knowledge_list` | 浏览库内容 | 分页 cursor |
| `openapi/wiki/v1/get_media_info` | 取原文签名链 | 返回 `data.url_info.url`（res-skb.ima.qq.com 签名 URL，**永不外泄、永不写进对话**） |
| `openapi/wiki/v1/check_repeated_names` | 上传前重名预检 | 重名须改名（桥接加时间戳后缀） |
| `openapi/wiki/v1/create_media` → COS 上传 → `add_knowledge` | 上传三步 | 见 ima-bridge.cjs 实现 |
| `openapi/wiki/v1/import_urls` | 导入网页 | 技能包文档登记，未实测 |

**IMA OpenAPI 无删除端点**（2026-09-28 实证+文档确认）——删文件只能在 IMA 客户端手动。任何"自动清理副本"的承诺都是假话。

## 目标库纪律

- 现役目标库 = 「月之暗面的游乐场ima」，ID 存 `/root/.<ima_kb_name>`；主库 ID 存 `/root/.ima_kb_main`（均 600）。
- 命令里用 `"$(cat /root/.<ima_kb_name>)"` 引用，**stdout 永不打印全量 ID**。
- 面向用户永不暴露 knowledge_base_id / media_id / folder_id / 签名 URL。

## ima_fetch.sh（scripts/ 正本）

```bash
/tmp/ima_fetch.sh <media_id>   # 取原文到 stdout：markdown 直出，docx 解 document.xml 剥标签
```

内部链：get_media_info → curl 签名链 → 按 media_id 前缀分流解析 → 临时文件即删。

## ima-bridge.cjs（实例 /opt/star-owner/tools/）

- `--once` 单轮验证；`--daemon 120` 常驻（**每次应用被重启后必验存活**）。
- 环境变量：`IMA_TARGET_KB_ID`（目标库，用 $(cat ...) 喂）、`IMA_BRIDGE_LEDGER`（台账路径，现役=workspace/.ima-sync-ledger-playground.json）。
- 链：Knowledge API 目录 → 全文分页 → preflight → 重名检查 → create_media → COS → add_knowledge → 台账（mediaId+appUpdatedAt 去重锚）。
- 两处协议补丁见 references/pitfalls.md 第 18 条；改前必有 `.bak`。
