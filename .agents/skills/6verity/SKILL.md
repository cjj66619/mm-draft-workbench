---
name: 6verity
description: "数学建模论文项目最终验证和验收阶段。用于 paper/sections/*.md 写完后检查章节完整性与顺序、一级标题、图/表/公式交叉引用、图片文件、占位符、内部文件名泄露、摘要与关键词、数值与 RESULTS_REPORT.md 一致性、参考文献、代码可复现性与提交就绪状态，输出 reports/VERIFY_REPORT.md。"
---

# 验证和验收（Markdown 论文项目）

本 skill 是整个流程的最后一关。它不重新建模、不生成新结果、不代替写作阶段重写论文；它负责发现硬错误、修复可直接修复的问题，并输出 `reports/VERIFY_REPORT.md`。

验收对象是一个 draft 项目文件夹：论文正文 = `paper/sections/*.md`（一章一文件）+ `paper/paper.yaml`；数值真源 = `reports/RESULTS_REPORT.md`；图 = `figures/<fig_id>/`。验收标准是**可以直接提交**：任何“以后再改”的想法都不成立，问题要么当场修，要么判 FAIL 退回前序阶段。

## 数学建模规范参考

如需领域判断，读取 `../_references/math_modeling_norms.md` 中的"论文验收与一致性"小节。华为杯（`plan.md` §1 竞赛类型为华为杯）额外读取 `../_references/huaweibei_excellent_paper_patterns.md` §1 与 §6，执行下文 Step 6b。

## 阶段边界

- 本阶段负责：结构验收、文本质量门禁、图表引用检查、结果一致性检查、代码可复现检查、提交清单。
- 本阶段不负责：重新设计模型、重新跑大规模实验、重新组织整篇论文、任何排版输出。
- 发现硬错误时，优先做小范围修复；如果需要回到前序阶段，写入 `reports/VERIFY_REPORT.md` 并标记为未通过。

## 输入

1. `paper/paper.yaml`（title / keywords / sections）与 `paper/sections/*.md`。
2. `reports/ANALYSIS_MODELING_REPORT.md`、`reports/RESULTS_REPORT.md`、`reports/ROBUSTNESS_REPORT.md`、`reports/DATA_REPORT.md`（存在则读）。
3. `figures/<fig_id>/`（PDF/PNG、README、review.json）与 `figures/FIGURE_REVIEW.md`。
4. `code/`、`results/`、`run_all.py`、`doctor.py`。

## 工作流程

### Step 1: 运行章节自检脚本

在项目目录：

```bash
python tools/paper_check.py --require --strict
```

（等价：`python run_all.py paper --strict`，结果在 `reports/PAPER_CHECK.md`。）脚本检查：`paper.yaml` 有效且题目非占位符、`sections` 列出的文件都存在、`00_abstract.md` 存在且有 `**关键词：**` 行、每章一个一级标题、占位符（`[TODO]`、`{{...}}`、`待补充` 等）、内部名泄露（`reports/`、`figures/`、`AGENTS.md`、`run_all` 等）、`@fig:/@tbl:/@eq:` 未定义或标签重复、图片文件不存在、图无 `{#fig:}` 标签、表无 `Table:` 题、`@fig:` 前多写“图”等。

FAIL 是硬错误，必须修复后重跑到 0；WARN 逐条看，能修就修，确认为误报的在报告里说明原因。

### Step 2: 章节完整性和顺序

- `paper.yaml` 的 `sections` 顺序是否符合数模论文结构：摘要 → 问题重述 → 问题分析 → 模型假设 → 符号说明 → 各问建模与求解 → 灵敏度/稳健性 → 模型评价 → 参考文献（附录可选）。
- 子问题章节数量与 `ANALYSIS_MODELING_REPORT.md` 的子问题数一致；不是三问就不要强凑三章。
- 每问内部是否具备“问题分析 / 模型建立 / 求解 / 结果分析与验证 / 小结”。缺“结果分析与验证”或“小结”判 FAIL。
- 一级标题编号连续（一、二、三…），与文件名前缀顺序一致。

### Step 3: 图表与章节匹配

- `figures/<fig_id>/` 下每张图是否在正文被引用（`paper_check.py` 报 unused 的要么补引用、要么在报告里说明为备用）。
- 数据图放在对应结果/分析章节，技术路线图放在问题分析章节，模型结构图放在模型建立小节。
- 图题/表题能独立读懂（不是“结果图”“参数表”这种）；图后有解读段落（说明看到什么、意味着什么），表后有说明。
- 连续两个图/表之间至少有一段解释文字。
- 图片文件引用 `../../figures/<fig_id>/<fig_id>.pdf`；`figures/FIGURE_REVIEW.md` 中 FAIL 为 0，示意图（drawio）在 `HANDOFF.md` 标明“草稿，需人工重画”。

### Step 4: 写作质量

检查并修复：

