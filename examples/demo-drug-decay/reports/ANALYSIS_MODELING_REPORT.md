# ANALYSIS_MODELING_REPORT — 赛题分析与建模设计

> 题面：`problem/statement.md`；附件：`problem/attachments.md`。本报告是代码实现（`code/`）与论文模型章节的共同依据；公式编号 (1)–(9) 在代码 docstring 与 `paper/sections/` 中引用。
> 演示项目：数据为合成，治疗窗 3–12 mg/L 为假想设定，任何结论都不是临床建议。

## 1. 问题拆解

| 子问题 | 要回答什么 | 输入 | 输出 | 主要方法 |
| --- | --- | --- | --- | --- |
| Q1 参数估计 | 一室口服模型能否刻画数据；参数及其不确定性；拟合优度与预测能力 | `data/clean/pk_clean.csv`（use_for_fit 行） | 个体与合并参数 (A, ka, ke) 及 se / 95% CI；派生量 t1/2、Tmax、Cmax、AUC；RMSE、R²、留一 RMSE；置信带 | 非线性最小二乘 (`scipy.optimize.curve_fit`)；delta 法；留一交叉验证 |
| Q2 方案比较 | R1–R4 的稳态峰/谷/波动/达稳时间；哪些方案全程在窗内；推荐哪个 | Q1 合并参数；四种方案 (dose, τ) | 每方案 css_max、css_min、PTF、蓄积比、t90；窗内判定；推荐方案 | 线性叠加原理；稳态解析式；网格积分判定 |
| Q3 稳健性 | 参数不确定性与个体差异对 Q2 结论的影响 | Q1 参数与协方差；个体参数；清洗前后数据 | 局部灵敏度（±10%、±20%）；Monte Carlo 达标概率；个体复算；清洗影响 | 单因素扰动；多元正态抽样（seed=42, n=2000）；对照拟合 |

三个子问题串联：Q1 的 (A, ka, ke) 是 Q2、Q3 的唯一输入，Q3 反过来说明 Q2 推荐的可信度。

## 2. 数据理解（详见 `DATA_REPORT.md`）

- 3 名受试者 × 12 个时刻（0.25–24 h）共 36 行，时间网格一致。
- 三处瑕疵：S02 6 h 缺失；S01 3 h 24.04 mg/L（约为邻点 2.5 倍，明显离群）；S03 24 h 为 -0.12 mg/L（负值，物理不可能）。
- 有效点 33 个，每人 11 个，足以估计 3 个参数（每人自由度 8）。
- 采样在吸收相（0.25–2 h）有 5 个点、消除相（4–24 h）有 6 个点，ka 与 ke 均可识别；末端 24 h 浓度约 0.35–0.40 mg/L，对 ke 的约束较强。

## 3. 模型假设

| 编号 | 假设 | 用途 | 风险 |
| --- | --- | --- | --- |
| H1 | 一室开放模型，药物在体内瞬时均匀分布 | 决定式 (1) 的形式 | 若存在分布相（二室），消除相早期会呈双指数；用残差趋势检查 |
| H2 | 一级吸收、一级消除，速率常数 ka、ke 与剂量无关（线性药动学） | 式 (1)；叠加原理 (4) | 非线性（饱和）代谢时 Q2 的叠加失效 |
| H3 | 无滞后时间（tlag = 0），t = 0 时浓度为 0 | 式 (1) 少一个参数 | 0.25 h 已测到 ~3 mg/L，滞后可忽略 |
| H4 | 生物利用度 F 与分布容积 V 不可分离，只估计幅值 A = F·D·ka/(V(ka−ke)) | 参数可识别 | 只给 500 mg 一种剂量，F/V 不可分是结构性限制 |
| H5 | 测量误差独立、近似同方差（普通最小二乘） | curve_fit 的 pcov 有效 | 高浓度点误差可能更大（比例误差）；灵敏度分析中用 Monte Carlo 覆盖 |
| H6 | 受试者间仅参数不同，结构相同；合并拟合的 pcov 同时吸收测量误差与个体差异 | 合并拟合作为“群体典型值” | 3 人样本太小，不做混合效应模型，个体差异用 Q3 个体复算体现 |
| H7 | 多次给药时每次剂量的药动学行为相同，剂量按时刻准确给予 | 式 (4)、(5) | 服药依从性不在本题范围 |
| H8 | 治疗窗 [3, 12] mg/L 为题给（假想）常数 | Q2 判据 | 演示设定，不是临床值 |

