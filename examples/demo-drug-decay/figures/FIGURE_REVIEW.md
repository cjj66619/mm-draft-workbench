# 审图清单（FIGURE_REVIEW）

> 由 `tools/figure_index.py` 汇总各图 `review.json`。做绘图优化时：逐图核对下列清单 → 修改 `make_figure.py`/`.drawio` 并重跑 → 在 `review.json` 的 `human` 字段记录 reviewer/date/verdict/notes → 重新运行本脚本。

## 通用核对项

- [ ] 文字与线/柱/图例无重叠（review.json 的 text_overlap / legend_over_data / pdf_line_through_text 已清零或注明可接受）
- [ ] 无越界/裁切；面板大小一致；(a)(b) 标签位置一致
- [ ] 字号：5 pt ≤ 全部文字 ≤ 1.6×基准；同类图字号一致
- [ ] 配色只用 COLORS/PALETTES；同一变量在全文各图颜色一致；无彩虹色
- [ ] 坐标轴有标签与单位；图例不遮挡；中文与论文语言一致
- [ ] 图意与论文正文/图题一致；数值与 reports/RESULTS_REPORT.md 一致
- [ ] 示意图（drawio）已按 REDRAW_NOTES.md 人工重画或确认可用

## 逐图状态

### fig01_roadmap（diagram）

- 用途：| 文件 | 说明 |
- 源文件：`fig01_roadmap.drawio`（draw.io 桌面版/网页版可编辑；导出后替换同名 PDF/PNG）
- 人工审图：reviewed，结论：draft-needs-redraw
  - PNG 逐块核对：数值与 RESULTS_REPORT 一致；缩写与箭头分组问题见 REDRAW_NOTES.md；交稿前必须人工重画。
- 重画说明：见 `fig01_roadmap/REDRAW_NOTES.md`

### fig02_q1_fit（data）

- 用途：fig02_q1_fit/make_figure.py — 问题一：Bateman 模型拟合结果与残差。
- 脚本：`make_figure.py`
- 数据：`q1_fitted.csv` ← `results/q1_fitted.csv`
- 数据：`q1_curve.csv` ← `results/q1_curve.csv`
- 数据：`pk_clean.csv` ← `data/clean/pk_clean.csv`
- 人工审图：reviewed，结论：accept-draft
  - 合并曲线与 95% 置信带覆盖三人观测；离群点/负值以叉号单独标出；残差无系统趋势。
  - S03 末端（16–24 h）残差偏负，与其 ke 偏高一致，非绘图问题。
- 自动检查：无发现

### fig03_q2_regimens（data）

- 用途：fig03_q2_regimens/make_figure.py — 问题二：四种给药方案的浓度–时间曲线与稳态峰/谷浓度对比。
- 脚本：`make_figure.py`
- 数据：`q2_profiles.csv` ← `results/q2_profiles.csv`
- 数据：`q2_regimens.csv` ← `results/q2_regimens.csv`
- 人工审图：reviewed，结论：accept-draft
  - 四条曲线颜色与图例一一对应；治疗窗灰带清楚；柱状图峰/谷数值标注与 results/q2_regimens.csv 一致。
  - R3 峰值柱较高，但未越界。
- 自动检查：无发现

### fig04_sensitivity（data）

- 用途：fig04_sensitivity/make_figure.py — 问题三：推荐方案对参数扰动的敏感性与参数不确定性传播。
- 脚本：`make_figure.py`
- 数据：`q3_sens_local.csv` ← `results/q3_sens_local.csv`
- 数据：`q3_sens_mc.csv` ← `results/q3_sens_mc.csv`
- 人工审图：reviewed，结论：accept-draft
  - (a) 龙卷风图 ke 条最长，与表 6 一致；(b) 区间条与达标率标注与 results/q3_sens_mc.csv 一致。
  - 字号一致，无重叠。
- 自动检查：无发现
