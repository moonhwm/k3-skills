import json, sys, time, base64, urllib.request
import websocket

DEBUG = "http://127.0.0.1:13337"

def get_page_ws():
    tabs = json.load(urllib.request.urlopen(DEBUG + "/json/list", timeout=5))
    for t in tabs:
        if t.get("type") == "page" and "devtools" not in t.get("url", ""):
            return t["webSocketDebuggerUrl"], t.get("url", "")
    raise RuntimeError("no page target: " + json.dumps(tabs)[:300])

class CDP:
    def __init__(self):
        self.ws_url, self.url = get_page_ws()
        self.ws = websocket.create_connection(self.ws_url, timeout=30, suppress_origin=True)
        self.mid = 0
    def cmd(self, method, params=None):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.mid:
                if "error" in msg:
                    raise RuntimeError(json.dumps(msg["error"]))
                return msg.get("result", {})
    def eval(self, expr):
        r = self.cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        res = r.get("result", {})
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:400])
        return res.get("value")
    def click(self, x, y):
        for t in ("mousePressed", "mouseReleased"):
            self.cmd("Input.dispatchMouseEvent", {"type": t, "x": x, "y": y, "button": "left", "clickCount": 1})
            time.sleep(0.12)
    def shot(self, path):
        r = self.cmd("Page.captureScreenshot", {"format": "png"})
        with open(path, "wb") as f:
            f.write(base64.b64decode(r["data"]))
        return path

if __name__ == "__main__":
    c = CDP()
    print("page:", c.url)
    op = sys.argv[1]
    if op == "eval":
        print(json.dumps(c.eval(sys.argv[2]), ensure_ascii=False)[:3000])
    elif op == "click":
        c.click(int(sys.argv[2]), int(sys.argv[3]))
        print("clicked", sys.argv[2], sys.argv[3])
    elif op == "shot":
        print(c.shot(sys.argv[2]))
