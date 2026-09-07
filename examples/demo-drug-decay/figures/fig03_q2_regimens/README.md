# fig03_q2_regimens

> 本文件由 `mm_plot_style.save_fig` 自动生成，最后一节“人工备注”之后的内容会被保留。

## 图的作用与机理（摘自 make_figure.py 头部 docstring）

fig03_q2_regimens/make_figure.py — 问题二：四种给药方案的浓度–时间曲线与稳态峰/谷浓度对比。

============================== 图的说明 ==============================
1. 回答什么问题
   问题二：在相同日剂量下，给药间隔如何影响稳态血药浓度的峰、谷与波动？哪种方案能把浓度维持在假想治疗窗内？
   （对应论文 §6.3–6.4，式 (7)–(9)）
2. 每个图元对应的机理
   - 左图四条曲线：按叠加原理（式 (7)）计算的 0–72 h 多次给药浓度曲线，每个方案一种颜色（R1–R4 的剂量/间隔见右图横轴）；
     曲线在每次给药后出现一个峰，随剂量累积逐渐趋于稳态（约 3–4 个半衰期，即 ≈14 h 后）
   - 左图浅灰横带：假想治疗窗 [3, 12] mg/L（演示用设定，非真实药理数据）
   - 右图成对柱：各方案稳态峰浓度 C_ss,max（深色）与谷浓度 C_ss,min（浅色），解析式 (8)–(9)；
     灰带同为治疗窗，柱顶超出灰带上边或谷柱低于灰带下边即"不达标"；柱顶数字为具体值 (mg/L)
3. 输入数据每列的含义与来源
   q2_profiles.csv（results/q2_profiles.csv 快照）：regimen 方案编号、label 方案描述、t (h)、conc (mg/L)
   q2_regimens.csv（results/q2_regimens.csv 快照）：regimen、label、dose_mg、tau_h、css_max、css_min、css_avg、ptf、in_window
4. 参数与随机种子
   无随机性；参数为 code/10_q1_fit_bateman.py 的 pooled 估计，方案与治疗窗定义在 code/20_q2_dosing_sim.py
5. 已知视觉缺陷 / 需要人工确认
   - R3（1000 mg q24h）峰值近 19 mg/L，且为给图例留白把 y 轴上限设到 27，其他曲线纵向被压缩；若只强调达标方案可另附放大图
   - 四条曲线在 0–6 h 起始段重叠；左图图例只写 R1–R4 编号，具体剂量靠右图横轴和正文表格说明
=====================================================================

## 文件

| 文件 | 说明 |
| --- | --- |
| `make_figure.py` | 绘图脚本，在项目根目录运行 `python figures/fig03_q2_regimens/make_figure.py` 重新生成 |
| `fig03_q2_regimens.pdf` | PDF 输出（论文/Word 用） |
| `fig03_q2_regimens.png` | PNG 输出（预览） |
| `fig03_q2_regimens.svg` | SVG 输出（可编辑矢量） |
| `q2_profiles.csv` | 数据快照，来源 `results/q2_profiles.csv`；列：regimen, label, t, conc |
| `q2_regimens.csv` | 数据快照，来源 `results/q2_regimens.csv`；列：regimen, label, dose_mg, tau_h, daily_dose_mg, css_max, css_min, css_avg, tmax_ss_h, ptf, accumulation, t90_h, frac_in_window, in_window |
| `manifest.json` | 生成记录（脚本、数据、参数、字体、检查结果） |
| `review.json` | 版式自检结果 + 人工审图记录 |

## 参数

```json
{
  "window_mg_L": [
    3.0,
    12.0
  ],
  "t_end_h": 72
}
```

## 自动检查

- 无发现

字体：Latin `Liberation Sans` / 中文 `WenQuanYi Micro Hei`；生成时间 2026-09-07T04:22:39

## 人工备注

### 人工审图（2026-09-07，Devin/Ubuntu）
- 已打开 PNG 核对：四条曲线颜色与右图柱色一致；R3 峰值明显越过灰带上界、R1/R4 谷值落到灰带下方，R2 全程在灰带内，与 q2_regimens.csv 的 in_window 一致。
- 右图柱顶数值与 RESULTS_REPORT §Q2 表一致（10.9/2.3、7.8/4.3、18.8/0.5、8.2/1.7）。
- 左图图例只标 R1–R4，剂量信息由右图横轴给出；正文图注需写明“灰带为假想治疗窗”。对应正文：图 3（§6.4）。
- y 轴上限 27 是为了给图例留白，曲线略显矮；可接受。
