# results/ — 模型输出（数值的唯一来源）

- 由 `code/1x_*.py`、`2x_*.py`… 写入：`q1_fit_params.csv`、`q2_schedule.json`、`sensitivity_grid.csv` 等。
- 命名：`q<问题号>_<内容>.<csv|json>`；跨问汇总用 `summary_*.csv`。
- CSV 用 UTF-8、逗号分隔、表头英文或拼音（避免 Excel 直接打开乱码的问题：用"数据→从文本导入"选 UTF-8）。
- 论文里出现的每个数字都要能在这里找到出处，并汇总进 `reports/RESULTS_REPORT.md`（写清来自哪个文件、哪一行/哪个键）。
- 不要手改这里的文件；要改就改代码重跑。
