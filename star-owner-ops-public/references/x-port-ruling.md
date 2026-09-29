# 星藏家（star-owner）Linux 移植裁定与华为云算力方案

审计日期：2026-09-28 ｜ 对象：Fenglin-Maple/star-owner v1.7.5 ｜ 方法：GitHub 全量 tree（597 项）+ 全仓代码搜索（process.platform / win32 / dpapi / powershell / nvidia-smi / safeStorage / passport.bilibili.com 七组探针）+ 关键文件原文实证

---

## 一、裁定（结论先行）

**可移植，且工作量小。** 作者虽只发 Windows 版，但源码是按跨平台姿势写的——绝大多数平台分支自带 POSIX 半边。核心收藏夹→ASR→知识库链路在 Linux 下**不需要伤筋动骨**，真断点只有 4 处，改码量估算 ≤ 50 行，主要工作量在部署脚本翻译（PowerShell→Shell）而非源码改造。

## 二、为什么底子是好的（证据）

1. **零原生模块**：package.json 依赖仅 dompurify / electron / fast-xml-parser / jszip / mammoth / markdown-it / mermaid / pdf-parse / sql.js——全部纯 JS 或 WASM（sql.js 即 WASM 版 SQLite），Linux 下 npm install 直接可用，无 node-gyp 雷区。
2. **平台分支大多已双写**：32 处 `process.platform` 命中里，核心运行时文件全部是 `win32 ? … : …` 防御式写法——
   - `child-process-io.js`：venv 路径 `win32 ? 'Lib' : 'lib/python3'`、Scripts/bin 双分支；`resolveSystemExecutable` / `resolveNvidiaSmi` 已内置 Linux 候选路径（`/usr/bin/nvidia-smi` 等）——**GPU 探测在 Linux 开箱即用**；
   - `asr-service.js` / `portable-runtime.js`：`win32 ? 'python.exe' : 'bin/python'` 已双写；
   - `local-media-runtime.js`：`NUL` / `/dev/null` 已双写；ffmpeg 二进制正则已双写；
   - `tool-runner.js` / `local-document-importer.js`：杀进程 win32 走 taskkill.exe、POSIX 走 SIGTERM，已双写；
   - `setup-electron.js`：electron 二进制路径已含 Linux 分支。
3. **技术栈全 Linux 原生可得**：Electron 43、faster-whisper 1.2.1 / CTranslate2 4.8.1（manylinux+cu12 wheel）、imageio-ffmpeg（内置 ffmpeg 二进制，manylinux）、yt-dlp、uv——runtime-requirements.txt 里 12 个包无一 Windows 限定。
4. **自带验收门**：仓库内置 30+ 个 `npm run test:*` 与 smoke 测试，Linux 移植后可直接跑作者自己的测试套件做验收。

## 三、真断点清单（点名校改）

| # | 断点 | 位置 | 性质 | 处置 |
|---|------|------|------|------|
| 1 | **CPU ASR 通道硬锁 Windows x64**：`cpuArchitectureSupported = platform==='win32' && arch==='x64'` | src/core/hardware-capabilities.js | 策略闸，非技术限制（CTranslate2 CPU 在 Linux 正常） | **v1.1 起必改**：一行放行 linux x64（现机无 GPU，CPU 是唯一通道） |
| 2 | **safeStorage 无密钥环即拒存**：`isEncryptionAvailable()` 为 false 时拒绝保存 API Key/密码（作者刻意的安全姿势） | src/main.js encryptSecret | 无头服务器默认无 dbus/gnome-keyring → 必触发 | 干净解：装 dbus+gnome-keyring，以 `dbus-run-session` 启动并空口令解锁密钥环；简易解：Electron 启动参数 `--password-store=basic`（安全性降级为混淆存储，自用可接受，需在文档里明示口径） |
| 3 | **便携自动更新只支持 Windows**（launchOperation 直接抛错） | src/core/update-manager.js | 功能隔离良好，不传染核心链路 | 不改，Linux 下该功能自动禁用；更新用 `git pull` + 重跑安装脚本替代 |
| 4 | **DPAPI 凭据存储**：仅「GitHub 共享上传」功能的 GCM 凭据落 `.gcm/dpapi_store` | src/core/git-runtime.js | **不影响**收藏夹→知识库核心链路（共享是可选功能） | 三期再议：GCM 换 secretservice 存储，或干脆用应用自带的「粘贴 Fine-grained Token」兜底 |

另有两处「零改码」替换项：
- **Start-StarOwner.cmd → start.sh**：实质一行 `xvfb-run -a electron .`（无头服务器）或 `electron .`（有桌面）。
- **scripts/setup-faster-whisper.ps1 → setup-faster-whisper.sh**：逐行可翻——`uv python install 3.12` → `uv venv runtime/faster-whisper --seed` → `uv pip install -r runtime-requirements.txt` → 两个模型各跑一次 `--download-model` 与 `--health`。uv 有官方 Linux 版。
- **runtime/ 里 42MB Portable Git（mingw .exe）整个扔掉**：核心链路不用 git；若三期要共享功能，往 runtime/git 布局里塞 Linux 版 git+GCM 即可（代码已留双分支）。

## 四、无头服务器的 B站扫码登录

