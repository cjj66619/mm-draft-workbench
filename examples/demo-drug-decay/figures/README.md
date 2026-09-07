# 图表索引

> 由 `tools/figure_index.py` 自动生成。每张图一个文件夹：图 + 绘图代码/源文件 + 数据快照 + README/REDRAW_NOTES + review.json。
> 数据图由 `make_figure.py` 重生成；示意图（drawio）为机器草稿，**必须人工重画后**才可用于终稿。

| 图 | 类型 | 用途 | 自检 | 人工审图 | 输出 |
| --- | --- | --- | --- | --- | --- |
| [`fig01_roadmap`](fig01_roadmap/) | diagram | | 文件 | 说明 | | 机器草稿 | reviewed | fig01_roadmap.pdf, fig01_roadmap.png |
| [`fig02_q1_fit`](fig02_q1_fit/) | data | fig02_q1_fit/make_figure.py — 问题一：Bateman 模型拟合结果与残差。 | OK | reviewed | fig02_q1_fit.pdf, fig02_q1_fit.png, fig02_q1_fit.svg |
| [`fig03_q2_regimens`](fig03_q2_regimens/) | data | fig03_q2_regimens/make_figure.py — 问题二：四种给药方案的浓度–时间曲线与稳态峰/谷浓度对比。 | OK | reviewed | fig03_q2_regimens.pdf, fig03_q2_regimens.png, fig03_q2_regimens.svg |
| [`fig04_sensitivity`](fig04_sensitivity/) | data | fig04_sensitivity/make_figure.py — 问题三：推荐方案对参数扰动的敏感性与参数不确定性传播。 | OK | reviewed | fig04_sensitivity.pdf, fig04_sensitivity.png, fig04_sensitivity.svg |

## 重新生成全部数据图

```
python run_all.py figures
```

## 单张图

```
python figures/<fig_id>/make_figure.py
```
