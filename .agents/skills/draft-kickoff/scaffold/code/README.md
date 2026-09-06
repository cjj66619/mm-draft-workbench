# code/ — 数据处理与模型代码

| 前缀 | 用途 | 输入 | 输出 |
| --- | --- | --- | --- |
| `00_*.py` | 数据处理：读 `data/raw/`（只读）→ 清洗 → `data/clean/` | data/raw | data/clean, reports/DATA_REPORT.md 中的统计 |
| `10_*.py` `20_*.py` … | 每个子问题一个脚本：建模、求解、验证 | data/clean | results/q<N>_*.csv/json |
| `3x_*.py` | 稳健性 / 敏感性 / 基线对比 | data/clean, results | results/sens_*.csv |
| `90_*.py` | 汇总：把 results/ 中的关键数值整理为报告用表 | results | results/summary_*.csv |
| `common.py` | 路径 / 种子 / 保存工具（所有脚本 import 它） | — | — |
| `_*.py` | 草稿或被 `run_all.py` 跳过的辅助模块 | — | — |

`python run_all.py code` 按文件名顺序逐个执行（`_` 开头与 `common.py` 除外）。每个脚本必须能独立运行、幂等（重复跑结果一致）。

脚本头部 docstring 模板见 `_template_model.py`：写清 **输入 → 模型（对应报告哪一节、公式编号）→ 输出 → 运行时间量级 → 已知限制**。
画图不在这里做：图的脚本在 `figures/<fig_id>/make_figure.py`，只读 `results/` 与 `data/clean/`。