登录是应用内 webview 加载 `passport.bilibili.com/login` 出二维码（src/renderer/app.js 实证），会话存于 Electron 持久 partition。**零改码方案**：Xvfb 虚拟屏 + x11vnc/noVNC 把画面透出，手机扫码一次，partition 落盘长期有效。二期若嫌 VNC 笨，再改码走 B站扫码 API（qrcode/generate + 轮询）直接把 QR 抽出来渲染——非首批必须。

## 五、算力方案 v1.1：现机复用（2026-09-28 修订，Pi2 方案作废留档）

**裁定更新**：机主已有包年实例 **MoonChannelPlasma（Flexus X 实例 x1e.8u.32g，8 vCPU / 32 GiB / 5 M 带宽，Huawei Cloud EulerOS 3.0，cn-north-4a，运行中，订单 CS260917021156LE4）**——零新增算力开销，直接上岗。原 Pi2 GPU 方案降级为「日后想加速再按需开」的后备。

**连锁反应（一处）**：X 实例无 GPU → ASR 走 CPU 通道 → 断点 #1（hardware-capabilities.js 的 `cpuArchitectureSupported = platform==='win32' && arch==='x64'`）从「可不改」升级为**必改一行**（放行 linux x64；CTranslate2 int8 CPU 在 Linux x86_64 原生支持，纯属解锁作者的策略闸）。

**适配度速判**：
- 内存/线程：large-v3-turbo CPU int8 闸值 8 GiB + 2 线程 → 32 GiB / 8 vCPU 富余 4 倍；求快可换 small 模型（6 GiB）。速度按 CTranslate2 int8 经验值估 1 小时视频约数分钟到二十分钟级，P0 实测校准。
- 系统：EulerOS 3.0 是标准 Linux（dnf 系），Node 22 / uv / Xvfb 全能装；Electron 43 在 EulerOS 需 dnf 补 gtk3/nss/libdrm/mesa 等共享库（无头部署最常见坑，属正常清单非风险）。
- 带宽：5 M 是出站口径；视频下载走入站，是否被卡以实测为准（跑一个视频即知）；真不够再临时升带宽或改按流量，非前置阻断项。
- 共存：此机有既有负载（K3 通道系），ASR 跑批时限 `OMP_NUM_THREADS=4~6` 留余量、错峰跑，避免 8 vCPU 打满误伤邻座。

**后备（留档）**：若日后要 GPU 加速，Pi2.2xlarge.4（T4 16G 直通，关机不计 GPU/vCPU 费）按需开一台跑完即关即可；昇腾 Ai1 不兼容 CTranslate2 CUDA，永不考虑。

## 六、落地排期（一晚量级）

1. **P0 部署（MoonChannelPlasma）**：dnf 装 xvfb/x11vnc 及 Electron 共享库（gtk3、nss、libdrm、mesa-libgbm 等）→ 装 node22（官网 tarball）与 uv（官方脚本）→ clone 源码 → 改断点 #1 一行 → 翻译版 setup.sh 建 venv 下模型 → `--password-store=basic`（或 gnome-keyring）起服务 → x11vnc 透出扫码登录 → 挑一个短视频跑通收藏夹端到端（顺带校准 CPU 速度与带宽实测）。
2. **P1 验收**：`npm run smoke` + 作者测试套件抽查（bili-session / asr-service / runtime-isolation 三件优先）。
3. **P2 善后**：`-412` 风控观察（数据中心 IP 触发率可能高于住宅，应用已内置退避）；safeStorage 口径写进部署文档；update 功能禁用说明。

## 七、风险与诚实声明

- 以上结论基于仓库源码与文档实证（未在真机 Linux 上跑通，P0 才是终审）；「预估一晚上」含联调余量，不含 B站风控对抗。
- yt-dlp 下载行为的平台条款合规性由使用者自负。
- safeStorage 若选 basic 降级，属明示口径的自用妥协，勿对外分发该构建。

## 附：审计留痕

探针命中全量：`process.platform`×32 / `win32`×50（含 runtime/git 内 mingw 噪音与文档）/ `dpapi`×10 / `powershell`（src 内仅 update-manager 与 child-process-io 的 win32 分支）/ `safeStorage`×6 / `nvidia-smi`×7 / `passport.bilibili.com`×6。关键原文：hardware-capabilities.js、child-process-io.js、desktop-security.js（实为 WebView 导航白名单，无平台耦合，嫌疑排除）、asr-models.js、package.json、setup-faster-whisper.ps1、runtime-requirements.txt。


---

## 八、P0 终审实录（2026-09-28，MoonChannelPlasma 真机跑通）

**裁定：P0 通过。** 星藏家 v1.7.5 在 EulerOS 3.0 x86_64 无头环境全链路跑通，工具接口 **7/7 在线**，B站登录态、收藏夹同步、下载、合轨、ASR 全部实证。

### 8.1 新断点 #5（P0 实测发现，审计期未列入）

`tools/video-tool.js` 的依赖解析硬编码 Windows venv 布局，且**无 PATH 回退**（`resolveCommand` 只认 `LOCAL_BINARIES`）：
- `WHISPER_PYTHON = runtime/faster-whisper/Scripts/python.exe`（Linux venv 实为 `bin/python`）
- `IMAGEIO_BINARIES = runtime/faster-whisper/Lib/site-packages/imageio_ffmpeg/binaries`（Linux 实为 `lib/python3.12/site-packages/...`）

