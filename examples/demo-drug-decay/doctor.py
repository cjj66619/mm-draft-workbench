#!/usr/bin/env python3
"""doctor.py — 检查本机能否复现本项目（Windows / Linux / macOS）。

    python doctor.py            # 表格 + 结论；核心项缺失时退出码 1
    python doctor.py --json     # 机器可读

核心项（必须）：Python ≥ 3.10、numpy、pandas、matplotlib、scipy、可写的 results/ figures/ reports/、
中文 TrueType 字体（tools/fonts/ 随项目自带，或系统 SimHei/微软雅黑）。
可选项（缺了只影响对应功能）：pymupdf（PDF 图版式检查/转 PNG）、openpyxl（读 Excel 附件）、
scikit-learn、PyYAML（读 paper.yaml / project.yaml；缺了用内置最小解析）、draw.io 桌面版（重新导出示意图，平时只需编辑 .drawio）。
论文正文是 paper/sections/*.md，任何文本编辑器可读写，不需要额外软件。
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

CORE_PKGS = [("numpy", "numpy"), ("pandas", "pandas"), ("matplotlib", "matplotlib"), ("scipy", "scipy")]
OPT_PKGS = [("pymupdf", "pymupdf"), ("openpyxl", "openpyxl"), ("sklearn", "scikit-learn"), ("yaml", "PyYAML")]
WRITABLE = ("results", "figures", "reports", "data/clean")


def _pkg(mod: str) -> tuple[bool, str]:
    try:
        m = importlib.import_module(mod)
        return True, str(getattr(m, "__version__", "") or "")
    except Exception as e:  # noqa: BLE001
        return False, str(e).splitlines()[0][:60]


def _drawio() -> str | None:
    env = os.environ.get("DRAWIO_BIN")
    if env and Path(env).exists():
        return env
    for n in ("drawio", "draw.io", "draw.io.exe", "drawio.exe"):
        if shutil.which(n):
            return shutil.which(n)
    cands = []
    if platform.system() == "Windows":
        cands = [r"%ProgramFiles%\draw.io\draw.io.exe", r"%LocalAppData%\Programs\draw.io\draw.io.exe"]
    elif platform.system() == "Darwin":
        cands = ["/Applications/draw.io.app/Contents/MacOS/draw.io"]
    for c in cands:
        if Path(os.path.expandvars(c)).exists():
            return os.path.expandvars(c)
    return None


def _fonts() -> tuple[bool, str]:
    try:
        import mm_plot_style as mps
        info = mps.resolve_fonts(lang="zh")
    except Exception as e:  # noqa: BLE001
        return False, f"mm_plot_style 导入失败: {e}"
    cjk, kind = info.get("cjk"), info.get("cjk_kind")
    if not cjk:
        return False, "无中文字体：把 wqy-microhei.ttc 放到 tools/fonts/，或安装 SimHei/微软雅黑"
    if kind != "truetype":
        return False, f"{cjk} 非 TrueType（{kind}），PDF 中文可能损坏；改用 tools/fonts/ 内字体"
    return True, f"中文 {cjk}（{kind}），Latin {info.get('latin')}"


def check() -> dict:
    rows: list[dict] = []

    def add(group: str, item: str, ok: bool, detail: str, required: bool) -> None:
        rows.append({"group": group, "item": item, "ok": ok, "detail": detail, "required": required})

    v = sys.version_info
    add("python", "Python >= 3.10", v >= (3, 10), f"{platform.python_version()} @ {sys.executable}", True)
    add("python", "UTF-8 模式", (sys.flags.utf8_mode == 1) or os.environ.get("PYTHONUTF8") == "1",
        "建议设置环境变量 PYTHONUTF8=1（run_all.py 会自动设置）", False)
    for mod, pip in CORE_PKGS:
        ok, d = _pkg(mod)
        add("package", pip, ok, d if ok else f"pip install {pip}", True)
    for mod, pip in OPT_PKGS:
        ok, d = _pkg(mod)
        add("package(optional)", pip, ok, d if ok else f"pip install {pip}", False)
    ok, d = _fonts()
    add("fonts", "中文 TrueType 字体", ok, d, True)
    for rel in WRITABLE:
        p = ROOT / rel
        try:
            p.mkdir(parents=True, exist_ok=True)
            t = p / ".doctor_write_test"
            t.write_text("ok", encoding="utf-8")
            t.unlink()
            add("fs", f"{rel}/ 可写", True, str(p), True)
        except OSError as e:
            add("fs", f"{rel}/ 可写", False, str(e), True)
    raw = ROOT / "data" / "raw"
    n_raw = sum(1 for p in raw.iterdir() if not p.name.startswith(".")) if raw.is_dir() else 0
    add("fs", "data/raw/ 存在（只读原始数据）", raw.is_dir(), f"{n_raw} 个文件", False)
    dio = _drawio()
    add("tool(optional)", "draw.io 命令行", bool(dio), dio or "未安装：编辑 .drawio 用桌面版/网页版即可，导出用 File→Export", False)
    add("tool(optional)", "tools/fonts/ 自带字体", (ROOT / "tools" / "fonts").is_dir() and any((ROOT / "tools" / "fonts").iterdir()),
        ", ".join(p.name for p in (ROOT / "tools" / "fonts").glob("*")) if (ROOT / "tools" / "fonts").is_dir() else "无（将使用系统字体，出图字形可能与交付版略有差异）", False)
    core_ok = all(r["ok"] for r in rows if r["required"])
    return {"platform": platform.platform(), "root": str(ROOT), "core_ok": core_ok, "rows": rows}


def _pad(s: str, width: int) -> str:
    """按显示宽度补空格（CJK 记 2 列），让表格在终端对齐。"""
    import unicodedata
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, width - w)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rep = check()
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"平台：{rep['platform']}\n项目：{rep['root']}\n")
        w = max(len(_pad(r["item"], 0)) + sum(1 for c in r["item"] if ord(c) > 0x2E7F) for r in rep["rows"]) + 2
        for r in rep["rows"]:
            mark = "OK  " if r["ok"] else ("FAIL" if r["required"] else "MISS")
            print(f"{mark} {_pad(r['item'], w)} {r['detail']}")
        print("\n结论：" + ("核心环境齐全，可运行 python run_all.py" if rep["core_ok"]
                          else "核心项缺失（FAIL），请按提示安装后重试；MISS 为可选项"))
    return 0 if rep["core_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
