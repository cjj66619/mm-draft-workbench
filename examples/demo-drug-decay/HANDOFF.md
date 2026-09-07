# HANDOFF.md — 当前状态与下一步

> 每次交接（换人 / 换智能体 / 换会话）前更新本文件。写"做了什么、验证了什么、剩什么、坑在哪"，不写过程流水账。
> 规则看 `AGENTS.md`，决策看 `plan.md`，细粒度待办看 `todo.md`。

## 项目

- 题目：口服药物血药浓度的一室模型参数估计与给药方案模拟
- 生成时间：2026-09-07（mm-draft-workbench）
- 生成环境：Linux 5.15.200 / Python 3.10.12；目标运行环境：Windows / Linux / macOS，Python 3.10+

## 阶段状态

| 阶段 | 状态 | 产物 | 备注 |
| --- | --- | --- | --- |
| 题面理解与建模设计 | 已完成 | `reports/ANALYSIS_MODELING_REPORT.md`, `plan.md` | 合成题面见 `problem/`；模型为 Bateman 一室口服模型 |
| 数据审计与清洗 | 已完成 | `reports/DATA_REPORT.md`, `data/clean/pk_clean.csv` | 36 行原始数据全部保留并打 flag：1 缺失、1 离群（MAD z=10.98）、1 负值 |
| 代码实现与求解 | 已完成 | `code/00,10,20,30_*.py`, `results/`, `reports/RESULTS_REPORT.md` | 固定种子；干净副本复现结果逐字节一致 |
| 数据图 | 已完成 | `figures/fig02_q1_fit`, `fig03_q2_regimens`, `fig04_sensitivity` | `figures/FIGURE_REVIEW.md` FAIL 0 / WARN 0；PNG 已人工看过（review.json human 段） |
| 示意图（drawio） | 已完成-有已知问题 | `figures/fig01_roadmap/` (`.drawio` + PNG/PDF + `REDRAW_NOTES.md`) | **草稿**，交稿前需在 draw.io 人工重画：缩写多、箭头与 R1–R4 非严格一对一、公式为纯文本 |
| 稳健性 / 敏感性 | 已完成 | `reports/ROBUSTNESS_REPORT.md`, `code/30_sensitivity.py` | 局部扰动 / Monte Carlo(2000, seed 42) / 个体复算 / 清洗对比 |
| Word 初稿 | 已完成（已冻结） | `paper/main.docx`（PDF 预览 14 页，4 图、9 编号表、8 编号公式） | 2026-09-07 于 Devin/Linux 生成并 `--freeze`；`--strict` 审计 0 错 0 警；正文排版细节（表格列宽、分页）未精修，用户在 Word 里直接调 |
| 一致性与质量审计 | 已完成-轻量 | 本文件 §已知问题 | 数值链 results → RESULTS_REPORT → 论文章节逐项核对过；未单独产出 `reports/AUDIT_*.md` |

状态取值：未开始 / 进行中 / 已完成 / 已完成-有已知问题。

## 最近一次完整复现

- 时间 / 平台：2026-09-07，Ubuntu 22.04 / Python 3.10.12（Devin 侧）
- 命令：`python run_all.py --strict`；另在删除 `results/`、`data/clean/`、各图 PDF/PNG/SVG 与数据快照后的干净副本上重跑，12 步全 OK，`results/` 与原副本逐字节一致
- 结果：`reports/RUN_STATUS.md` FAIL 0 / WARN 0；`python tools/portability_check.py .` FAIL 0
- **Windows（GitHub Actions windows-latest，Python 3.11，2026-09-07）**：`doctor` / `run_all --strict` / `figure_index --check` / `portability_check` / 冻结检查全部通过（工作流 `windows-smoke`，run 34083900482）。同一工作流里仓库级 `scripts/smoke_test.py` 曾因 Windows 控制台 cp1252 打印中文报错，已修（与项目无关）。**未在本机 Windows + 真实 Word 环境实测**，接手时请先 `python doctor.py`。

## 已知问题 / 需要人工判断

- [ ] 示意图 `fig01_roadmap` 需人工重画（见 `figures/fig01_roadmap/REDRAW_NOTES.md`），重画后替换 Word 图 1
- [x] 数据图版式自检 WARN 已清零（`figures/FIGURE_REVIEW.md`）
- [ ] Word 表格列宽/跨页由脚本按内容估算，个别表头仍换行；在 Word 里手工微调即可，不要重生成
- [ ] 治疗窗 3–12 mg/L、剂量、参数均为合成设定，不对应任何真实药物；正文已声明，勿当作临床结论
- [ ] 参考文献 6 条为经典教材/论文与 SciPy，未逐条核对页码

## 下一步（按优先级）

1. 在 draw.io 打开 `figures/fig01_roadmap/fig01_roadmap.drawio` 按 `REDRAW_NOTES.md` 重画，导出后替换 Word 图 1。
2. Word 内排版精修：表 2–9 列宽、图题位置、目录刷新（F9）。
3. 若要作为真实赛题模板使用：替换 `data/raw/`、`problem/`，重跑 `run_all.py`，比对 `RESULTS_REPORT.md` 差异后再改 Word。

## 给下一位的提醒

- Word 是正文唯一真源；数字改动必须先改代码/结果报告，再改 Word。
- `data/raw/` 别动；`figures/*/manifest.json`、`review.json`、`figures/README.md` 等是自动生成的，别手改。
- 跑不起来先 `python doctor.py`。
