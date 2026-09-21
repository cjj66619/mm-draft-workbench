# plan.md — 方案与决策记录

> 本文件记录"为什么这么做"。每一条关键决策（模型选型、假设取舍、数据处理口径、丢弃的方案）都写在 §3，带日期与理由；
> 后续任何人改变决策，追加新条目而不是删旧条目。

## 1. 题目与目标

- 题目：{{TITLE}}
- 竞赛 / 场景：{{CONTEST}}
- 子问题数量：待分析确定
- 交付形式：可复现项目文件夹（本目录），论文正文为 `paper/sections/*.md`（一章一文件，提交质量的终稿）

## 2. 工作流

```text
step  阶段                       负责 skill / 方法                 产物
1     赛题分析与建模设计          2analysis-modeling                reports/ANALYSIS_MODELING_REPORT.md
1.5   数据审计与清洗（有附件时）  data-auditor-cleaner              reports/DATA_REPORT.md, data/clean/
2     编程实现与数据图            3coding-visual（一图一文件夹）    code/, results/, reports/RESULTS_REPORT.md, figures/figNN_*/
2.5   稳健性 / 敏感性             robustness-checker                reports/ROBUSTNESS_REPORT.md
3     示意图（草稿）              4drawio / scibox-diagram          figures/figNN_*/*.drawio + PNG/PDF + REDRAW_NOTES.md
4     论文正文                    draft-writing                     paper/sections/*.md, paper/paper.yaml（python run_all.py paper 自检 FAIL 0）
5     验收与审计                  6verity / consistency-auditor / quality-assurance-auditor   reports/AUDIT_*.md
```

## 3. 决策记录（追加式）

| 日期 | 决策 | 备选 | 理由 / 证据 | 影响范围 |
| --- | --- | --- | --- | --- |
| {{DATE}} | 项目初始化，论文正文以 `paper/sections/*.md` 一章一文件维护，图/表/公式用标签引用不手写编号 | 单文件长稿 / 办公文档格式 | 纯文本可 diff、可自动校验（交叉引用、图路径、泄露），章节独立便于分头修改 | paper/ |
| {{DATE}} | 一图一文件夹，图与数据快照、代码、说明同放 | 图统一放 figures/ 根目录 | 便于后续单独优化某张图、追溯数据来源 | figures/ |

## 4. 风险与对策

| 风险 | 对策 |
| --- | --- |
| 示意图质量达不到论文标准 | 明确标注为草稿，附 REDRAW_NOTES.md 指导人工重画 |
| 数据图存在字图重叠 / 配色不一致等细节问题 | save_fig 内置版式 lint + FIGURE_REVIEW.md 清单 + 人工目检 |
| 换机（Windows）跑不通 | 纯 Python 入口、tools/ 自带脚本与字体、portability_check、doctor |
| 数字不一致 | 数值单一真源 results/ → RESULTS_REPORT.md → paper/sections/*.md；改数必须重跑 |
| 正文引用断裂 / 残留占位符 | `python run_all.py paper`（tools/paper_check.py）FAIL 0 才算完成 |
