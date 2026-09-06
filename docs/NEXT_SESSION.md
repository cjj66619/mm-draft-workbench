# 下个 session 的提示词（复制给 Devin 即可）

> 仓库：mm-draft-workbench（本地 zip 解压 / 已 push 到 GitHub）。先读 `AGENTS.md`、`README.md`、`.agents/skills/draft-kickoff/SKILL.md`、`.agents/skills/docx-build/SKILL.md`，再读本文件。
>
> **背景**：这是 mm-workbench 的迭代版，目标是在 Devin 上产出一个 Windows 可复现的「初稿项目文件夹」（Word 初稿 + 建模报告 + 数据/模型代码 + 一图一文件夹数据图 + drawio 示意图草稿 + 交接文档）。Word 只在 Devin 侧用 `docx-build` 生成一次并冻结，Windows 上直接用 Word 编辑、不重生成；Windows 只需 Python 重跑 `run_all.py`。
>
> **已完成并 smoke 通过（Linux）**：`new_draft_project.py` 生成骨架 → 复制 `_template_model.py`/`_template_figure` → `python run_all.py --strict` 7 步 0 FAIL 0 WARN；`portability_check.py` 对 skills 脚本 0 FAIL；`build_docx.py` 曾单独 smoke 过（Markdown→DOCX、OMML 公式、冻结机制），但**没有**在一个完整项目里端到端跑过。
>
> **本 session 要做（按顺序，每步完成后 commit）**：
> 1. 用合成数据做一个端到端演示项目 `examples/demo-drug-decay/`（题目：口服药物血药浓度 Bateman 一室模型 C(t)=A·(e^{-ke t}-e^{-ka t}) 的参数估计与给药方案模拟；合成数据脚本 `code/_make_synthetic_raw.py`：3 名受试者、12 个采样点、固定种子 20260906、人为加入 1 条缺失、1 个异常高值、1 个负值）。需要：`00_data_prep.py`（MAD 异常检测、flag 列不删行）、`10_q1_fit_bateman.py`（curve_fit、SE/CI、LOO-RMSE、delta 法置信带）、`20_q2_dosing_sim.py`（多次给药叠加、稳态谷/峰浓度）、`30_sensitivity.py`；`reports/{DATA,ANALYSIS_MODELING,RESULTS,ROBUSTNESS}_REPORT.md`；至少 2 张数据图（拟合+残差、给药方案对比）+ 1 张 drawio 技术路线图（`.drawio + PNG/PDF + REDRAW_NOTES.md`）；`paper/sections/*.md` → `build_docx.py --pdf --strict --freeze` 得到 `paper/main.docx`；`HANDOFF.md` 写实。演示项目要在 `.gitignore` 里放行（当前 `projects/` 被忽略，`examples/` 不忽略）。
> 2. 从干净副本验证：复制项目到临时目录，删 `results/ data/clean/ figures/*/{*.pdf,*.png,*.svg,data.csv}` 后 `python run_all.py --strict` 全绿。
> 3. 加 `.github/workflows/windows-smoke.yml`（windows-latest：`pip install -r requirements.txt` → `python doctor.py` → `python run_all.py --strict` → `python tools/portability_check.py .`，对 `examples/demo-drug-decay` 跑）。
> 4. 修已知小问题：`save_fig(source=...)` 与 `snapshot_data(name="data.csv")` 同时用时图文件夹里会出现两份数据快照（`data.csv` 与 `q1_fitted.csv`），去重为一份；`doctor.py` 把 `data/raw/.gitkeep` 计入文件数；模板 make_figure 里 CI 阴影带在 docstring 提到但代码未画，二者对齐。
> 5. 用 `mm-workbench` 的 `scripts/smoke_test.sh` 思路写一个本仓库的 `scripts/smoke_test.py`（纯 Python：生成临时项目 → 跑 run_all → 跑 build_docx → 断言产物），并写进 `AGENTS.md` 自检节。
>
> **约束**：不要求 Windows 跑 Word 生成/pandoc/LibreOffice/draw.io CLI；输出项目里禁止绝对路径、bash、硬编码 `python`、无 encoding 的文本 I/O（`portability_check.py` FAIL 必须 0）；同一字符串不要混用中文与 `$公式$`；机器画的示意图必须标注为草稿并附 `REDRAW_NOTES.md`；不编造数据/文献；不要 push、不要建 PR，本地 commit 后打 zip 给我。**注意额度：优先保证第 1、2 步完成并 commit，再做 3–5。**
