# paper/ — Word 初稿

| 文件 | 角色 |
| --- | --- |
| `main.docx` | **正文唯一真源**。用 Word 打开直接编辑：润色、排版、编号、插图替换都在这里做 |
| `main.pdf` | 生成时的渲染抽检（可能没有，仅供参考） |
| `DOCX_FREEZE.json` | 冻结记录：生成时间、来源章节哈希、`frozen: true` 表示以后**不再**由 Markdown 重生成 |
| `paper.yaml` | 生成时的题目 / 摘要 / 关键词 / 章节顺序（历史记录） |
| `sections/*.md` | 生成 `main.docx` 时用的 Markdown 章节（LaTeX 公式、`@fig:`/`@tbl:`/`@eq:` 交叉引用）。**历史源，不再维护**；想查某段最初怎么写的可以看 |
| `docx_build_report.md` | 生成时的审计报告：段落/公式/图表数量、占位符与内部名称检查 |

规则：
1. 改数字先改代码 → 重跑 → `reports/RESULTS_REPORT.md` → 再改 Word。
2. 图改了之后，把 `figures/<fig_id>/<fig_id>.png` 重新插入 Word（右键图片 → 更改图片）。
3. 不要在本机重新生成 docx 覆盖 `main.docx`；确有需要（例如重来一版）请先把现有 `main.docx` 另存为 `main_v1_手工.docx`。
