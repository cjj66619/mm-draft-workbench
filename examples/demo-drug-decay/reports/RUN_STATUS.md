# 最近一次 run_all 结果

- 时间：2026-09-21T08:36:41
- 平台：linux，Python 3.10.12
- 日志：`reports/_logs/run_20260921-083633.log`

| 阶段 | 步骤 | 结果 | 耗时(s) |
| --- | --- | --- | --- |
| code | `00_data_prep.py` | OK | 0.3 |
| code | `10_q1_fit_bateman.py` | OK | 0.7 |
| code | `20_q2_dosing_sim.py` | OK | 0.3 |
| code | `30_sensitivity.py` | OK | 0.8 |
| figures | `fig02_q1_fit` | OK | 1.6 |
| figures | `fig03_q2_regimens` | OK | 1.4 |
| figures | `fig04_sensitivity` | OK | 1.3 |
| figcheck | `check_figures` | OK | 0.4 |
| figcheck | `fig_layout_lint` | OK | 0.4 |
| figcheck | `figure_index` | OK | 0.0 |
| paper | `paper_check` | OK | 0.0 |
| check | `doctor` | OK | 0.7 |
| check | `portability_check` | OK | 0.1 |

FAIL 的步骤看日志末尾的 traceback；WARN 表示可选检查未通过（例如缺少可选工具）。