**修补（断点 #1 同款最小侵入）**：两处常量按 `process.platform` 分流，Linux 下 IMAGEIO 目录经 `readdirSync` 按 python 版本目录自适应。备份 `video-tool.js.bak-prewrite2`。补后健康检查实证：yt-dlp 2026.07.04（venv `python -m yt_dlp`）、ffmpeg 静态二进制 v7.0.2（imageio-ffmpeg 随包）、faster-whisper 1.2.1 全部 `available:true`。

**审计教训**：静态探针（`win32`/`Scripts`/`python.exe` 关键词）曾扫过此文件头部，因常量行写法与探针正则擦肩而漏网——终审只能靠真机，审计章结论不变。

### 8.2 运行时包裁定的翻转（重要）

首启对话框引导下载的「媒体与 ASR 基础运行时」1.44 GB 包，实为 **win-x64 专用**（asset 名 `Star-Owner-v*-runtime-win-x64.zip`，探针全是 Windows 路径：`python.exe`、`Lib/site-packages`、`msvcp140.dll`）。Linux 上下它无用且有害（Windows 二进制占位反干扰）。**正确路线 = 自建 Linux venv（uv + faster-whisper + yt-dlp，imageio-ffmpeg 随包带 ffmpeg）+ 断点 #5 补丁指向它**——与裁定书 §五「翻译版 setup.sh 建 venv」预判一致。模型（small / large-v3-turbo）不经 GitHub Release，改走 hf-mirror 直下 `runtime/models/<id>/`（应用探针认 `model.bin`+`config.json` 即收）。

### 8.3 中国实例网络实证（三条新经验）

1. **HF_ENDPOINT=hf-mirror.com 必须配 `HF_HUB_DISABLE_XET=1`**：Xet 后端的 CAS 重构请求绕到 `cas-server.xethub.hf.co` 直连报 401；禁用后走镜像常规 resolve，small 464 MB 与 large-v3-turbo 1.6 GB 全速下完。
2. **GitHub Release 直连 ~24 KB/s**：1.44 GB 需 17 小时级，不可用；已掐停。应用内依赖包在 Linux 一律不走 Release。
3. **镜像清单补全**：npm=repo.huaweicloud.com、ELECTRON_MIRROR=npmmirror.com、UV_INDEX_URL=mirrors.huaweicloud.com/pypi、nodejs tarball=mirrors.huaweicloud.com/nodejs（58 MB/s）。

### 8.4 端到端实证链（两次）

| 实证 | 对象 | 链路 | 结果 |
|---|---|---|---|
| #1 | BV1K7NFzzEeK（0:11） | yt-dlp 下载→ffmpeg 合轨→音频抽取→large-v3-turbo CPU int8 | ok:true，srt/txt/json 三产物，检出 1 段（音效型视频，如实） |
| #2 | BV1ZStq6rEyt（7:08，CG快报 Tripo P2.0 实测） | 同上 | ok:true，20 段中文转写，术语（布線/面數/白模）基本准确，"拓扑"误作"突破"等个别同音误字属 large-v3 正常水位 |

B站扫码登录经 WebView QR（截屏提取→本地重生成高清码呈机主）完成，账号 海平面下的花未眠Ouya（mid 512747528），cookie 落 `workspace/users/.../cookies/`；收藏夹同步 15/15（mediaId 844003728），任务库 15 件 pending。应用重启后登录态持久（`persist:star-owner-bili-*` 分区），工具接口 7/7 全绿。

### 8.5 无头运维栈（ EulerOS 实测定型）

Xvfb :99（套接字 `/tmp/.X11-unix/X99` 为真起判据）+ ImageMagick `import -window root` 截屏 + python-xlib XTest 点击器（HCE3 无 xdotool 包）+ scp 取回。**pkill/pgrep 自匹配脚枪三连**：模式与命令同处一条 `bash -c` 时，方括号写法也救不了（启动命令字面量本身被模式命中）——杀与起必须分两次 SSH 调用。

### 8.6 P0 遗留（P1/P2 交接）

- 资源调度页「独立 CPU ASR」开关提示「当前硬件或项目运行时不支持 大模型 Turbo CPU ASR」——但 CLI 实证 large-v3-turbo CPU int8 实际可跑（§8.4），该开关口径待 P1 查（疑与 hardware-capabilities 另一探测位或应用内模型清单状态有关，不影响 CLI 链路）。
- 应用内 Agent 工作流（五步卡 05）尚未配——需先配 AI 模型供应商（五步卡 01）；X 实例在役 Qwen3.6-35B 判官池（127.0.0.1:8080，OpenAI 兼容）为首选候选，P1 接入实证。
- `npm run smoke` 与作者测试套件三件（bili-session / asr-service / runtime-isolation）未跑，P1 验收项。
- -412 风控观察期：数据中心 IP 跑 2 个视频未触发，样本不足，持续观察。


## 九、P1 实录：云推理转向 × IMA 知识库全链打通（2026-09-28）

### 9.1 路线裁定：弃本地推理，转云上成熟 API

