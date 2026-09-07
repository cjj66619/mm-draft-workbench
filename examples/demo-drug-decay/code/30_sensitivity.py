"""30_sensitivity.py — 灵敏度与稳健性检验（对应 reports/ROBUSTNESS_REPORT.md；模型见 ANALYSIS_MODELING_REPORT.md §5）。

输入
    results/q1_summary.json  ：pooled 与各受试者的参数、pcov
    results/q2_regimens.csv  ：候选方案（剂量、间隔）与治疗窗判定
    data/clean/pk_clean.csv  ：用于"不清洗直接拟合"的对照
做什么
    S1 局部单因素灵敏度（OAT）：对 pooled 参数 A、ka、ke 分别 ±10%、±20%，重算各方案的 C_ss,max、C_ss,min、
       窗内占比；报告相对变化与弹性系数 E = (ΔY/Y)/(Δθ/θ)。
    S2 参数不确定性传播（蒙特卡洛，seed=42，N=2000）：从 N(θ̂, pcov) 抽样（截断到 A>0、ka>ke>0），
       对每个方案计算 C_ss,min、C_ss,max 的 2.5%/50%/97.5% 分位数及"同时满足治疗窗"的概率。
    S3 个体层面检验：用 S01–S03 各自的参数评估每个方案是否满足治疗窗（群体推荐是否对个体都成立）。
    S4 数据清洗的影响：不剔除离群/负值（仅去缺失）直接做 pooled 拟合，对比参数与 RMSE 的变化，
       说明清洗规则对结论的影响方向与幅度。
输出
    results/q3_sens_local.csv     ：regimen, param, delta, css_max, css_min, frac_in_window, rel_change_css_min, elasticity_css_min
    results/q3_sens_mc.csv        ：regimen, metric, q025, q50, q975, mean；以及 p_in_window
    results/q3_individual.csv     ：regimen, subject, css_max, css_min, in_window
    results/q3_cleaning_effect.csv：variant, n, A, ka, ke, rmse
    results/q3_summary.json       ：关键结论（最敏感参数、推荐方案的达标概率、个体一致性）
运行时间：< 10 s
随机性：S2 使用 numpy default_rng(42)
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from common import RESULTS, banner, load_clean, load_json, save_json, save_table

sys.path.insert(0, str(Path(__file__).resolve().parent))
q1 = importlib.import_module("10_q1_fit_bateman")
q2 = importlib.import_module("20_q2_dosing_sim")

SEED = 42
N_MC = 2000
DELTAS = (-0.2, -0.1, 0.1, 0.2)


def metrics_for(reg: pd.DataFrame, A: float, ka: float, ke: float) -> list[dict]:  # noqa: N803
    return [{"regimen": r.regimen, **q2.regimen_metrics(r.dose_mg, r.tau_h, A, ka, ke)} for r in reg.itertuples()]


def main() -> None:
    banner("灵敏度与稳健性检验")
    summ = load_json("q1_summary.json")
    reg = pd.read_csv(RESULTS / "q2_regimens.csv", encoding="utf-8")
    p = summ["pooled"]["params"]
    theta = np.array([p["A"], p["ka"], p["ke"]])
    pcov = np.array(summ["pooled"]["pcov"])
    base = {m["regimen"]: m for m in metrics_for(reg, *theta)}

    # S1 局部单因素
    rows = []
    for j, name in enumerate(q1.PARAMS):
        for d in DELTAS:
            th = theta.copy()
            th[j] *= 1 + d
            if not th[1] > th[2]:
                continue
            for m in metrics_for(reg, *th):
                b = base[m["regimen"]]
                rel = (m["css_min"] - b["css_min"]) / b["css_min"]
                rows.append({"regimen": m["regimen"], "param": name, "delta": d, "css_max": m["css_max"], "css_min": m["css_min"],
                             "frac_in_window": m["frac_in_window"], "in_window": m["in_window"],
                             "rel_change_css_min": rel, "elasticity_css_min": rel / d,
                             "rel_change_css_max": (m["css_max"] - b["css_max"]) / b["css_max"]})
    local = pd.DataFrame(rows)
    save_table(local, "q3_sens_local.csv")
    elas = local[local["delta"].abs() == 0.2].groupby("param")["elasticity_css_min"].apply(lambda s: float(s.abs().mean()))
    most_sensitive = str(elas.idxmax())
    print("S1 弹性(|E| 均值, C_ss,min)：", elas.round(3).to_dict())

    # S2 蒙特卡洛
    rng = np.random.default_rng(SEED)
    draws = rng.multivariate_normal(theta, pcov, size=N_MC * 2)
    draws = draws[(draws[:, 0] > 0) & (draws[:, 2] > 0) & (draws[:, 1] > draws[:, 2])][:N_MC]
    mc_rows, p_in = [], {}
    for r in reg.itertuples():
        vals = np.array([[m["css_max"], m["css_min"], m["in_window"]]
                         for m in (q2.regimen_metrics(r.dose_mg, r.tau_h, *th) for th in draws)])
        for k, name in enumerate(("css_max", "css_min")):
            q = np.percentile(vals[:, k], [2.5, 50, 97.5])
            mc_rows.append({"regimen": r.regimen, "metric": name, "q025": q[0], "q50": q[1], "q975": q[2], "mean": vals[:, k].mean()})
        p_in[r.regimen] = float(vals[:, 2].mean())
        mc_rows.append({"regimen": r.regimen, "metric": "p_in_window", "q025": np.nan, "q50": np.nan, "q975": np.nan, "mean": p_in[r.regimen]})
        print(f"S2 [{r.regimen}] Css,min 95%区间 [{vals[:,1].min():.2f}…] q2.5={np.percentile(vals[:,1],2.5):.2f} "
              f"q97.5={np.percentile(vals[:,1],97.5):.2f}  P(达标)={p_in[r.regimen]:.3f}")
    save_table(pd.DataFrame(mc_rows), "q3_sens_mc.csv")

    # S3 个体层面
    ind_rows = []
    for sid, s in summ.items():
        if sid.startswith("_") or sid == "pooled":
            continue
        pi = s["params"]
        for m in metrics_for(reg, pi["A"], pi["ka"], pi["ke"]):
            ind_rows.append({"regimen": m["regimen"], "subject": sid, "css_max": m["css_max"], "css_min": m["css_min"],
                             "frac_in_window": m["frac_in_window"], "in_window": m["in_window"]})
    ind = pd.DataFrame(ind_rows)
    save_table(ind, "q3_individual.csv")
    consistency = ind.groupby("regimen")["in_window"].all().to_dict()
    print("S3 个体全部达标：", consistency)

    # S4 清洗影响
    clean = load_clean("pk_clean.csv")
    variants = {
        "cleaned(use_for_fit)": clean[clean["use_for_fit"]],
        "raw_no_missing": clean[clean["conc_raw"].notna()].assign(conc=lambda d: d["conc_raw"]),
    }
    ce_rows = []
    for name, d in variants.items():
        t, y = d["time_h"].to_numpy(float), d["conc"].to_numpy(float)
        popt, _ = q1.fit_one(t, y)
        resid = y - q1.bateman(t, *popt)
        ce_rows.append({"variant": name, "n": len(t), "A": popt[0], "ka": popt[1], "ke": popt[2],
                        "t_half": np.log(2) / popt[2], "rmse": float(np.sqrt(np.mean(resid**2)))})
    ce = pd.DataFrame(ce_rows)
    save_table(ce, "q3_cleaning_effect.csv")
    print(ce.round(4).to_string(index=False))

    rec = load_json("q2_summary.json")["recommended"]["regimen"]
    save_json({
        "seed": SEED, "n_mc": int(len(draws)), "deltas": list(DELTAS),
        "most_sensitive_param_css_min": most_sensitive,
        "elasticity_css_min_abs_mean": {k: float(v) for k, v in elas.items()},
        "p_in_window": p_in, "recommended_regimen": rec, "recommended_p_in_window": p_in[rec],
        "individual_all_in_window": {k: bool(v) for k, v in consistency.items()},
        "cleaning_effect": {"ke_rel_change": float(ce.loc[1, "ke"] / ce.loc[0, "ke"] - 1),
                            "A_rel_change": float(ce.loc[1, "A"] / ce.loc[0, "A"] - 1),
                            "rmse_ratio": float(ce.loc[1, "rmse"] / ce.loc[0, "rmse"])},
    }, "q3_summary.json")


if __name__ == "__main__":
    main()
