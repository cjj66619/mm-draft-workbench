#!/usr/bin/env python3
"""figure_index.py — 汇总 figures/<fig_id>/ 的生成记录与审图状态，生成
figures/README.md（总索引）和 figures/FIGURE_REVIEW.md（审图清单，供后续做绘图优化的人/智能体使用）。

识别两类图文件夹：
- 数据图：含 make_figure.py + manifest.json（mm_plot_style.save_fig 产出）
- 示意图：含 *.drawio（技术路线图、流程图、模型结构图），必须附 REDRAW_NOTES.md——
  机器生成的示意图只是"看起来对"的草稿，交稿前需要人工重画

用法（项目根目录）::

    python tools/figure_index.py            # 写 figures/README.md 与 figures/FIGURE_REVIEW.md
    python tools/figure_index.py --check    # 只检查：缺 README/REDRAW_NOTES/manifest 时非零退出
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REVIEW_CHECKLIST = [
    "文字与线/柱/图例无重叠（review.json 的 text_overlap / legend_over_data / pdf_line_through_text 已清零或注明可接受）",
    "无越界/裁切；面板大小一致；(a)(b) 标签位置一致",
    "字号：5 pt ≤ 全部文字 ≤ 1.6×基准；同类图字号一致",
    "配色只用 COLORS/PALETTES；同一变量在全文各图颜色一致；无彩虹色",
    "坐标轴有标签与单位；图例不遮挡；中文与论文语言一致",
    "图意与论文正文/图题一致；数值与 reports/RESULTS_REPORT.md 一致",
    "示意图（drawio）已按 REDRAW_NOTES.md 人工重画或确认可用",
]


def _load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _first_line(md: str) -> str:
    for line in md.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith(">"):
            return line[:80]
    return ""


def scan(figures: Path) -> list[dict]:
    rows: list[dict] = []
    for d in sorted(p for p in figures.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        drawio = sorted(d.glob("*.drawio"))
        manifest = _load_json(d / "manifest.json")
        review = _load_json(d / "review.json")
        kind = "diagram" if drawio else ("data" if manifest or (d / "make_figure.py").exists() else "other")
        readme = (d / "README.md").read_text(encoding="utf-8") if (d / "README.md").exists() else ""
        notes = (d / "REDRAW_NOTES.md").read_text(encoding="utf-8") if (d / "REDRAW_NOTES.md").exists() else ""
        purpose = ""
        if kind == "data" and "## 图的作用与机理" in readme:
            body = readme.split("## 图的作用与机理", 1)[1].split("\n", 1)[-1]
            purpose = _first_line(body.split("\n## ", 1)[0])
        elif kind == "diagram":
            purpose = _first_line(notes) or _first_line(readme)
        else:
            purpose = _first_line(readme)
        auto = review.get("auto", {}).get("findings", []) + review.get("auto_pdf", {}).get("findings", [])
        n_fail = sum(f["level"] == "FAIL" for f in auto)
        n_warn = sum(f["level"] == "WARN" for f in auto)
        human = review.get("human", {})
        outputs = sorted(x.name for x in d.iterdir() if x.suffix.lower() in (".pdf", ".png", ".svg"))
        missing = []
        if kind == "data":
            if not (d / "make_figure.py").exists():
                missing.append("make_figure.py")
            if not manifest:
                missing.append("manifest.json")
            if not readme:
                missing.append("README.md")
            if not any(x.endswith(".pdf") for x in outputs):
                missing.append(f"{d.name}.pdf")
            if not manifest.get("data") and not manifest.get("source"):
                missing.append("数据快照/source 记录")
        elif kind == "diagram":
            if not notes:
                missing.append("REDRAW_NOTES.md")
            if not any(x.endswith((".pdf", ".png")) for x in outputs):
                missing.append("导出的 PDF/PNG")
        rows.append({
            "id": d.name, "kind": kind, "purpose": purpose, "outputs": outputs,
            "n_fail": n_fail, "n_warn": n_warn, "auto": auto,
            "human_status": human.get("status", "pending" if kind == "data" else "redraw-required"),
            "human_notes": human.get("notes", []), "human_verdict": human.get("verdict"),
            "missing": missing, "drawio": [x.name for x in drawio],
            "script": manifest.get("script"), "data": manifest.get("data", []),
        })
    return rows


def write_index(figures: Path, rows: list[dict]) -> None:
    lines = ["# 图表索引", "",
             "> 由 `tools/figure_index.py` 自动生成。每张图一个文件夹：图 + 绘图代码/源文件 + 数据快照 + README/REDRAW_NOTES + review.json。",
             "> 数据图由 `make_figure.py` 重生成；示意图（drawio）为机器草稿，**必须人工重画后**才可用于终稿。", "",
             "| 图 | 类型 | 用途 | 自检 | 人工审图 | 输出 |", "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        auto = "FAIL " + str(r["n_fail"]) if r["n_fail"] else (f"WARN {r['n_warn']}" if r["n_warn"] else "OK")
        if r["kind"] == "diagram":
            auto = "机器草稿"
        lines.append(f"| [`{r['id']}`]({r['id']}/) | {r['kind']} | {r['purpose']} | {auto} | {r['human_status']} | {', '.join(r['outputs'])} |")
    lines += ["", "## 重新生成全部数据图", "", "```", "python run_all.py figures", "```", "",
              "## 单张图", "", "```", "python figures/<fig_id>/make_figure.py", "```", ""]
    (figures / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_review(figures: Path, rows: list[dict]) -> None:
    lines = ["# 审图清单（FIGURE_REVIEW）", "",
             "> 由 `tools/figure_index.py` 汇总各图 `review.json`。做绘图优化时：逐图核对下列清单 → 修改 `make_figure.py`/`.drawio` 并重跑 → "
             "在 `review.json` 的 `human` 字段记录 reviewer/date/verdict/notes → 重新运行本脚本。", "",
             "## 通用核对项", ""]
    lines += [f"- [ ] {item}" for item in REVIEW_CHECKLIST]
    lines += ["", "## 逐图状态", ""]
    for r in rows:
        lines.append(f"### {r['id']}（{r['kind']}）")
        lines.append("")
        if r["purpose"]:
            lines.append(f"- 用途：{r['purpose']}")
        if r["script"]:
            lines.append(f"- 脚本：`{r['script']}`")
        for d in r["data"]:
            lines.append(f"- 数据：`{d.get('snapshot')}` ← `{d.get('source')}`")
        for name in r["drawio"]:
            lines.append(f"- 源文件：`{name}`（draw.io 桌面版/网页版可编辑；导出后替换同名 PDF/PNG）")
        if r["missing"]:
            lines.append(f"- **缺失**：{', '.join(r['missing'])}")
        lines.append(f"- 人工审图：{r['human_status']}" + (f"，结论：{r['human_verdict']}" if r["human_verdict"] else ""))
        for n in r["human_notes"]:
            lines.append(f"  - {n}")
        if r["auto"]:
            lines.append("- 自动检查：")
            for f in r["auto"]:
                lines.append(f"  - {f['level']} `{f['code']}`: {f['message']}")
        elif r["kind"] == "data":
            lines.append("- 自动检查：无发现")
        if r["kind"] == "diagram":
            lines.append(f"- 重画说明：见 `{r['id']}/REDRAW_NOTES.md`")
        lines.append("")
    (figures / "FIGURE_REVIEW.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--figures", default="figures", help="图目录，默认 figures/")
    ap.add_argument("--check", action="store_true", help="只检查完整性，不写文件")
    args = ap.parse_args(argv)
    figures = Path(args.figures)
    if not figures.is_dir():
        print(f"[figure_index] 目录不存在: {figures}", file=sys.stderr)
        return 2
    rows = scan(figures)
    problems = [(r["id"], r["missing"]) for r in rows if r["missing"]]
    fails = [r["id"] for r in rows if r["n_fail"]]
    if not args.check:
        write_index(figures, rows)
        write_review(figures, rows)
        print(f"[figure_index] {len(rows)} 个图文件夹 → {figures / 'README.md'}, {figures / 'FIGURE_REVIEW.md'}")
    for fid, miss in problems:
        print(f"[figure_index] 缺失 {fid}: {', '.join(miss)}", file=sys.stderr)
    for fid in fails:
        print(f"[figure_index] {fid} 自检存在 FAIL", file=sys.stderr)
    return 1 if (problems or fails) else 0


if __name__ == "__main__":
    sys.exit(main())
