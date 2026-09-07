# DATA_REPORT — 数据审计与清洗

> 清洗代码：`code/00_data_prep.py`；数值来源：`results/data_quality.json`、`results/data_quality_flags.csv`；输出：`data/clean/pk_clean.csv`。
> 原始数据由 `code/_make_synthetic_raw.py`（seed=20260906）合成，`data/raw/` 生成后只读。

## 1. 附件与字段

| 文件 | 行数 | 字段 | 说明 |
| --- | --- | --- | --- |
| `data/raw/pk_raw.csv` | 36 | `subject`（S01–S03）、`time_h`（0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 16, 24）、`conc_mg_L` | 单次口服 500 mg 后血药浓度 |
| `data/raw/pk_raw_truth.json` | — | 合成真值 | 仅供演示自检，建模不使用 |

结构检查：3 名受试者时间网格完全一致（`same_time_grid: true`），每人 12 点。

## 2. 质量问题

| 受试者 | 时刻 (h) | 原值 (mg/L) | 标记 | 依据 |
| --- | --- | --- | --- | --- |
| S02 | 6.0 | 空 | `missing` | 空单元 |
| S03 | 24.0 | −0.12 | `negative` | 浓度不可能为负；视为低于检测限或录入错误 |
| S01 | 3.0 | 24.0411 | `outlier` | 留一对数线性插值残差的 MAD 稳健 z = 10.98 ≫ 3.5 |

有效值范围（flag = ok）：0.3529–10.3907 mg/L。

## 3. 清洗方法

1. **不删行**：所有 36 行保留；新增 `flag`、`use_for_fit` 列。`conc_raw` 保留原值，`conc` 在 flag ≠ ok 时置空。
2. **离群判定**（对 C > 0 的点）：对每个受试者，用相邻两个有效点在 (t, ln C) 平面线性插值预测第 i 点，残差 r_i = ln C_i − 预测值；首末两点不参与（外推不可靠，是本方法的已知局限）。所有受试者残差合并，取中位数 0.0469、MAD 0.0440，稳健 z = (r − 中位数)/(1.4826·MAD)，阈值 3.5（Leys et al., 2013）。逐个剔除：每轮只标记 |z| 最大且超阈的一点并重算，最多 5 轮，避免掩蔽效应。
3. **为什么不用跨个体规则**：3 名受试者的个体间变异（ke 差约 30%）会被“与其他人中位数比较”的规则误判为离群；个体内相邻点插值只看曲线的局部光滑性。

## 4. 清洗结果与影响

| 项 | 值 |
| --- | --- |
| flag 计数 | ok 33、outlier 1、missing 1、negative 1 |
| 每人可用点 | S01 11、S02 11、S03 11 |
| 清洗对合并拟合的影响 | 见 `ROBUSTNESS_REPORT.md` §4：不清洗（仅去缺失）时 ke 高估 47%、A 高估 98%、RMSE 变为 3.9 倍 |

## 5. 输出说明

`data/clean/pk_clean.csv` 列：`subject, time_h, conc_raw, conc, log_resid, robust_z, flag, use_for_fit`。下游脚本只用 `use_for_fit == True` 的行（`common.load_clean()`）。

## 6. 待确认

- 负值 −0.12 若来源于检测下限（LLOQ），更合理的处理是按 LLOQ/2 代入；本演示按“剔除不用”处理，对 ke 的影响见 `ROBUSTNESS_REPORT.md`。
- 首末两点不受离群规则约束，若真实数据在 0.25 h 或 24 h 出现离群，需人工检查。
