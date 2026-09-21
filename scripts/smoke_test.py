#!/usr/bin/env python3
"""smoke_test.py — 仓库级冒烟测试（纯 Python，Windows / Linux / macOS 通用）。

    python scripts/smoke_test.py                 # 新建临时项目 → doctor → run_all → 写最小 Markdown 章节 → run_all paper
    python scripts/smoke_test.py --keep          # 保留临时项目目录便于排查

检查点：
1. new_draft_project.py 能生成骨架（含 tools/paper_check.py），doctor.py 通过；
2. run_all.py 在模板代码/模板图上全绿（reports/RUN_STATUS.md 无 FAIL；没有章节时 paper 阶段不算失败）；
3. 写入摘要 + 一章 Markdown 后，`run_all.py paper` 通过（FAIL 0）并生成 reports/PAPER_CHECK.md；
4. 故意写入占位符 / 未定义引用 / 内部名泄露的章节时，paper_check.py 必须报 FAIL。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NEW_PROJECT = REPO / ".agents" / "skills" / "draft-kickoff" / "scripts" / "new_draft_project.py"

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

ABSTRACT = """这是冒烟测试用的摘要：用指数模型 $y = a e^{-bt} + c$ 拟合一组合成观测值，并给出参数估计，得到 $a = 1.0$、$b = 0.2$。

**关键词**：冒烟测试；指数模型
"""

BAD_SECTION = """# 二、问题分析

本节数据来自 reports/RESULTS_REPORT.md，结果见 @fig:missing。[TODO: 补充分析]
"""

EXPECTED_FILES = (
    "AGENTS.md", "HANDOFF.md", "plan.md", "todo.md", "doctor.py", "run_all.py", "requirements.txt",
    "code/common.py", "tools/mm_plot_style.py", "tools/paper_check.py", "tools/portability_check.py",
    "figures/_template_figure/make_figure.py", "paper/paper.yaml", "paper/README.md",
)


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run(cmd: list[str], cwd: Path, label: str, expect_fail: bool = False) -> str:
    print(f"\n[smoke] {label}\n  $ {' '.join(Path(c).name if Path(c).is_absolute() else c for c in cmd)}", flush=True)
    p = subprocess.run(cmd, cwd=str(cwd), env=_env(), text=True, encoding="utf-8", errors="replace",
                       capture_output=True)
    out = p.stdout + p.stderr
    tail = out[-3000:]
    if (p.returncode != 0) != expect_fail:
        print(tail)
        want = "非零" if expect_fail else "0"
        raise SystemExit(f"[smoke] FAIL: {label} (exit {p.returncode}，预期 {want})")
    print(tail.strip().splitlines()[-1] if tail.strip() else "(no output)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keep", action="store_true", help="保留临时项目目录")
    ap.add_argument("--dest", type=Path, default=None, help="临时项目位置（默认系统临时目录）")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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

        sections = proj / "paper" / "sections"
        sections.mkdir(parents=True, exist_ok=True)
        (sections / "00_abstract.md").write_text(ABSTRACT, encoding="utf-8")
        (sections / "01_restatement.md").write_text(SECTION, encoding="utf-8")
        run([py, "run_all.py", "paper"], proj, "run_all.py paper")
        report = proj / "reports" / "PAPER_CHECK.md"
        if not report.is_file() or "**PASS**" not in report.read_text(encoding="utf-8"):
            raise SystemExit("[smoke] FAIL: reports/PAPER_CHECK.md 未生成或结论非 PASS")

        (sections / "02_analysis.md").write_text(BAD_SECTION, encoding="utf-8")
        out = run([py, str(Path("tools") / "paper_check.py")], proj, "paper_check.py 应对坏章节报 FAIL", expect_fail=True)
        for token in ("placeholder", "leak", "xref_undefined"):
            if token not in out:
                raise SystemExit(f"[smoke] FAIL: paper_check.py 未报出 {token}")
        print("\n[smoke] PASS")
    finally:
        if args.keep:
            print(f"[smoke] 保留 {tmp_root}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
