"""fig04_sensitivity/make_figure.py — 问题三：推荐方案对参数扰动的敏感性与参数不确定性传播。

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
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
import pandas as pd  # noqa: E402

from mm_plot_style import PALETTES, apply_style, figsize, label_panels, save_fig, snapshot_data  # noqa: E402

FIG_ID = HERE.name
SOURCES = [ROOT / "results" / "q3_sens_local.csv", ROOT / "results" / "q3_sens_mc.csv"]
TARGET = "R2"
WINDOW = (3.0, 12.0)


def main() -> None:
    apply_style(lang="zh", base_size=9, palette="default")
    loc = pd.read_csv(snapshot_data(SOURCES[0], HERE), encoding="utf-8")
    mc = pd.read_csv(snapshot_data(SOURCES[1], HERE), encoding="utf-8")
    pal = PALETTES["default"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize("full", aspect=0.42))

    d = loc[loc["regimen"] == TARGET]
    params = ["ke", "A", "ka"]
    y = np.arange(len(params))
    for i, p in enumerate(params):
        for delta, alpha in ((0.2, 0.4), (0.1, 1.0)):
            lo = float(d[(d["param"] == p) & (d["delta"] == -delta)]["rel_change_css_min"].iloc[0]) * 100
            hi = float(d[(d["param"] == p) & (d["delta"] == delta)]["rel_change_css_min"].iloc[0]) * 100
            ax1.barh(i, hi, height=0.6, color=pal[0], alpha=alpha, lw=0)
            ax1.barh(i, lo, height=0.6, color=pal[1], alpha=alpha, lw=0)
            if delta == 0.2:
                for val, col in ((hi, pal[0]), (lo, pal[1])):
                    ax1.text(val + (1.5 if val >= 0 else -1.5), i, f"{val:+.1f}%", va="center",
                             ha="left" if val >= 0 else "right", fontsize=7, color=col)
    ax1.plot([0, 0], [-0.5, len(params) - 0.5], color="#4D4D4D", lw=0.8)
    ax1.set_yticks(y)
    ax1.set_yticklabels(params)
    ax1.set_xlim(-45, 62)
    ax1.set_ylim(-0.5, len(params) - 0.5 + 1.3)
    ax1.set_xlabel("稳态谷浓度相对变化 / %")
    ax1.set_ylabel("被扰动参数")
    ax1.set_title(f"{TARGET} 局部敏感性", loc="left")
    handles = [Patch(color=pal[0], alpha=0.4, label="参数 +20%（深色为 +10%）"),
               Patch(color=pal[1], alpha=0.4, label="参数 -20%（深色为 -10%）")]
    ax1.legend(handles=handles, loc="upper right", frameon=False, fontsize=7.5)

    regimens = list(dict.fromkeys(mc["regimen"]))
    x = np.arange(len(regimens))
    ax2.axhspan(*WINDOW, color="#D9D9D9", alpha=0.7, lw=0, zorder=0, label="假想治疗窗")
    for j, (metric, mfc, lab) in enumerate((("css_max", "full", "稳态峰浓度 95% 区间"), ("css_min", "none", "稳态谷浓度 95% 区间"))):
        off = -0.15 if j == 0 else 0.15
        for i, r in enumerate(regimens):
            row = mc[(mc["regimen"] == r) & (mc["metric"] == metric)].iloc[0]
            ax2.plot([i + off, i + off], [row["q025"], row["q975"]], color=pal[i], lw=1.2)
            ax2.plot(i + off, row["q50"], "o", ms=4.5, color=pal[i], mfc=pal[i] if mfc == "full" else "white", mew=1.2)
        ax2.plot([], [], "o", color="#4D4D4D", mfc="#4D4D4D" if mfc == "full" else "white", ms=4.5, label=lab)
    pw = {r: float(mc[(mc["regimen"] == r) & (mc["metric"] == "p_in_window")]["mean"].iloc[0]) for r in regimens}
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{r}\n{pw[r]:.1%}" for r in regimens], fontsize=7.5)
    ax2.set_xlabel("方案（下行：达标概率）")
    ax2.set_ylim(0, 30)
    ax2.set_ylabel("稳态浓度 / mg/L")
    ax2.set_title("参数不确定性传播", loc="left")
    ax2.legend(loc="upper center", frameon=False, fontsize=7.5, ncol=1)
    label_panels((ax1, ax2))

    save_fig(fig, HERE / FIG_ID, source=SOURCES, params={"target": TARGET, "deltas": [0.1, 0.2], "window_mg_L": list(WINDOW)})


if __name__ == "__main__":
    main()
