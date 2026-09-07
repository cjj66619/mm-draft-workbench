# mm-draft-workbench

数学建模「初稿项目」工作台：在 Devin/Ubuntu 上运行，产出一个 **Windows 可复现、自包含** 的初稿项目文件夹——
Word 初稿 + 建模报告 + 数据处理/模型代码 + 一图一文件夹的数据图 + drawio 示意图草稿 + 给后续人/智能体的交接文档。

基于 [mm-workbench](https://github.com/cjj66619/mm-workbench)（六阶段 skills 流水线），新增：

- `draft-kickoff`：生成项目骨架（`new_draft_project.py`），把绘图/审图/可移植性工具 vendored 到项目 `tools/`；
- 一图一文件夹：`mm_plot_style.save_fig(layout="folder")` + `fig_layout_lint.py`（字图重叠/越界/尺寸不均/配色越界）+ `figure_index.py`（汇总 `figures/FIGURE_REVIEW.md`）；
- `docx-build`：Markdown 章节 → Word（公式 OMML、图表编号、A4 中文格式、审计）→ 冻结，Word 成为唯一真源；
- 输出项目自带 `run_all.py`/`doctor.py`/`portability_check.py`，纯 Python，无 bash/pandoc/draw.io 依赖。

## 使用

```bash
# 1. 新建项目（在本仓库根目录）
python3 .agents/skills/draft-kickoff/scripts/new_draft_project.py projects/2025-B --title "某问题的建模与求解" --contest 华为杯 --git
# 2. 按 .agents/skills/draft-kickoff/SKILL.md 六阶段推进（Devin 自动调用各 skill）
# 3. 项目内自检
cd projects/2025-B && python doctor.py && python run_all.py && python tools/portability_check.py .
```

输出项目在 Windows 上：安装 Python 3.10+，`pip install -r requirements.txt`，`python doctor.py`，`python run_all.py`（或双击 `run_all.bat`）；
`paper/main.docx` 直接用 Word 编辑；`figures/*/*.drawio` 用 draw.io 桌面版/网页版编辑。

## 目录

```text
.agents/skills/
  draft-kickoff/      入口 skill；scaffold/ 项目模板；scripts/new_draft_project.py, portability_check.py
  docx-build/         scripts/build_docx.py（Devin 侧）
  3coding-visual/     scripts/mm_plot_style.py, fig_layout_lint.py, figure_index.py, check_figures.py
  2analysis-modeling/ 4drawio/ 6verity/ scibox-diagram/ data-auditor-cleaner/ robustness-checker/
  consistency-auditor/ quality-assurance-auditor/ mathmodel-figure-templates/ _references/
AGENTS.md             Devin 使用规则
THIRD_PARTY_NOTICES.md
projects/             生成的项目（.gitignore 忽略）
```

Devin 侧依赖：Python 科学栈、pandoc、python-docx、pymupdf、LibreOffice（可选）、draw.io（可选，见 mm-workbench `scripts/setup_env.sh`）。

## 示例项目

`examples/demo-drug-decay/`：用合成药动学数据（口服一室 Bateman 模型：参数估计、给药方案模拟、灵敏度分析）端到端跑通的完整初稿项目，
含 4 个 `code/` 脚本、3 张数据图 + 1 张 drawio 技术路线图草稿、4 份 `reports/`、已冻结的 `paper/main.docx` 与写实的 `HANDOFF.md`。
可作为真实赛题项目的参照：`cd examples/demo-drug-decay && python doctor.py && python run_all.py --strict && python tools/portability_check.py .`。

## 状态

- 脚手架、工具链、`docx-build`、示例项目均已完成；Linux 上 `run_all --strict` 12 步 0 FAIL 0 WARN，`portability_check` 0 FAIL。
- `.github/workflows/windows-smoke.yml` 在 windows-latest 上对示例项目跑 doctor → run_all --strict → figure_index --check → portability_check → 冻结检查，再跑仓库级 `scripts/smoke_test.py`（无 pandoc 时跳过 Word 步骤）；Windows 实测结果以该工作流为准。
- 仓库自检命令见 `AGENTS.md`「仓库维护」节。
