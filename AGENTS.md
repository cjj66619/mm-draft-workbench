# mm-draft-workbench — 数学建模「初稿项目」工作台（Devin 使用说明）

由 [mm-workbench](https://github.com/cjj66619/mm-workbench) 迭代而来。区别：mm-workbench 的产物是一篇 Typst/LaTeX 论文；本仓库的产物是一个**自包含、Windows 可复现的初稿项目文件夹**（`projects/<年>-<题号>/`），交给人/后续智能体继续排版、优化图、补实验、润色。

本仓库本身只在 Devin/Ubuntu 运行；**输出项目在 Windows 上只靠 Python 就能重跑数据处理、模型、绘图与自检**。Word 初稿在 Devin 侧生成一次并冻结，用户在 Windows 上直接用 Word 编辑，不重生成。

## 入口

| 场景 | 调用 |
| --- | --- |
| 拿到题目/附件，出一版初稿项目 | `draft-kickoff`（内含 draft-writing 写法说明） |
| Markdown 章节 → Word 初稿并冻结 | `docx-build` |
| 只想新建/升级项目骨架 | `python3 .agents/skills/draft-kickoff/scripts/new_draft_project.py <dir> --title ... [--update-tools]` |

## 流程

```text
draft-kickoff(生成骨架) → 2analysis-modeling → data-auditor-cleaner → 3coding-visual → robustness-checker
    → 4drawio / scibox-diagram → draft-writing(paper/sections/*.md) → docx-build(--freeze) → 6verity / consistency-auditor / quality-assurance-auditor
```

阶段之间只通过文件交接（`plan.md`、`todo.md`、`reports/*.md`、`code/`、`results/`、`figures/`、`paper/`），不要假设上一阶段的对话上下文仍在。

## 输出项目的硬规则（写在项目内 `AGENTS.md`，此处摘要）

1. **数值单一真源**：`results/` → `reports/RESULTS_REPORT.md` → Word；`data/raw/` 只读；固定随机种子。
2. **Windows 可复现**：`pathlib.Path`、文本 I/O 显式 `encoding="utf-8"`、子进程用 `sys.executable`，不依赖 bash/xvfb/draw.io CLI/pandoc/LibreOffice。`python tools/portability_check.py .` FAIL 必须为 0。
3. **一图一文件夹**：`figures/<fig_id>/{make_figure.py, data.csv, <id>.pdf/png/svg, README.md, manifest.json, review.json}`；脚本统一 `from mm_plot_style import apply_style, figsize, save_fig, snapshot_data`，`save_fig(fig, HERE / FIG_ID, source=..., params=...)` 自动版式 lint（字图重叠/越界/尺寸不均/配色越界）并写 review。docstring 五要素：回答什么问题 / 图元↔机理 / 每列含义与来源 / 参数与种子 / 已知缺陷。
4. **示意图是草稿**：drawio 技术路线图/模型结构图交付 `.drawio + PNG/PDF + REDRAW_NOTES.md`，明确标注需人工重画；PNG/PDF 在 Devin 侧用 `scibox-diagram/scripts/export_figure.py` 导出。
5. **Word 冻结后为唯一真源**：`paper/DOCX_FREEZE.json frozen=true` 后不再运行任何重生成命令覆盖 `paper/main.docx`；`paper/sections/*.md` 仅作历史源。
6. **正文干净**：不出现 `reports/`、`figures/`、`AGENTS.md` 等内部名与占位符。
7. **交接写实**：`HANDOFF.md` 记录每阶段状态与最近一次完整复现的平台/结果；未在 Windows 实测就不要写"已验证"。

## 仓库维护

- `SKILL.md` frontmatter 只保留 `name` 与 `description`。
- 改工具脚本（`3coding-visual/scripts/*.py`、`draft-kickoff/scripts/portability_check.py`）后，对已生成项目用 `new_draft_project.py <dir> --update-tools` 同步。
- 自检：`python3 -m compileall -q .agents/skills`；`python3 .agents/skills/draft-kickoff/scripts/portability_check.py .agents/skills/3coding-visual/scripts .agents/skills/draft-kickoff`；新建临时项目跑 `python doctor.py && python run_all.py`。
- 第三方来源与许可见 `THIRD_PARTY_NOTICES.md`；`projects/` 默认被 `.gitignore` 忽略，不要提交比赛数据、队号、API Key。
