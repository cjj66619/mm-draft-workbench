# AGENTS.md — 给在本项目上工作的智能体 / 协作者

本文件是本项目文件夹的**规则**；当前状态与下一步看 `HANDOFF.md`；决策记录看 `plan.md`；待办看 `todo.md`。
先读这四个文件，再读 `reports/ANALYSIS_MODELING_REPORT.md` 与 `reports/RESULTS_REPORT.md`，最后才动代码。

## 0. 环境与运行

- 目标平台：Windows / Linux / macOS，**只依赖 Python 3.10+**（`requirements.txt`），不依赖 bash、draw.io CLI 或任何办公软件。
- 入口只有两个：`python doctor.py`（体检）、`python run_all.py [code|figures|figcheck|paper|check|<fig_id>]`（复现 + 自检）。
- 所有脚本以项目根为工作目录运行；路径一律 `pathlib.Path`，相对 `code/common.py` 里的 `ROOT`；文本 I/O 一律显式 `encoding="utf-8"`；子进程用 `sys.executable`。
- 提交前跑 `python tools/portability_check.py .`，FAIL 必须清零。

## 1. 单一真源（改数字前先看这里）

| 内容 | 真源 | 派生物 |
| --- | --- | --- |
| 论文正文 | `paper/sections/*.md`（一章一文件，顺序与元数据在 `paper/paper.yaml`） | 无。这就是论文终稿，按提交质量写 |
| 所有数值 | `results/*.csv|json` → 汇总在 `reports/RESULTS_REPORT.md` | 正文里的数字、图上的标注 |
| 模型定义 | `reports/ANALYSIS_MODELING_REPORT.md` §模型 + `code/1x_*.py` | 正文的模型章节 |
| 数据 | `data/raw/`（只读）→ `code/00_*.py` → `data/clean/` | `results/`、`figures/*/data.csv` |
| 图 | `figures/<fig_id>/make_figure.py` + 该文件夹内数据快照 | 同文件夹的 PDF/PNG/SVG |

规则：
1. `data/raw/` 只读。清洗逻辑全在 `code/00_*.py`，输出到 `data/clean/`。
2. 改了代码 → 必须重跑 `python run_all.py code figures` → 更新 `reports/RESULTS_REPORT.md` → 再改 `paper/sections/*.md` 里的数字。不允许只改正文里的数字。
3. 正文只有一份：`paper/sections/*.md`。润色、改结论、换图都直接改它；图/表/公式用 `{#fig:x}` `{#tbl:x}` `{#eq:x}` 标签与 `@fig:x` 引用，不手写编号。改完跑 `python run_all.py paper`（交叉引用、图路径、占位符、内部名泄露），FAIL 必须清零。
4. 所有随机过程固定种子（`common.set_seed(42)`），能从干净状态一遍跑通。
5. 论文正文中不得出现内部路径/工作流名（`reports/`、`figures/`、`results/`、`AGENTS.md`、`plan.md`、`todo.md`、`run_all`），也不得有占位符。图片引用路径 `../../figures/<id>/<id>.pdf` 是唯一例外。

## 2. 图（一图一文件夹）

```text
figures/fig02_q1_fit/
├── make_figure.py     # 唯一生成脚本：模块 docstring 必须写清 ①回答什么问题 ②每个图元对应什么机理 ③每列数据含义与来源 ④参数与种子 ⑤已知缺陷
├── data.csv           # 绘图所需数据快照（由 snapshot_data 自动拷来，别手改；改数据请改 code/）
├── fig02_q1_fit.pdf/.png/.svg
├── README.md          # 自动生成：数据来源、参数、字体、自检结果（保留人工补充段）
├── manifest.json      # 自动生成：文件、脚本、来源、参数、字体、检查
└── review.json        # 自动生成：版式自检发现（FAIL/WARN/INFO）
```

