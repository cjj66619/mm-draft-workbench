"""figNN_<名字>/make_figure.py — 数据图脚本模板（复制整个文件夹并改名后填空；`_` 开头的文件夹被 run_all 跳过）。

============================== 图的说明（必填，这一段会被同步到本文件夹 README.md）==============================
1. 回答什么问题
   问题一：指数衰减模型能否刻画观测序列？拟合优度如何？（对应论文 §5.4 结果分析，式 (1)）
2. 每个图元对应的机理
   - 散点：原始观测 y(t)，来自 data/clean/q1_series.csv（清洗规则见 reports/DATA_REPORT.md §2）
   - 实线：拟合曲线 y_hat = a·exp(-b·t) + c，参数来自 results/q1_fit_params.csv
   - 阴影：参数 95% 置信区间对应的曲线带（a、c 各取 ±1.96·se，b 取点估计）——只表征参数不确定性，不含观测噪声
   - 右子图：残差 y - y_hat 随 t 的分布，用来看是否存在系统性偏差（若呈趋势，说明模型缺项）
3. 输入数据每列的含义与来源
   data.csv（由 snapshot_data 从 results/q1_fitted.csv 拷贝）：t 时间(天)、y 观测、y_hat 拟合值、resid 残差
4. 参数与随机种子
   无随机性；拟合参数来自 code/10_q1_fit.py（seed=42）
5. 已知视觉缺陷 / 需要人工确认
   - 数据点密集时散点可能压住拟合线，必要时减小 marker 或加透明度
   - 图例位置 auto，若压到数据请手动指定 loc
   - 同一字符串里不要混用中文与 $公式$：Matplotlib mathtext 不做字体回退，中文会渲染成 ¤（lint 会报 pdf_text_outside『¤¤¤』）。
     公式单独放一条 ax.text()，或用纯中文/纯 ASCII 的标签
====================================================================================================================
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from mm_plot_style import apply_style, figsize, label_panels, save_fig, snapshot_data  # noqa: E402

FIG_ID = HERE.name                          # 文件夹名即图名，例如 fig02_q1_fit
SOURCE = ROOT / "results" / "q1_fitted.csv"  # 绘图数据的真源（改这里，不要手改 data.csv）


def main() -> None:
    apply_style(lang="zh", base_size=9, palette="default")
    data = snapshot_data(SOURCE, HERE, name="data.csv")   # 一图一文件夹：把数据快照进来
    df = pd.read_csv(data, encoding="utf-8")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize("full", aspect=0.42))
    ax1.scatter(df["t"], df["y"], s=12, alpha=0.7, label="观测")
    ax1.plot(df["t"], df["y_hat"], lw=1.4, label="拟合曲线")
    ax1.set_xlabel("时间 t / 天")
    ax1.set_ylabel("观测值 y")
    ax1.legend(loc="best", frameon=False)
    ax1.set_title("拟合结果", loc="left")

    ax2.axhline(0, color="0.5", lw=0.8)
    ax2.scatter(df["t"], df["resid"], s=12, alpha=0.7)
    ax2.set_xlabel("时间 t / 天")
    ax2.set_ylabel("残差")
    ax2.set_title("残差", loc="left")
    label_panels((ax1, ax2))

    save_fig(fig, HERE / FIG_ID, source=SOURCE, params={"seed": 42, "ci": 0.95})


if __name__ == "__main__":
    main()