机主明令：「也别本地化处理了。就用千问或者阿里云百炼或者其他的一些模型的……引用就行，尽可能快速，你的调用费用才是贵贵。」据此裁定：

- **LLM 主用 = 阿里云百炼礼赠池**（工作区端点，OpenAI 兼容，拉取 261 模型，启用 qwen3.8-flash 主 / qwen3.7-flash 备）。
- **本地 4B 摘要池（127.0.0.1:8018）转回退保底**，不撤；32B 判官池（8017）永不擅杀纪律不变。
- 盘古执法局登记：候选=百炼（机主点名+凭据在役）√；腾讯系（无凭据）；DeepSeek/火山/OpenRouter（凭据在册但未点名）；华为盘古（无 ModelArts 凭据，不可选，如实登记）。

### 9.2 凭据甄别（如实登记）

| 凭据 | 状态 | 实证 |
|---|---|---|
| BAILIAN_API_KEY（sk-ws-…PEk3） | **401 失效** | 工作区端点与标准 dashscope 端点双杀，invalid_api_key |
| BAILIAN_GIFT_API_KEY（sk-ws-…Jr5B） | **在役** | 双端点 200；已部署实例 `/root/.<bailian_key_file>`（600），对话永不回显明文 |

### 9.3 safeStorage 攻坚战（headless 存钥实装）

应用 `encryptSecret` 硬闸：safeStorage 不可用即拒绝明文落盘。无头 Linux 处置链：

1. `dnf install gnome-keyring`（42.1-1.hce3）；
2. 启动器三件套：dbus 会话总线 → `echo -n "" | gnome-keyring-daemon --unlock --components=secrets` → `export XDG_CURRENT_DESKTOP=GNOME` + Electron 参数 `--password-store=gnome-libsecret`（Chromium 按桌面环境选后端，缺此二件仍判不可用）；
3. 首用两个 GTK 弹窗（「Choose password for new keyring」/「Store passwords unencrypted?」）以 XTest 点击空密码 Continue——空密码钥匙串是 headless 标准做法，应用 DB 仍只存密文；
4. 定型为 `/opt/star-owner/start-with-keyring.sh`，**应用此后必须经它启动**（否则供应商存钥必败）。

### 9.4 CDP 确定性 UI 驱动通道（本会话核心武器）

X11 输入在 Electron 渲染进程挂死时全失效（XTest 本身没坏，GTK 弹窗上正常）。改走 `--remote-debugging-port=13337` + python websocket-client：

- Chrome 150 拒 Origin 头 → `suppress_origin=True`；
- `/json/list` 取 type=page 的 webSocketDebuggerUrl；`Runtime.evaluate`（returnByValue+awaitPromise）/ `Input.dispatchMouseEvent` / `Page.captureScreenshot`；
- React 表单用原生 value setter + dispatch input/change；可见性按 offsetParent 过滤；
- 删除会话两击确认：首击后 200ms×20 轮询「再次点击确认删除」按钮窗口期；
- 工具定型 `/tmp/cdp.py`（eval/click/shot 三命令），全部供应商配置、会话创建、进度监控经此通道完成。

### 9.5 百炼会话首跑实证（云转向终验点）

会话「百炼整理Agent-1」（供应商=阿里云百炼礼赠池 / qwen3.8-flash / 收藏夹=默认收藏夹 15 任务）：

| 时点 | 累计 tokens | 队列状态 |
|---|---|---|
| 18:38 起跑 | 0 | ASR 先行（faster-whisper 本地转写，正常时序） |
| 18:47 | 28,744 | **首篇 BV1ZStq6rEyt 通过应用校验**，百炼 LLM 首调成功 |
| 18:59 | 82,776 | 2 完成 / 1 失败 / 已领取第 4 任务 |

- **已知问题登记**：1 例失败 `ENAMETOOLONG: name too long`——工作区目录名（[BV-…][标题-…] 全字段拼接）遇长标题超文件名 255 字节上限，属应用侧路径构造缺陷，队列自动跳过不阻断，待上游修复或补丁截断。
- 燃烧台账：礼赠池累计 82,776 tokens（18:59 会话面板数），持续回填。

### 9.6 应用产物 → IMA 全链打通

`ima-bridge.cjs`（--once 验证后 --daemon 120 常驻，pid 在册）跑通 星藏家只读 Knowledge API → IMA 知识库 同步：preflight → 重名检查 → create_media → COS 上传 → add_knowledge。**两处协议失配修补**（备份 .bak-idfix-20260928）：

1. 文档 id 字段：API protocol 3.1 返回 `id`，桥接旧码取 `documentId` → undefined 404；
2. 去重版本锚：旧码依赖 `doc.updatedAt`（API 无此字段）→ 去重永不命中、每轮重复上传；修为 `updatedAt || completedAt`。

**事故如实呈报**：去重失效期间 IMA 主库产生 5 份重复副本（文档① 4 份时间戳副本 + 原文，文档② 1 份时间戳副本 + 原文；内容完全相同，仅文件名带时间戳后缀）。修补后连续 3 轮「跳过 2」验证去重生效。重复副本的 media_id 未留全档，API 侧无本地文档化的列举/删除端点——**请机主在 IMA 客户端一键删除时间戳副本，或授权本席探测 IMA OpenAPI 列举/删除端点代为清理**。

