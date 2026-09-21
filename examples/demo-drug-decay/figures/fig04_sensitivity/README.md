# fig04_sensitivity

> 本文件由 `mm_plot_style.save_fig` 自动生成，最后一节“人工备注”之后的内容会被保留。

## 图的作用与机理（摘自 make_figure.py 头部 docstring）

fig04_sensitivity/make_figure.py — 问题三：推荐方案对参数扰动的敏感性与参数不确定性传播。

============================== 图的说明 ==============================
1. 回答什么问题
   问题三：推荐方案 R2（250 mg q6h）的稳态谷浓度对 A、ka、ke 三个参数各有多敏感？
   把问题一估计的参数不确定性传播到各方案的稳态峰/谷浓度后，结论是否稳健？（对应论文 §7，式 (10)–(11)）
2. 每个图元对应的机理
   - 左图（龙卷风图）：对 R2，把单个参数分别改动 ±10%、±20%（其余不变），横条为稳态谷浓度 C_ss,min 的相对变化；
     浅色长条 = ±20%，深色短条 = ±10%（叠在长条上）；条越长越敏感。蓝色 = 参数增大，红色 = 参数减小。ke 最长（消除越快谷越低，弹性约 -1.3 到 -2.0），A 弹性恰为 1（线性），ka 几乎无影响
   - 右图：四个方案的稳态峰（实心圆）与谷（空心圆）浓度的 Monte Carlo 95% 区间（竖线），
     参数按拟合协方差的多元正态抽样 2000 次；灰带为假想治疗窗 [3, 12] mg/L。
     只有 R2 的峰和谷区间都落在窗内；R1 谷区间跨越下界（P(达标)=3.5%），R3/R4 谷始终低于下界
3. 输入数据每列的含义与来源
   q3_sens_local.csv（results/q3_sens_local.csv 快照）：regimen、param、delta、css_max、css_min、rel_change_css_min、elasticity_css_min…
   q3_sens_mc.csv   （results/q3_sens_mc.csv 快照）   ：regimen、metric (css_max/css_min/p_in_window)、q025、q50、q975、mean
4. 参数与随机种子
   Monte Carlo：seed=42，n=2000（code/30_sensitivity.py）；局部扰动无随机性
5. 已知视觉缺陷 / 需要人工确认
   - 左图 ka 的横条几乎为零长度，读者可能误以为漏画；已在条旁标数值（数值颜色 = 对应扰动方向）
   - ke 的两条方向与颜色“交叉”（ke 增大→谷浓度降低，蓝条在左），需在图注里提醒读者
   - 右图 R3 峰值区间 (17.7–19.5) 远高于其他，纵轴被拉长
=====================================================================

## 文件

| 文件 | 说明 |
| --- | --- |
| `make_figure.py` | 绘图脚本，在项目根目录运行 `python figures/fig04_sensitivity/make_figure.py` 重新生成 |
| `fig04_sensitivity.pdf` | PDF 输出（论文引用） |
| `fig04_sensitivity.png` | PNG 输出（预览） |
| `fig04_sensitivity.svg` | SVG 输出（可编辑矢量） |
| `q3_sens_local.csv` | 数据快照，来源 `results/q3_sens_local.csv`；列：regimen, param, delta, css_max, css_min, frac_in_window, in_window, rel_change_css_min, elasticity_css_min, rel_change_css_max |
| `q3_sens_mc.csv` | 数据快照，来源 `results/q3_sens_mc.csv`；列：regimen, metric, q025, q50, q975, mean |
| `manifest.json` | 生成记录（脚本、数据、参数、字体、检查结果） |
| `review.json` | 版式自检结果 + 人工审图记录 |

## 参数

```json
{
  "target": "R2",
  "deltas": [
    0.1,
    0.2
  ],
  "window_mg_L": [
    3.0,
    12.0
  ]
}
```

## 自动检查

- 无发现

字体：Latin `Liberation Sans` / 中文 `WenQuanYi Micro Hei`；生成时间 2026-09-21T08:36:40

## 人工备注

### 人工审图（2026-09-07，Devin/Ubuntu）
- 已打开 PNG 核对：ke 条最长、A 恰为 ±20%/±10%、ka 几乎为零，与 q3_sens_local.csv 一致。
- 注意 ke 行蓝条在左（ke 增大 → 谷浓度下降），颜色表示扰动方向而非结果符号；正文图注已解释。
- 右图仅 R2 的峰/谷区间均落在灰带内，R1 谷区间上端刚触到下界（P=3.5%），与 q3_summary.json 的 p_in_window 一致。
- 自动 lint 无发现。对应正文：图 4（§7.2–7.3）。
