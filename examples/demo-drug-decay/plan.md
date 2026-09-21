# plan.md — 方案与决策记录

> 本文件记录"为什么这么做"。每一条关键决策（模型选型、假设取舍、数据处理口径、丢弃的方案）都写在 §3，带日期与理由；
> 后续任何人改变决策，追加新条目而不是删旧条目。

## 1. 题目与目标

- 题目：口服药物血药浓度的一室模型参数估计与给药方案模拟
- 竞赛 / 场景：演示项目（合成数据）
- 子问题数量：3（Q1 参数估计与不确定性；Q2 四种给药方案稳态比较；Q3 灵敏度 / Monte Carlo / 个体差异 / 清洗影响）
- 交付形式：可复现项目文件夹（本目录），论文正文为 `paper/sections/*.md`（一章一文件）

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
| 2026-09-07 | 项目初始化，论文正文以 `paper/sections/*.md` 一章一文件维护，图/表/公式用标签引用不手写编号 | 单文件长稿 / 办公文档格式 | 纯文本可 diff、可自动校验（交叉引用、图路径、泄露），章节独立便于分头修改 | paper/ |
| 2026-09-07 | 一图一文件夹，图与数据快照、代码、说明同放 | 图统一放 figures/ 根目录 | 便于后续单独优化某张图、追溯数据来源 | figures/ |
| 2026-09-07 | 数据全部合成（Bateman 真值 ka=1.2, ke=0.15, V=40 L, F=1，seed 20260906，含 1 缺失 / 1 离群 / 1 负值） | 用公开真实药动学数据 | 演示项目不引入版权与真实性问题，且可对照真值检验拟合 | data/raw/, code/_make_synthetic_raw.py |
| 2026-09-07 | 异常值用逐受试者留一对数线性插值残差 + MAD 稳健 z（阈 3.5），只打 flag 不删行 | 3σ 规则 / 直接删 | 样本小、含离群点时均值方差不稳健；保留原值便于审计 | code/00_data_prep.py, reports/DATA_REPORT.md |
| 2026-09-07 | Q1 用 scipy curve_fit 非线性最小二乘 + delta 法置信带 + 留一 CV；个体拟合与合并拟合并列 | 对数线性两段法 / 混合效应模型 | 数据量小、模型解析；混合效应超出初稿范围（写入改进方向） | code/10_q1_fit_bateman.py |
| 2026-09-07 | Q2 稳态用解析叠加式，同时做 0–72 h 数值叠加互验（差 < 2e-4 mg/L）；治疗窗 3–12 mg/L 为假想 | 只做数值模拟 | 解析式便于灵敏度；互验防抄错公式 | code/20_q2_dosing_sim.py |
| 2026-09-07 | Q2 推荐规则：窗内方案取 PTF 最小；无窗内方案则取窗内时间占比最高并说明未达标 | 只看 Css,avg | 峰谷波动是安全性/有效性的直接指标 | code/20_q2_dosing_sim.py, 论文 §6 |
| 2026-09-07 | Q3 Monte Carlo 从 N(θ̂, pcov) 抽样，剔除 A≤0 / ke≤0 / ka≤ke 后取前 2000 组，seed 42 | Bootstrap | 样本 33 点 bootstrap 不稳定；pcov 已由 curve_fit 给出 | code/30_sensitivity.py |
| 2026-09-21 | 论文章节自检（`tools/paper_check.py`）接入 `run_all.py paper` 阶段，作为交付门禁 | 只靠人工审读 | 交叉引用/图路径/占位符/内部名泄露适合机器查，人工只看数值与措辞 | paper/, reports/PAPER_CHECK.md |

## 4. 风险与对策

| 风险 | 对策 |
| --- | --- |
| 示意图质量达不到论文标准 | 明确标注为草稿，附 REDRAW_NOTES.md 指导人工重画 |
| 数据图存在字图重叠 / 配色不一致等细节问题 | save_fig 内置版式 lint + FIGURE_REVIEW.md 清单 + 人工目检 |
| 换机（Windows）跑不通 | 纯 Python 入口、tools/ 自带脚本与字体、portability_check、doctor |
| 数字不一致 | 数值单一真源 results/ → RESULTS_REPORT.md → paper/sections/*.md；改数必须重跑 |
| 正文引用断裂 / 残留占位符 | `python run_all.py paper`（tools/paper_check.py）FAIL 0 才算完成 |
