# DRAWIO_REPORT — 示意图

| 图 | 文件夹 | 用途 | 模板 / 方式 | 状态 |
| --- | --- | --- | --- | --- |
| fig01 技术路线图 | `figures/fig01_roadmap/` | 论文 §二 问题分析：一页看懂 提出问题 → 数据假设 → 建模求解 → 结果对比 → 评价推广 | `scibox-diagram` 模板 `roadmap-5band`（`content.json` → `roadmap_5band.py` → `.drawio`），`export_figure.py` 导出 PNG/PDF | 草稿；容量检查与 `check_layout.py` 通过（FAIL 0 / WARN 0）；PNG 已肉眼核对；需人工重画，见 `REDRAW_NOTES.md` |

## 元素与已知缺陷

详见 `figures/fig01_roadmap/REDRAW_NOTES.md` §2–§3。要点：
- 为适配模板字数预算，多处文案缩写（“日 1000 / 日 750”“R1 q12h”），重画时恢复全称。
- 带④右侧两条箭头标签与四个方案框不是一一对应，重画时改为分组框。
- 图内数值（ke 0.168、ka 1.15、t1/2 4.1 h、留一 RMSE 0.72、R2 谷 4.3 / 峰 7.8、N = 36 / n = 33、seed = 42、达标率 100%）均抄自 `RESULTS_REPORT.md`；改数值先改 `content.json`。

## 未画的图

- 一室模型结构图（口服 → 吸收室 → 中央室 → 消除）：正文用公式 (1) 已足够，若评审需要可在 draw.io 手绘 3 个盒子 2 个箭头。