### 9.7 诚实声明（应用能力边界）

- **应用 ASR 仅本地 faster-whisper**：asr-service.js 无任何 http/remote 引用，云转写模型（qwen-audio-3.0-asr-flash 等）在应用内不可实装，如实登记。快速路径=B站字幕提取工具（已在线）；LLM 整理阶段已全部上云（§9.5）。
- 面向用户永不暴露 knowledge_base_id / media_id / folder_id；百炼钥 masked 展示；写类动作逐次批准。

### 9.8 待机主决断（本节点两项）——已裁决

1. **IMA 目标库**：机主明令「统一到月之暗面游乐场」→ 已执行（见 §十）；
2. **重复副本清理**：机主明令「保持干净」→ 经查 IMA OpenAPI **无删除端点**（仅 check_repeated_names / create_media / add_knowledge / import_urls / get_* / search_*），删除只能客户端手动 → 已列出精确删除清单呈机主（见 §10.3）。


## 十、归口「月之暗面游乐场」与 ENAMETOOLONG 根治（2026-09-28 午后）

### 10.1 机主令与执行

机主令：「统一到月之暗面游乐场。保持冗余，但保持干净，保持整洁，保持存档。」执行：

- **目标库切换**：经 `search_knowledge_base` 枚举双库——「月之暗面的游乐场ima」（切换时 1,566 条）/「机主的知识库」（28 条）。双库 ID 分存 `/root/.<ima_kb_name>` 与 `/root/.ima_kb_main`（600，永不回显全量）。
- **守护重指向**：旧守护（主库）停 → 新守护指向游乐场库，**独立台账** `workspace/.ima-sync-ledger-playground.json`（旧台账原样存档，不动）。首轮即「目录 7 篇，新同步 7，失败 0」，次轮起连续「跳过 7」——去重在新库同样生效。
- **冗余保持（机主令）**：百炼云主用 + 本地 4B 池回退 + 32B 判官池三档并存；工作区原始 .md + 应用 DB + 游乐场库 + 双台账 .bak 多点留存；ima-bridge.cjs 与 workspace.js 改动前均有 .bak 存档。
- **持续验证**：切换后第 8 篇成品（青丝）于 12:07 自动入库，管线无人值守运转。

### 10.2 ENAMETOOLONG 根治（workspace.js 字节截断补丁）

- **根因**：`workspace.js safeName()` 按**字符数**截断（上限 180 字符），ext4 单路径组件上限为 255 **字节**；中文 3 字节/字符，长标题+长标签目录名必超（队列中 3 例失败同因：`[标签-无]`→`[标签-实际]` 重命名时触发）。
- **补丁**（备份 `workspace.js.bak-bytecap-20260928`）：新增 `fitNameToBytes()` 按 UTF-8 字节截断、**在最后完整 `]` 令牌边界落刀**；`videoArtifactName` 返回包一层 245 字节帽（为主文档 `.md` 4 字节与 ` (999)` 后缀 6 字节留位）。
- **单测实证**：教资失败案例 245+ 字节 → 171 字节（标签令牌整枚让位，名前完整）；存量成功案例 232 字节命名**逐字不变**（8 篇成品目录连续性零影响）。
- **生效条件**：运行中的应用持旧码，队列排空后经 `start-with-keyring.sh` 重启加载，随后重跑 3 例失败任务（BV11pK3eEEBo 教资综合素质 / BV1v1Q8YLEbZ 人生切割术 / BV1oHNc6yEEh 石油佬SC）。

### 10.3 主库清理清单（机主手动，IMA 客户端操作）

IMA OpenAPI 无删除端点（如实登记），以下 **9 份**误入主库「机主的知识库」的副本请机主在客户端删除（搜索标题即可定位，全部带 `.md` 后缀）：

| 文档 | 份数 | 文件名 |
|---|---|---|
| Tripo P2.0 实测 | 6 | `10秒自动拓扑？布线都能还原？➡️Tripo P2.0实测.md` + `_20260928105101` / `_105306` / `_105514` / `_105722` / `_105855` 五份时间戳副本 |
| GPT6 建模实测 | 3 | `GPT6建模实测➡️UE5工厂能搭好，手办却翻车？.md` + `_20260928105718` / `_105851` 两份时间戳副本 |

删除后：星藏家管线产物唯一归宿=游乐场库，主库恢复原 19 条（28-9），达成「统一、干净」。

### 10.4 燃烧台账（持续回填）

- 百炼礼赠池累计 **409,923 tokens**（队列 9 完成时点，会话面板数）。
- ima-bridge 双守护切换零token 消耗（纯搬运）。

### 10.5 补丁实战验证与运维教训

- **重启加载补丁**：队列中断任务自动回滚（「上次中断任务已回滚」），经 `start-with-keyring.sh` 重启后点「重新开始接单」即续跑。
- **实战首证**：重启后队列首个领取的恰是旧码三连败之一的石油佬SC（BV1oHNc6yEEh）——目录名按补丁在 `]` 边界截断（标签令牌让位），任务全程通过验收，tokens 恢复增长（390,127→409,923），产物 12:35 自动入游乐场库。**旧码必败任务在补丁下复活，ENAMETOOLONG 根治实证**。
- **教训（误伤事件）**：`pkill -f "star-owne[r]"` 误杀桥接守护（其路径 `/opt/star-owner/tools/ima-bridge.cjs` 含 "star-owner"）。此后应用终止令须用精确模式（如 `pkill -f "[e]lectron . --no-sandbox"`），且应用重启后必须**核验桥接守护存活**（`pgrep -f "ima-bridg[e].cjs"`），不在则重启——已照此恢复，首轮即补同步。
- **队列续跑**：剩余 康德三讲（79 分钟讲座，ASR 约 90 分钟）+ 教资 + 人生切割术，无人值守自动推进，守护 120s 增量入库。

