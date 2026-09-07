"""20_q2_dosing_sim.py — 问题二：多次给药方案模拟与稳态谷/峰浓度（对应 reports/ANALYSIS_MODELING_REPORT.md §4，式 (7)–(10)）。

输入
    results/q1_summary.json ：pooled 拟合的 A、ka、ke（单次 500 mg 口服）
做什么
    线性药动学假设下，剂量 D 的单次给药曲线 C_1(t; D) = (D/500)·A·(exp(-ke·t) - exp(-ka·t))。
    多次给药（每 τ 小时一次，共 N 次）按叠加原理：                                   (7)
        C(t) = Σ_{k=0}^{N-1} C_1(t - k·τ; D) · 1[t ≥ k·τ]
    稳态（N→∞）一个给药间隔内的解析式：                                              (8)
        C_ss(t) = (D/500)·A·[ exp(-ke·t)/(1-exp(-ke·τ)) - exp(-ka·t)/(1-exp(-ka·τ)) ],  0 ≤ t < τ
    稳态峰浓度 C_ss,max = max_t C_ss(t)（网格 + 局部精细搜索），稳态谷浓度 C_ss,min = C_ss(τ⁻)（对本模型
    C_ss 在 [tmax_ss, τ) 单调下降，因此谷值在给药前一刻取得）。                        (9)
    累积系数 R = 1/(1-exp(-ke·τ))；波动度 PTF = (C_ss,max - C_ss,min)/C_ss,avg，C_ss,avg = AUC_τ/τ = (D/500)·A·(1/ke-1/ka)/τ；
    达到 90% 稳态所需时间 t_90 = ln(10)/ke（≈3.32 个半衰期）。                            (10)
    评价指标：给定"假想治疗窗" [C_low, C_high] = [3, 12] mg/L（演示用设定，非真实药物数据），
    计算稳态一个间隔内浓度落在窗内的时间占比 frac_in_window，以及 C_ss,min ≥ C_low 且 C_ss,max ≤ C_high 是否同时满足。
    候选方案（日总量均为 1000 mg，另加一个低日剂量参照）：
        R1 500 mg q12h · R2 250 mg q6h · R3 1000 mg q24h · R4 375 mg q12h（日总量 750 mg）
输出
    results/q2_regimens.csv ：regimen, dose_mg, tau_h, daily_dose_mg, css_max, css_min, css_avg, ptf, accumulation, t90_h,
                              frac_in_window, in_window（供 RESULTS_REPORT 与 fig03）
    results/q2_profiles.csv ：regimen, t, conc（0–72 h 叠加曲线，步长 0.05 h；供 figures/fig03_q2_regimens 使用）
    results/q2_summary.json ：治疗窗、参数来源、推荐方案
运行时间：< 2 s
随机性：无
已知限制：线性叠加假设；用 pooled 参数忽略个体差异（个体层面的结论见 30_sensitivity.py）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import banner, load_json, save_json, save_table

REF_DOSE = 500.0
WINDOW = (3.0, 12.0)   # 假想治疗窗 mg/L（演示用）
REGIMENS = [
    {"regimen": "R1", "label": "500 mg q12h", "dose_mg": 500.0, "tau_h": 12.0},
    {"regimen": "R2", "label": "250 mg q6h", "dose_mg": 250.0, "tau_h": 6.0},
    {"regimen": "R3", "label": "1000 mg q24h", "dose_mg": 1000.0, "tau_h": 24.0},
    {"regimen": "R4", "label": "375 mg q12h", "dose_mg": 375.0, "tau_h": 12.0},
]
T_END, DT = 72.0, 0.05


def single_dose(t: np.ndarray, dose: float, A: float, ka: float, ke: float) -> np.ndarray:  # noqa: N803
    t = np.asarray(t, dtype=float)
    return np.where(t >= 0, (dose / REF_DOSE) * A * (np.exp(-ke * np.clip(t, 0, None)) - np.exp(-ka * np.clip(t, 0, None))), 0.0)


def superpose(t: np.ndarray, dose: float, tau: float, A: float, ka: float, ke: float) -> np.ndarray:  # noqa: N803
    n_doses = int(np.floor(t.max() / tau)) + 1
    return sum(single_dose(t - k * tau, dose, A, ka, ke) for k in range(n_doses))


def steady_state(t: np.ndarray, dose: float, tau: float, A: float, ka: float, ke: float) -> np.ndarray:  # noqa: N803
    scale = (dose / REF_DOSE) * A
    return scale * (np.exp(-ke * t) / (1 - np.exp(-ke * tau)) - np.exp(-ka * t) / (1 - np.exp(-ka * tau)))


def regimen_metrics(dose: float, tau: float, A: float, ka: float, ke: float) -> dict:  # noqa: N803
    grid = np.linspace(0.0, tau, 4001)
    css = steady_state(grid, dose, tau, A, ka, ke)
    css_max, css_min = float(css.max()), float(css[-1])
    css_avg = float((dose / REF_DOSE) * A * (1 / ke - 1 / ka) / tau)
    in_win = (css >= WINDOW[0]) & (css <= WINDOW[1])
    return {
        "css_max": css_max, "css_min": css_min, "css_avg": css_avg,
        "tmax_ss_h": float(grid[int(css.argmax())]),
        "ptf": (css_max - css_min) / css_avg,
        "accumulation": 1 / (1 - np.exp(-ke * tau)),
        "t90_h": float(np.log(10) / ke),
        "frac_in_window": float(in_win.mean()),
        "in_window": bool(css_min >= WINDOW[0] and css_max <= WINDOW[1]),
    }


def main() -> None:
    banner("问题二：多次给药方案模拟")
    q1 = load_json("q1_summary.json")
    p = q1["pooled"]["params"]
    A, ka, ke = p["A"], p["ka"], p["ke"]  # noqa: N806
    t = np.round(np.arange(0.0, T_END + 1e-9, DT), 4)

    rows, profiles = [], []
    for r in REGIMENS:
        m = regimen_metrics(r["dose_mg"], r["tau_h"], A, ka, ke)
        rows.append({**r, "daily_dose_mg": r["dose_mg"] * 24 / r["tau_h"], **m})
        conc = superpose(t, r["dose_mg"], r["tau_h"], A, ka, ke)
        profiles.append(pd.DataFrame({"regimen": r["regimen"], "label": r["label"], "t": t, "conc": conc}))
        print(f"[{r['regimen']}] {r['label']:13s} Css,max={m['css_max']:.2f} Css,min={m['css_min']:.2f} "
              f"Css,avg={m['css_avg']:.2f} PTF={m['ptf']:.2f} R={m['accumulation']:.2f} 窗内占比={m['frac_in_window']:.2f} 达标={m['in_window']}")

    reg = pd.DataFrame(rows)
    save_table(reg, "q2_regimens.csv")
    save_table(pd.concat(profiles, ignore_index=True), "q2_profiles.csv")

    ok = reg[reg["in_window"]]
    # 推荐规则：先满足治疗窗；再取波动度最小者；若全不达标，取窗内占比最高者
    best = (ok.sort_values("ptf").iloc[0] if len(ok) else reg.sort_values("frac_in_window", ascending=False).iloc[0])
    save_json({
        "params_source": "results/q1_summary.json (pooled)", "params": {"A": A, "ka": ka, "ke": ke},
        "ref_dose_mg": REF_DOSE, "window_mg_L": list(WINDOW), "window_note": "假想治疗窗，演示用设定",
        "t_end_h": T_END, "dt_h": DT,
        "recommended": {"regimen": best["regimen"], "label": best["label"], "rule": "满足治疗窗中 PTF 最小"},
        "n_in_window": int(reg["in_window"].sum()),
    }, "q2_summary.json")
    print(f"推荐方案：{best['regimen']} {best['label']}")


if __name__ == "__main__":
    main()
