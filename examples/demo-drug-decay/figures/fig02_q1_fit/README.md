# fig02_q1_fit

> 本文件由 `mm_plot_style.save_fig` 自动生成，最后一节“人工备注”之后的内容会被保留。

## 图的作用与机理（摘自 make_figure.py 头部 docstring）

fig02_q1_fit/make_figure.py — 问题一：Bateman 模型拟合结果与残差。

============================== 图的说明 ==============================
1. 回答什么问题
   问题一：一室口服模型 C(t)=A·(e^{-ke t}-e^{-ka t}) 能否刻画三名受试者的血药浓度–时间曲线？
   群体（合并）拟合的不确定性有多大？残差是否有系统性偏差？（对应论文 §5.4，式 (1)、(6)）
2. 每个图元对应的机理
   - 左图实心散点：清洗后进入拟合的观测点（use_for_fit=True），三名受试者三种颜色
   - 左图灰色叉号：被清洗规则标记而未进入拟合的点（离群高值 24.04 mg/L；负值 -0.12 mg/L 画在 0 线附近），
     显示"标记不删行"的处理方式；缺失点无法画出
   - 左图黑色实线：合并（pooled）拟合曲线 C_hat(t)；阴影：delta 法 95% 置信带（式 (6)），只含参数不确定性
   - 左图细虚线：各受试者单独拟合曲线，用于看个体差异（S03 消除更快，尾部更低）
   - 右图：合并拟合的残差 y - C_hat(t) 随时间分布，颜色同左图；零线为参考。残差在吸收相（t<2 h）略呈正负交替，
     反映个体 tmax 的差异，而非模型缺项
3. 输入数据每列的含义与来源
   q1_fitted.csv（results/q1_fitted.csv 快照）：subject、t (h)、y 观测 (mg/L)、y_hat 拟合、resid 残差
   q1_curve.csv （results/q1_curve.csv 快照） ：subject、t、c_hat、ci_low、ci_high（0–24 h 网格）
   pk_clean.csv （data/clean/pk_clean.csv 快照）：subject、time_h、conc_raw、flag（取 flag ∉ {ok, missing} 的行画叉号）
4. 参数与随机种子
   无随机性；参数来自 code/10_q1_fit_bateman.py（curve_fit，确定性）
5. 已知视觉缺陷 / 需要人工确认
   - 离群点 24.04 mg/L 会拉高左图 y 轴上限；已把 y 轴截断到 13，该点的叉号画在上边缘并标注实际值
   - 三条个体曲线与合并曲线在 t>8 h 处接近，可能重叠；打印版建议只保留合并曲线
=====================================================================

## 文件

| 文件 | 说明 |
| --- | --- |
| `make_figure.py` | 绘图脚本，在项目根目录运行 `python figures/fig02_q1_fit/make_figure.py` 重新生成 |
| `fig02_q1_fit.pdf` | PDF 输出（论文/Word 用） |
| `fig02_q1_fit.png` | PNG 输出（预览） |
| `fig02_q1_fit.svg` | SVG 输出（可编辑矢量） |
| `q1_fitted.csv` | 数据快照，来源 `results/q1_fitted.csv`；列：subject, t, y, y_hat, resid |
| `q1_curve.csv` | 数据快照，来源 `results/q1_curve.csv`；列：subject, t, c_hat, ci_low, ci_high |
| `pk_clean.csv` | 数据快照，来源 `data/clean/pk_clean.csv`；列：subject, time_h, conc_raw, conc, log_resid, robust_z, flag, use_for_fit |
| `manifest.json` | 生成记录（脚本、数据、参数、字体、检查结果） |
| `review.json` | 版式自检结果 + 人工审图记录 |

## 参数

```json
{
  "ci": 0.95,
  "y_max_clip": 13.0,
  "fit": "pooled + per-subject"
}
```

## 自动检查

- 无发现

字体：Latin `Liberation Sans` / 中文 `WenQuanYi Micro Hei`；生成时间 2026-09-07T04:22:37

## 人工备注

### 人工审图（2026-09-07，Devin/Ubuntu）
- 已打开 PNG 逐项核对：三名受试者散点与各自虚线曲线颜色一致；合并拟合黑线穿过点云中部；灰色置信带窄（参数不确定性小）符合 RESULTS_REPORT §Q1 的 se。
- 两个剔除点（S01 3 h 离群、S03 24 h 负值）以叉号显示，离群点因超出 y 轴被画在上边缘并标“实际 24.0”，不会被误读为观测。
- 残差图无明显趋势；S03 残差整体偏负，反映 S03 消除更快（个体差异），已在正文 §5.4 说明。
- 图例不压数据，自动 lint 无发现。对应正文：图 2（§5.4）。
- 待办：投稿版可考虑去掉三条个体虚线，只保留合并曲线与置信带。