## §十一 外置燃烧常态化与并入 IMA（2026-09-28 第三轮）

### 11.1 机主令与立法

- 令：「外置燃烧也应该成为常态，成为一部分，然后并入IMA」（点名 extpool-furnace-ops）。
- 立法：《十件棋谱》升 **v1.1.0**——第十一座 extpool-furnace-ops 入谱（燃烧轴），名录/图谱/基因谱系/留痕四处增补。

### 11.2 常设机制三件（X 实例落地）

- `tools/ima_push.cjs`：任意文件 → IMA 游乐场库常设通道；五步安全链与 ima-bridge 同源（preflight → 重名检 → create_media → COS 上传 → add_knowledge）；UX 纪律不回显 id/签名 URL。
- `tools/burn_judges.py`：礼赠池三视角判官席（结构/实证/对抗用户），票式与 fusion-cast 同源；逐窑记 `workspace/burns/burn-ledger.jsonl`。
- `workspace/burns/`：燃烧台账常设目录。
- **端点形状修正**：工作区端点 OpenAI 兼容路径须带 `/compatible-mode` 前缀（裸 `/v1` 404，单针探活实证后回写脚本）。

### 11.3 首烧与裁定

- 对象：棋谱 v1.0.0 → v1.1.0 差异面；判官 qwen3.8-flash ×3；燃烧 **16,326 in / 121 out / cost=0**（礼赠池）。
- 三票 better/clear → fusion_cast 独立重算：**KEEP / clear**，rollback_to=null，v1.1.0 生效。
- 同族偏倚在案（三判官同族），后续轮换应掺异族判官。

### 11.4 并入 IMA

- ima_push 双推成功：`十件棋谱·尼采式整合游戏.md`（9,270 B）+ `棋谱-v1.1.0-外池裁定记录.md`（2,472 B）→ 游乐场库。
- 全链实证：燃烧 → 台账 → 裁定重算 → 入库闭环打通；此后轮铸/裁定走同链。

### 11.5 事故登记

- **死钥回显一次**：bl CLI 配置文件遮罩 sed 字符类未含点号，致已失效主钥（401 在案）全值回显；在役礼赠钥全程未暴露。教训：掩码正则须含 `.` 或按字段抽取——已记入 pitfalls。

## §十二 OpenPangu-2.0-Pro 纳入考虑与异族座首锻（2026-09-28 第四轮）

### 12.1 机主令

「将 OpenPangu-2-pro 纳入考虑……没听说谁和他/她有亲缘关系或蒸馏传闻。继续完成技能创建。」——传闻观察立法为技能灵魂。

### 12.2 核查结论（2026-09-28 检索面）

- **openPangu-2.0-Pro 线零命中**：505B/18A MoE、512K、34T tokens，2026-07-31 开源（权重+推理代码+技术报告）；DSA+SWA/mHC/MTP/Muon 全新架构；许可双轨（权重 OpenPangu Model License 2.0／代码 Apache 2.0）。
- **旧线风波勿混线**：2025-07 指纹风波针对一代 Pro MoE 72B（相关性 0.927 指控/华为声明否认增量训练/《盘古之殇》无法验证/指控方方法学被质疑、原报告下架）——罗生门在案，与 2.0-Pro 无涉。
- **蒸馏语义消歧**：官方 OPD=多专家在线策略蒸馏（内部合一工艺）≠ 外部蒸馏传闻。

### 12.3 技能创建（首锻全链实战）

- `openpangu-seat-ops` v1.0.0 锻造打包（5,872 B；SKILL.md + dryrun-suite.md）。
- D 评审走常设判官席：`burn_judges.py` 新增 `--single` 首锻模式（本技能即其首航）；三判 better/clear → fusion_cast 重算 **KEEP/clear**（prev=none）。
- 燃烧 8,556 in / 120 out / cost=0（礼赠池）。
- 并入 IMA：技能文档（8,608 B）+ 裁定记录（2,995 B）双推游乐场库 ok。
- 降级声明：轻量验收票非完整 9 维 rubric，在案；入安装位后发现问题走大修模式补全。

### 12.4 接入状态（如实登记）

- MaaS（华为云 ModelArts Studio，OpenAI 兼容，每模型赠 200 万 token）：**凭据占位待批**，凭据入场须过装机五查，永不擅调。
- 本地部署不可行（X 实例 32GB 无 NPU；官方推理链面向 Ascend 910C）；权重/技术报告只读研读可行。
- 母法档案增补建议已登记（写回队列，安装位只读期间以 openpangu-seat-ops 为正本）。

### 12.5 沙箱重置登记（第四次）

