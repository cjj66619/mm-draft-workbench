"""common.py — 所有 code/*.py 共用的路径、随机种子与保存工具（跨平台）。

用法（在 code/ 下任意脚本）：

    from common import ROOT, DATA_RAW, DATA_CLEAN, RESULTS, set_seed, save_table, save_json, load_clean

    set_seed(42)
    df = load_clean("q1_series.csv")
    ...
    save_table(params, "q1_fit_params.csv")     # → results/q1_fit_params.csv（UTF-8）
    save_json({"rmse": 0.12}, "q1_metrics.json") # → results/q1_metrics.json

约定：
- 一切路径都从 ROOT 派生，脚本无论从哪个目录启动都能跑（run_all.py 以项目根为 cwd，直接双击/IDE 运行也可）。
- 文本文件一律 UTF-8；CSV 不写索引；JSON 缩进 2、保留中文。
- 只固定 numpy / random 的种子；如用到 torch / sklearn，请在各自脚本里再固定并写进 RESULTS_REPORT.md。
"""
from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PROBLEM = ROOT / "problem"
DATA_RAW = ROOT / "data" / "raw"
DATA_CLEAN = ROOT / "data" / "clean"
RESULTS = ROOT / "results"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "figures"
TOOLS = ROOT / "tools"

for _p in (DATA_CLEAN, RESULTS, REPORTS, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)
if str(TOOLS) not in sys.path:      # 让 code/ 里也能 import mm_plot_style
    sys.path.insert(0, str(TOOLS))

DEFAULT_SEED = 42


def set_seed(seed: int = DEFAULT_SEED) -> int:
    """固定 random / numpy 种子并写入环境变量 PYTHONHASHSEED（子进程可见）。返回 seed。"""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    return seed


def save_table(df: Any, name: str, *, folder: Path = RESULTS, index: bool = False) -> Path:
    """DataFrame → UTF-8 CSV。name 可含子目录。返回写入路径。"""
    out = folder / name
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=index, encoding="utf-8", lineterminator="\n")
    return out


def save_json(obj: Any, name: str, *, folder: Path = RESULTS) -> Path:
    out = folder / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")
    return out


def load_json(name: str, *, folder: Path = RESULTS) -> Any:
    return json.loads((folder / name).read_text(encoding="utf-8"))


def load_clean(name: str, **kw: Any):
    """读取 data/clean/<name>（csv / parquet），返回 DataFrame。"""
    import pandas as pd
    p = DATA_CLEAN / name
    if p.suffix.lower() == ".parquet":
        return pd.read_parquet(p, **kw)
    kw.setdefault("encoding", "utf-8")
    return pd.read_csv(p, **kw)


def load_raw(name: str, **kw: Any):
    """读取 data/raw/<name>（csv / xlsx / xls）。只读，不要写回 data/raw/。"""
    import pandas as pd
    p = DATA_RAW / name
    if p.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        return pd.read_excel(p, **kw)
    if "encoding" not in kw:
        for enc in ("utf-8", "utf-8-sig", "gb18030"):
            try:
                return pd.read_csv(p, encoding=enc, **kw)
            except UnicodeDecodeError:
                continue
    return pd.read_csv(p, **kw)


def _json_default(o: Any) -> Any:
    try:
        import numpy as np
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    if isinstance(o, Path):
        return o.as_posix()
    raise TypeError(f"无法序列化 {type(o).__name__}")


def banner(title: str) -> None:
    print(f"\n==== {title} ====", flush=True)