- 只用 `tools/mm_plot_style.py`：`apply_style()` → 画 → `save_fig(fig, folder / "fig02_q1_fit", source=..., params=...)`。它自动产出 PDF/PNG/SVG、快照数据、README/manifest/review，并跑字体检查与版式 lint。
- 同一字符串不要混用中文与 `$公式$`（Matplotlib mathtext 不做字体回退，中文会变 ¤）：公式单独 `ax.text()`，标签用纯中文或纯 ASCII。
- 尺寸用 `figsize("full"|"half"|"third")`（版心 16 cm；aspect 控高）；字号 7–9 pt；配色用 `PALETTES`，同一概念全篇同色。
- **绘图优化清单**（`figures/FIGURE_REVIEW.md` 自动汇总，逐条清零）：
  `text_overlap` 字图重叠 · `text_clipped` 文字越界 · `legend_over_data`/`text_over_data` 图例/标注压数据 · `tick_crowded` 刻度拥挤 ·
  `font_too_small`/`font_size_spread` 字号过小/不统一 · `color_off_palette`/`label_color_inconsistent` 配色越界/不一致 ·
  `panel_size_uneven`/`panel_label_misaligned` 子图大小不均/标签不齐 · `fig_too_wide` 超宽 · `axis_label_missing` 缺轴标签 ·
  `pdf_text_overlap`/`pdf_text_outside`/`pdf_line_through_text` PDF 级重叠/越界/线穿字。
- 自检是启发式，不能替代肉眼：改完图**必须打开 PNG 看一眼**，并在 `README.md` 的"人工审图"段记录结论。
- 示意图（技术路线图、流程图、模型结构图）：`figures/<fig_id>/*.drawio` 是源，PNG/PDF 是已导出的成品；它们是**草稿**，交稿前必须按同文件夹 `REDRAW_NOTES.md` 在 draw.io 里手工重画（元素清单、箭头语义、已知重叠都写在里面）。不要求安装 draw.io CLI；用桌面版/网页版打开 `.drawio` 编辑后 File → Export 导出即可。

## 3. 代码

- `code/common.py`：`ROOT/DATA_RAW/DATA_CLEAN/RESULTS/FIGURES`、`set_seed()`、`save_table()`、`save_json()`、`load_clean()`。所有脚本 `from common import *` 风格取路径，不要自己拼。
- 命名：`00_数据处理`、`10_问题1模型`、`20_问题2模型`…、`90_汇总`；`_` 开头的文件 run_all 跳过。
- 每个脚本头部 docstring：输入（哪些文件）→ 做什么（模型/方法、公式对应报告哪一节）→ 输出（写到哪）→ 运行时间量级。
- 输出到 `results/` 的 csv 用 UTF-8；面向报告的数值再汇总进 `reports/RESULTS_REPORT.md`（带来源文件名）。
- 不要引入新的重依赖（如 torch）除非 `plan.md` 记录了决策；新增依赖写进 `requirements.txt` 并标注必需/可选。

## 4. 常见任务怎么做

| 任务 | 步骤 |
| --- | --- |
| 润色 / 改文字 | 直接改 `paper/sections/*.md` → `python run_all.py paper`；改动数字要回到 §1 规则 2 |
| 绘图优化 | `python run_all.py figcheck` → 看 `figures/FIGURE_REVIEW.md` → 改 `make_figure.py` → `python run_all.py figures <fig_id>` → 看 PNG（正文引的是同名 PDF，自动更新） |
| 补实验 | 新增 `code/3x_*.py` 与 `figures/figNN_*/make_figure.py`（用 `_template_figure/` 起手）→ 重跑 → `RESULTS_REPORT.md` 加节 → 对应章节 `.md` 加内容 → `todo.md`/`HANDOFF.md` 更新 |
| 换数据 | 只改 `data/raw/`（新增文件不覆盖旧文件）与 `code/00_*.py` → 全量重跑 → 比对 `RESULTS_REPORT.md` 差异 |
| 交接 | 更新 `HANDOFF.md`（做了什么、验证了什么、剩什么、坑在哪）与 `todo.md` |

## 5. 禁止

- 修改 `data/raw/`。
- 在正文里手写图/表/公式编号（“如图 3”）——用 `@fig:x`；在 `@fig:x` 前再写“图”（会变成“图 图3”）。
- 在代码里写绝对路径、调用 bash/sh、`subprocess.run(["python", ...])`。
- 手工编辑自动生成文件：`figures/*/manifest.json`、`review.json`、`figures/README.md`、`figures/FIGURE_REVIEW.md`、`reports/RUN_STATUS.md`、`reports/PAPER_CHECK.md`。
- 编造数据、参考文献、结论；不确定的写进 `todo.md` 而不是写进论文。
