# _template_figure — 数据图模板文件夹

复制整个文件夹为 `figNN_<问题>_<内容>/`（例：`fig02_q1_fit`），修改 `make_figure.py` 顶部说明与绘图代码，然后：

```text
python run_all.py figures fig02_q1_fit
```

`save_fig` 会在本文件夹生成：`figNN_xxx.pdf/.png/.svg`、`data.csv`（快照）、`README.md`（自动，含机理说明与自检结果）、`manifest.json`、`review.json`。

看图必做：打开 PNG，对照 `review.json` 里的 WARN 逐条确认；结论写进 README.md 的"人工审图"段。
