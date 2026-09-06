---
name: draft-kickoff
description: "mm-draft-workbench 入口：拿到题目/附件后，生成一个 Windows 可复现的自包含初稿项目文件夹（Word 初稿 + 建模报告 + 数据/模型代码 + 一图一文件夹的数据图 + drawio 示意图草稿 + 交接文档），并按 2analysis-modeling → 3coding-visual → 4drawio → draft-writing → docx-build → 6verity 推进。用户说“出一版初稿 / 用 X 题做个初稿项目 / 开始 draft”时使用。"
---

# draft-kickoff — 初稿项目入口

本 skill 在 **Devin/Ubuntu** 侧运行；产出的项目文件夹要能在 **Windows 上只靠 Python** 重跑数据处理、模型、绘图。
Word 初稿在 Devin 侧生成一次并冻结，用户之后直接用 Word 编辑；**Windows 上不重生成 Word**。

## 一句话原则

- 数值单一真源（`results/` → `reports/RESULTS_REPORT.md` → Word）；原始数据只读；固定种子。
- 一图一文件夹（`figures/<fig_id>/`：图 + `make_figure.py` + 数据快照 + README/manifest/review）。
- 示意图（技术路线图/模型结构图）只是**草稿**，必须附 `REDRAW_NOTES.md` 指导人工重画。
- 输出文件夹里禁止：绝对路径、bash、`subprocess.run(["python", ...])`、未指定 encoding 的文本 I/O。

## 步骤

### 0. 生成项目文件夹

```bash
python3 .agents/skills/draft-kickoff/scripts/new_draft_project.py projects/<年>-<题号> \
    --title "<题目>" --contest "<竞赛/场景>" [--git]
```

得到 `README.md AGENTS.md HANDOFF.md plan.md todo.md project.yaml run_all.py run_all.bat doctor.py requirements.txt`
以及 `problem/ data/{raw,clean} code/(common.py) results/ reports/ figures/(_template_figure) paper/(paper.yaml, sections/) tools/`。
`tools/` 由脚本从本仓库拷入：`mm_plot_style.py fig_layout_lint.py check_figures.py figure_index.py portability_check.py fonts/wqy-microhei.ttc`。
以后升级工具只需 `--update-tools`。

在项目目录 `python doctor.py` 确认核心项全 OK。

### 1. 题面与附件

- 题面整理到 `problem/statement.md`（保留原编号原话），附件清单 `problem/attachments.md`，原始文件放 `data/raw/`（此后只读）。
- 只问会实质影响流程的问题（竞赛类型、语言、子问题数是否已知），答案写进 `plan.md` §1。

### 2. 六阶段（文件交接，不依赖对话上下文）

| 步 | skill | 产物 | 本仓库的额外要求 |
| --- | --- | --- | --- |
| 1 | `2analysis-modeling` | `reports/ANALYSIS_MODELING_REPORT.md` | 每个模型公式编号，后面代码 docstring 要引用编号 |
| 1.5 | `data-auditor-cleaner`（有附件时） | `reports/DATA_REPORT.md`, `data/clean/` | 清洗代码写成 `code/00_*.py`，用 `common.load_raw/save_table` |
| 2 | `3coding-visual` | `code/1x_*.py …`, `results/`, `reports/RESULTS_REPORT.md`, `figures/figNN_*/` | 图脚本从 `figures/_template_figure/` 复制；`save_fig(fig, HERE / FIG_ID, source=..., params=...)`；docstring 五要素（回答什么问题 / 图元↔机理 / 每列含义与来源 / 参数与种子 / 已知缺陷） |
| 2.5 | `robustness-checker` | `reports/ROBUSTNESS_REPORT.md`, `code/3x_*.py` | |
| 3 | `4drawio` / `scibox-diagram` | `figures/figNN_*/<id>.drawio` + PNG/PDF + `REDRAW_NOTES.md` | 在 Devin 侧用 `scibox-diagram/scripts/export_figure.py` 导出 PNG/PDF；`REDRAW_NOTES.md` 写元素清单、箭头语义、已知重叠/配色问题、建议重画方式 |
| 4 | `draft-writing`（见下） | `paper/sections/*.md` | Markdown + LaTeX 公式，`@fig:`/`@tbl:`/`@eq:` 交叉引用 |
| 5 | `docx-build` | `paper/main.docx`, `paper/DOCX_FREEZE.json`, `paper/docx_build_report.md` | `--pdf --strict` 通过后 `--freeze` |
| 6 | `6verity` / `consistency-auditor` / `quality-assurance-auditor` | `reports/AUDIT_*.md` | 对 Markdown 源与 `RESULTS_REPORT.md` 做数值一致性；docx 用 build 报告的审计结果 |

