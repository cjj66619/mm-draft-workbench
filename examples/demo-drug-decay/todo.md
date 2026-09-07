# todo.md — 待办

> 阶段级 checklist；完成一项就勾掉并写上产物路径。细节问题也可以挂在对应阶段下面。

## 阶段

- [x] 1. 赛题分析与建模设计 → `reports/ANALYSIS_MODELING_REPORT.md`
- [x] 1.5 数据审计与清洗 → `reports/DATA_REPORT.md`, `data/clean/`
- [x] 2. 编程实现与数据图 → `code/`, `results/`, `reports/RESULTS_REPORT.md`, `figures/figNN_*/`
- [x] 2.5 稳健性 / 敏感性 → `reports/ROBUSTNESS_REPORT.md`
- [x] 3. 示意图草稿 → `figures/figNN_*/*.drawio` + `REDRAW_NOTES.md`
- [x] 4. Markdown 章节 → `paper/sections/*.md`
- [x] 5. Word 初稿生成并冻结 → `paper/main.docx`, `paper/DOCX_FREEZE.json`
- [x] 6. 验收与审计（轻量，结论记在 `HANDOFF.md`；未单独出 `reports/AUDIT_*.md`）
- [x] 7. `python run_all.py --strict` 全绿（Linux，含干净副本）；`HANDOFF.md` 更新

## 交稿前人工必做

- [ ] 所有示意图按 `REDRAW_NOTES.md` 手工重画并替换 Word 中的图
- [x] `figures/FIGURE_REVIEW.md` 中 FAIL 清零、WARN 清零
- [ ] Word 中每个数字与 `reports/RESULTS_REPORT.md` 核对一遍
- [ ] 参考文献真实可查

## 遗留 / 待确认

- [ ] Windows 实测（CI `windows-smoke` 推送后才有结果）
- [ ] Word 表格列宽 / 跨页微调（在 Word 内做）
- [ ] 示意图 fig01 人工重画后替换 Word 图 1
