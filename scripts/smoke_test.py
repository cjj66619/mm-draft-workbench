#!/usr/bin/env python3
"""smoke_test.py — 仓库级冒烟测试（纯 Python，Windows / Linux / macOS 通用）。

    python scripts/smoke_test.py                 # 新建临时项目 → doctor → run_all → 写一节 Markdown → build_docx
    python scripts/smoke_test.py --keep          # 保留临时项目目录便于排查
    python scripts/smoke_test.py --require-docx  # 没有 pandoc 时视为失败（默认没有 pandoc 则跳过 Word 步骤）

检查点：
1. new_draft_project.py 能生成骨架，doctor.py 通过；
2. run_all.py 在模板代码/模板图上全绿（reports/RUN_STATUS.md 无 FAIL）；
3. 有 pandoc 时，docx-build 能把一节 Markdown 合成 paper/main.docx 并通过 --strict 审计。
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NEW_PROJECT = REPO / ".agents" / "skills" / "draft-kickoff" / "scripts" / "new_draft_project.py"
BUILD_DOCX = REPO / ".agents" / "skills" / "docx-build" / "scripts" / "build_docx.py"

SECTION = """# 一、问题重述

这是冒烟测试用的最小章节，含一个行内公式 $y = a e^{-bt} + c$ 与一个编号公式：

$$
y(t) = a e^{-bt} + c
$$ {#eq:model}

模型见 @eq:model。

## 1.1 小节

| 参数 | 估计值 |
| --- | --- |
| $a$ | 1.0 |
| $b$ | 0.2 |

Table: 冒烟测试表 {#tbl:smoke}

结果见 @tbl:smoke。
"""

ABSTRACT = """这是冒烟测试用的摘要：用指数模型 $y = a e^{-bt} + c$ 拟合一组合成观测值，并给出参数估计。

**关键词**：冒烟测试；指数模型
"""

EXPECTED_FILES = (
    "AGENTS.md", "HANDOFF.md", "plan.md", "todo.md", "doctor.py", "run_all.py", "requirements.txt",
    "code/common.py", "tools/mm_plot_style.py", "tools/portability_check.py", "figures/_template_figure/make_figure.py",
    "paper/paper.yaml",
)


def run(cmd: list[str], cwd: Path, label: str) -> None:
    print(f"\n[smoke] {label}\n  $ {' '.join(Path(c).name if Path(c).is_absolute() else c for c in cmd)}", flush=True)
    p = subprocess.run(cmd, cwd=str(cwd), text=True, encoding="utf-8", errors="replace", capture_output=True)
    tail = (p.stdout + p.stderr)[-3000:]
    if p.returncode != 0:
        print(tail)
        raise SystemExit(f"[smoke] FAIL: {label} (exit {p.returncode})")
    print(tail.strip().splitlines()[-1] if tail.strip() else "(no output)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keep", action="store_true", help="保留临时项目目录")
    ap.add_argument("--require-docx", action="store_true", help="缺 pandoc 时视为失败")
    ap.add_argument("--dest", type=Path, default=None, help="临时项目位置（默认系统临时目录）")
    args = ap.parse_args()

    py = sys.executable
    tmp_root = args.dest or Path(tempfile.mkdtemp(prefix="mm-smoke-"))
    proj = tmp_root / "smoke-project"
    print(f"[smoke] 临时项目：{proj}")
    try:
        run([py, str(NEW_PROJECT), str(proj), "--title", "冒烟测试题目", "--contest", "smoke"], REPO, "生成骨架")
        missing = [f for f in EXPECTED_FILES if not (proj / f).is_file()]
        if missing:
            raise SystemExit(f"[smoke] FAIL: 骨架缺文件 {missing}")
        run([py, "doctor.py"], proj, "doctor.py")
        run([py, "run_all.py"], proj, "run_all.py")
        status = (proj / "reports" / "RUN_STATUS.md").read_text(encoding="utf-8")
        if "| FAIL |" in status:
            print(status)
            raise SystemExit("[smoke] FAIL: RUN_STATUS.md 含 FAIL")
        run([py, str(Path("tools") / "portability_check.py"), "."], proj, "portability_check")

        if shutil.which("pandoc") is None and not (Path.home() / ".local" / "bin" / "pandoc").exists():
            msg = "[smoke] 未找到 pandoc，跳过 Word 步骤"
            if args.require_docx:
                raise SystemExit(msg + "（--require-docx）")
            print(msg)
        else:
            sections = proj / "paper" / "sections"
            sections.mkdir(parents=True, exist_ok=True)
            (sections / "00_abstract.md").write_text(ABSTRACT, encoding="utf-8")
            (sections / "01_restatement.md").write_text(SECTION, encoding="utf-8")
            run([py, str(BUILD_DOCX), "--strict"], proj, "build_docx --strict")
            docx = proj / "paper" / "main.docx"
            if not docx.is_file() or docx.stat().st_size < 10_000:
                raise SystemExit("[smoke] FAIL: paper/main.docx 未生成或过小")
            run([py, str(BUILD_DOCX), "--freeze"], proj, "build_docx --freeze")
            if not (proj / "paper" / "DOCX_FREEZE.json").is_file():
                raise SystemExit("[smoke] FAIL: 未写 DOCX_FREEZE.json")
        print("\n[smoke] PASS")
    finally:
        if args.keep:
            print(f"[smoke] 保留 {tmp_root}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
