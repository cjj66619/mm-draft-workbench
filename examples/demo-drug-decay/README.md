# 口服药物血药浓度的一室模型参数估计与给药方案模拟

> 数学建模论文初稿项目（由 mm-draft-workbench 生成，2026-09-07）。
> 这是一个**自包含、可复现**的项目文件夹：Windows / Linux / macOS 上只要有 Python 3.10+ 就能重跑所有数据处理、模型与图。

## 5 分钟上手

```text
python doctor.py          # 1. 体检：缺什么包会直接告诉你 pip install 什么
python run_all.py         # 2. 复现：code/ → figures/ → 图自检 → 可移植性检查
```

Windows 可直接双击 `run_all.bat`（等价于第 2 步）。运行结果见 `reports/RUN_STATUS.md`，详细日志在 `reports/_logs/`。

## 交付物在哪

| 想要 | 位置 | 说明 |
| --- | --- | --- |
| Word 初稿 | `paper/main.docx` | **唯一真源**，直接用 Word 编辑。`paper/sections/*.md` 是生成它的历史源，冻结后不再重生成（见 `paper/README.md`） |
| 建模思路 | `reports/ANALYSIS_MODELING_REPORT.md` | 问题拆解、假设、符号、模型公式、求解策略、决策记录 |
| 数据说明 | `reports/DATA_REPORT.md` | 原始附件清单、清洗步骤、质量问题 |
| 结果数值 | `reports/RESULTS_REPORT.md` + `results/` | 论文中所有数字的唯一来源 |
| 数据处理代码 | `code/00_*.py` | 读 `data/raw/`（只读）→ 写 `data/clean/` |
| 模型代码 | `code/10_*.py`, `20_*.py`… | 每问一个脚本，固定随机种子，结果写 `results/` |
| 图 | `figures/<fig_id>/` | **一图一文件夹**：图（PDF/PNG/SVG）+ `make_figure.py` + 数据快照 + `README.md`（机理说明）+ `review.json`（版式自检） |
| 技术路线图 / 模型结构图 | `figures/<fig_id>/*.drawio` + PNG/PDF | 机器生成的**草稿**，交稿前必须按 `REDRAW_NOTES.md` 人工重画 |
| 图的总索引与审图清单 | `figures/README.md`, `figures/FIGURE_REVIEW.md` | `python run_all.py figcheck` 重建 |
| 给智能体的说明 | `AGENTS.md`, `HANDOFF.md` | 规则、当前状态、下一步 |

## 目录结构

```text
.
├── README.md / AGENTS.md / HANDOFF.md / plan.md / todo.md / project.yaml
├── run_all.py  run_all.bat  doctor.py  requirements.txt
├── problem/          题面与附件说明
├── data/raw/         原始数据（只读，不要改）      data/clean/  清洗结果
├── code/             00_数据处理  10_/20_模型  90_汇总  common.py(路径/种子/保存工具)
├── results/          模型输出（csv/json）
├── reports/          建模报告、数据报告、结果报告、运行状态
├── figures/          一图一文件夹（见上）
├── paper/            main.docx（冻结）  sections/*.md（历史源）  DOCX_FREEZE.json
└── tools/            随项目交付的绘图/检查脚本与字体（不依赖仓库，Windows 可用）
```

## 修改与优化怎么做

- **改模型/参数**：改 `code/` → `python run_all.py code figures` → 数值进 `results/` 与 `reports/RESULTS_REPORT.md` → 手工同步到 Word（Word 是真源，数字以报告为准）。
- **改一张图**：改 `figures/<fig_id>/make_figure.py` → `python run_all.py figures <fig_id>` → 看 `figures/<fig_id>/review.json` 的自检 → 把新 PNG 插回 Word。
- **绘图优化**：看 `figures/FIGURE_REVIEW.md`，逐条清零 `text_overlap` / `legend_over_data` / `font_size_spread` / `color_off_palette` 等发现；自检不能替代肉眼，务必打开 PNG 看。
- **补实验**：新增 `code/3x_*.py` 与 `figures/figNN_xxx/`，在 `reports/RESULTS_REPORT.md` 记录数值来源，再改 Word。
- **文字润色 / 格式调整**：直接在 Word 里做；不要再跑 Markdown→Word。

## 依赖

`pip install -r requirements.txt`（numpy / pandas / scipy / matplotlib 必需；pymupdf / openpyxl / scikit-learn / PyYAML 可选）。
中文字体随项目放在 `tools/fonts/`（TrueType），保证 Windows 与生成时出图一致；没有时回退到系统 SimHei/微软雅黑。

## 已知限制

- 示意图（技术路线图、流程图、模型结构图）由程序排版，只保证"结构正确"，不保证论文级美观；请在 draw.io 里按 `REDRAW_NOTES.md` 重画。
- 数据图的自动版式检查（重叠/越界/字号/配色）覆盖常见问题，但不能替代人工审图。
- Word 初稿的格式（字体、行距、图表编号）按通用中文论文格式生成，投稿/参赛模板细节需在 Word 中调整。
