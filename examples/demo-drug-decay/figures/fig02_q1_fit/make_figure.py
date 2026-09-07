"""fig02_q1_fit/make_figure.py — 问题一：Bateman 模型拟合结果与残差。

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
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from mm_plot_style import PALETTES, apply_style, figsize, label_panels, save_fig, snapshot_data  # noqa: E402

FIG_ID = HERE.name
SOURCES = [ROOT / "results" / "q1_fitted.csv", ROOT / "results" / "q1_curve.csv", ROOT / "data" / "clean" / "pk_clean.csv"]
Y_MAX = 13.0


def main() -> None:
    apply_style(lang="zh", base_size=9, palette="default")
    fitted = pd.read_csv(snapshot_data(SOURCES[0], HERE), encoding="utf-8")
    curve = pd.read_csv(snapshot_data(SOURCES[1], HERE), encoding="utf-8")
    clean = pd.read_csv(snapshot_data(SOURCES[2], HERE), encoding="utf-8")
    subjects = sorted(s for s in fitted["subject"].unique() if s != "pooled")
    colors = dict(zip(subjects, PALETTES["default"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize("full", aspect=0.42))

    pooled = curve[curve["subject"] == "pooled"]
    ax1.fill_between(pooled["t"], pooled["ci_low"], pooled["ci_high"], color="#7F7F7F", alpha=0.3, lw=0, label="95% 置信带")
    for sid in subjects:
        c = curve[curve["subject"] == sid]
        ax1.plot(c["t"], c["c_hat"], color=colors[sid], lw=0.8, ls="--", alpha=0.8)
        obs = fitted[fitted["subject"] == sid]
        ax1.scatter(obs["t"], obs["y"], s=14, color=colors[sid], label=f"{sid} 观测", zorder=3)
    ax1.plot(pooled["t"], pooled["c_hat"], color="#000000", lw=1.4, label="合并拟合")

    flagged = clean[~clean["flag"].isin(["ok", "missing"])]
    ax1.scatter(flagged["time_h"], flagged["conc_raw"].clip(lower=0.0, upper=Y_MAX - 0.3), marker="x", s=30,
                color="#4D4D4D", lw=1.2, label="剔除点", zorder=4)
    for r in flagged.itertuples():
        if r.conc_raw > Y_MAX:
            ax1.annotate(f"实际 {r.conc_raw:.1f}", xy=(r.time_h + 0.4, Y_MAX - 0.3), xytext=(r.time_h + 1.6, Y_MAX - 0.7),
                         fontsize=7, color="#4D4D4D", va="center")
    ax1.set_ylim(-0.5, Y_MAX)
    ax1.set_xlim(-0.5, 24.5)
    ax1.set_xlabel("给药后时间 / h")
    ax1.set_ylabel("血药浓度 / mg/L")
    ax1.legend(loc="upper right", frameon=False, fontsize=7.5, ncol=1)
    ax1.set_title("拟合曲线", loc="left")

    ax2.axhline(0, color="#7F7F7F", lw=0.8)
    res = fitted[fitted["subject"] == "pooled"]
    for sid in subjects:
        pts = fitted[fitted["subject"] == sid][["t", "y"]]
        rr = res.merge(pts, on=["t", "y"])
        ax2.scatter(rr["t"], rr["resid"], s=14, color=colors[sid], label=sid)
    ax2.set_xlim(-0.5, 24.5)
    ax2.set_ylim(min(-1.8, float(res["resid"].min()) - 0.45), float(res["resid"].max()) + 0.2)
    ax2.set_xlabel("给药后时间 / h")
    ax2.set_ylabel("残差 / mg/L")
    ax2.set_title("合并拟合残差", loc="left")
    ax2.legend(loc="lower right", frameon=False, fontsize=7.5, ncol=3)
    label_panels((ax1, ax2))

    save_fig(fig, HERE / FIG_ID, source=SOURCES, params={"ci": 0.95, "y_max_clip": Y_MAX, "fit": "pooled + per-subject"})


if __name__ == "__main__":
    main()
