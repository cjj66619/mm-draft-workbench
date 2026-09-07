# tools/fonts/ 字体许可

- `wqy-microhei.ttc`（文泉驿微米黑，WenQuanYi Micro Hei）
  版权：© 2007-2009 Qianqian Fang and the WenQuanYi Project Board of Trustees；
  许可：Apache License 2.0 与 GPLv3（含字体嵌入例外，embedding exception）双许可。
  随项目分发的目的：保证 Windows / Linux / macOS 出图中文字形一致、PDF 可嵌入 TrueType（pdf.fonttype=42）。
  原始来源：http://wenq.org/ ；Debian 软件包 fonts-wqy-microhei。

`mm_plot_style.register_bundled_fonts()` 会在 apply_style 时自动注册本目录的 .ttf/.ttc/.otf，并优先于系统字体使用。