## 4. 符号

| 符号 | 含义 | 单位 |
| --- | --- | --- |
| t | 给药后时间 | h |
| C(t) | 血药浓度 | mg/L |
| D | 单次剂量（参考 500 mg） | mg |
| ka, ke | 一级吸收 / 消除速率常数 | 1/h |
| A | 幅值参数，A = F·D·ka / (V(ka − ke)) | mg/L |
| t1/2 | 消除半衰期 = ln2 / ke | h |
| Tmax, Cmax | 单剂量达峰时间与峰浓度 | h, mg/L |
| AUC | 单剂量浓度–时间曲线下面积 (0, ∞) | mg·h/L |
| τ | 给药间隔 | h |
| Css,max, Css,min | 稳态峰 / 谷浓度 | mg/L |
| Css,avg | 稳态平均浓度 = AUC / τ | mg/L |
| PTF | 峰谷波动 = (Css,max − Css,min) / Css,avg | — |
| Rac | 蓄积比 = 1 / (1 − e^{−ke τ}) | — |
| t90 | 达到 90% 稳态所需时间 = ln10 / ke | h |
| [L, U] | 治疗窗 [3, 12] | mg/L |

## 5. 模型

### 5.1 Q1：单剂量 Bateman 模型

$$C(t) = A\left(e^{-k_e t} - e^{-k_a t}\right), \quad A = \frac{F D k_a}{V (k_a - k_e)} \tag{1}$$

参数 θ = (A, ka, ke) 由加权最小二乘（等权）估计：

$$\hat\theta = \arg\min_{\theta \ge 0} \sum_{i} \left[y_i - C(t_i;\theta)\right]^2 \tag{2}$$

初值：ke0 由末端 4 点 ln C 的斜率给出（截断到 [0.02, 2]）；ka0 = 5·ke0；A0 由峰值点反解 A = y_max / (e^{-ke0 t} − e^{-ka0 t})。约束 θ ≥ 0（`bounds=(0, inf)`）。要求 ka > ke（否则 A 变号）；拟合后检查。

派生量（式 (3)）：

$$t_{1/2} = \frac{\ln 2}{k_e},\quad T_{max} = \frac{\ln(k_a/k_e)}{k_a - k_e},\quad C_{max} = C(T_{max}),\quad AUC_{0\to\infty} = A\left(\frac1{k_e} - \frac1{k_a}\right) \tag{3}$$

不确定性：se 来自 curve_fit 的协方差 pcov（残差方差按 n−3 自由度校正）；95% CI 用 t(n−3) 分位数；派生量与拟合曲线的 se 用 delta 法 Var(g) = ∇gᵀ · pcov · ∇g（数值梯度）。

拟合优度：RMSE、R²、AIC；预测能力：留一交叉验证 RMSE（LOO-RMSE，每次留一个点重新拟合）。

拟合分两层：每个受试者单独拟合（个体参数）；三人有效点合并拟合（群体典型值，供 Q2 使用）。

### 5.2 Q2：多次给药

线性叠加（H2、H7）：每 τ 小时给 D，第 n 次给药后

$$C_n(t) = \sum_{j=0}^{n-1} C_1(t - j\tau)\,\mathbb 1[t \ge j\tau] \tag{4}$$

