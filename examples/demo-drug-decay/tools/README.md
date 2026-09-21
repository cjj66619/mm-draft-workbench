# tools/ — 随项目交付的脚本与字体（不依赖任何外部仓库）

| 文件 | 用途 | 依赖 |
| --- | --- | --- |
| `mm_plot_style.py` | 统一绘图样式：`apply_style` / `figsize_cm` / `snapshot_data` / `save_fig`（一图一文件夹、PDF/PNG/SVG、manifest、README、版式 lint） | matplotlib |
| `fig_layout_lint.py` | 图版式自检：字图重叠、越界、图例压数据、字号、配色、子图尺寸；`python tools/fig_layout_lint.py figures [--strict]` | matplotlib，PDF 级检查需 pymupdf |
| `check_figures.py` | PDF 图字体审计（中文 TrueType、fonttype 42）：`python tools/check_figures.py --expect-cjk figures` | pymupdf |
| `figure_index.py` | 扫描 `figures/*/` 生成 `figures/README.md` 与 `FIGURE_REVIEW.md`；`--check` 缺文件即报错 | — |
| `paper_check.py` | 论文章节 `paper/sections/*.md` 自检：未定义/重复的 `@fig:/@tbl:/@eq:`、图片路径、占位符、内部名泄露、一级标题、摘要关键词、`paper.yaml` 一致性；写 `reports/PAPER_CHECK.md`（含图/表/公式编号表）；`python tools/paper_check.py [--strict]` | —（PyYAML 可选） |
| `portability_check.py` | 扫代码里的绝对路径、bash、GBK 编码陷阱等 Windows 跑不通的写法 | — |
| `fonts/` | 中文 TrueType 字体（文泉驿微米黑，GPLv2 + 字体例外），保证各平台出图字形一致 | — |

这些脚本由 mm-draft-workbench 在生成项目时拷入；以后要升级就整目录替换，不要在项目里 fork 修改（要改就同步回 workbench）。