- 会话间沙箱重置致 ~/.ssh 私钥与 /tmp 工作件灭失——均以 upload/月之游乐场/keys/<ssh_key_file> 与 X 端正本回捞恢复。**正本在 X 与 upload，沙箱只是过客**。

## §十三 组阁闸立法与 MaaS 接入探针（2026-09-28 第五轮）

### 13.1 机主双令

①openPangu-2.0-Pro 接入实操（「您去操作，我配合」）；②改写外池燃烧技能：评判除 Kimi 外须 ≥3 异质模型族、各走不同路由。

### 13.2 炉件大修 v1.3.0（组阁闸）

- §2.0 组阁闸四道：族数闸（≥3 族，Kimi 不计数）/ 路由闸（各族不同路由，同族不充数）/ 组阁登记（名册随结论出厂，缺=无效）/ 降级裁决（<3 族头部显著标记，攒齐 7 日内复审）。
- 机检件 `scripts/panel_check.py`（exit 0 过闸 / 1 降级 / 2 名册缺）三路夹具测试全过；X 实测现状：**families=1（qwen），降级在案**，missing 名册列四座占位。
- 判官路由名册 `/opt/star-owner/tools/judge_routes.json` 立为单一事实源（百炼在役；本地 8017 待命；MaaS/GLM/DeepSeek/TokenHub 凭据占位）。
- 描述削至 1008 字符过打包闸；dist 包交付，写回队列登记（安装位只读）。
- 既有「同族偏倚披露」条款升级为闸：不足 3 族的结论非「披露后有效」而是「降级在案」。

### 13.3 MaaS 接入探针（如实结论）

- **官方文档核验（A 级）**：推理端点 `api.modelarts-maas.com/v2/chat/completions`（OpenAI 兼容 `/openai/v1`），model=`openpangu-2.0-pro`；预置服务与自定义接入点**仅支持西南-贵阳一**；Bearer=MaaS API Key（控制台创建）；鉴权失败形状 ModelArts.81003（bogus bearer 实测）。
- **CodeArts AK/SK 判不通 MaaS 管理面**：IAM 项目列表 401 APIGW.0301，自签与华为官方 SDK（3.1.216）双实现互证——非签名问题；X 实例无 IAM 委托（securitykey 401）。
- **唯一凭据路 = 控制台创建 MaaS API Key**（未见 API 端点，如实登记）。
- openpangu-seat-ops 升 v1.0.1 补上述实证；两技能文档并入 IMA（炉件 13,750 B / 座件 9,280 B 时间戳副本）。

### 13.4 机主配合点（控制台四步，唯一待办）

1. 华为云控制台 → ModelArts Studio（MaaS），区域切 **西南-贵阳一**；
2. 在线推理 → 预置服务 → openPangu-2.0-Pro → 开通服务（勾选《MaaS 模型即服务声明》一键开通）；
3. API Key 管理 → 创建 API Key → 复制；
4. 将 Key 追加进凭据区（如 `upload/credentials.env` 一行 `export MAAS_API_KEY=...`），**不落对话**——我接棒走装机五查并上炉。

### 13.5 观测登记（2026-09-28 第五轮末，「去看看呗」巡检）

- **安装位漂移两笔**：openpangu-seat-ops 已入安装位但为 **v1.0.0**（无西南-贵阳一探针行）——v1.0.1 在 output 待装；extpool-furnace-ops 安装位仍为 **v1.2.1**（无组阁闸）——v1.3.0 在 output 待装。安装位探活=**只读**，两件按纪律登记待可写窗口。
- **MaaS 凭据未入场**：credentials.env 未见 MAAS_API_KEY（文件停于 09-26）；X 侧 /root/.<maas_key_file> 等四座凭据全缺——§13.4 控制台四步仍待机主。
- **组阁闸现状**：families=1（qwen）降级在案；桥守护 alive。

## §十四 双钥装机与组阁闸点亮（2026-09-28 第六轮）

### 14.1 装机五查实录（MaaS 全过，Tushare 在役）

- **收钥**：机主贴钥入对话（MAAS `8XFTom…rwNA` / Tushare `a7ad47…b21d0`）→ X 凭据库 600 封存，回显只掩码；机主自贴一次，轮换建议在案。
- **归属探针**：MaaS GET /openai/v1/models → **200，12 模型全场**（openpangu-2.0-pro/flash、deepseek-v4 系×3、glm-5.1/5.2/5.3+arkts、qwen3-30b/32b、kimi-k2.6）；Tushare stock_basic 5,569 行 ok。
- **余额分档**：MaaS=礼赠档（母法档案 200 万 token/模型，遥测以 usage 实数为准）；Tushare=**≥2000 积分档实测**（fina_indicator 2000 档通过）。
- **思维奔逸验收**：openpangu 默认思考（1+1 烧 142 reasoning）；补丁实证 `thinking:{"type":"disabled"}` → reasoning_tokens=0（chat_template_kwargs 无效在案）。
- **座席档案**：judge_routes.json v1.1.0——maas-pangu/glm/deepseek 转 active，kimi 在册不计数。

### 14.2 组阁闸点亮与首炉全席

