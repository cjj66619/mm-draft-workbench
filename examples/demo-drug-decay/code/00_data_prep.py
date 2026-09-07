"""00_data_prep.py — 原始血药浓度数据审计与清洗（对应 reports/DATA_REPORT.md §2–§3）。

输入
    data/raw/pk_raw.csv ：subject（受试者编号）、time_h（给药后时间，h）、conc_mg_L（血药浓度，mg/L）
做什么
    1. 结构检查：列名、受试者数、每人采样点数、时间网格是否一致。
    2. 逐行打标（不删行，所有原始行保留）：
       - missing  ：浓度为空
       - negative ：浓度 < 0（物理上不可能，视为检测下限以下或录入错误）
       - outlier  ：MAD 稳健 z 值 > 3.5（Leys et al., 2013）。统计量为"留一对数线性插值残差"：
                    对每个受试者，用相邻两个有效点在 (t, ln C) 平面上线性插值预测第 i 点（首尾两点不参与：
                    外推在吸收相与末端相都不可靠，它们只受 missing/negative 规则约束，这是本方法的已知局限），
                    r_i = ln C_i - 预测值；所有受试者的 r 合并后取中位数与 MAD。只对 C > 0 的点计算。
                    逐个剔除：每轮只标记 |z| 最大且 > 3.5 的一点，重算后继续，直到无点超阈（最多 5 轮），
                    以免已知离群点污染邻点的插值预测（掩蔽效应）。
                    选择个体内相邻点而不是跨个体中位数，是因为 3 名受试者的个体间变异本身就会被误判为离群
       - ok       ：其余
    3. 输出清洗表：conc_raw 保留原值；conc 在 flag != ok 时置 NaN；use_for_fit = (flag == ok)。
输出
    data/clean/pk_clean.csv      ：subject, time_h, conc_raw, conc, log_resid, robust_z, flag, use_for_fit
    results/data_quality.json    ：行数、各类 flag 计数、每个受试者可用点数、MAD 参数（供 DATA_REPORT 引用）
    results/data_quality_flags.csv：被标记行的清单
运行时间：< 1 s
随机性：无
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import DATA_CLEAN, banner, load_raw, save_json, save_table

RAW_FILE = "pk_raw.csv"
MAD_THRESHOLD = 3.5
MAD_SCALE = 1.4826  # 正态一致性常数
MAX_OUTLIERS = 5    # 逐个剔除的上限，防止循环失控


def loo_linear_predict(t: np.ndarray, y: np.ndarray) -> np.ndarray:
    """对已按 t 排序的序列，用相邻两点线性插值预测每个内点；两端点无法插值，返回 NaN。"""
    n = len(t)
    pred = np.full(n, np.nan)
    for i in range(1, n - 1):
        j, k = i - 1, i + 1
        slope = (y[k] - y[j]) / (t[k] - t[j])
        pred[i] = y[j] + slope * (t[i] - t[j])
    return pred


def main() -> None:
    banner("数据审计与清洗：pk_raw.csv → pk_clean.csv")
    df = load_raw(RAW_FILE)
    expected = ["subject", "time_h", "conc_mg_L"]
    if list(df.columns) != expected:
        raise ValueError(f"列名不符：{list(df.columns)}，期望 {expected}")
    df = df.rename(columns={"conc_mg_L": "conc_raw"}).sort_values(["subject", "time_h"]).reset_index(drop=True)

    grids = df.groupby("subject")["time_h"].apply(lambda s: tuple(sorted(s)))
    same_grid = grids.nunique() == 1

    flag = pd.Series("ok", index=df.index, dtype=object)
    flag[df["conc_raw"].isna()] = "missing"
    flag[(flag == "ok") & (df["conc_raw"] < 0)] = "negative"

    # MAD 稳健离群检测：个体内留一对数线性插值残差，逐个剔除（避免离群点污染邻点的预测值）
    log_resid = pd.Series(np.nan, index=df.index)
    robust_z = pd.Series(np.nan, index=df.index)
    center = mad = float("nan")
    flagged_z: dict[int, float] = {}
    while True:
        pos = (flag == "ok") & (df["conc_raw"] > 0)
        log_resid[:] = np.nan
        for _, idx in df[pos].groupby("subject").groups.items():
            idx = list(idx)
            t = df.loc[idx, "time_h"].to_numpy(float)
            y = np.log(df.loc[idx, "conc_raw"].to_numpy(float))
            log_resid[idx] = y - loo_linear_predict(t, y)
        center = float(np.nanmedian(log_resid))
        mad = float(np.nanmedian(np.abs(log_resid - center)))
        if not mad > 0:
            break
        robust_z = (log_resid - center) / (MAD_SCALE * mad)
        worst = robust_z.abs().idxmax()
        if not robust_z.abs()[worst] > MAD_THRESHOLD or len(flagged_z) >= MAX_OUTLIERS:
            break
        flag[worst] = "outlier"
        flagged_z[int(worst)] = float(robust_z[worst])
    for i, z in flagged_z.items():   # 离群点记录被标记时的 z（剔除后不再参与计算）
        robust_z[i] = z

    out = df.copy()
    out["conc"] = out["conc_raw"].where(flag == "ok")
    out["log_resid"] = log_resid.round(5)
    out["robust_z"] = robust_z.round(3)
    out["flag"] = flag
    out["use_for_fit"] = flag == "ok"
    save_table(out, "pk_clean.csv", folder=DATA_CLEAN)

    flagged = out[out["flag"] != "ok"][["subject", "time_h", "conc_raw", "robust_z", "flag"]]
    save_table(flagged, "data_quality_flags.csv")
    summary = {
        "raw_file": RAW_FILE,
        "n_rows": int(len(out)),
        "n_subjects": int(out["subject"].nunique()),
        "n_timepoints": int(out["time_h"].nunique()),
        "same_time_grid": bool(same_grid),
        "time_grid_h": [float(x) for x in sorted(out["time_h"].unique())],
        "flag_counts": {k: int(v) for k, v in out["flag"].value_counts().items()},
        "usable_per_subject": {k: int(v) for k, v in out.groupby("subject")["use_for_fit"].sum().items()},
        "mad": {"threshold": MAD_THRESHOLD, "scale": MAD_SCALE, "center_log_resid": round(center, 5), "mad_log_resid": round(mad, 5)},
        "conc_range_ok": [float(out["conc"].min()), float(out["conc"].max())],
        "flagged_rows": flagged.to_dict(orient="records"),
    }
    save_json(summary, "data_quality.json")
    print(out[["subject", "time_h", "conc_raw", "robust_z", "flag"]].to_string(index=False))
    print(f"\nflag 统计：{summary['flag_counts']}；MAD(log_resid)={mad:.4f}")


if __name__ == "__main__":
    main()
