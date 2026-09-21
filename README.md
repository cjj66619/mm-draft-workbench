# mm-draft-workbench

数学建模「论文项目」工作台：在 Devin/Ubuntu 上运行，产出一个 **Windows 可复现、自包含** 的项目文件夹——
论文正文（`paper/sections/*.md`，一章一文件）+ 建模报告 + 数据处理/模型代码 + 一图一文件夹的数据图 + drawio 示意图草稿 + 给后续人/智能体的交接文档。

基于 [mm-workbench](https://github.com/cjj66619/mm-workbench)（skills 流水线），新增：

- `draft-kickoff`：生成项目骨架（`new_draft_project.py`），把绘图/审图/论文自检/可移植性工具 vendored 到项目 `tools/`；
- 一图一文件夹：`mm_plot_style.save_fig(layout="folder")` + `fig_layout_lint.py`（字图重叠/越界/尺寸不均/配色越界）+ `figure_index.py`（汇总 `figures/FIGURE_REVIEW.md`）；
- 论文正文以 Markdown 章节交付：`paper/paper.yaml`（题目/关键词/章节顺序）+ `paper/sections/NN_*.md`，`@fig:`/`@tbl:`/`@eq:` 交叉引用；`paper_check.py` 检查交叉引用、图路径、占位符、内部名泄露、摘要关键词、元数据一致性，写 `reports/PAPER_CHECK.md`；
- 输出项目自带 `run_all.py`/`doctor.py`/`portability_check.py`，纯 Python，无 bash/draw.io/办公软件依赖。

## 使用

```bash
# 1. 新建项目（在本仓库根目录）
python3 .agents/skills/draft-kickoff/scripts/new_draft_project.py projects/2025-B --title "某问题的建模与求解" --contest 华为杯 --git
# 2. 按 .agents/skills/draft-kickoff/SKILL.md 各阶段推进（Devin 自动调用各 skill），论文正文写到 paper/sections/*.md
# 3. 项目内自检
cd projects/2025-B && python doctor.py && python run_all.py --strict && python tools/portability_check.py .
```

输出项目在 Windows 上：安装 Python 3.10+，`pip install -r requirements.txt`，`python doctor.py`，`python run_all.py`（或双击 `run_all.bat`）；
`paper/sections/*.md` 用任何文本编辑器修改后 `python run_all.py paper` 自检；`figures/*/*.drawio` 用 draw.io 桌面版/网页版编辑。

## 目录

```text
.agents/skills/
  draft-kickoff/      入口 skill；scaffold/ 项目模板；scripts/new_draft_project.py, paper_check.py, portability_check.py
  3coding-visual/     scripts/mm_plot_style.py, fig_layout_lint.py, figure_index.py, check_figures.py
  2analysis-modeling/ 4drawio/ 6verity/ scibox-diagram/ data-auditor-cleaner/ robustness-checker/
  consistency-auditor/ quality-assurance-auditor/ mathmodel-figure-templates/ _references/
AGENTS.md             Devin 使用规则
THIRD_PARTY_NOTICES.md
projects/             生成的项目（.gitignore 忽略）
```

Devin 侧依赖：Python 科学栈、pymupdf、draw.io（可选，见 mm-workbench `scripts/setup_env.sh`）。

## 示例项目

`examples/demo-drug-decay/`：用合成药动学数据（口服一室 Bateman 模型：参数估计、给药方案模拟、灵敏度分析）端到端跑通的完整项目，
含 4 个 `code/` 脚本、3 张数据图 + 1 张 drawio 技术路线图草稿、4 份 `reports/`、10 个 `paper/sections/*.md` 章节与写实的 `HANDOFF.md`。
可作为真实赛题项目的参照：`cd examples/demo-drug-decay && python doctor.py && python run_all.py --strict && python tools/portability_check.py .`。

## 状态

- 脚手架、工具链、论文章节自检、示例项目均已完成；Linux 上示例 `run_all --strict` 0 FAIL，`portability_check` 0 FAIL。
- `.github/workflows/windows-smoke.yml` 在 windows-latest 上对示例项目跑 doctor → run_all --strict → figure_index --check → paper_check --require --strict → portability_check，再跑仓库级 `scripts/smoke_test.py`；Windows 实测结果以该工作流为准。
- 仓库自检命令见 `AGENTS.md`「仓库维护」节。
