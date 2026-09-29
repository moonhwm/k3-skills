#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""daily_quote.py — K3集群 每日一语引擎（三语料 × kindle-ai-quota-dashboard）
语料纪律（voices.md 立法）：
  萧红   —— FTS5 实引，凡引号必带档号（doc#para(year)），库 xh_corpus.db
  尼采   —— epub 实时提取真实句，因译本混杂按纪律标「拟」（tentative=true）
  海德格尔 —— 云侧缺藏在册，禁伪引；显式点播时出「缺藏标记」，不入默认轮换
轮换：默认按日期序数在 [萧红, 尼采] 间交替；同一日期同一结果（确定性可复现）。
用法：
  python3 daily_quote.py today                    # 今日一句（按日期定声部）
  python3 daily_quote.py today --voice xiaohong   # 指定声部
  python3 daily_quote.py today --date 2026-09-23  # 指定日期
  python3 daily_quote.py today --outdir DIR       # 落 quote.json + 追加 quotes.md
  python3 daily_quote.py --self-test
输出 schema（对接 dashboard config/quote.json；键名对照 examples/quote.example.json 可微调）：
  {date, voice, text, author, source, citation, tentative}
"""
import os, re, sys, json, sqlite3, zipfile, datetime

XH_DB = "/mnt/agents/upload/萧红文本/xh_corpus.db"
NIETZSCHE_EPUB = "/mnt/agents/upload/nietzsche_books/1504/谁是谁的太阳：尼采随笔.epub"

# 萧红关键词轮换环（trigram 词元需≥3字，以下全部经 FTS 实库验证有命中）
XH_KEYWORDS = ["火烧云", "后花园", "呼兰河", "大泥坑", "老祖父", "小黄瓜",
               "倭瓜花", "蒲公英", "满天星", "月亮地", "商市街", "生死场",
               "牛车上", "小城三月", "马伯乐", "大太阳"]

HEIDEGGER_ABSENT = ("（海德格尔语料在册缺藏：云侧无藏，待桌面席投喂或主理人直传后入轮。"
                    "本句为缺藏标记，非引文。——书记官）")


def date_ordinal(d):
    return int(d.strftime("%Y%m%d"))


def pick_voice(d):
    return ["xiaohong", "nietzsche"][date_ordinal(d) % 2]


def quote_xiaohong(d):
    """FTS 实引：关键词环取词 → BM25 命中集 → 日期定序选段。引号必带档号。"""
    ordv = date_ordinal(d)
    con = sqlite3.connect("file:%s?mode=ro" % XH_DB, uri=True)
    kw, cands = None, []
    for step in range(len(XH_KEYWORDS)):  # 哑火回退：顺移下一词
        kw = XH_KEYWORDS[(ordv + step) % len(XH_KEYWORDS)]
        rows = con.execute(
            """SELECT p.doc, p.year, p.para, p.text
               FROM paras_fts f JOIN paras p ON p.id = f.rowid
               WHERE paras_fts MATCH ? ORDER BY bm25(paras_fts) LIMIT 40""",
            (f'"{kw}"',)).fetchall()
        for doc, year, para, text in rows:
            t = re.sub(r"\s+", "", text)
            if not (10 <= len(t) <= 120):  # 适合推送的段长
                continue
            if re.search(r"(原刊|署名|收入《|载于|载《|发表|初刊|刊于|选自|编者按)", t):
                continue  # 编务/出版注记，非文学文本
            if re.search(r"[：:，、；—…]$", t):
                continue  # 截断残句
            cands.append((doc, year, para, t))
        if cands:
            break
    con.close()
    if not cands:
        raise RuntimeError("萧红 FTS 全词环无合适段落")
    doc, year, para, t = cands[(ordv // len(XH_KEYWORDS)) % len(cands)]
    title = os.path.splitext(os.path.basename(doc))[0]
    return {
        "date": d.isoformat(), "voice": "xiaohong", "text": t,
        "author": "萧红",
        "source": "《%s》（%s）" % (title, year if year else "年份不详"),
        "citation": "%s#%s(%s) · xh_corpus.db FTS 实引 · 检索词「%s」" % (doc, para, year, kw),
        "tentative": False,
    }


def _epub_sentences(path):
    z = zipfile.ZipFile(path)
    parts = sorted(n for n in z.namelist() if n.endswith((".html", ".xhtml", ".htm")))
    blob = []
    for n in parts:
        h = z.read(n).decode("utf-8", "ignore")
        h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
        h = re.sub(r"(?s)<[^>]+>", "\n", h)
        blob.append(h)
    text = "\n".join(blob)
    text = (text.replace("&nbsp;", " ").replace("&ldquo;", "\u201c").replace("&rdquo;", "\u201d")
            .replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))
    sents = re.split(r"(?<=[。！？])\s*|\n+", text)
    out = []
    for s in sents:
        s = re.sub(r"\s+", "", s)
        # 箴言相：12-70 字、含句读、无目录/版权杂讯
        if not (12 <= len(s) <= 70):
            continue
        if re.search(r"(版权|出版|ISBN|目录|译者|序言|第[一二三四五六七八九十\d]+章)", s):
            continue
        if not re.search(r"[。！？]$", s):
            continue
        out.append(s)
    # 去重保序
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def quote_nietzsche(d):
    """epub 实时提取真实句；译本混杂，按纪律标「拟」（tentative=true）。"""
    ordv = date_ordinal(d)
    sents = _epub_sentences(NIETZSCHE_EPUB)
    if not sents:
        raise RuntimeError("尼采 epub 提取为空")
    s = sents[ordv % len(sents)]
    return {
        "date": d.isoformat(), "voice": "nietzsche", "text": s,
        "author": "尼采（拟）",
        "source": "《谁是谁的太阳：尼采随笔》",
        "citation": "epub 实时提取（译本混杂，按 voices.md 纪律标「拟」）· 句位 %d/%d" % (ordv % len(sents), len(sents)),
        "tentative": True,
    }


def quote_heidegger(d):
    return {
        "date": d.isoformat(), "voice": "heidegger", "text": HEIDEGGER_ABSENT,
        "author": "海德格尔（缺藏标记）", "source": "—",
        "citation": "晨报附页三 R24-27 在册：云侧无藏，禁伪引", "tentative": True,
    }


def human_line(q):
    tail = q["source"] if q["source"] != "—" else ""
    return "「%s」 —— %s%s" % (q["text"], q["author"], (" · " + tail) if tail else "")


def parse_args(argv):
    opts = {"date": None, "voice": None, "outdir": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--date":
            opts["date"] = argv[i + 1]; i += 2
        elif a == "--voice":
            opts["voice"] = argv[i + 1]; i += 2
        elif a == "--outdir":
            opts["outdir"] = argv[i + 1]; i += 2
        elif a in ("today",):
            i += 1
        else:
            i += 1
    return opts


def produce(opts):
    d = (datetime.date.fromisoformat(opts["date"]) if opts["date"]
         else datetime.date.today())
    voice = opts["voice"] or pick_voice(d)
    fn = {"xiaohong": quote_xiaohong, "nietzsche": quote_nietzsche,
          "heidegger": quote_heidegger}[voice]
    return fn(d)


def self_test():
    # 两日确定性 + schema + 纪律标记
    q1 = produce({"date": "2026-09-22", "voice": None, "outdir": None})
    q2 = produce({"date": "2026-09-22", "voice": None, "outdir": None})
    assert q1 == q2, "同日两次结果不一致"
    q3 = produce({"date": "2026-09-23", "voice": None, "outdir": None})
    assert q3["voice"] != q1["voice"], "相邻日未轮换"
    for q in (q1, q3):
        assert set(("date", "voice", "text", "author", "source", "citation", "tentative")) <= set(q), "schema 缺键"
        assert q["text"] and q["citation"], "引文/溯源为空"
    qn = produce({"date": "2026-09-22", "voice": "nietzsche", "outdir": None})
    assert qn["tentative"] is True and "拟" in qn["author"], "尼采未标拟"
    qh = produce({"date": "2026-09-22", "voice": "heidegger", "outdir": None})
    assert "缺藏" in qh["text"], "海德格尔缺藏标记缺失"
    qx = produce({"date": "2026-09-22", "voice": "xiaohong", "outdir": None})
    assert re.search(r"#\d+\(\d{4}\)", qx["citation"]), "萧红档号格式异常"
    print("SELF-TEST PASS")
    print(" sample xiaohong :", human_line(qx))
    print(" sample nietzsche:", human_line(qn))
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    opts = parse_args(argv[1:])
    q = produce(opts)
    line = human_line(q)
    print(line)
    print("  citation:", q["citation"])
    if opts["outdir"]:
        os.makedirs(opts["outdir"], exist_ok=True)
        tmp = os.path.join(opts["outdir"], "quote.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(q, f, ensure_ascii=False, indent=2)
        os.replace(tmp, os.path.join(opts["outdir"], "quote.json"))  # 原子落盘
        with open(os.path.join(opts["outdir"], "quotes.md"), "a", encoding="utf-8") as f:
            f.write("- %s · %s —— %s（%s）\n" % (q["date"], q["voice"], line, q["citation"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))