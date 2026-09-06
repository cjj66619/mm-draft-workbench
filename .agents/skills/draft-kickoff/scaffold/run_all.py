#!/usr/bin/env python3
"""run_all.py — 一键复现本项目（Windows / Linux / macOS 通用，纯 Python，不需要 bash）。

    python run_all.py              # = all：code → figures → figcheck → check
    python run_all.py code         # 只跑 code/*.py（数据处理 + 模型，按文件名顺序）
    python run_all.py figures      # 只重画 figures/*/make_figure.py
    python run_all.py figcheck     # 图的字体/版式自检 + 重建 figures/README.md、FIGURE_REVIEW.md
    python run_all.py check        # 环境体检 + 可移植性扫描
    python run_all.py figures fig02_q1_fit   # 只重画一张图
    python run_all.py --continue   # 某一步失败不中断，最后汇总

阶段约定（不用配置文件，靠目录与命名）：
- code/NN_*.py 按数字前缀顺序执行（00_ 数据处理、10_/20_ 各问模型、90_ 汇总），前缀 _ 的文件跳过；
- figures/<fig_id>/make_figure.py 每个文件夹一张图；
- 所有脚本以项目根目录为工作目录、用当前解释器（sys.executable）运行、强制 UTF-8；
- 每次运行写日志到 reports/_logs/run_<时间>.log 与 reports/RUN_STATUS.md（最近一次各阶段结果）。

Word 初稿（paper/main.docx）不在此脚本范围：它由建模侧一次性生成并冻结，之后直接用 Word 编辑。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
LOG_DIR = ROOT / "reports" / "_logs"
STAGES = ("code", "figures", "figcheck", "check")


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["MPLBACKEND"] = env.get("MPLBACKEND", "Agg")
    env["PYTHONPATH"] = os.pathsep.join(x for x in (str(TOOLS), str(ROOT / "code"), env.get("PYTHONPATH", "")) if x)
    return env


class Runner:
    def __init__(self, log: Path, keep_going: bool) -> None:
        self.log = log
        self.keep_going = keep_going
        self.results: list[tuple[str, str, str, float]] = []   # stage, name, status, seconds
        self.failed = False

    def run(self, stage: str, name: str, cmd: list[str], *, optional: bool = False) -> bool:
        if self.failed and not self.keep_going:
            self.results.append((stage, name, "SKIP", 0.0))
            return False
        shown = " ".join(Path(c).name if os.sep in c else c for c in cmd)
        print(f"\n[{stage}] {name}\n  $ {shown}", flush=True)
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(ROOT), env=_env(), text=True, encoding="utf-8", errors="replace",
                           capture_output=True)
        dt = time.time() - t0
        out = (p.stdout or "") + (p.stderr or "")
        with self.log.open("a", encoding="utf-8") as fh:
            fh.write(f"\n===== [{stage}] {name} | exit {p.returncode} | {dt:.1f}s\n$ {shown}\n{out}")
        tail = out.strip().splitlines()[-12:]
        for line in tail:
            print("  " + line)
        ok = p.returncode == 0
        status = "OK" if ok else ("WARN" if optional else "FAIL")
        print(f"  -> {status} ({dt:.1f}s)")
        self.results.append((stage, name, status, dt))
        if not ok and not optional:
            self.failed = True
        return ok


def py_files(folder: Path) -> list[Path]:
    return sorted(p for p in folder.glob("*.py") if not p.name.startswith("_") and p.name != "common.py")


def figure_scripts(only: list[str]) -> list[Path]:
    figs = ROOT / "figures"
    if not figs.is_dir():
        return []
    out = []
    for d in sorted(p for p in figs.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        if only and d.name not in only:
            continue
        mk = d / "make_figure.py"
        if mk.exists():
            out.append(mk)
    return out


def write_status(r: Runner, log: Path) -> None:
    lines = ["# 最近一次 run_all 结果", "",
             f"- 时间：{_dt.datetime.now().isoformat(timespec='seconds')}",
             f"- 平台：{sys.platform}，Python {sys.version.split()[0]}",
             f"- 日志：`{log.relative_to(ROOT).as_posix()}`", "",
             "| 阶段 | 步骤 | 结果 | 耗时(s) |", "| --- | --- | --- | --- |"]
    for stage, name, status, dt in r.results:
        lines.append(f"| {stage} | `{name}` | {status} | {dt:.1f} |")
    lines += ["", "FAIL 的步骤看日志末尾的 traceback；WARN 表示可选检查未通过（例如缺少可选工具）。", ""]
    (ROOT / "reports" / "RUN_STATUS.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stages", nargs="*", default=["all"], help="all | " + " | ".join(STAGES) + " | 图文件夹名")
    ap.add_argument("--continue", dest="keep_going", action="store_true", help="失败不中断")
    ap.add_argument("--strict", action="store_true", help="figcheck 中版式 WARN 也视为失败")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    wanted = [s for s in args.stages if s in STAGES or s == "all"]
    only_figs = [s for s in args.stages if s not in STAGES and s != "all"]
    if only_figs and not wanted:
        wanted = ["figures"]
    if "all" in wanted:
        wanted = list(STAGES)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f"run_{_dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    r = Runner(log, args.keep_going)
    py = sys.executable
    print(f"项目：{ROOT}\n解释器：{py}\n阶段：{', '.join(wanted)}" + (f"（图：{', '.join(only_figs)}）" if only_figs else ""))

    if "code" in wanted:
        scripts = py_files(ROOT / "code")
        if not scripts:
            print("[code] code/ 下没有可执行脚本（NN_*.py）")
        for s in scripts:
            r.run("code", s.name, [py, str(s)])

    if "figures" in wanted:
        scripts = figure_scripts(only_figs)
        if not scripts:
            print("[figures] 没有找到 figures/*/make_figure.py")
        for s in scripts:
            r.run("figures", s.parent.name, [py, str(s)])

    if "figcheck" in wanted:
        r.run("figcheck", "check_figures", [py, str(TOOLS / "check_figures.py"), "--expect-cjk", "figures"], optional=True)
        lint_cmd = [py, str(TOOLS / "fig_layout_lint.py"), "figures"]
        if args.strict:
            lint_cmd.append("--strict")
        r.run("figcheck", "fig_layout_lint", lint_cmd, optional=not args.strict)
        r.run("figcheck", "figure_index", [py, str(TOOLS / "figure_index.py")], optional=True)

    if "check" in wanted:
        r.run("check", "doctor", [py, str(ROOT / "doctor.py")], optional=True)
        r.run("check", "portability_check", [py, str(TOOLS / "portability_check.py"), "."], optional=True)

    write_status(r, log)
    n_fail = sum(1 for *_, st, _ in r.results if st == "FAIL")
    n_warn = sum(1 for *_, st, _ in r.results if st == "WARN")
    print(f"\n完成：{len(r.results)} 步，FAIL {n_fail}，WARN {n_warn}；详情 reports/RUN_STATUS.md，日志 {log.relative_to(ROOT).as_posix()}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
