# HANDOFF.md — 当前状态与下一步

> 每次交接（换人 / 换智能体 / 换会话）前更新本文件。写"做了什么、验证了什么、剩什么、坑在哪"，不写过程流水账。
> 规则看 `AGENTS.md`，决策看 `plan.md`，细粒度待办看 `todo.md`。

## 项目

- 题目：{{TITLE}}
- 生成时间：{{DATE}}（mm-draft-workbench）
- 生成环境：{{GEN_PLATFORM}}；目标运行环境：Windows / Linux / macOS，Python 3.10+

## 阶段状态

| 阶段 | 状态 | 产物 | 备注 |
| --- | --- | --- | --- |
| 题面理解与建模设计 | 未开始 | `reports/ANALYSIS_MODELING_REPORT.md`, `plan.md` | |
| 数据审计与清洗 | 未开始 | `reports/DATA_REPORT.md`, `data/clean/` | |
| 代码实现与求解 | 未开始 | `code/`, `results/`, `reports/RESULTS_REPORT.md` | |
| 数据图 | 未开始 | `figures/figNN_*/` | `figures/FIGURE_REVIEW.md` 中 FAIL/WARN 数： |
| 示意图（drawio） | 未开始 | `figures/figNN_*/*.drawio` + PNG/PDF + `REDRAW_NOTES.md` | 全部为草稿，需人工重画 |
| 稳健性 / 敏感性 | 未开始 | `reports/ROBUSTNESS_REPORT.md` | |
| Word 初稿 | 未开始 | `paper/main.docx` | 冻结状态见 `paper/DOCX_FREEZE.json` |
| 一致性与质量审计 | 未开始 | `reports/AUDIT_*.md` | |

状态取值：未开始 / 进行中 / 已完成 / 已完成-有已知问题。

## 最近一次完整复现

- 时间 / 平台：
- 命令：`python run_all.py`
- 结果：`reports/RUN_STATUS.md`（FAIL 0 才算通过）

## 已知问题 / 需要人工判断

- [ ] 示意图需人工重画（见各文件夹 `REDRAW_NOTES.md`）
- [ ] 数据图版式自检 WARN 待逐条确认（`figures/FIGURE_REVIEW.md`）
- [ ]

## 下一步（按优先级）

1.
2.
3.

## 给下一位的提醒

- Word 是正文唯一真源；数字改动必须先改代码/结果报告，再改 Word。
- `data/raw/` 别动；`figures/*/manifest.json`、`review.json`、`figures/README.md` 等是自动生成的，别手改。
- 跑不起来先 `python doctor.py`。
