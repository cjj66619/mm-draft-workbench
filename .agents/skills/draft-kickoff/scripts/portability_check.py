#!/usr/bin/env python3
"""portability_check.py — 扫描项目文件夹，找出在 Windows 上跑不通的写法。

    python tools/portability_check.py .            # 扫描整个项目
    python tools/portability_check.py code figures # 只扫指定目录
    python tools/portability_check.py . --strict   # WARN 也非零退出

检查项（FAIL = 换机必炸；WARN = 可能出问题，请人工确认）：
- FAIL abs_path        : 写死的绝对路径（/home/、/usr/、/tmp/、C:\\Users\\…、/Users/）
- FAIL shell_dep       : 调用 bash / sh / xvfb-run / *.sh
- FAIL unix_cmd        : subprocess/os.system 里用 ls、rm、cp、mv、cat、sed、awk、grep、which
- FAIL hardcoded_python: subprocess 中写死 "python3"/"python"（应用 sys.executable）
- WARN open_no_encoding: 文本模式 open() 未指定 encoding（Windows 默认 GBK → 中文乱码/UnicodeDecodeError）
- WARN read_text_no_enc: Path.read_text()/write_text() 未指定 encoding
- WARN subprocess_no_enc: subprocess.run(text=True) 未指定 encoding
- WARN backslash_path  : 字符串里的反斜杠路径分隔（应用 pathlib / os.path.join）
- WARN posix_only_api  : os.fork / pwd / grp / fcntl / signal.SIGKILL 等仅 POSIX 的 API
- WARN case_mismatch   : 引用的相对路径大小写与磁盘不一致（Linux 能跑、Windows 也能跑，但 git 会乱）
- INFO chmod_exec      : 只靠 shebang/chmod 执行的脚本（Windows 需 python xxx.py）

扫描范围：*.py *.md *.txt *.yaml *.yml *.json *.bat *.ps1 *.toml *.cfg；
跳过 .git、__pycache__、.venv、node_modules、data/raw、tools/fonts；行内含 `# noqa: portability` 的行跳过。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EXTS = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".bat", ".ps1", ".toml", ".cfg"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "raw", "fonts", "_logs", ".mypy_cache", ".pytest_cache"}
NOQA = "noqa: portability"

# (级别, 代码, 正则, 适用后缀, 是否按整条语句匹配)
RULES: list[tuple[str, str, re.Pattern, set[str], bool]] = [
    ("FAIL", "abs_path", re.compile(r'(?<![\w/])(/home/|/usr/(?!share/fonts|bin/env)|/tmp/|/opt/|/Users/|[A-Za-z]:\\Users\\)'), EXTS, False),
    ("FAIL", "shell_dep", re.compile(r'(subprocess\.\w+|os\.system|os\.popen)\([^\n]*(?<![\w.])(bash|/bin/sh|xvfb-run|\.sh\b)'), {".py"}, True),
    ("WARN", "shell_dep", re.compile(r'(?<![\w.])(bash|/bin/sh|xvfb-run)\s|\.sh\b(?![\w-])'), {".bat", ".ps1", ".md"}, False),
    ("INFO", "shell_mention", re.compile(r'(?<![\w.])(bash|xvfb-run)\s|\.sh\b(?![\w-])'), {".py"}, False),
    ("FAIL", "unix_cmd", re.compile(r'(subprocess\.(run|call|Popen|check_output)|os\.system)\(\s*\[?\s*["\'](ls|rm|cp|mv|cat|sed|awk|grep|which|chmod|find)\b'), {".py"}, True),
    ("FAIL", "hardcoded_python", re.compile(r'(subprocess\.(run|call|Popen|check_output)|os\.system)\(\s*\[?\s*["\']python3?["\']'), {".py"}, True),
    ("WARN", "open_no_encoding", re.compile(r'(?<![\w.])open\((?![^\n]*["\'][rwa]?b[+]?["\'])(?![^\n]*encoding=)'), {".py"}, True),
    ("WARN", "read_text_no_enc", re.compile(r'\.(read_text|write_text)\((?![^\n]*encoding=)'), {".py"}, True),
    ("WARN", "subprocess_no_enc", re.compile(r'subprocess\.(run|Popen|check_output)\((?=[^\n]*text=True)(?![^\n]*encoding=)'), {".py"}, True),
    ("WARN", "backslash_path", re.compile(r'["\'][A-Za-z0-9_.]+\\+[A-Za-z0-9_.]+\\*'), {".py"}, False),
    ("WARN", "posix_only_api", re.compile(r'\bos\.(fork|setsid|getuid|geteuid|killpg)\b|^\s*import (pwd|grp|fcntl|termios|resource)\b|signal\.SIG(KILL|USR1|USR2|HUP)\b'), {".py"}, False),
]
SELF = Path(__file__).name


def statement_at(lines: list[str], i: int, max_lines: int = 15) -> str:
    """从第 i 行（0 基）起，合并到括号平衡为止的语句文本（多行调用一起看），换行替换为空格。"""
    depth = 0
    buf: list[str] = []
    for line in lines[i:i + max_lines]:
        buf.append(line)
        depth += line.count("(") + line.count("[") + line.count("{") - line.count(")") - line.count("]") - line.count("}")
        if depth <= 0:
            break
    return " ".join(x.strip() for x in buf)
REL_PATH = re.compile(r'["\']((?:\.{1,2}/)?(?:[\w\-. ]+/)+[\w\-. ]+\.\w{1,5})["\']')


def iter_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if root.is_file():
            out.append(root)
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in EXTS and not (set(p.parts) & SKIP_DIRS):
                out.append(p)
    return sorted(set(out))


def case_mismatch(file: Path, line: str, root: Path) -> str | None:
    for m in REL_PATH.finditer(line):
        rel = m.group(1)
        if rel.startswith(("http", "mailto")) or "{" in rel:
            continue
        for base in (file.parent, root):
            target = (base / rel)
            if target.exists():
                try:
                    real = target.resolve()
                    if real.name != target.name:
                        return f"路径大小写不一致：{rel} → 磁盘上是 {real.name}"
                except OSError:
                    pass
                break
    return None


def scan(roots: list[Path], project_root: Path) -> list[tuple[str, str, Path, int, str]]:
    findings: list[tuple[str, str, Path, int, str]] = []
    for f in iter_files(roots):
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(("FAIL", "non_utf8_file", f, 0, "文件不是 UTF-8 编码（Windows 记事本另存为 UTF-8）"))
            continue
        except OSError:
            continue
        if f.suffix == ".py" and text.startswith("#!") and f.parent.name in ("code",):
            findings.append(("INFO", "chmod_exec", f, 1, "有 shebang：Windows 上请用 python 运行，run_all.py 已处理"))
        if f.name == SELF:
            continue
        in_code_block = False
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            if NOQA in line:
                continue
            if f.suffix == ".md":
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
            stripped = line.strip()
            if f.suffix == ".py" and (stripped.startswith("#") or stripped.startswith("#!")):
                continue
            for level, code, rx, exts, whole in RULES:
                if f.suffix.lower() not in exts:
                    continue
                if f.suffix == ".md" and code != "abs_path" and not in_code_block:
                    continue   # Markdown 正文提到 bash 不算，只查代码块
                if code == "abs_path" and f.suffix == ".md" and "http" in line:
                    continue
                target = statement_at(lines, i - 1) if whole else line
                if rx.search(target):
                    findings.append((level, code, f, i, stripped[:110]))
            if f.suffix in (".py", ".md"):
                msg = case_mismatch(f, line, project_root)
                if msg:
                    findings.append(("WARN", "case_mismatch", f, i, msg))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."], help="要扫描的目录/文件")
    ap.add_argument("--root", default=None, help="项目根（默认第一个路径）")
    ap.add_argument("--strict", action="store_true", help="WARN 也非零退出")
    ap.add_argument("--max", type=int, default=60, help="最多打印条数")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    roots = [Path(p) for p in a.paths]
    project_root = Path(a.root) if a.root else (roots[0] if roots[0].is_dir() else roots[0].parent)
    findings = scan(roots, project_root.resolve())
    order = {"FAIL": 0, "WARN": 1, "INFO": 2}
    findings.sort(key=lambda x: (order[x[0]], str(x[2]), x[3]))
    for level, code, f, ln, msg in findings[: a.max]:
        try:
            rel = f.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            rel = str(f)
        print(f"{level} {code:<18} {rel}:{ln}  {msg}")
    if len(findings) > a.max:
        print(f"... 另有 {len(findings) - a.max} 条未显示（--max 调大）")
    n_fail = sum(1 for x in findings if x[0] == "FAIL")
    n_warn = sum(1 for x in findings if x[0] == "WARN")
    print(f"\n[portability_check] FAIL {n_fail}，WARN {n_warn}，INFO {len(findings) - n_fail - n_warn}")
    if n_fail or (a.strict and n_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
