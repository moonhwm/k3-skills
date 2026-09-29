#!/bin/bash
# 用法: ima_fetch.sh <media_id> — 取 IMA 原文转文本到 stdout，不回显任何 id/签名链
MID="$1"
KB="$(cat /root/.<ima_kb_name>)"
URL=$(/opt/node22/bin/node /opt/ima-skill/ima_api.cjs "openapi/wiki/v1/get_media_info" "{\"knowledge_base_id\":\"$KB\",\"media_id\":\"$MID\"}" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[\"data\"][\"url_info\"][\"url\"] if d.get(\"code\")==0 else \"\")")
[ -z "$URL" ] && echo "FETCH_FAIL" && exit 1
TMP=$(mktemp /tmp/imadoc_XXXXXX)
curl -s "$URL" -o "$TMP"
case "$MID" in
  markdown_*|word_md*) cat "$TMP" ;;
  word_*) unzip -p "$TMP" word/document.xml 2>/dev/null | python3 -c "
import sys,re
x=sys.stdin.read()
x=re.sub(r\"</w:p>\",\"\n\",x)
x=re.sub(r\"<[^>]+>\",\"\",x)
print(x)" ;;
  *) file "$TMP"; head -c 2000 "$TMP" ;;
esac
rm -f "$TMP"
