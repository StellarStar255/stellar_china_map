# Stellar China Map

Interactive China geography map — 用真实地形数据讲中国历史地理的交互图系列（山河舆图）。

- **壹 · 山河之限**：为什么中国吞得下山东，却吞不下朝鲜（`山河之限_中国山东与朝鲜地形交互图.html`）
- **贰 · 百二秦关**：为什么吞并六国的是秦（`百二秦关_秦并六国战略地形交互图.html`）

两张图均为**零依赖单文件 HTML**：数据内嵌，**双击即可离线打开**（`index.html` 是导航页，也可双击）。
Python 只在「重新生成数据」和「改源码后重新构建」时才需要，日常看图用不到。

## 启动（可选）

只有想通过 `http://localhost` 访问（如手机/局域网设备）时才需要服务器：
双击 `start_server.command`（macOS），或 `python3 -m http.server 8471`。

## 目录结构

```
├── index.html                    导航首页
├── 山河之限_….html / 百二秦关_….html   成品（由 build 生成，可直接打开）
├── src/                          页面源模板（含全部叙事文本/图层/交互逻辑，数据用占位符）
│   ├── shanhe_template.html
│   └── qin_template.html
├── data/
│   ├── dem_shanhe/  dem_qin/     高程栅格（PNG 双通道编码 + meta.json，编码公式见各 meta）
│   └── vectors/                  国界与河流（Natural Earth 裁剪简化）
└── tools/
    ├── build.py                  构建：数据注入模板 → 成品 HTML
    ├── dem_shanhe.py  dem_qin.py 高程管线：AWS Terrarium 瓦片 → height.png（可重新生成 data/）
    └── clip_rivers_qin.py        河流裁剪管线（Natural Earth 10m）
```

## 修改与重建

改文案/图层/样式 → 编辑 `src/*.html` → `python3 tools/build.py`（可带参数 `shanhe` / `qin` 只构建一张）。
改区域/分辨率 → 编辑 `tools/dem_*.py` 顶部常量并运行（需 `numpy`、`Pillow`，瓦片缓存于 `tools/.tiles_cache/`）→ 再 build。
注意：模板内高程解码公式须与 `data/dem_*/meta.json` 的编码一致（山河之限 `*4-800`，百二秦关 `*8-800`）。

## 数据与考据

- 地形：Mapzen/AWS Terrain Tiles（SRTM/GMTED/ETOPO1 合成，z6 ≈ 1.9 km/像素）
- 边界、河流：Natural Earth（朝鲜内陆河流该数据集缺失，清川江/大同江为手工概略线）
- 史实以《史记》《隋书》《战国策》《华阳国志》《资治通鉴》等为据；战国七国疆域为约前 262 年**概略示意**，
  进军路线为概略复原——正式引用请核对谭其骧《中国历史地图集》等专业文献

## Repo
