# 第三方来源与许可说明

本仓库为**个人参赛用途**，vendored 内容如下。任何商业用途前请先核对各上游许可。

| 目录（`.agents/skills/`） | 上游 | 许可 | 本仓库改动 |
| --- | --- | --- | --- |
| `2analysis-modeling` `3coding-visual` `4drawio` `6verity` `_references` `mathmodel-figure-templates` | [cjj66619/mm-workbench](https://github.com/cjj66619/mm-workbench)（其上游为 [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) `skills/`） | 作者自定：个人免费使用、禁止商业用途、禁止闭源分发（见上游 `docs/md/License.md`） | `3coding-visual/scripts/mm_plot_style.py`：新增 `layout=folder` 一图一文件夹、`snapshot_data`、`register_bundled_fonts`、README/manifest/review 产出、版式 lint 集成；新增 `fig_layout_lint.py`、`figure_index.py` |
| `_references/figure_style.md`、`mm_plot_style.py` 的规范来源 | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | Apache-2.0 | 参考设计原则自行实现，未 vendored 源代码 |
| `scibox-diagram` | [jihe520/sci-box](https://github.com/jihe520/sci-box) `skills/` | 上游未附独立 LICENSE，按 MathModelAgent 同等条款理解 | `scripts/export_figure.py`：Windows/macOS draw.io 可执行文件探测、UTF-8 子进程、目录递归、缺失时手动导出提示 |
| `data-auditor-cleaner` `robustness-checker` `consistency-auditor` `quality-assurance-auditor` | [zhnnky329/MathModeling-skills](https://github.com/zhnnky329/MathModeling-skills) | MIT（Copyright (c) 2026 Zhijun Zhang） | 沿用 mm-workbench 的路径适配说明 |
| `draft-kickoff` `docx-build` | 本仓库原创（`docx-build/scripts/build_docx.py` 由 mm-workbench `docx-export/scripts/paper2docx.py` 改写为 Markdown 输入） | 与本仓库相同 | — |

字体：输出项目 `tools/fonts/wqy-microhei.ttc`（文泉驿微米黑）© Qianqian Fang & WenQuanYi Project，Apache-2.0 / GPLv3 含字体嵌入例外双许可，随项目分发用于跨平台出图一致（说明见项目内 `tools/fonts/LICENSE.md`）。
