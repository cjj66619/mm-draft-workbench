#!/usr/bin/env python3
"""paper_check.py — 论文 Markdown 章节（paper/sections/*.md）自检。纯 Python，Windows / Linux / macOS 通用。

    python tools/paper_check.py                 # 检查 paper/，写 reports/PAPER_CHECK.md；有 FAIL 退出码 1
    python tools/paper_check.py --strict        # WARN 也非零退出
    python tools/paper_check.py --require       # paper/sections/ 为空也算 FAIL（默认视为"尚未写作"，退出 0）
    python tools/paper_check.py --json          # 机器可读
    python tools/paper_check.py --paper paper   # 指定 paper/ 目录（默认项目根下 paper/）

检查项（FAIL = 提交前必须修；WARN = 请人工确认）：
- FAIL meta            : paper.yaml 缺失 / title 为空或仍是占位符 / sections 列出的文件不存在
- FAIL abstract        : 缺 00_abstract.md；摘要没有关键词（`**关键词：**a；b；c` 行或 paper.yaml keywords）
- FAIL heading         : 正文章节没有一级标题 `# 一、xxx`
- FAIL placeholder     : 模板占位符（[论文标题]、[TODO]、{{TITLE}}、待补充…）
- FAIL leak            : 正文出现内部文件名（reports/、figures/、AGENTS.md、make_figure.py…）
- FAIL xref_undefined  : 引用了未定义的 @fig:/@tbl:/@eq: 标签
- FAIL xref_duplicate  : 同一标签定义了两次
- FAIL image_missing   : 图片路径不存在（相对 paper/sections/）
- WARN xref_unused     : 定义了标签但正文从未引用
- WARN figure_untagged : 图片没有 {#fig:xxx} 标签 / 图题为空
- WARN table_uncaptioned: 管道表上方没有 `Table: 表题 {#tbl:xxx}`
- WARN double_prefix   : "图 @fig:x" / "表 @tbl:x" / "式 @eq:x"（@ref 自带"图N/表N/式(N)"，会变成"图 图1"）
- WARN abstract_heading: 摘要文件带标题（摘要不写标题）
- WARN references      : 没有"参考文献"章节 / 参考文献条目为空
- WARN yaml_order      : paper.yaml sections 非空但有章节文件未列入（会按文件名追加到末尾）
- INFO numbering       : 按出现顺序解析出的图/表/式编号表（写在 reports/PAPER_CHECK.md 里便于核对）

章节约定：`paper/sections/NN_xxx.md`，`_` 开头的文件忽略；00_abstract.md 是摘要（无标题）；顺序由 paper.yaml
的 sections 决定，为空时按文件名排序。图 `![图题](../../figures/<id>/<id>.pdf){#fig:xxx}`，
表 `Table: 表题 {#tbl:xxx}` 紧贴管道表的上一行或下一行，公式 `$$ ... $$ {#eq:xxx}`，正文引用 `@fig:xxx`。
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ABSTRACT_NAMES = ("00_abstract.md", "abstract.md", "摘要.md")
REPORT_NAME = "PAPER_CHECK.md"

PLACEHOLDER = re.compile(
    r"\{\{[A-Z_]+\}\}|\[(论文标题|学校名称|参赛队号|成员 ?[A-C]|关键词\d?|中文摘要内容[^\]]*|封面[^\]]*|TODO[^\]]*|"
    r"待补[^\]]*|待填[^\]]*|PLACEHOLDER[^\]]*)\]|(?<![\w/])(TODO|TBD|待补充|待续写|待填写|示例数据)(?![\w/])"
)
INTERNAL_NAMES = ("reports/", "figures/", "results/", "data/raw", "data/clean", "code/", "tools/", "paper/sections",
                  "RESULTS_REPORT", "ANALYSIS_MODELING_REPORT", "DATA_REPORT", "ROBUSTNESS_REPORT",
                  "CLAUDE.md", "AGENTS.md", "HANDOFF.md", "plan.md", "todo.md", "run_all", "doctor.py",
                  "make_figure.py", "review.json", "manifest.json", "REDRAW_NOTES")
# 图片路径本身会含 figures/，检查泄露前先把图片语法整体抹掉
IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+\"[^\"]*\")?\)(?P<attr>\s*\{[^}]*\})?")
FIG_DEF = re.compile(r"!\[[^\]]*\]\([^)]*\)\s*\{[^}]*#(fig:[\w:.-]+)[^}]*\}")
TBL_DEF = re.compile(r"^(?:Table|表)\s*[:：]\s*(?P<cap>[^\n]*?)\{[^}]*#(?P<lab>tbl:[\w:.-]+)[^}]*\}\s*$", re.M)
TBL_CAPTION_LINE = re.compile(r"^(?:Table|表)\s*[:：]", re.M)
EQ_DEF = re.compile(r"\$\$(?:[^$]|\$(?!\$))*\$\$\s*(\{[^}]*#(eq:[\w:.-]+)[^}]*\})?")
REF = re.compile(r"(?<![\w@])@((?:fig|tbl|eq):[\w:.-]*[\w])")
DOUBLE_PREFIX = re.compile(r"(图|表|式)\s*[（(]?\s*@(fig|tbl|eq):")
H1 = re.compile(r"^#\s+\S", re.M)
ANY_HEADING = re.compile(r"^#{1,6}\s+\S", re.M)
KEYWORDS = re.compile(r"^\**关键词\**[：:]\**\s*(.+)$", re.M)
FENCE = re.compile(r"```.*?```", re.S)
PIPE_ROW = re.compile(r"^\s*\|.*\|\s*$")
PIPE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


@dataclass
class Finding:
    level: str      # FAIL / WARN / INFO
    code: str
    where: str      # 文件名[:行]
    msg: str


def load_meta(paper: Path) -> dict:
    """paper/paper.yaml：title / keywords / sections。没有 PyYAML 时用最小解析（键: 值、- 列表、[a, b] 行内列表）。"""
    f = paper / "paper.yaml"
    if not f.exists():
        return {}
    text = f.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text) or {}
        return data if isinstance(data, dict) else {}
    except ImportError:
        pass
    data: dict = {}
    key = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")) and key:
            item = line.strip().lstrip("-").strip().strip("\"'")
            data.setdefault(key, [])
            if isinstance(data[key], list):
                data[key].append(item)
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key, val = key.strip(), val.split(" #", 1)[0].strip()
            if val.startswith("[") and val.endswith("]"):
                data[key] = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
            else:
                data[key] = val.strip("\"'") if val else []
    return data


def collect_sections(sec_dir: Path, meta: dict, out: list[Finding]) -> tuple[Path | None, list[Path]]:
    order = meta.get("sections")
    all_md = sorted(p for p in sec_dir.glob("*.md") if not p.name.startswith("_"))
    if isinstance(order, list) and order:
        files: list[Path] = []
        for name in order:
            p = sec_dir / str(name)
            if not p.suffix:
                p = p.with_suffix(".md")
            if p.exists():
                files.append(p)
            else:
                out.append(Finding("FAIL", "meta", "paper.yaml", f"sections 列出的 {name} 不存在"))
        extra = [p for p in all_md if p not in files]
        for p in extra:
            out.append(Finding("WARN", "yaml_order", p.name, "未列在 paper.yaml sections 中，将按文件名追加到末尾"))
        files += extra
    else:
        files = all_md
    abstract = next((p for p in files if p.name in ABSTRACT_NAMES), None)
    return abstract, [p for p in files if p is not abstract]


def strip_code(text: str) -> str:
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def check_meta(paper: Path, meta: dict, out: list[Finding]) -> None:
    if not (paper / "paper.yaml").exists():
        out.append(Finding("FAIL", "meta", "paper.yaml", "缺失：需要 title / keywords / sections"))
        return
    title = str(meta.get("title") or "").strip()
    if not title:
        out.append(Finding("FAIL", "meta", "paper.yaml", "title 为空"))
    elif PLACEHOLDER.search(title) or title.startswith("（待"):
        out.append(Finding("FAIL", "meta", "paper.yaml", f"title 仍是占位符：{title}"))


def check_abstract(abstract: Path | None, meta: dict, out: list[Finding]) -> None:
    if abstract is None:
        out.append(Finding("FAIL", "abstract", "paper/sections", "缺 00_abstract.md（摘要，无标题，最后一行 **关键词：**a；b；c）"))
        return
    text = abstract.read_text(encoding="utf-8")
    body = strip_code(text)
    if ANY_HEADING.search(body):
        out.append(Finding("WARN", "abstract_heading", abstract.name, "摘要不写标题（题目与\"摘要\"二字由排版决定）"))
    kws = meta.get("keywords") or []
    if isinstance(kws, str):
        kws = [k for k in re.split(r"[;；,，]", kws) if k.strip()]
    m = KEYWORDS.search(body)
    if not m and not kws:
        out.append(Finding("FAIL", "abstract", abstract.name, "没有关键词：在摘要末尾写 `**关键词：**a；b；c`，或在 paper.yaml 填 keywords"))
    n_chars = len(re.sub(r"\s", "", body))
    if n_chars < 200:
        out.append(Finding("WARN", "abstract", abstract.name, f"摘要过短（{n_chars} 字符），一般 800–1800 字符"))
    if not REF.search(body) and not re.search(r"\d", body):
        out.append(Finding("WARN", "abstract", abstract.name, "摘要中没有任何数值结果"))


def check_section_text(p: Path, text: str, is_body: bool, out: list[Finding]) -> None:
    body = strip_code(text)
    if is_body and not H1.search(body):
        out.append(Finding("FAIL", "heading", p.name, "没有一级标题（# 一、xxx）"))
    for m in PLACEHOLDER.finditer(body):
        out.append(Finding("FAIL", "placeholder", f"{p.name}:{line_no(body, m.start())}", f"占位符 {m.group(0)}"))
    no_img = IMAGE.sub(" ", body)
    for name in INTERNAL_NAMES:
        for m in re.finditer(re.escape(name), no_img):
            out.append(Finding("FAIL", "leak", f"{p.name}:{line_no(no_img, m.start())}", f"正文出现内部文件名 {name}"))
    for m in DOUBLE_PREFIX.finditer(body):
        out.append(Finding("WARN", "double_prefix", f"{p.name}:{line_no(body, m.start())}",
                           f"“{m.group(0)}…”：@{m.group(2)}: 会解析成“图N/表N/式(N)”，前面不要再写“{m.group(1)}”"))
    for m in IMAGE.finditer(body):
        ln = line_no(body, m.start())
        attr = m.group("attr") or ""
        if "#fig:" not in attr:
            out.append(Finding("WARN", "figure_untagged", f"{p.name}:{ln}", f"图片缺 {{#fig:xxx}} 标签：{m.group('src')}"))
        if not m.group("alt").strip():
            out.append(Finding("WARN", "figure_untagged", f"{p.name}:{ln}", f"图题为空：{m.group('src')}"))
        src = m.group("src")
        if not re.match(r"^[a-z]+://", src):
            target = (p.parent / src).resolve()
            if not target.exists():
                out.append(Finding("FAIL", "image_missing", f"{p.name}:{ln}", f"图片不存在：{src}"))
    # 管道表：紧邻的上一行或下一行应有 Table: 题注
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if PIPE_ROW.match(lines[i]) and i + 1 < len(lines) and PIPE_SEP.match(lines[i + 1]):
            j = i
            while j < len(lines) and PIPE_ROW.match(lines[j]):
                j += 1
            above = lines[i - 1] if i >= 1 else ""
            above2 = lines[i - 2] if i >= 2 and not above.strip() else ""
            below = lines[j] if j < len(lines) else ""
            below2 = lines[j + 1] if j + 1 < len(lines) and not below.strip() else ""
            if not any(TBL_CAPTION_LINE.match(x) for x in (above, above2, below, below2)):
                out.append(Finding("WARN", "table_uncaptioned", f"{p.name}:{i + 1}", "管道表缺 `Table: 表题 {#tbl:xxx}` 题注行"))
            i = j
        else:
            i += 1


def check_crossrefs(sections: list[Path], out: list[Finding]) -> dict[str, str]:
    """按出现顺序给 fig/tbl/eq 编号；检查重复定义、未定义引用、未引用定义。返回 {标签: 图N/表N/式(N)}。"""
    numbers: dict[str, str] = {}
    defined_at: dict[str, str] = {}
    fig_n = tbl_n = eq_n = 0
    texts: list[tuple[Path, str]] = []
    for sec in sections:
        text = strip_code(sec.read_text(encoding="utf-8"))
        texts.append((sec, text))
        events: list[tuple[int, str, str | None]] = []
        for m in FIG_DEF.finditer(text):
            events.append((m.start(), "fig", m.group(1)))
        for m in TBL_DEF.finditer(text):
            events.append((m.start(), "tbl", m.group("lab")))
        for m in EQ_DEF.finditer(text):
            events.append((m.start(), "eq", m.group(2)))
        for pos, kind, label in sorted(events):
            if kind == "fig":
                fig_n += 1
                num = f"图{fig_n}"
            elif kind == "tbl":
                tbl_n += 1
                num = f"表{tbl_n}"
            else:
                eq_n += 1
                num = f"式({eq_n})"
            if not label:
                continue
            where = f"{sec.name}:{line_no(text, pos)}"
            if label in defined_at:
                out.append(Finding("FAIL", "xref_duplicate", where, f"标签 #{label} 重复定义（首次在 {defined_at[label]}）"))
                continue
            defined_at[label] = where
            numbers[label] = num
    used: set[str] = set()
    for sec, text in texts:
        for m in REF.finditer(text):
            lab = m.group(1)
            used.add(lab)
            if lab not in numbers:
                out.append(Finding("FAIL", "xref_undefined", f"{sec.name}:{line_no(text, m.start())}", f"引用了未定义的 @{lab}"))
    for lab, where in defined_at.items():
        if lab not in used:
            lvl = "INFO" if lab.startswith("eq:") else "WARN"
            out.append(Finding(lvl, "xref_unused", where, f"#{lab} 已定义但正文没有 @{lab} 引用"))
    return numbers


def check_references(sections: list[Path], out: list[Finding]) -> None:
    for sec in sections:
        text = strip_code(sec.read_text(encoding="utf-8"))
        m = re.search(r"^#\s+.*参考文献.*$", text, re.M)
        if m:
            rest = text[m.end():]
            items = [l for l in rest.splitlines() if re.match(r"^\s*(\[\d+\]|\d+[.、)]|-|\*)\s*\S", l)]
            if not items:
                out.append(Finding("WARN", "references", sec.name, "参考文献章节没有条目"))
            return
    out.append(Finding("WARN", "references", "paper/sections", "没有“参考文献”一级标题的章节"))


def run_checks(paper: Path, require: bool) -> tuple[list[Finding], dict[str, str], list[Path]]:
    out: list[Finding] = []
    sec_dir = paper / "sections"
    meta = load_meta(paper)
    if not sec_dir.is_dir() or not any(p.suffix == ".md" and not p.name.startswith("_") for p in sec_dir.iterdir()):
        lvl = "FAIL" if require else "INFO"
        out.append(Finding(lvl, "sections", "paper/sections", "没有任何章节文件（论文尚未开始写作）"))
        return out, {}, []
    check_meta(paper, meta, out)
    abstract, body = collect_sections(sec_dir, meta, out)
    check_abstract(abstract, meta, out)
    if not body:
        out.append(Finding("FAIL", "sections", "paper/sections", "只有摘要，没有正文章节"))
    for p in ([abstract] if abstract else []) + body:
        check_section_text(p, p.read_text(encoding="utf-8"), is_body=p is not abstract, out=out)
    numbers = check_crossrefs(([abstract] if abstract else []) + body, out)
    if body:
        check_references(body, out)
    return out, numbers, ([abstract] if abstract else []) + body


def write_report(dst: Path, root: Path, findings: list[Finding], numbers: dict[str, str], files: list[Path]) -> None:
    n = {lvl: sum(1 for f in findings if f.level == lvl) for lvl in ("FAIL", "WARN", "INFO")}
    verdict = "PASS" if n["FAIL"] == 0 else "FAIL"
    lines = ["# 论文章节自检（自动生成，勿手改）", "",
             f"- 时间：{datetime.datetime.now().isoformat(timespec='seconds')}",
             f"- 章节：{len(files)} 个文件：" + ("、".join(p.name for p in files) if files else "（无）"),
             f"- 结论：**{verdict}**（FAIL {n['FAIL']}，WARN {n['WARN']}，INFO {n['INFO']}）", "",
             "## 发现", ""]
    if findings:
        lines += ["| 级别 | 类别 | 位置 | 说明 |", "| --- | --- | --- | --- |"]
        for f in sorted(findings, key=lambda f: ("FAIL", "WARN", "INFO").index(f.level)):
            msg = f.msg.replace("|", "\\|")
            lines.append(f"| {f.level} | `{f.code}` | `{f.where}` | {msg} |")
    else:
        lines.append("无。")
    lines += ["", "## 图 / 表 / 公式编号（按正文出现顺序）", ""]
    if numbers:
        lines += ["| 标签 | 编号 |", "| --- | --- |"]
        for lab, num in numbers.items():
            lines.append(f"| `#{lab}` | {num} |")
    else:
        lines.append("（无带标签的图/表/公式）")
    lines += ["", f"重新生成：`python tools/{Path(__file__).name}`", ""]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paper", type=Path, default=None, help="paper/ 目录（默认：脚本所在项目根下的 paper/）")
    ap.add_argument("--strict", action="store_true", help="WARN 也非零退出")
    ap.add_argument("--require", action="store_true", help="没有章节文件也算 FAIL")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-report", action="store_true", help="不写 reports/PAPER_CHECK.md")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    root = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "tools" else Path.cwd()
    paper = (a.paper or (root / "paper")).resolve()
    if a.paper is not None:
        root = paper.parent
    findings, numbers, files = run_checks(paper, a.require)
    n_fail = sum(1 for f in findings if f.level == "FAIL")
    n_warn = sum(1 for f in findings if f.level == "WARN")

    if not a.no_report and (root / "reports").is_dir():
        write_report(root / "reports" / REPORT_NAME, root, findings, numbers, files)
    if a.json:
        print(json.dumps({"paper": str(paper), "fail": n_fail, "warn": n_warn, "numbers": numbers,
                          "findings": [f.__dict__ for f in findings]}, ensure_ascii=False, indent=2))
    else:
        print(f"paper：{paper}\n章节：{len(files)} 个")
        for f in sorted(findings, key=lambda f: ("FAIL", "WARN", "INFO").index(f.level)):
            print(f"{f.level:4} {f.code:18} {f.where:32} {f.msg}")
        if numbers:
            print("编号：" + "，".join(f"{lab}→{num}" for lab, num in numbers.items()))
        print(f"\n结果：FAIL {n_fail}，WARN {n_warn}" + ("" if a.no_report else f"；报告 reports/{REPORT_NAME}"))
    return 1 if n_fail or (a.strict and n_warn) else 0


if __name__ == "__main__":
    sys.exit(main())
