"""10_q1_fit_bateman.py — 问题一：Bateman 一室口服模型的参数估计（对应 reports/ANALYSIS_MODELING_REPORT.md §3，式 (1)–(6)）。

输入
    data/clean/pk_clean.csv ：subject, time_h, conc, flag, use_for_fit（由 00_data_prep.py 生成；只用 use_for_fit=True 的行）
模型
    C(t) = A·(exp(-ke·t) - exp(-ka·t))                                   (1)
    - A = F·D·ka / (V·(ka - ke))，mg/L；ka 吸收速率常数 (1/h)；ke 消除速率常数 (1/h)
    - 参数约束 A>0、ka>ke>0（bounds 下界 0；A>0 使 ka>ke 分支被自动选中）
    - 拟合方法：非线性最小二乘 scipy.optimize.curve_fit（Levenberg–Marquardt / trf），
      初值：ke 由末端 4 点 ln C 的线性回归斜率给出；ka = 5·ke；A = Cmax/(exp(-ke·tmax) - exp(-ka·tmax))
    - 不确定性：SE 取 sqrt(diag(pcov))；95% CI 用 t(n-3) 分位数                         (2)
    - 派生量：t_half = ln2/ke；tmax = ln(ka/ke)/(ka-ke)；Cmax = C(tmax)；AUC(0,∞) = A·(1/ke - 1/ka)  (3)–(5)
      派生量的 SE 用 delta 法：Var(g) = ∇g^T · pcov · ∇g（数值梯度）
    - 曲线 95% 置信带：delta 法 Var(C(t)) = ∇_θ C^T · pcov · ∇_θ C，带宽 = t(n-3) · sqrt(Var)      (6)
    - 验证：残差 RMSE、R²、留一交叉验证 LOO-RMSE（逐点剔除后重拟合并预测被剔点）
    - 拟合对象：每名受试者单独拟合（S01–S03）+ 三人合并的"群体"拟合（pooled，naive pooled data 方法）
输出
    results/q1_fit_params.csv ：subject, param, value, se, ci_low, ci_high（含 A、ka、ke 与 4 个派生量）
    results/q1_metrics.csv    ：subject, n, rmse, r2, loo_rmse, aic
    results/q1_fitted.csv     ：subject, t, y, y_hat, resid（供 figures/fig02_q1_fit 使用）
    results/q1_curve.csv      ：subject, t, c_hat, ci_low, ci_high（t 网格 0–24 h，步长 0.1 h）
    results/q1_summary.json   ：pooled 参数点估计与 pcov（供 20_q2、30_sensitivity 使用）
运行时间：< 5 s（CPU）
随机性：无（curve_fit 是确定性算法）
已知限制：受试者有效点 < 6 时跳过并记录；合并拟合忽略个体间差异，参数 SE 会偏小。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import curve_fit

from common import banner, load_clean, save_json, save_table

PARAMS = ("A", "ka", "ke")
MIN_POINTS = 6
CI_LEVEL = 0.95
T_GRID = np.round(np.arange(0.0, 24.0 + 1e-9, 0.1), 3)


def bateman(t: np.ndarray, A: float, ka: float, ke: float) -> np.ndarray:  # noqa: N803
    return A * (np.exp(-ke * t) - np.exp(-ka * t))


def initial_guess(t: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    order = np.argsort(t)
    t, y = t[order], y[order]
    tail = slice(max(0, len(t) - 4), len(t))
    slope, _ = np.polyfit(t[tail], np.log(np.clip(y[tail], 1e-6, None)), 1)
    ke0 = float(min(max(-slope, 0.02), 2.0))
    ka0 = 5.0 * ke0
    i = int(np.argmax(y))
    denom = np.exp(-ke0 * t[i]) - np.exp(-ka0 * t[i])
    a0 = float(y[i] / denom) if denom > 1e-9 else float(y.max() * 2)
    return a0, ka0, ke0


def fit_one(t: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p0 = initial_guess(t, y)
    popt, pcov = curve_fit(bateman, t, y, p0=p0, bounds=(0.0, np.inf), maxfev=20000)
    return popt, pcov


def num_grad(func, theta: np.ndarray, rel: float = 1e-6) -> np.ndarray:
    """对 func(theta) → 向量 求数值梯度，返回形状 (len(output), len(theta))。"""
    base = np.atleast_1d(func(theta))
    grad = np.zeros((base.size, theta.size))
    for j in range(theta.size):
        h = rel * max(abs(theta[j]), 1e-3)
        tp, tm = theta.copy(), theta.copy()
        tp[j] += h
        tm[j] -= h
        grad[:, j] = (np.atleast_1d(func(tp)) - np.atleast_1d(func(tm))) / (2 * h)
    return grad


def derived(theta: np.ndarray) -> np.ndarray:
    A, ka, ke = theta  # noqa: N806
    tmax = np.log(ka / ke) / (ka - ke)
    return np.array([np.log(2) / ke, tmax, bateman(tmax, A, ka, ke), A * (1 / ke - 1 / ka)])


DERIVED_NAMES = ("t_half", "tmax", "Cmax", "AUC_inf")


def loo_rmse(t: np.ndarray, y: np.ndarray) -> float:
    errs = []
    for i in range(len(t)):
        mask = np.arange(len(t)) != i
        try:
            popt, _ = fit_one(t[mask], y[mask])
        except RuntimeError:
            continue
        errs.append(y[i] - bateman(t[i], *popt))
    return float(np.sqrt(np.mean(np.square(errs)))) if errs else float("nan")


def main() -> None:
    banner("问题一：Bateman 一室模型参数估计")
    df = load_clean("pk_clean.csv")
    df = df[df["use_for_fit"]].copy()
    groups = {sid: g for sid, g in df.groupby("subject")}
    groups["pooled"] = df

    params_rows, metric_rows, fitted_rows, curve_rows = [], [], [], []
    summary: dict = {}
    for sid, g in groups.items():
        t, y = g["time_h"].to_numpy(float), g["conc"].to_numpy(float)
        n = len(t)
        if n < MIN_POINTS:
            print(f"[{sid}] 有效点 {n} < {MIN_POINTS}，跳过")
            continue
        popt, pcov = fit_one(t, y)
        dof = n - len(PARAMS)
        tq = float(stats.t.ppf(0.5 + CI_LEVEL / 2, dof))
        se = np.sqrt(np.diag(pcov))
        y_hat = bateman(t, *popt)
        resid = y - y_hat
        rss = float(np.sum(resid**2))
        rmse = float(np.sqrt(rss / n))
        r2 = float(1 - rss / np.sum((y - y.mean()) ** 2))
        aic = float(n * np.log(rss / n) + 2 * len(PARAMS))
        loo = loo_rmse(t, y)

        for name, v, s in zip(PARAMS, popt, se):
            params_rows.append({"subject": sid, "param": name, "value": v, "se": s, "ci_low": v - tq * s, "ci_high": v + tq * s})
        d = derived(popt)
        gd = num_grad(derived, popt)
        d_se = np.sqrt(np.einsum("ij,jk,ik->i", gd, pcov, gd))
        for name, v, s in zip(DERIVED_NAMES, d, d_se):
            params_rows.append({"subject": sid, "param": name, "value": v, "se": s, "ci_low": v - tq * s, "ci_high": v + tq * s})
        metric_rows.append({"subject": sid, "n": n, "rmse": rmse, "r2": r2, "loo_rmse": loo, "aic": aic})
        fitted_rows.append(pd.DataFrame({"subject": sid, "t": t, "y": y, "y_hat": y_hat, "resid": resid}))

        c_hat = bateman(T_GRID, *popt)
        gc = num_grad(lambda th: bateman(T_GRID, *th), popt)
        c_se = np.sqrt(np.einsum("ij,jk,ik->i", gc, pcov, gc))
        curve_rows.append(pd.DataFrame({"subject": sid, "t": T_GRID, "c_hat": c_hat,
                                        "ci_low": c_hat - tq * c_se, "ci_high": c_hat + tq * c_se}))
        summary[sid] = {"n": n, "params": dict(zip(PARAMS, popt.tolist())), "se": dict(zip(PARAMS, se.tolist())),
                        "pcov": pcov.tolist(), "derived": dict(zip(DERIVED_NAMES, d.tolist())),
                        "rmse": rmse, "r2": r2, "loo_rmse": loo, "t_quantile": tq}
        print(f"[{sid:6s}] n={n:2d} A={popt[0]:.3f} ka={popt[1]:.3f} ke={popt[2]:.4f} "
              f"t1/2={d[0]:.2f}h tmax={d[1]:.2f}h Cmax={d[2]:.2f} RMSE={rmse:.3f} LOO={loo:.3f} R2={r2:.4f}")

    save_table(pd.DataFrame(params_rows), "q1_fit_params.csv")
    save_table(pd.DataFrame(metric_rows), "q1_metrics.csv")
    save_table(pd.concat(fitted_rows, ignore_index=True), "q1_fitted.csv")
    save_table(pd.concat(curve_rows, ignore_index=True), "q1_curve.csv")
    summary["_meta"] = {"model": "C(t)=A*(exp(-ke*t)-exp(-ka*t))", "ci_level": CI_LEVEL, "min_points": MIN_POINTS,
                        "dose_mg": 500.0, "method": "scipy.optimize.curve_fit, bounds>=0"}
    save_json(summary, "q1_summary.json")


if __name__ == "__main__":
    main()
