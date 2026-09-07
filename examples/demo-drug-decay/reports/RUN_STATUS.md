# 最近一次 run_all 结果

- 时间：2026-09-07T04:22:44
- 平台：linux，Python 3.10.12
- 日志：`reports/_logs/run_20260907-042230.log`

| 阶段 | 步骤 | 结果 | 耗时(s) |
| --- | --- | --- | --- |
| code | `00_data_prep.py` | OK | 0.5 |
| code | `10_q1_fit_bateman.py` | OK | 1.1 |
| code | `20_q2_dosing_sim.py` | OK | 0.5 |
| code | `30_sensitivity.py` | OK | 1.4 |
| figures | `fig02_q1_fit` | OK | 2.9 |
| figures | `fig03_q2_regimens` | OK | 2.5 |
| figures | `fig04_sensitivity` | OK | 2.4 |
| figcheck | `check_figures` | OK | 0.7 |
| figcheck | `fig_layout_lint` | OK | 0.7 |
| figcheck | `figure_index` | OK | 0.0 |
| check | `doctor` | OK | 1.1 |
| check | `portability_check` | OK | 0.2 |

FAIL 的步骤看日志末尾的 traceback；WARN 表示可选检查未通过（例如缺少可选工具）。
