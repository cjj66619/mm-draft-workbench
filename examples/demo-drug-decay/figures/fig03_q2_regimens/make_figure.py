"""fig03_q2_regimens/make_figure.py — 问题二：四种给药方案的浓度–时间曲线与稳态峰/谷浓度对比。

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
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from mm_plot_style import PALETTES, apply_style, figsize, label_panels, save_fig, snapshot_data  # noqa: E402

FIG_ID = HERE.name
SOURCES = [ROOT / "results" / "q2_profiles.csv", ROOT / "results" / "q2_regimens.csv"]
WINDOW = (3.0, 12.0)


def main() -> None:
    apply_style(lang="zh", base_size=9, palette="default")
    prof = pd.read_csv(snapshot_data(SOURCES[0], HERE), encoding="utf-8")
    reg = pd.read_csv(snapshot_data(SOURCES[1], HERE), encoding="utf-8")
    regimens = list(reg["regimen"])
    colors = dict(zip(regimens, PALETTES["default"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize("full", aspect=0.42))

    ax1.axhspan(*WINDOW, color="#D9D9D9", alpha=0.7, lw=0, zorder=0, label=f"假想治疗窗 {WINDOW[0]:g}–{WINDOW[1]:g} mg/L")
    for r in reg.itertuples():
        d = prof[prof["regimen"] == r.regimen]
        ax1.plot(d["t"], d["conc"], color=colors[r.regimen], lw=1.0, label=r.regimen)
    ax1.set_xlim(0, 72)
    ax1.set_ylim(0, 27)
    ax1.set_xticks(np.arange(0, 73, 12))
    ax1.set_xlabel("首次给药后时间 / h")
    ax1.set_ylabel("血药浓度 / mg/L")
    ax1.set_title("多次给药曲线", loc="left")
    ax1.legend(loc="upper right", frameon=False, fontsize=7.5, ncol=3, columnspacing=0.8, handlelength=1.2, handletextpad=0.4)

    x = np.arange(len(regimens))
    w = 0.38
    ax2.bar(x - w / 2, reg["css_max"], w, color=[colors[r] for r in regimens], label="稳态峰浓度")
    ax2.bar(x + w / 2, reg["css_min"], w, color=[colors[r] for r in regimens], alpha=0.45, label="稳态谷浓度")
    ax2.axhspan(*WINDOW, color="#D9D9D9", alpha=0.7, lw=0, zorder=0)
    for i, r in enumerate(reg.itertuples()):
        ax2.text(i - w / 2, r.css_max + 0.3, f"{r.css_max:.1f}", ha="center", va="bottom", fontsize=7)
        ax2.text(i + w / 2, r.css_min + 0.3, f"{r.css_min:.1f}", ha="center", va="bottom", fontsize=7)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{r.regimen}\n{r.label.replace(' q', chr(10) + 'q')}" for r in reg.itertuples()], fontsize=7.5)
    ax2.set_ylim(0, 27)
    ax2.set_ylabel("稳态浓度 / mg/L")
    ax2.set_title("稳态峰/谷浓度", loc="left")
    ax2.legend(loc="upper left", frameon=False, fontsize=7.5)
    label_panels((ax1, ax2))

    save_fig(fig, HERE / FIG_ID, source=SOURCES, params={"window_mg_L": list(WINDOW), "t_end_h": 72})


if __name__ == "__main__":
    main()
