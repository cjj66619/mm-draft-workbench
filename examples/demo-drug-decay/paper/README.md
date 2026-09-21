# paper/ — 论文正文

| 文件 | 角色 |
| --- | --- |
| `paper.yaml` | 题目 `title`、关键词 `keywords`、章节顺序 `sections`（为空时按 `sections/` 文件名排序） |
| `sections/00_abstract.md` | 摘要。不写标题；最后一行 `**关键词：**a；b；c` |
| `sections/NN_xxx.md` | 正文，**一章一个文件**，每个文件一个一级标题 `# 一、问题重述`。`_` 开头的文件被忽略 |

正文就是这些 Markdown 文件，没有别的副本。写法约定（`python run_all.py paper` 会检查）：

| 元素 | 写法 | 正文引用 |
| --- | --- | --- |
| 公式 | `$$ ... $$ {#eq:q1_model}`（行内 `$...$`） | `@eq:q1_model` → 式(1) |
| 图 | `![图题](../../figures/fig02_q1_fit/fig02_q1_fit.pdf){#fig:q1_fit}` | `@fig:q1_fit` → 图1 |
| 表 | Markdown 管道表，紧邻的上一行或下一行写 `Table: 表题 {#tbl:q1_params}` | `@tbl:q1_params` → 表1 |

- 图/表/公式**不手写编号**，也不要在 `@fig:x` 前再写“图”（会变成“图 图1”）。
- 图片一律引用 `figures/<fig_id>/<fig_id>.pdf`（重画后路径不变，正文不用改）。
- 所有数字来自 `reports/RESULTS_REPORT.md`；改数字先改代码 → 重跑 → 更新报告 → 再改这里。
- 正文中不得出现 `reports/`、`figures/`、`results/`、`AGENTS.md`、`run_all` 等内部名称，不得有 `[TODO]`、`[待补充]`、未替换的模板变量等占位符。
- 自检：`python run_all.py paper`（或 `python tools/paper_check.py --strict`），结果在 `reports/PAPER_CHECK.md`，FAIL 必须清零。

推荐章节文件：`00_abstract.md`、`01_restatement.md`（问题重述）、`02_analysis.md`（问题分析）、`03_assumptions.md`（模型假设）、
`04_symbols.md`（符号说明）、`05_problem1.md` … `0N_problemN.md`（各问建模与求解）、`08_sensitivity.md`（灵敏度/稳健性）、
`09_evaluation.md`（模型评价与推广）、`10_references.md`（参考文献）。