稳态解析式（0 ≤ t' < τ 为剂量间隔内时间）：

$$C_{ss}(t') = A\left(\frac{e^{-k_e t'}}{1 - e^{-k_e \tau}} - \frac{e^{-k_a t'}}{1 - e^{-k_a \tau}}\right) \tag{5}$$

由 (5) 在 t' ∈ [0, τ) 上取极值得 Css,max、Css,min；Css,avg = AUC_D / τ（AUC_D 由 (3) 按剂量线性缩放）；PTF、Rac、t90 见符号表。

判据：方案“在窗内”当且仅当 Css,min ≥ L 且 Css,max ≤ U；并报告稳态一个间隔内浓度落在窗内的时间占比 frac_in_window。推荐规则：在窗内方案中取 PTF 最小者；若无方案在窗内，取 frac_in_window 最高者并说明未达标。

### 5.3 Q3：稳健性

- **局部灵敏度**：对合并参数 A、ka、ke 逐个 ±10%、±20%，重算 R1–R4 的 Css,max/Css,min 与窗内判定；弹性 E = (ΔCss,min/Css,min) / (Δp/p)。
- **Monte Carlo**：从 N(θ̂, pcov) 抽样（seed=42），剔除 A ≤ 0、ke ≤ 0 或 ka ≤ ke 的样本后取前 2000 组，对每个方案计算 Css,max、Css,min 的 2.5%/50%/97.5% 分位与窗内概率 P_in。
- **个体复算**：用 S01–S03 的个体参数分别重算四方案，检查推荐是否对每个个体都成立。
- **清洗影响**：用“未清洗（只去缺失）”数据重新做合并拟合，对比参数与 RMSE 变化，说明清洗的必要性。

## 6. 求解策略与代码映射

| 步骤 | 脚本 | 输出 |
| --- | --- | --- |
| 清洗与标记 | `code/00_data_prep.py` | `data/clean/pk_clean.csv`、`results/data_quality*.{json,csv}` |
| Q1 拟合 | `code/10_q1_fit_bateman.py` | `results/q1_fit_params.csv`、`q1_metrics.csv`、`q1_fitted.csv`、`q1_curve.csv`、`q1_summary.json` |
| Q2 模拟 | `code/20_q2_dosing_sim.py` | `results/q2_profiles.csv`、`q2_regimens.csv`、`q2_summary.json` |
| Q3 稳健性 | `code/30_sensitivity.py` | `results/q3_sens_local.csv`、`q3_sens_mc.csv`、`q3_individual.csv`、`q3_cleaning_effect.csv`、`q3_summary.json` |
| 图 | `figures/fig02_q1_fit`、`fig03_q2_regimens`、`fig04_sensitivity` | 数据图；`fig01_roadmap` 为技术路线图草稿 |

运行：`python run_all.py`（全部）或 `python run_all.py code`。所有随机性只在 Q3 Monte Carlo（seed=42）。

## 7. 决策与风险

| 决策 | 备选 | 理由 |
| --- | --- | --- |
| 不估计 tlag | 带滞后的四参数模型 | 0.25 h 已有明显浓度，且 11 点估 4 参数不稳 |
| 不做非线性混合效应（NLME） | nlmixr / 两阶段法 | 3 人样本；合并拟合 + 个体复算已足以展示个体差异 |
| 稀疏离群用 MAD 稳健 z 标记而不删行 | 直接删除 / Grubbs 检验 | 保留可追溯性；MAD 对小样本更稳健 |
| 推荐规则取 PTF 最小 | 取 Css,avg 最接近窗中心 | 窗内波动小更符合“平稳”目标；两种规则在本数据下结论相同（仅 R2 在窗内） |

风险：治疗窗为假想值——所有“推荐”均限定在演示语境；合并 pcov 混合了个体差异与测量误差，Monte Carlo 区间应解读为“群体典型值的不确定性”，不是个体预测区间。
