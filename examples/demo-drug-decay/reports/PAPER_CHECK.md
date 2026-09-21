# 论文章节自检（自动生成，勿手改）

- 时间：2026-09-21T08:36:41
- 章节：10 个文件：00_abstract.md、01_restatement.md、02_analysis.md、03_assumptions.md、04_symbols.md、05_problem1.md、06_problem2.md、08_sensitivity.md、09_evaluation.md、10_references.md
- 结论：**PASS**（FAIL 0，WARN 0，INFO 4）

## 发现

| 级别 | 类别 | 位置 | 说明 |
| --- | --- | --- | --- |
| INFO | `xref_unused` | `05_problem1.md:13` | #eq:mad 已定义但正文没有 @eq:mad 引用 |
| INFO | `xref_unused` | `05_problem1.md:25` | #eq:nls 已定义但正文没有 @eq:nls 引用 |
| INFO | `xref_unused` | `05_problem1.md:29` | #eq:derived 已定义但正文没有 @eq:derived 引用 |
| INFO | `xref_unused` | `05_problem1.md:33` | #eq:delta 已定义但正文没有 @eq:delta 引用 |

## 图 / 表 / 公式编号（按正文出现顺序）

| 标签 | 编号 |
| --- | --- |
| `#fig:roadmap` | 图1 |
| `#tbl:symbols` | 表1 |
| `#eq:mad` | 式(1) |
| `#eq:bateman` | 式(2) |
| `#eq:nls` | 式(3) |
| `#eq:derived` | 式(4) |
| `#eq:delta` | 式(5) |
| `#tbl:q1_params` | 表2 |
| `#tbl:q1_derived` | 表3 |
| `#tbl:q1_metrics` | 表4 |
| `#fig:q1_fit` | 图2 |
| `#eq:superpose` | 式(6) |
| `#eq:steady` | 式(7) |
| `#eq:window` | 式(8) |
| `#tbl:q2_regimens` | 表5 |
| `#fig:q2_regimens` | 图3 |
| `#tbl:q3_local` | 表6 |
| `#tbl:q3_mc` | 表7 |
| `#fig:sensitivity` | 图4 |
| `#tbl:q3_indiv` | 表8 |
| `#tbl:q3_clean` | 表9 |

重新生成：`python tools/paper_check.py`