- 列表式写作过多（整节都是 `-` 列表而无成段论述）。
- 段落反复以“如图”“由图”“图 X 展示了”开头。
- 公式后没有变量含义、符号未出现在符号说明表中。
- 结论只报数不解释（每个关键数字后要有“说明了什么”）。
- 模型评价写成套话（“模型简单易懂”）；应写本文具体做法的优缺点与改进方向。
- 摘要：每问一段，写模型、方法、关键数值结论；关键词 4–6 个；不出现图/表/公式引用。

### Step 5: 数值和结果一致性

逐个对照 `paper/sections/*.md` 中的数字与 `reports/RESULTS_REPORT.md`（及其指向的 `results/*.csv|json`）：

- 参数估计值、误差指标、目标函数值、排名、权重、阈值、灵敏度结论必须一致（保留位数可不同，数值不能冲突）。
- 摘要中的数字与正文对应章节一致。
- `RESULTS_REPORT.md` 中的核心结果在正文都有落点。
- 正文中出现、但 `RESULTS_REPORT.md` 找不到来源的数字，一律判 FAIL（除常识常数与题面给定值）。

发现冲突时不要自行发明新结果：回到 `results/` 或重跑 `python run_all.py code`，先改报告再改正文。若有条件，用 `consistency-auditor` 做系统对照。

### Step 6: 参考文献与规范

- `10_references.md`（或 `paper.yaml` 中列出的参考文献章节）存在，条目真实可查（作者、题名、来源、年份齐全）；正文中提到的方法/数据来源在文献中有对应条目。
- 中文论文的图题、表题、摘要保持中文；术语首次出现给出全称。
- 不出现队号、学校、姓名等身份信息（题目要求匿名时）。

### Step 6b: 华为杯官方要求与国一对标（仅华为杯）

按 `huaweibei_excellent_paper_patterns.md` §6 的清单逐项检查，等级以该表为准。其中必须人工确认的硬项：

- **AI 工具使用声明**：参考文献中存在 `工具名称, 版本/型号, 开发机构, 使用日期` 格式的条目；AI 生成的段落/代码在对应位置有标注。缺失判 FAIL。
- **摘要**：每个子问题在摘要中有对应段落（“针对问题 N”）。缺小问判 FAIL；段内无任何数值或明确定性结论判 WARN。
- **验证证据**：对 `ANALYSIS_MODELING_REPORT.md` 列出的每个主模型，在论文中定位至少一处误差/基线对比/扰动或灵敏度/约束满足性的证据。缺失判 FAIL。

其余（小结、单位列、关键词数、模型评价具体性、附录文件清单、重述照抄）为 WARN。结果写入 `reports/VERIFY_REPORT.md` 的“华为杯对标”小节，逐项列出位置（文件 + 标题）。

### Step 7: 代码可复现

```bash
python doctor.py
python run_all.py --strict            # code → figures → figcheck → paper → check
python tools/figure_index.py --check
python tools/portability_check.py .
```

`reports/RUN_STATUS.md` FAIL 必须为 0；`portability_check` FAIL 为 0。若完整复现耗时过长，至少跑 `python run_all.py figures figcheck paper check` 并在报告注明。

### Step 8: 写验收报告

创建 `reports/VERIFY_REPORT.md`：

```markdown
# 验证和验收报告

## 结论
PASS / FAIL

## 检查项
| 检查项 | 结果 | 说明 |
| --- | --- | --- |

## 章节结构

## 图表引用

## 数值一致性（逐数对照表）

## 文本质量门禁（paper_check FAIL/WARN 与处置）

## 代码可复现

## 华为杯对标（仅华为杯）

## 仍需处理的问题
```

只有当硬错误都修复、`paper_check.py --require --strict` 通过（或 WARN 均已说明）、核心图表都引用、数值一致、`run_all.py --strict` 全绿时，才写 PASS。同时更新 `HANDOFF.md` 的阶段状态表与 `todo.md`。

## 硬错误标准

以下问题必须判定 FAIL：

- `paper/paper.yaml` 缺失/无效，或 `sections` 列出的章节文件不存在。
- 缺摘要、缺任何一问的建模与求解章节、缺参考文献。
- 正文章节缺少一级标题，或标题顺序错误/重复。
- 正文仍有占位符或模板变量。
- 正文泄露内部文件名（`reports/`、`figures/`（图片路径除外）、`results/`、`AGENTS.md`、`run_all` 等）。
- `@fig:/@tbl:/@eq:` 引用未定义、标签重复、引用的图片文件不存在。
- 关键数值与 `RESULTS_REPORT.md` 冲突，或来源不明。
- 某问缺少任何验证证据（误差/基线/灵敏度/约束满足性）。
- `python run_all.py --strict` 有 FAIL。
- 华为杯：缺 AI 工具使用声明、摘要缺小问、主模型无任何验证证据、匿名要求下出现身份信息。

## 警告标准

以下问题可判定为 WARN，但应尽量修复：

- 未引用的备用图片、未被引用的公式标签。
- 某章节过短或明显不均衡。
- 图题/表题偏长或偏泛，图表后解释文字不足。
- 参考文献偏少（< 8 条）。
- 摘要偏短或缺数值结论。
- 代码完整复现耗时过长，只做了轻量检查。
- 华为杯对标清单中标为 WARN 的项。
