# mm-draft-workbench — 数学建模「论文项目」工作台（Devin 使用说明）

由 [mm-workbench](https://github.com/cjj66619/mm-workbench) 迭代而来。区别：mm-workbench 的产物是一篇 Typst/LaTeX 论文；本仓库的产物是一个**自包含、Windows 可复现的论文项目文件夹**（`projects/<年>-<题号>/`）：题面、数据、代码、结果、报告、图、以及以 `paper/sections/*.md`（一章一文件）交付的论文正文。正文按可直接提交的质量写完，不是大纲。

本仓库本身只在 Devin/Ubuntu 运行；**输出项目在 Windows 上只靠 Python 就能重跑数据处理、模型、绘图、论文章节自检**；论文正文是纯文本 Markdown，不依赖任何办公软件。

## 入口

| 场景 | 调用 |
| --- | --- |
| 拿到题目/附件，出一个论文项目 | `draft-kickoff`（内含 draft-writing 写法说明） |
| 验收已写完的项目 | `6verity`（`tools/paper_check.py` + 数值一致性） |
| 只想新建/升级项目骨架 | `python3 .agents/skills/draft-kickoff/scripts/new_draft_project.py <dir> --title ... [--update-tools]` |

## 流程

```text
draft-kickoff(生成骨架) → 2analysis-modeling → data-auditor-cleaner → 3coding-visual → robustness-checker
    → 4drawio / scibox-diagram → draft-writing(paper/sections/*.md, run_all.py paper) → 6verity / consistency-auditor / quality-assurance-auditor
```

阶段之间只通过文件交接（`plan.md`、`todo.md`、`reports/*.md`、`code/`、`results/`、`figures/`、`paper/`），不要假设上一阶段的对话上下文仍在。

## 输出项目的硬规则（写在项目内 `AGENTS.md`，此处摘要）

1. **数值单一真源**：`results/` → `reports/RESULTS_REPORT.md` → `paper/sections/*.md`；`data/raw/` 只读；固定随机种子。
2. **Windows 可复现**：`pathlib.Path`、文本 I/O 显式 `encoding="utf-8"`、子进程用 `sys.executable`，不依赖 bash/xvfb/draw.io CLI/办公软件。`python tools/portability_check.py .` FAIL 必须为 0。
3. **一图一文件夹**：`figures/<fig_id>/{make_figure.py, data.csv, <id>.pdf/png/svg, README.md, manifest.json, review.json}`；脚本统一 `from mm_plot_style import apply_style, figsize, save_fig, snapshot_data`，`save_fig(fig, HERE / FIG_ID, source=..., params=...)` 自动版式 lint（字图重叠/越界/尺寸不均/配色越界）并写 review。docstring 五要素：回答什么问题 / 图元↔机理 / 每列含义与来源 / 参数与种子 / 已知缺陷。
4. **示意图是草稿**：drawio 技术路线图/模型结构图交付 `.drawio + PNG/PDF + REDRAW_NOTES.md`，明确标注需人工重画；PNG/PDF 在 Devin 侧用 `scibox-diagram/scripts/export_figure.py` 导出。
5. **论文正文只有一份**：`paper/sections/*.md`（一章一文件）+ `paper/paper.yaml`（title / keywords / sections 顺序）。图/表/公式用 `{#fig:x}` `{#tbl:x}` `{#eq:x}` 标签与 `@fig:x` 引用，不手写编号；不合并成单文件，不生成其他格式的副本。`python run_all.py paper`（`tools/paper_check.py`）FAIL 必须为 0。
6. **正文干净**：不出现 `reports/`、`figures/`、`AGENTS.md` 等内部名与占位符（图片路径 `../../figures/<id>/<id>.pdf` 除外）。
7. **交接写实**：`HANDOFF.md` 记录每阶段状态与最近一次完整复现的平台/结果；未在 Windows 实测就不要写"已验证"。

## 仓库维护

- `SKILL.md` frontmatter 只保留 `name` 与 `description`。
- 改工具脚本（`3coding-visual/scripts/*.py`、`draft-kickoff/scripts/paper_check.py`、`draft-kickoff/scripts/portability_check.py`）后，对已生成项目用 `new_draft_project.py <dir> --update-tools` 同步（示例项目也要同步）。
- 自检：`python3 -m compileall -q .agents/skills`；`python3 .agents/skills/draft-kickoff/scripts/portability_check.py .agents/skills/3coding-visual/scripts .agents/skills/draft-kickoff`；`python3 scripts/smoke_test.py`（新建临时项目 → doctor → run_all → 写最小 Markdown 章节 → run_all paper --strict → portability_check）。
- 示例项目 `examples/demo-drug-decay/`（合成药动学数据，端到端跑通）：`python run_all.py --strict && python tools/paper_check.py --require --strict && python tools/portability_check.py .`；`.github/workflows/windows-smoke.yml` 在 windows-latest 上跑同一套命令 + smoke_test（首次推送后才有实测结果，之前不要写"Windows 已验证"）。
- 第三方来源与许可见 `THIRD_PARTY_NOTICES.md`；`projects/` 默认被 `.gitignore` 忽略，不要提交比赛数据、队号、API Key。
