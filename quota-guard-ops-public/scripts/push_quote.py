#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""push_quote.py — 每日一语手机推送层（quota-guard-ops 层三）
通道抽象（优先级序，首个已配置且发送成功即停；--channel 可指定）：
  lark       飞书机器人直推（首选，bot 身份，一次授权永久有效）  config: lark-target.json
  feishu     飞书自定义机器人 webhook      env: FEISHU_BOT_WEBHOOK
  wecom      企业微信群机器人 webhook      env: WECOM_BOT_WEBHOOK
  serverchan Server酱（推送到个人微信）    env: SERVERCHAN_SENDKEY
lark 通道说明：依赖 lark-cli 已完成应用配置（bot ready）；目标用户 open_id 存于
  脚本同目录 lark-target.json（标识符非密钥，可入技能包）；appId/appSecret 由
  lark-cli 本地配置保管，永不在本脚本出现。沙箱重建后先从 /mnt/agents/upload/
  lark-cli-config-backup/ 恢复 ~/.lark-cli 即可免再授权。
红线合规：不自动化个人微信账号（无 itchat/wxauto 类通道，永不添加）。
凭证零明文：一律从环境变量读；推荐 `export X=$(grep '^X=' /mnt/agents/upload/credentials.env | cut -d= -f2-)` 注入。
用法：
  python3 push_quote.py send [--date YYYY-MM-DD] [--voice V] [--channel C|all] [--title T]
  python3 push_quote.py send --dry-run          # 只组报文不发送
  python3 push_quote.py channels                # 查各通道配置状态（不报钥值，只报在/缺）
  python3 push_quote.py --self-test             # 离线自检（零网络）
