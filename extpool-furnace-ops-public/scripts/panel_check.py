#!/usr/bin/env python3
"""panel_check.py — 评判组阁闸（extpool-furnace-ops §2.0 机检件 v1.0.0）
读判官路由名册，出组阁裁定：异质族数（Kimi 不计）、路由去重、凭据在场性。
用法: panel_check.py [--roster <judge_routes.json>]
输出: 组阁 JSON（families/family_list/routes/degraded/missing/available）。
exit: 0=过闸（≥3 异质族） 1=降级（<3） 2=名册缺失/损坏。
纪律: 只读名册与凭据文件存在性（st 模式位即可），永不读凭据内容、永不外发。
"""
import argparse
import json
import os
import sys

DEFAULT_ROSTER = "/opt/star-owner/tools/judge_routes.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", default=DEFAULT_ROSTER)
    a = ap.parse_args()
    if not os.path.exists(a.roster):
        print(json.dumps({"ok": False, "error": "roster missing", "path": a.roster}))
        sys.exit(2)
    try:
        roster = json.load(open(a.roster, encoding="utf8"))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": "roster broken: %s" % e}))
        sys.exit(2)

    available, missing = [], []
    for r in roster.get("routes", []):
        key_file = r.get("key_file") or ""
        key_ok = (not key_file) or os.path.exists(key_file)
        if r.get("status") == "active" and key_ok:
            available.append(r)
        else:
            missing.append({"name": r.get("name"), "family": r.get("family"),
                            "status": r.get("status"),
                            "reason": "key absent" if (r.get("status") == "active" and not key_ok)
                                      else r.get("status")})

    families = sorted({r["family"] for r in available if r.get("family") != "kimi"})
    routes = sorted({r.get("endpoint", "") for r in available})
    degraded = len(families) < 3
    out = {"ok": True, "families": len(families), "family_list": families,
           "routes": routes, "degraded": degraded,
           "panel": [{"judge_seat": r.get("name"), "family": r.get("family"),
                      "endpoint": r.get("endpoint"), "cost_tier": r.get("cost_tier")}
                     for r in available],
           "missing": missing,
           "verdict": "PASS(>=3 families)" if not degraded
                      else "DEGRADED(%d family)——降级裁决在案，结论须头部标记" % len(families)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(1 if degraded else 0)


if __name__ == "__main__":
    main()