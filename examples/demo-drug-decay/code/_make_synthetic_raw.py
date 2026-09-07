"""_make_synthetic_raw.py — 生成演示用合成原始数据 data/raw/pk_raw.csv（仅运行一次；`_` 前缀使 run_all 跳过）。

输入
    无外部输入。全部参数写在本文件顶部。
做什么
    以 Bateman 一室口服模型 C(t) = A·(exp(-ke·t) - exp(-ka·t)) 为"真实机理"，
    为 3 名受试者各生成 12 个采样点的血药浓度，加入个体间变异与测量噪声，
    再人为注入 3 处数据缺陷（1 条缺失、1 个异常高值、1 个负值），供 00_data_prep.py 演示清洗规则。
    真值参数（用于事后核对拟合结果，写在 data/raw/pk_raw_truth.json）：
        剂量 D = 500 mg，生物利用度 F = 1，表观分布容积 V = 40 L，
        ka = 1.2 /h，ke = 0.15 /h（个体参数在群体值基础上乘 lognormal(0, 0.12)）。
    噪声：比例误差 6% + 加性误差 0.08 mg/L（正态）。
输出
    data/raw/pk_raw.csv         ：subject, time_h, conc_mg_L（含缺陷，作为"原始数据"之后只读）
    data/raw/pk_raw_truth.json  ：生成参数与缺陷位置（演示项目专用，真实赛题不存在此文件）
运行时间：< 1 s
随机性：seed = 20260906（numpy default_rng）
注意：data/raw/ 生成后即只读。若确需重新生成，先删除旧文件并在 plan.md 记录原因。
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from common import DATA_RAW

SEED = 20260906
SUBJECTS = ["S01", "S02", "S03"]
TIMES_H = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0]
DOSE_MG, F, V_L = 500.0, 1.0, 40.0
KA, KE = 1.2, 0.15
IIV_SD = 0.12           # 个体间变异（lognormal 的 sigma）
CV_PROP, SD_ADD = 0.06, 0.08


def bateman(t: np.ndarray, dose: float, f: float, v: float, ka: float, ke: float) -> np.ndarray:
    a = dose * f * ka / (v * (ka - ke))
    return a * (np.exp(-ke * t) - np.exp(-ka * t))


def main() -> None:
    rng = np.random.default_rng(SEED)
    t = np.asarray(TIMES_H, dtype=float)
    rows, truth = [], {}
    for sid in SUBJECTS:
        ka_i = KA * float(np.exp(rng.normal(0.0, IIV_SD)))
        ke_i = KE * float(np.exp(rng.normal(0.0, IIV_SD)))
        v_i = V_L * float(np.exp(rng.normal(0.0, IIV_SD)))
        c_true = bateman(t, DOSE_MG, F, v_i, ka_i, ke_i)
        noise = c_true * rng.normal(0.0, CV_PROP, size=t.size) + rng.normal(0.0, SD_ADD, size=t.size)
        c_obs = c_true + noise
        truth[sid] = {"ka": ka_i, "ke": ke_i, "V": v_i, "A": DOSE_MG * F * ka_i / (v_i * (ka_i - ke_i))}
        for ti, ci in zip(t, c_obs):
            rows.append({"subject": sid, "time_h": ti, "conc_mg_L": round(float(ci), 4)})
    df = pd.DataFrame(rows)

    # 人为缺陷：S02 t=6 h 缺失；S01 t=3 h 异常高值（×3）；S03 t=24 h 负值
    defects = {
        "missing": ("S02", 6.0),
        "outlier_high": ("S01", 3.0),
        "negative": ("S03", 24.0),
    }
    idx = lambda s, tt: df.index[(df["subject"] == s) & (df["time_h"] == tt)][0]  # noqa: E731
    df.loc[idx(*defects["missing"]), "conc_mg_L"] = np.nan
    df.loc[idx(*defects["outlier_high"]), "conc_mg_L"] = round(float(df.loc[idx(*defects["outlier_high"]), "conc_mg_L"]) * 3.0, 4)
    df.loc[idx(*defects["negative"]), "conc_mg_L"] = -0.12

    DATA_RAW.mkdir(parents=True, exist_ok=True)
    out = DATA_RAW / "pk_raw.csv"
    if out.exists():
        raise SystemExit(f"{out} 已存在：data/raw/ 只读，如需重生成请先手动删除并在 plan.md 记录。")
    df.to_csv(out, index=False, encoding="utf-8", lineterminator="\n")
    (DATA_RAW / "pk_raw_truth.json").write_text(json.dumps({
        "seed": SEED, "dose_mg": DOSE_MG, "F": F, "V_L_pop": V_L, "ka_pop": KA, "ke_pop": KE,
        "iiv_sd": IIV_SD, "cv_prop": CV_PROP, "sd_add": SD_ADD, "times_h": TIMES_H,
        "subjects": truth, "defects": {k: {"subject": v[0], "time_h": v[1]} for k, v in defects.items()},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"写入 {out}（{len(df)} 行，{df['conc_mg_L'].isna().sum()} 个缺失）")


if __name__ == "__main__":
    main()
