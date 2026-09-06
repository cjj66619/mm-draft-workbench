# data/

- `raw/`：**只读**。比赛附件原样存放，文件名不改，任何人不要编辑。数据说明见 `../problem/attachments.md`。
- `clean/`：由 `code/00_*.py` 生成的清洗结果（UTF-8 CSV / parquet）。删掉整个目录后 `python run_all.py code` 应能完整重建。

每一步清洗（去重、缺失处理、单位换算、异常剔除、口径统一）在 `reports/DATA_REPORT.md` 记录：做了什么、影响多少行、为什么。
