"""_template_model.py — 子问题模型脚本模板（复制为 10_q1_<模型名>.py 后填空；本文件本身被 run_all 跳过）。

输入
    data/clean/q1_series.csv ：列 t（时间，天）、y（观测值，单位 …）；由 00_data_prep.py 生成。
模型（对应 reports/ANALYSIS_MODELING_REPORT.md §3.1，式 (1)–(3)）
    y(t) = a·exp(-b·t) + c
    - a：初始幅度；b：衰减率（1/天）；c：稳态水平
    - 拟合方法：非线性最小二乘（scipy.optimize.curve_fit），初值 a=y0-y_end, b=0.1, c=y_end
    - 验证：残差 RMSE、留一交叉验证
输出
    results/q1_fit_params.csv   ：a, b, c 及 95% 置信区间
    results/q1_metrics.json     ：rmse, r2, n
    results/q1_fitted.csv       ：t, y, y_hat, resid（供 figures/fig02_q1_fit 使用）
运行时间：< 5 s（CPU）
随机性：无（若有，set_seed(42) 并在 RESULTS_REPORT.md 记录）
已知限制：t 需单调；数据点 < 5 时不拟合并抛错。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import banner, load_clean, save_json, save_table, set_seed


def model(t: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.exp(-b * t) + c


def main() -> None:
    set_seed(42)
    banner("问题一：指数衰减拟合（模板）")
    df = load_clean("q1_series.csv")
    if len(df) < 5:
        raise ValueError("数据点不足 5 个，无法拟合")
    from scipy.optimize import curve_fit

    t, y = df["t"].to_numpy(float), df["y"].to_numpy(float)
    p0 = (y[0] - y[-1], 0.1, y[-1])
    popt, pcov = curve_fit(model, t, y, p0=p0, maxfev=10000)
    se = np.sqrt(np.diag(pcov))
    y_hat = model(t, *popt)
    resid = y - y_hat
    rmse = float(np.sqrt(np.mean(resid**2)))
    r2 = float(1 - np.sum(resid**2) / np.sum((y - y.mean()) ** 2))

    save_table(pd.DataFrame({"param": ["a", "b", "c"], "value": popt, "se": se,
                             "ci_low": popt - 1.96 * se, "ci_high": popt + 1.96 * se}), "q1_fit_params.csv")
    save_json({"rmse": rmse, "r2": r2, "n": int(len(df)), "seed": 42}, "q1_metrics.json")
    save_table(pd.DataFrame({"t": t, "y": y, "y_hat": y_hat, "resid": resid}), "q1_fitted.csv")
    print(f"a={popt[0]:.4g} b={popt[1]:.4g} c={popt[2]:.4g}  RMSE={rmse:.4g} R2={r2:.4f}")


if __name__ == "__main__":
    main()
