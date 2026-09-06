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

## 状态

脚手架与工具链已完成并 smoke 测试（Linux）。尚未完成：端到端演示项目、Windows 真机/CI 验证——见 `docs/NEXT_SESSION.md`。
