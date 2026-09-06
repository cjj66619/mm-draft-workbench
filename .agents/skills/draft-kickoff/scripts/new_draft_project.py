#!/usr/bin/env python3
"""new_draft_project.py — 从脚手架生成一个自包含的初稿项目文件夹（Devin 侧运行）。

    python3 .agents/skills/draft-kickoff/scripts/new_draft_project.py projects/2025-B \
        --title "某某问题的建模与求解" --contest 华为杯
    python3 .agents/skills/draft-kickoff/scripts/new_draft_project.py projects/2025-B --update-tools   # 只刷新 tools/

做的事：
1. 复制 scaffold/ 到目标目录（已存在的文件默认不覆盖，--force 覆盖模板类文件）；
2. 把 skills 里的纯 Python 工具拷进 <项目>/tools/（mm_plot_style、fig_layout_lint、check_figures、figure_index、portability_check）；
3. 把中文 TrueType 字体拷进 <项目>/tools/fonts/（默认找系统 wqy-microhei.ttc；--font 指定），附许可说明；
4. 替换 {{TITLE}} {{CONTEST}} {{DATE}} {{PROJECT}} {{GEN_PLATFORM}} {{GEN_VERSION}} 占位符；
5. 写 tools/VENDORED.json 记录来源与哈希，便于以后 --update-tools 升级；
6. 可选 --git：在项目目录 git init 并做首次提交。

目标目录里的东西只依赖 Python，Windows 可直接使用；本脚本自身只在 workbench 里跑。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SKILLS = SKILL.parent
REPO = SKILLS.parent.parent
SCAFFOLD = SKILL / "scaffold"

TOOL_SOURCES = {
    "mm_plot_style.py": SKILLS / "3coding-visual" / "scripts" / "mm_plot_style.py",
    "fig_layout_lint.py": SKILLS / "3coding-visual" / "scripts" / "fig_layout_lint.py",
    "check_figures.py": SKILLS / "3coding-visual" / "scripts" / "check_figures.py",
    "figure_index.py": SKILLS / "3coding-visual" / "scripts" / "figure_index.py",
    "portability_check.py": HERE / "portability_check.py",
}
FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    Path("/usr/share/fonts/wqy-microhei/wqy-microhei.ttc"),
    Path.home() / ".fonts" / "wqy-microhei.ttc",
]
FONT_LICENSE = """# tools/fonts/ 字体许可

- `wqy-microhei.ttc`（文泉驿微米黑，WenQuanYi Micro Hei）
  版权：© 2007-2009 Qianqian Fang and the WenQuanYi Project Board of Trustees；
  许可：Apache License 2.0 与 GPLv3（含字体嵌入例外，embedding exception）双许可。
  随项目分发的目的：保证 Windows / Linux / macOS 出图中文字形一致、PDF 可嵌入 TrueType（pdf.fonttype=42）。
  原始来源：http://wenq.org/ ；Debian 软件包 fonts-wqy-microhei。

