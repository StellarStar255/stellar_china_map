#!/usr/bin/env python3
"""《百二秦关》河流数据管线：下载 Natural Earth 10m 河流，按名单裁剪到战国区域。

产物: data/vectors/rivers_qin.json
说明: 《山河之限》的 borders.json / rivers.json 同样来自 Natural Earth 50m/10m
      （国界线 + 鸭绿江/图们江等），当时的处理脚本未保留，数据文件已入库为准。
"""
import json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools/.tiles_cache/ne10_rivers.geojson")
OUT = os.path.join(ROOT, "data/vectors/rivers_qin.json")

KEEP = {"Yellow","Yangtze","Wei","Jing","Fen","Han","Huai","Jialing","Min","Xiang","Zhang","Liao","Luan"}
BB = (100.0, 25.0, 124.5, 42.5)   # lonMin, latMin, lonMax, latMax
inb = lambda p: BB[0] <= p[0] <= BB[2] and BB[1] <= p[1] <= BB[3]

if not os.path.exists(CACHE):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_rivers_lake_centerlines.geojson",
        CACHE)

def clip_line(line):
    out, cur = [], []
    for p in line:
        if inb(p): cur.append(p)
        elif cur: out.append(cur); cur = []
    if cur: out.append(cur)
    return [l for l in out if len(l) >= 2]

def dp(pts, tol):
    if len(pts) < 3: return pts
    def d2(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx-ax, by-ay
        if dx == dy == 0: return (px-ax)**2 + (py-ay)**2
        t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)))
        return (px-ax-t*dx)**2 + (py-ay-t*dy)**2
    keep = [0, len(pts)-1]; stack = [(0, len(pts)-1)]
    while stack:
        i, j = stack.pop()
        if j <= i+1: continue
        mi, md = -1, 0
        for k in range(i+1, j):
            dd = d2(pts[k], pts[i], pts[j])
            if dd > md: md, mi = dd, k
        if md > tol*tol:
            keep.append(mi); stack += [(i, mi), (mi, j)]
    return [pts[i] for i in sorted(set(keep))]

d = json.load(open(CACHE, encoding="utf-8"))
rivers = {}
for f in d["features"]:
    n = f["properties"].get("name_en") or f["properties"].get("name") or ""
    if n not in KEEP: continue
    g = f["geometry"]
    lines = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    for l in lines:
        for seg in clip_line(l):
            seg = [[round(p[0], 4), round(p[1], 4)] for p in dp(seg, 0.008)]
            rivers.setdefault(n, []).append(seg)

# 'Han' 需排除任何非中国汉水的同名河（本区域内汉水均在 116°E 以西）
if "Han" in rivers:
    rivers["Han"] = [l for l in rivers["Han"] if all(p[0] < 116 for p in l)]

json.dump({"rivers": [{"name": k, "lines": v} for k, v in rivers.items()]},
          open(OUT, "w", encoding="utf-8"), separators=(",", ":"))
print("done:", os.path.getsize(OUT)//1024, "KB,", len(rivers), "rivers")