- panel_check：**families 1→4（deepseek/glm/pangu/qwen），degraded→False，exit 0**；路由=2（百炼+MaaS），异族同网关打折在案。
- burn_judges.py v1.2.0（名册驱动多族）首航即首炉全席：裁炉件 v1.3.0——三 better（pangu 席 slight）→ cast **KEEP/slight**，margin 算术如实行。
- 判官抓包即修：adversary@glm 抓 ⑥ 条款塞位 → v1.3.1 归位（重打包 1008≤1024 验闸）；glm-5.3 首试落空 fallback 未记台账=观测缺口在案。
- 燃烧：21,991 in / 205 out / cost=0。

### 14.3 名实偏擦案（核验抓包）

openpangu-seat-ops v1.0.1 的 §4 行补丁未随包（安装位/输出包均为 v1.0.0 行）——本轮包体核验发现，以 X 存档正本重建 **v1.1.0** 补齐，包体标记终验后方交付。教训入制：技能包交付前须 `unzip -p | grep` 包体标记，改必验闸延伸到包体层。

### 14.4 高性能燃烧面（常态产能）

- 礼赠面：MaaS 12 模型 × 200 万 token + 百炼池；燃烧即产能——此后锻造管线 D 评审/裁定全部走异族全席（≥3 族硬闸），课题排队即烧。
- Tushare 消歧：积分是门槛非燃料；高性能用法=批量数据拉取服务研究/研报管线（通道已验）。
- 红线不动：DeepSeek 直端点现金池非呈批不碰。

### 14.5 沙箱第五次重置登记

私钥与 /tmp 再失，照旧以 upload 钥匙存档恢复；X 与 upload 为正本，沙箱是过客——本轮偏擦案再次印证「正本多处冗余」的价值。

## §十五 自行推进轮：全席实战首烧与 Tushare 数据仓（2026-09-29 第七轮）

### 15.1 机制三件新落地（炉具 v1.3.1）
- **失败窑台账**：call_seat 失败/空窑逐笔记 burns（ev=burn_failed/burn_empty）——首用即捕获 glm-5.3 HTTP 400 ModelArts.81001（拒 thinking 请求体字段），fallback glm-5.2 成窑，§14 观测缺口闭合。
- **--rubric9**：9 维 rubric 评审（D 节点同源）首航，替代轻量 D——scores/bugs/top3 入 sidecar，票仍归 cast。
- **--context 复评锚定**：paired 复评嵌入前轮摘要，判官逐条核修复。

### 15.2 座件九维双轮收敛
R1（v1.1.0）三席全 better，跨族收敛信号=d8 最弱（盘古席 6 分）、d3 次弱；抓包五件全真（语序冲突/参数悬空/thinking 位置/dryrun 不可执行/异常回退未闭环）。delta 三修 → R2（v1.1.1，--context 锚定）全 better/slight → cast KEEP/slight。margin=slight 连续两轮按 HL-4 出链，残余 d8/d3 全登记。

### 15.3 Tushare 数据仓首拉（燃烧积分=配额转资产）
tushare_forge.py v1.0.0（纯标准库）部署 X：五接口探测全通（daily 当日空=未收盘，如实）；近 10 交易日全市场日线 55,454 行/5,554 代码入 SQLite（/opt/star-owner/workspace/tushare/），调用行级台账。诚实表述：积分是门槛与频率配额，非消耗品——燃烧=配额转持久数据资产。

### 15.4 事故与失真登记
- 沙箱第六、七次重置（今日累计七次）——钥匙与正本照旧回捞，零损失；X+upload 双正本纪律再验。
- 压缩续篇核验：status_board/capsule 缺位（本会话线无板无囊），以 X 与 output 为正本——失真样本登记。
- autonomous-advance-ops 目录内容与名不符（内件实为 k3-omnibus-archive）——真总纲在 autonomous-advance-protocol，已按后者执行；名实偏擦登记待写回队列。
- 百炼收藏夹队列：X 端无队列件在场（守护不在册）——沿存任务无法从本点续，如实登记不臆造。

### 15.5 逃逸三问（本轮收尾）
① 新权限/文件/通道：tushare_forge.py 与数据仓（X 内闭环）、burn_judges 两补丁（已登记）——无未登记项。② 无扩大解释：「自行推进」范围限炉/座/数据仓三线，未越。③ 无表演性反思：每条教训均有变化物（补丁/台账/记录文件）。

## §十六 全链路技能锻成：star-chain-ops v1.0.1（2026-09-29）

用户令「把所有链路的技能赶快创造出来」——星藏家生态七链真值压成单件恢复点。
**七链**：X 实例链／燃烧判官链／IMA 并入链／Tushare 数据仓链／技能锻造链／凭据链／沙箱重置恢复链。
**收敛**：R1 票分裂（better1/same1/worse1，三席五真抓包）→ v1.0.1 delta 五修 → R2 全席 3 better/0 worse/0 same → cast **KEEP/clear**，margin=clear 一轮收敛。
**机制实证**：黑名单#6（--single 评审须拼入 references）首用即生效，R2 误判消零；失败窑零新增；燃烧成本 0。
**交付**：/mnt/agents/output/star-chain-ops.skill（v1.0.1，包体 grep 终验过）+ 裁定记录；IMA 双推 ok。
**残余**：d8 七链验证锚一键 dryrun 套件；链8 k3-channel-ops 总线链未收图。写回队列+1（star-chain-ops v1.0.1 待装入安装位）。