退出码：0=已送达 2=用法错误 3=无已配置通道 4=全部已配置通道发送失败
"""
import os, sys, json, urllib.request, datetime, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import daily_quote

SERVERCHAN_TPL = "https://sctapi.ftqq.com/%s.send"


def build_message(q):
    title = "每日一语 · %s" % q["date"]
    body = "%s\n\n—— %s · %s\n\n溯源：%s" % (
        daily_quote.human_line(q).split(" —— ")[0].strip("「」"),
        q["author"], q["source"] if q["source"] != "—" else "",
        q["citation"])
    if q.get("tentative"):
        body += "\n（拟体标注：译本混杂或缺藏，非逐字定本）"
    return title, body


def _post(url, payload, headers=None, timeout=12):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers or {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "ignore")[:300]


def send_feishu(title, body):
    url = os.environ.get("FEISHU_BOT_WEBHOOK", "").strip()
    if not url:
        return None, "FEISHU_BOT_WEBHOOK 未配置"
    st, resp = _post(url, {"msg_type": "text", "content": {"text": title + "\n" + body}})
    ok = '"code":0' in resp.replace(" ", "") or '"StatusCode":0' in resp
    return (ok, "HTTP %s %s" % (st, resp[:120]))


def send_wecom(title, body):
    url = os.environ.get("WECOM_BOT_WEBHOOK", "").strip()
    if not url:
        return None, "WECOM_BOT_WEBHOOK 未配置"
    st, resp = _post(url, {"msgtype": "text", "text": {"content": title + "\n" + body}})
    ok = '"errcode":0' in resp.replace(" ", "")
    return (ok, "HTTP %s %s" % (st, resp[:120]))


def send_serverchan(title, body):
    key = os.environ.get("SERVERCHAN_SENDKEY", "").strip()
    if not key:
        return None, "SERVERCHAN_SENDKEY 未配置"
    data = ("title=%s&desp=%s" % (
        urllib.parse.quote(title), urllib.parse.quote(body))).encode("utf-8")
    req = urllib.request.Request(SERVERCHAN_TPL % key, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=12) as r:
        resp = r.read().decode("utf-8", "ignore")[:300]
    ok = '"code":0' in resp.replace(" ", "")
    return (ok, resp[:120])


import urllib.parse  # noqa: E402  (serverchan 表单编码用)

LARK_TARGET_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lark-target.json")


def _lark_target():
    path = os.environ.get("LARK_TARGET_JSON", LARK_TARGET_DEFAULT)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("open_id") or None
    except Exception:
        return None


def send_lark(title, body):
    oid = _lark_target()
    if not oid:
        return None, "lark-target.json 未配置（open_id 缺失）"
    if os.system("command -v lark-cli >/dev/null 2>&1") != 0:
        return None, "lark-cli 不在 PATH"
    try:
        p = subprocess.run(
            ["lark-cli", "im", "+messages-send", "--as", "bot",
             "--user-id", oid, "--text", title + "\n" + body],
            capture_output=True, text=True, timeout=40)
        out = ((p.stdout or "") + (p.stderr or "")).replace("\n", " ")
        ok = p.returncode == 0 and '"ok":true' in out.replace(" ", "")
        return (ok, out.strip()[:160])
    except Exception as e:
        return (False, "lark-cli 调用异常: %s" % e)


CHANNELS = [("lark", send_lark), ("feishu", send_feishu), ("wecom", send_wecom), ("serverchan", send_serverchan)]


def channels_status():
    print("%-10s %s" % ("lark", "已配置（%s）" % _lark_target() if _lark_target() else "缺 lark-target.json"))
    envs = {"feishu": "FEISHU_BOT_WEBHOOK", "wecom": "WECOM_BOT_WEBHOOK", "serverchan": "SERVERCHAN_SENDKEY"}
    for name, env in envs.items():
        print("%-10s %s  %s" % (name, env, "已配置" if os.environ.get(env, "").strip() else "缺"))
    print("（lark 通道由 bot 身份直推，无需用户再授权；鉴权状态跑 `lark-cli auth status` 判定）")


def self_test():
    # 零网络：组报文 + 通道状态 + 未配置判定
    q = daily_quote.produce({"date": "2026-09-22", "voice": None, "outdir": None})
    title, body = build_message(q)
    assert title.startswith("每日一语 · 2026-09-22")
    assert "——" in body and "溯源：" in body
    assert len(body) < 2000, "报文过长"
    for env in ("FEISHU_BOT_WEBHOOK", "WECOM_BOT_WEBHOOK", "SERVERCHAN_SENDKEY"):
        os.environ.pop(env, None)
    ok, note = send_feishu("t", "b")
    assert ok is None and "未配置" in note
    os.environ["LARK_TARGET_JSON"] = "/nonexistent/lark-target.json"
    ok, note = send_lark("t", "b")
    assert ok is None and "未配置" in note
    os.environ.pop("LARK_TARGET_JSON", None)
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    _libs = ("itchat", "wxauto", "wxpy")
    banned = ["import " + w for w in _libs] + ["from " + w for w in _libs]
    for b in banned:
        assert b not in src, "红线违禁通道混入: %s" % b
    print("SELF-TEST PASS")
    print(" title:", title)
    print(" body  :", body.replace("\n", " / ")[:160])
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if len(argv) < 2 or argv[1] not in ("send", "channels"):
        print(__doc__)
        return 2
    if argv[1] == "channels":
        channels_status()
        return 0
    opts = {"date": None, "voice": None, "outdir": None}
    channel, title_override, dry = None, None, "--dry-run" in argv
    i = 2
    while i < len(argv):
        a = argv[i]
        if a == "--date":
            opts["date"] = argv[i + 1]; i += 2
        elif a == "--voice":
            opts["voice"] = argv[i + 1]; i += 2
        elif a == "--channel":
            channel = argv[i + 1]; i += 2
        elif a == "--title":
            title_override = argv[i + 1]; i += 2
        else:
            i += 1
    q = daily_quote.produce(opts)
    title, body = build_message(q)
    if title_override:
        title = title_override
    print("[报文] %s\n%s" % (title, body))
    if dry:
        print("[dry-run] 未发送")
        return 0
    pool = CHANNELS if channel in (None, "all") else [c for c in CHANNELS if c[0] == channel]
    if not pool:
        print("[FAIL] 未知通道: %s" % channel)
        return 2
    configured, failed = 0, []
    for name, fn in pool:
        ok, note = fn(title, body)
        if ok is None:
            print("[skip] %s: %s" % (name, note))
            continue
        configured += 1
        if ok:
            print("[SENT] %s: %s" % (name, note))
            return 0
        failed.append((name, note))
        print("[fail] %s: %s" % (name, note))
    if configured == 0:
        print("[FAIL] 无已配置通道——请配置 FEISHU_BOT_WEBHOOK / WECOM_BOT_WEBHOOK / SERVERCHAN_SENDKEY 之一，或由 Agent 走 lark-cli 飞书富通道（references/push-channels.md）")
        return 3
    print("[FAIL] 全部已配置通道发送失败: %s" % failed)
    return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv))