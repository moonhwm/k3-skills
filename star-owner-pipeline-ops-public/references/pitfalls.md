# 实证坑清单（每条都是真金白银烧出来的）

> 目录：①进程与 SSH ②应用与 CDP ③凭据与钥匙串 ④补丁与协议 ⑤B站与网络

## ① 进程与 SSH

1. **沙箱重置丢私钥**：`/tmp`、`~/.ssh` 随沙箱释放全失。恢复源 `/mnt/agents/upload/月之游乐场/keys/<ssh_key_file>`（chmod 600）。
2. **SSH 调用上限 ~330s**：本地 `sleep ≤240` 可用，`sleep 300+ssh` 触发 deadline_exceeded；远程有界轮询循环同样触发。一律短平快单查。
3. **nohup 启动调用会超时挂住但进程实际已起**——下次调用验证进程与端口即可，勿重复启动。
4. **pkill 双坑**：(a) 自杀——模式与命令同处一条 `bash -c` 时方括号也救不了，**杀与起必须分两次 SSH 调用**；(b) 误伤——`pkill -f "star-owne[r]"` 会命中路径含 star-owner 的桥接守护，**应用终止令用精确模式 `pkill -f "[e]lectron . --no-sandbox"`**，重启应用后必验桥接守护存活（`pgrep -f "ima-bridg[e].cjs"`），不在则重启守护。
5. **Electron 以 root 跑必须 `--no-sandbox`**，否则 FATAL。

## ② 应用与 CDP

6. **X11 输入"全失效"多为误判**：XTest 本身没坏（GTK 弹窗上正常），实为 Electron 渲染进程挂死。**首选 CDP 通道，X11 只做弹窗处置**。
7. **CDP 403**：Chrome 150 拒绝带 Origin 头的 WebSocket → `websocket.create_connection(..., suppress_origin=True)`。
8. **CDP 找页**：`/json/list` 取 `type=="page"` 且 url 无 devtools 的 `webSocketDebuggerUrl`。
9. **React 表单驱动**：原生 input/select 用 `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,"value").set.call(el,v)` + dispatch `input`/`change`（bubbles:true）；按钮需 `offsetParent!==null` 过滤可见性。
10. **删除会话两击确认**：首击「删除会话」后轮询 200ms×20 找标题「再次点击确认删除」的窗口期按钮再击。
11. **应用 UI 删除未落盘时被 pkill，重启后记录复活**（orchestrator.sqlite 是 sql.js 内存库+落盘）——删完给落盘时间。
12. **供应商保存阻塞 30s+**：多半是 GNOME 钥匙串 GTK 弹窗（无头无 prompter 永挂）——X11 截屏确认后 XTest 点 Continue。

## ③ 凭据与钥匙串

13. **凭据铁律**：仅 `set -a; . /mnt/agents/upload/credentials.env; set +a` 入环境；零凭据落盘；masked display（头6…尾4）。
14. **safeStorage 硬闸**：`encryptSecret` 在无后端时拒绝明文存钥。headless 解锁链：dnf 装 gnome-keyring → dbus 会话总线 → `echo -n "" | gnome-keyring-daemon --unlock --components=secrets` → `export XDG_CURRENT_DESKTOP=GNOME` + electron 参数 `--password-store=gnome-libsecret` → 首用两个弹窗空密码 Continue（headless 标准做法，DB 仍只存密文）。**已定型为 start-with-keyring.sh，应用必须经它启动**。
15. **百炼主钥 401 失效**（双端点 invalid_api_key），礼赠钥在役——以实例 `/root/.bailian_*` 文件状态为准，勿凭记忆。
16. **dash 无 `${VAR: -4}`**：取字符串尾部用 `bash -c` 包裹。

## ④ 补丁与协议

17. **ENAMETOOLONG（队列三连败根因）**：应用 `safeName()` 按**字符数**截断（180 字符），ext4 单组件上限 255 **字节**，中文 3 字节/字符必爆。补丁 `fitNameToBytes()`：UTF-8 字节截断、最后完整 `]` 令牌边界落刀、预算 245（给 `.md` 与 ` (999)` 留位）。改的是 `/opt/star-owner/src/core/workspace.js` 的 `videoArtifactName` 返回。**存量 ≤245 字节目录名逐字不变**。
18. **ima-bridge 两处协议失配**：(a) Knowledge API protocol 3.1 文档 id 字段是 `id` 不是 `documentId`（→ undefined 404）；(b) 去重锚 `updatedAt` API 不存在（→ 去重永不命中、每轮重复上传）。修为 `documentId: d.documentId || d.id`、`updatedAt: d.updatedAt || d.completedAt || ''`。修补后验证口径：连续轮「跳过 N」。
19. **undici headersTimeout**：应用自带 node_modules 里的 undici 默认头超时杀长流式——main.js 卷首 try{setGlobalDispatcher(new Agent({headersTimeout:3600000,...}))}catch。
20. **应用 ASR 仅本地 faster-whisper**（asr-service.js 无 remote 引用）——云转写在应用内不可实装，诚实声明；快速路径=B站字幕提取。

## ⑤ B站与网络

21. **HF_ENDPOINT=hf-mirror.com 必配 `HF_HUB_DISABLE_XET=1`**：Xet 后端绕到 cas-server.xethub.hf.co 直连 401；禁用后走镜像常规 resolve。
22. **GitHub Release 直连 ~24 KB/s 不可用**；镜像清单：npm=repo.huaweicloud.com、ELECTRON_MIRROR=npmmirror.com、UV_INDEX_URL=mirrors.huaweicloud.com/pypi、nodejs tarball=mirrors.huaweicloud.com/nodejs。
23. **-412 风控**：数据中心 IP 低强度跑未触发，样本不足持续观察——勿突发放量。
