#!/usr/bin/env python3
"""构建两张交互地形图：把 data/ 里的高程与矢量数据注入 src/ 模板，生成根目录下的成品 HTML。

用法:  python3 tools/build.py            # 构建两张图
       python3 tools/build.py shanhe     # 只构建《山河之限》
       python3 tools/build.py qin        # 只构建《百二秦关》
"""
import base64, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAPS = {
    "shanhe": {
        "template": "src/shanhe_template.html",
        "dem": "data/dem_shanhe",
        "inject": {"__BORDERS__": "data/vectors/borders.json",
                   "__RIVERS__": "data/vectors/rivers.json"},
        "title": "山河之限 · 为什么中国吞得下山东，却吞不下朝鲜",
        "out": "山河之限_中国山东与朝鲜地形交互图.html",
    },
    "qin": {
        "template": "src/qin_template.html",
        "dem": "data/dem_qin",
        "inject": {"__RIVERS__": "data/vectors/rivers_qin.json"},
        "title": "百二秦关 · 为什么吞并六国的是秦",
        "out": "百二秦关_秦并六国战略地形交互图.html",
    },
}

def build(key):
    cfg = MAPS[key]
    read = lambda p, mode="r": open(os.path.join(ROOT, p), mode,
                                    encoding=None if "b" in mode else "utf-8").read()
    out = read(cfg["template"])
    out = out.replace("__META__", read(cfg["dem"] + "/meta.json"))
    out = out.replace("__HEIGHT_B64__",
                      base64.b64encode(read(cfg["dem"] + "/height.png", "rb")).decode())
    for ph, path in cfg["inject"].items():
        out = out.replace(ph, read(path))
    for ph in ("__META__", "__HEIGHT_B64__", "__BORDERS__", "__RIVERS__"):
        assert ph not in out, f"placeholder {ph} not injected"
    full = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{cfg["title"]}</title>\n'
            '</head>\n<body>\n' + out + '\n</body>\n</html>\n')
    dst = os.path.join(ROOT, cfg["out"])
    open(dst, "w", encoding="utf-8").write(full)
    print(f"{cfg['out']}  {len(full)//1024} KB")

targets = sys.argv[1:] or list(MAPS)
for t in targets:
    build(t)
