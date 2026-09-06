#!/usr/bin/env python3
"""export_figure.py — 把 .drawio 导成 1:1 PNG 与矢量 PDF，供肉眼自检和交付。

    python export_figure.py fig.drawio                 # 出 fig.png + fig.pdf
    python export_figure.py fig.drawio --png-only -s 2 # 只出 2 倍图，便于看细节
    python export_figure.py figures/                   # 遍历 figures/*/ 里的 .drawio

依赖 draw.io 桌面版命令行。各平台自动探测：
- Linux：`drawio`（mm-draft-workbench 的 setup_env.sh 装了 headless wrapper）
- Windows：PATH 中的 `draw.io.exe` / `drawio.exe`，或默认安装目录
  `%ProgramFiles%\\draw.io\\draw.io.exe`、`%LocalAppData%\\Programs\\draw.io\\draw.io.exe`
- macOS：`/Applications/draw.io.app/Contents/MacOS/draw.io`
也可用环境变量 DRAWIO_BIN 指定。没装时给出替代方案，不静默失败；
mm-draft-workbench 的约定是：.drawio 与已导出的 PNG/PDF 一起交付，Windows 侧只编辑，
不强制重新导出（draw.io 桌面版 File → Export as 亦可）。
"""
from __future__ import annotations

import argparse
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys

_WIN_CANDIDATES = [
    r"%ProgramFiles%\draw.io\draw.io.exe",
    r"%ProgramFiles(x86)%\draw.io\draw.io.exe",
    r"%LocalAppData%\Programs\draw.io\draw.io.exe",
]
_MAC_CANDIDATES = ["/Applications/draw.io.app/Contents/MacOS/draw.io"]


def find_drawio() -> str | None:
    """返回可用的 draw.io 命令行路径，找不到返回 None。"""
    env = os.environ.get("DRAWIO_BIN")
    if env and pathlib.Path(env).exists():
        return env
    for name in ("drawio", "draw.io", "draw.io.exe", "drawio.exe"):
        hit = shutil.which(name)
        if hit:
            return hit
    cands = _WIN_CANDIDATES if platform.system() == "Windows" else (_MAC_CANDIDATES if platform.system() == "Darwin" else [])
    for c in cands:
        p = pathlib.Path(os.path.expandvars(c))
        if p.exists():
            return str(p)
    return None


def run(cmd: list[str]) -> bool:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    if p.returncode != 0:
        print(p.stdout + p.stderr, file=sys.stderr)
    return p.returncode == 0


def export_one(cli: str, src: pathlib.Path, *, scale: float = 1.0, png: bool = True, pdf: bool = True) -> bool:
    # 用画布宽度锁定输出，保证 1 单位 = 1 像素；否则 drawio 会按内容包围盒另算，
    # 输出比画布大几像素，没法和参考图做逐像素比对
    m = re.search(r'pageWidth="([\d.]+)"', src.read_text(encoding="utf-8"))
    width = ["--width", str(int(float(m.group(1)) * scale))] if m else []
    ok = True
    if png:
        out = src.with_suffix(".png")
        ok &= run([cli, "-x", "-f", "png", "-s", str(scale), "-b", "0", *width, "-o", str(out), str(src)])
        if ok:
            print(f"OK {out}")
    if pdf:
        out = src.with_suffix(".pdf")
        ok &= run([cli, "-x", "-f", "pdf", "--crop", "-o", str(out), str(src)])
        if ok:
            print(f"OK {out}")
    return ok


def iter_drawio(paths: list[str]) -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for p in paths:
        path = pathlib.Path(p)
        if path.is_dir():
            out.extend(sorted(path.glob("*.drawio")))
            for sub in sorted(x for x in path.iterdir() if x.is_dir() and not x.name.startswith(("_", "."))):
                out.extend(sorted(sub.glob("*.drawio")))
        elif path.suffix == ".drawio" and path.exists():
            out.append(path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help=".drawio 文件或目录")
    ap.add_argument("-s", "--scale", type=float, default=1, help="PNG 缩放，默认 1（1 单位=1 像素）")
    ap.add_argument("--png-only", action="store_true")
    ap.add_argument("--pdf-only", action="store_true")
    ap.add_argument("--allow-missing", action="store_true", help="找不到 drawio 时退出码 0（只提示），供 run_all.py 在 Windows 上跳过")
    a = ap.parse_args()

    files = iter_drawio(a.paths)
    if not files:
        print("没有找到 .drawio 文件", file=sys.stderr)
        return 2
    cli = find_drawio()
    if not cli:
        msg = ("未找到 draw.io 命令行（drawio / draw.io.exe）。\n"
               "  Windows: 安装 https://github.com/jgraph/drawio-desktop/releases 后重试，或设 DRAWIO_BIN\n"
               "  Linux : bash scripts/setup_env.sh（mm-draft-workbench 仓库）\n"
               "  或用 draw.io 桌面版/网页版打开 .drawio → File → Export as → PNG/PDF，保存到同一文件夹并同名\n"
               "  注意：没有渲染图就无法自检；交付包里应已附带导出图，Windows 侧只编辑不必重导。")
        print(msg, file=sys.stderr)
        return 0 if a.allow_missing else 1
    ok = True
    for src in files:
        ok &= export_one(cli, src, scale=a.scale, png=not a.pdf_only, pdf=not a.png_only)
    if not ok:
        return 1
    print("接下来务必打开 PNG 逐块核对：文字有无溢出/压线、箭头方向、数值有没有抄错；示意图终稿需人工重画，见 REDRAW_NOTES.md。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
