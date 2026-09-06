---
name: docx-build
description: "把初稿项目的 paper/sections/*.md（Markdown + LaTeX 公式）一次性合成 Word 初稿 paper/main.docx（公式为 Word 原生 OMML，PDF 图自动转 PNG，图表公式自动编号，A4 中文论文格式，占位符/内部名称审计），并冻结为唯一真源。只在 Devin 侧运行；输出项目在 Windows 上直接用 Word 编辑，不重生成。"
---

# docx-build

脚本：`scripts/build_docx.py`（pandoc + python-docx）。在**项目目录**运行：

```bash
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --pdf --strict   # 生成 paper/main.docx + PDF 抽检 + 审计
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --freeze         # 冻结（写 paper/DOCX_FREEZE.json frozen=true）
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --status         # 查看状态：unfrozen / frozen / frozen-edited
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --force          # 冻结后强制重生成（自动备份 main.docx.bak-<时间>）
python3 ../../.agents/skills/docx-build/scripts/build_docx.py --unfreeze
```

输入约定见 `../draft-kickoff/SKILL.md` 的 draft-writing 节（章节命名、`@fig:`/`@tbl:`/`@eq:` 引用、`paper/paper.yaml`）。

流程：`--pdf --strict` 无 error → 目检 PDF（标题/摘要/目录/公式/图/表/参考文献）→ `--freeze` → 在 `HANDOFF.md` 记录"Word 已冻结"。
冻结后任何数值修改都走：改代码 → 重跑 → `RESULTS_REPORT.md` → 手改 Word。

依赖只在 Devin：pandoc、python-docx、pymupdf（或 pdftoppm）、LibreOffice（`--pdf`）。它们**不进输出项目**，输出项目的 `doctor.py` 也不检查它们。
有当届官方 Word 模板时 `--reference 官方模板.docx` 套用其页面设置。