`mm_plot_style.register_bundled_fonts()` 会在 apply_style 时自动注册本目录的 .ttf/.ttc/.otf，并优先于系统字体使用。
"""
# 只有这些"模板文件"在 --force 时会被覆盖；用户内容目录（code/ figures/ paper/ reports/…）永不覆盖
TEMPLATE_FILES = {"run_all.py", "run_all.bat", "doctor.py", "requirements.txt", "tools/README.md",
                  "figures/_template_figure/make_figure.py", "figures/_template_figure/README.md",
                  "code/_template_model.py", "code/common.py", "code/README.md"}
PLACEHOLDER_EXTS = {".md", ".yaml", ".yml", ".txt", ".json"}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def git_version() -> str:
    try:
        r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=10)
        return r.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def copy_scaffold(dst: Path, force: bool) -> tuple[list[str], list[str]]:
    created, skipped = [], []
    for src in sorted(SCAFFOLD.rglob("*")):
        rel = src.relative_to(SCAFFOLD)
        target = dst / rel
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists() and not (force and rel.as_posix() in TEMPLATE_FILES):
            skipped.append(rel.as_posix())
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        created.append(rel.as_posix())
    return created, skipped


def vendor_tools(dst: Path, font: Path | None) -> dict:
    tools = dst / "tools"
    tools.mkdir(exist_ok=True)
    record = {"generated": _dt.datetime.now().isoformat(timespec="seconds"), "workbench_commit": git_version(),
              "files": {}}
    for name, src in TOOL_SOURCES.items():
        if not src.exists():
            raise FileNotFoundError(f"缺少工具源文件：{src}")
        shutil.copy2(src, tools / name)
        record["files"][name] = {"from": src.relative_to(REPO).as_posix(), "sha256_16": sha256(src)}
    fonts = tools / "fonts"
    fonts.mkdir(exist_ok=True)
    chosen = font if font else next((c for c in FONT_CANDIDATES if c.exists()), None)
    if chosen and chosen.exists():
        shutil.copy2(chosen, fonts / chosen.name)
        (fonts / "LICENSE.md").write_text(FONT_LICENSE, encoding="utf-8")
        record["files"][f"fonts/{chosen.name}"] = {"from": str(chosen), "sha256_16": sha256(chosen)}
    else:
        print("[warn] 未找到 wqy-microhei.ttc，tools/fonts/ 为空；Windows 将回退到系统 SimHei/微软雅黑（字形与生成时可能不同）")
    (tools / "VENDORED.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def fill_placeholders(dst: Path, mapping: dict[str, str]) -> int:
    n = 0
    for p in dst.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in PLACEHOLDER_EXTS or "tools" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        for k, v in mapping.items():
            new = new.replace("{{" + k + "}}", v)
        if new != text:
            p.write_text(new, encoding="utf-8")
            n += 1
    return n


def git_init(dst: Path) -> None:
    def run(*args: str) -> None:
        subprocess.run(["git", "-C", str(dst), *args], check=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if not (dst / ".git").exists():
        run("init", "-b", "main")
    run("add", "-A")
    run("-c", "user.name=mm-draft-workbench", "-c", "user.email=noreply@localhost",
        "commit", "-q", "-m", "init: mm-draft-workbench 脚手架", "--allow-empty")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dest", help="项目目录（不存在则创建）")
    ap.add_argument("--title", default="（待填题目）")
    ap.add_argument("--contest", default="（待填竞赛/场景）")
    ap.add_argument("--font", type=Path, default=None, help="要随项目分发的中文 TrueType 字体文件")
    ap.add_argument("--force", action="store_true", help="覆盖模板类文件（run_all/doctor/common/模板）")
    ap.add_argument("--update-tools", action="store_true", help="只刷新 tools/（不碰其他文件）")
    ap.add_argument("--git", action="store_true", help="git init + 首次提交")
    a = ap.parse_args(argv)

    dst = Path(a.dest).resolve()
    dst.mkdir(parents=True, exist_ok=True)
    if a.update_tools:
        rec = vendor_tools(dst, a.font)
        print(f"tools/ 已刷新：{', '.join(rec['files'])}")
        return 0

    created, skipped = copy_scaffold(dst, a.force)
    rec = vendor_tools(dst, a.font)
    mapping = {
        "TITLE": a.title, "CONTEST": a.contest, "PROJECT": dst.name,
        "DATE": _dt.date.today().isoformat(),
        "GEN_PLATFORM": f"{platform.system()} {platform.release()} / Python {platform.python_version()}",
        "GEN_VERSION": rec["workbench_commit"],
    }
    n = fill_placeholders(dst, mapping)
    print(f"项目：{dst}\n新建 {len(created)} 个文件，跳过已存在 {len(skipped)} 个，替换占位符 {n} 个文件")
    print("tools/: " + ", ".join(rec["files"]))
    if a.git:
        git_init(dst)
        print("git: 已初始化并提交")
    print("\n下一步：\n  cd", dst, "\n  python doctor.py\n  然后按 .agents/skills/draft-kickoff/SKILL.md 推进六阶段。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
