#!/usr/bin/env python3
"""《百二秦关》高程数据管线：下载 AWS Terrarium DEM 瓦片(z6)、拼接、裁剪、量化编码。

产物: data/dem_qin/height.png + meta.json
编码: h = (R*256 + G) * 8 - 800 米（区域含川西高原，量化 8m、上限 7200m）
依赖: numpy, Pillow;  瓦片缓存在 tools/.tiles_cache/
"""
import json, math, os, urllib.request
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILE_DIR = os.path.join(ROOT, "tools/.tiles_cache"); os.makedirs(TILE_DIR, exist_ok=True)
OUT = os.path.join(ROOT, "data/dem_qin"); os.makedirs(OUT, exist_ok=True)

Z = 6
X0, X1 = 49, 54
Y0, Y1 = 23, 27
LON_MIN, LON_MAX = 100.0, 124.5
LAT_MIN, LAT_MAX = 25.0, 42.5
H_MIN, H_MAX, QUANT = -800, 7200, 8
WORLD = 256 * (2 ** Z)

merc_x = lambda lon: (lon + 180) / 360 * WORLD
def merc_y(lat):
    r = math.radians(lat)
    return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * WORLD

def fetch(z, x, y):
    p = os.path.join(TILE_DIR, f"{z}_{x}_{y}.png")
    if not os.path.exists(p):
        urllib.request.urlretrieve(
            f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png", p)
    return p

mos = np.zeros(((Y1-Y0+1)*256, (X1-X0+1)*256), dtype=np.float32)
for ty in range(Y0, Y1+1):
    for tx in range(X0, X1+1):
        a = np.asarray(Image.open(fetch(Z, tx, ty)).convert("RGB"), dtype=np.float32)
        mos[(ty-Y0)*256:(ty-Y0+1)*256, (tx-X0)*256:(tx-X0+1)*256] = \
            a[:,:,0]*256 + a[:,:,1] + a[:,:,2]/256 - 32768
    print("row", ty, flush=True)

px0 = int(round(merc_x(LON_MIN))) - X0*256
px1 = int(round(merc_x(LON_MAX))) - X0*256
py0 = int(round(merc_y(LAT_MAX))) - Y0*256
py1 = int(round(merc_y(LAT_MIN))) - Y0*256
crop = mos[py0:py1, px0:px1]
H, W = crop.shape
print(f"crop {W}x{H}, range {crop.min():.0f}..{crop.max():.0f}")

v = np.round((np.clip(crop, H_MIN, H_MAX) - H_MIN) / QUANT).astype(np.uint16)
enc = np.zeros((H, W, 3), dtype=np.uint8)
enc[:,:,0] = (v >> 8).astype(np.uint8)
enc[:,:,1] = (v & 255).astype(np.uint8)
Image.fromarray(enc, "RGB").save(os.path.join(OUT, "height.png"), optimize=True)

inv_x = lambda p: p/WORLD*360 - 180
inv_y = lambda p: math.degrees(math.atan(math.sinh(math.pi*(1-2*p/WORLD))))
meta = {"width": W, "height": H,
        "lonMin": inv_x(px0+X0*256), "lonMax": inv_x(px1+X0*256),
        "latMax": inv_y(py0+Y0*256), "latMin": inv_y(py1+Y0*256),
        "encode": f"h=(R*256+G)*{QUANT}-{-H_MIN}"}
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
print("done:", os.path.getsize(os.path.join(OUT, "height.png"))//1024, "KB")