每步结束：更新 `todo.md` 勾选、`plan.md` §3 追加决策、`HANDOFF.md` 阶段状态表。

### 3. 交付前自检（都在项目目录）

```bash
python run_all.py                  # code → figures → figcheck → check，reports/RUN_STATUS.md FAIL 必须为 0
python tools/figure_index.py --check
python tools/portability_check.py .            # FAIL 必须为 0
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --status   # 必须 frozen
```

再从**干净副本**验证一次：复制项目到临时目录、删除 `results/ data/clean/ figures/*/{*.pdf,*.png,*.svg,data.csv}` 后 `python run_all.py` 仍全绿。

### 4. 交接文档必须写实

- `HANDOFF.md`：每阶段状态、最近一次完整复现的时间/平台/结果、已知问题（示意图待重画、FIGURE_REVIEW 的 WARN 数）、下一步。
- `figures/FIGURE_REVIEW.md`（自动）+ 每图 `README.md` 的"人工审图"段（手写结论）。
- 不要声称"已在 Windows 验证"除非真的跑过（可在 HANDOFF 写"仅 Linux 验证；Windows 请先 `python doctor.py`"）。

## draft-writing（Markdown 章节，替代 5writing）

`paper/sections/` 文件命名沿用 5writing 的中文通用结构，扩展名 `.md`：

```text
00_abstract.md        摘要（无标题；最后一段可写 "关键词：a；b；c"，或在 paper.yaml 填 keywords）
01_restatement.md     一、问题重述
02_analysis.md        二、问题分析（含技术路线图 @fig:roadmap）
03_assumptions.md     三、模型假设
04_symbols.md        四、符号说明（表，Table: 主要符号说明 {#tbl:symbols}）
05_problem1.md        五、问题一的建模与求解（N.1 问题分析 / N.2 模型建立 / N.3 求解 / N.4 结果分析与验证 / N.5 小结）
06_problem2.md        …
08_sensitivity.md     灵敏度分析与模型检验
09_evaluation.md      模型评价与推广
10_references.md      参考文献（真实可查）
```

写法：一级标题 `# 一、问题重述`；公式 `$$ ... $$ {#eq:q1_model}`；图 `![图题](../../figures/fig02_q1_fit/fig02_q1_fit.pdf){#fig:q1_fit}`；
表用 Markdown 管道表 + 上一行 `Table: 表题 {#tbl:xxx}`；正文引用 `@fig:q1_fit`、`@tbl:xxx`、`@eq:xxx`。
数值一律抄自 `reports/RESULTS_REPORT.md`，正文不出现 `reports/`、`figures/`、`AGENTS.md` 等内部名。
写作规范读 `../_references/math_modeling_norms.md`、华为杯段落骨架读 `../_references/huaweibei_excellent_paper_patterns.md` §4。

## docx-build（Devin 侧一次性）

```bash
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --pdf --strict   # 生成 + LibreOffice 渲染抽检 + 审计
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --freeze         # 冻结：Word 成为唯一真源
```

依赖 pandoc、python-docx（必需），pymupdf（PDF 图转 PNG），soffice（可选）。这些只装在 Devin，**不进输出项目**。
冻结后若用户明确要求重生成：`--force`（自动备份 `main.docx.bak-<时间>`）。
