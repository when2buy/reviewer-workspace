# QF-Bench PR Review — Complete Summary

**Date:** 2026-04-23 | **Reviewed:** 105 PRs (excluding #4 mega-PR and #145 docs-only)
**Total:** ✅ 建议Merge: 83 | ❌ 不建议Merge: 35 | 🟡 需要Human Review: 20

> **2026-04-27 update:** Completed S4.5+O4.6 三模型 deep review of 17 tasks. 14→✅ Merge, 3→🟡 Human Review. Moved #174,#176 from ❌→✅; #172,#164 from 🟡→✅; #169 from ✅→🟡.

> **2026-04-26 PQCat re-test:** Promoted #119, #125, #172 from 🟡 Human Review → ✅ Merge after fresh Haiku/Sonnet/Opus runs (all H:O:S = 1:1:1). Also added **PR #211** (Docker SHA-pin fix for #119 — *must be merged before #119*). See `HUMAN-REVIEW-SUMMARY.md` for full re-test details and the Corrado-formula concern that may move #88 from ✅ Merge → 🟡 in a future update.

> **2026-04-26 update:** Added 17 Haiku-pass tasks from PR#180-209 to ✅ Merge. Added 3 tasks needing human review (convention/parameterization issues). 3 tasks (var-es-estimation, smith-tail-index, creditrisk-plus-model) pending Sonnet/Opus trials.

---

## ✅ 建议 Merge (55)

| PR | Task | Author | H:O:S | 备注 | Final Approval |
|---|---|---|---|---|---|
| #38 | zero-coupon-bootstrapping | Dongzhikang | 1:1:1 | 正确，无区分度 | |
| #39 | corporate-action-adjustment | Dongzhikang | 1:1:1 | 正确，无区分度 | ✅ |
| #40 | earnings-surprise-calculator | Dongzhikang | 1:1:1 | 过于简单 | |
| #41 | interest-rate-cap-floor | Dongzhikang | 0:1:1 | ⭐ fixing-time convention 真正quant难度 | ✅ |
| #42 | pca-factor-portfolio | Dongzhikang | 1:1:1 | 建议改 hard→medium | |
| #51 | binance-btc-participation-tca | Runder-sun | N/A | 设计优秀，修 Docker sha256 | ✅ |
| #52 | ust-carry-roll-down-attribution | Runder-sun | 0:1:1 | 好区分度 | |
| #62 | cross-sectional-momentum | Dongzhikang | 1:1:1 | 建议改 hard→medium | ✅ |
| #63 | markowitz-efficient-frontier | Dongzhikang | 0:1:0 | ⭐ ERC portfolio 区分度好 | |
| #80 | credit-migration-matrix | pangjacque | 1:1:0→1:1:1 | Updated per reviewer feedback, S4.6+H4.5 63/63 | ✅ |
| #84 | cme-hdd-option-pricing | xinlan-technology | 0:1:1 | 好设计 | |
| #87 | yield-curve-bootstrap-immunization | harvenstar | 0:1:1 | 优秀多步固收 task | ✅ |
| #93 | yield-curve-pca-dynamics | wshi83 | 1:1:0 | 好 PCA task | |
| #96 | credit-spread-decomposition | wshi83 | 0:1:1 | 优秀信用分析 | ✅ |
| #98 | nelson-siegel-yield-curve-fit | wshi83 | 应该是easy outlier count window 太紧 | |
| #101 | sec-8k-event-alpha | boqiny | 0.96:1:0.54 | ⭐ 优秀区分度，partial credit | ✅ |
| #102 | intraday-volume-fitting | liup3424 | 0:1:1 | 好校准 | |
| #103 | fx-carry-forward-hedge | Jingyi-Jia | 30/36:30/36:30/36 | **2026-04-26 PQCat re-test: H/S/O all 30/36 with identical 3 universal failures (schema/convention issues, not methodology):** (1) **JSON output keys not pinned** — instruction says "structure like `{...}`" with placeholder syntax, but verifier expects specific keys (`t_base`, `swap_points`, `case_id`) that aren't named in the prose bullet list; (2) **`carry_signals.csv` row-filtering unclear** — instruction says "daily" + "monthly portfolio formation"; agents output all 2247 daily rows, test expects 1900–2100 (reference drops leading rows where some currencies have no forward-filled deposits); (3) **implied-yield bid/offer combination not pinned** — instruction says "correct bid/offer combination" without specifying which side of F/S/r_USD goes into bid vs offer (multiple defensible dealer conventions). Each agent additionally has 3 idiosyncratic failures on different currency pairs. Task content is excellent (one of the highest-quality FX desk tasks in the bench — 5-part dealer-style mechanics with NDF, GK, hedge Greeks); needs schema + convention pins before fair grading. | 🟡 |
| #105 | yield-curve-bond-immunization | Jingyi-Jia | KRD key format bug |
| #107 | realized-vol-estimators | yyu56253 | New test: Sonnet 108/141 + Opus 141/141 | 公式未在 instruction 说明 需要改instruction, 应该是easy; **2026-04-26 PQCat re-test: Sonnet 108/141 (BR + BNS variants off), Opus PERFECT 141/141.** Cites Bandi-Russell (2006) Section 3.1 + BNS (2004) Definition 1 — both **post-1994 references** (after Dupire local-vol). These are real but relatively-recent papers; not as universally trained as classical (BS, Black-76) formulas, so this task **also tests how well the agent has learned post-Dupire-era HF-econometrics literature**. Agents who internalized these papers in training pass; those who reconstruct from memory pick variant forms and fail. | ✅ |
| #108 | delta-hedging-pnl-simulation | yyu56253 | 0:1:1 | 干净衍生品 task | |
| #109 | variance-swap-replication | yyu56253 | 1:1:1 | Carr-Madan 正确 | ✅ |
| #110 | evt-pot-var | boqiny | 0.71:1:0.92 | ⭐ 全面尾部风险，partial credit | |
| #111 | historical-var-data-prep | YoutingWang | 1:1:1 | 干净，标 easy 诚实 | ✅ |
| #112 | ewma-portfolio-risk-decomposition | YoutingWang | 0:1:1 | ⭐ 优秀 debug task，verifier 重算 | |
| #114 | brinson-sector-attribution | boqiny | 0:1:0 | Reviewer-iterated, full BF framework with drift+rebalance, 3-tier discrimination | ✅ |
| #117 | credit-portfolio-var-cvar | pangjacque | 0:1:0 | Good 3-tier discrimination. Fix: obligor count ~50→991, remove 0.8 multiplier in t-copula tail test | |
| #120b | ipca-latent-factors | GinkgoGao | 0.33:0.69:0.29 | 好区分度，partial credit | ✅ |
| #121 | alpha-hedge-strategy | GinkgoGao | 0.64:1:1 | O+S 过 H 挂 | |
| #129 | fx-forward-cross-rate | bochencs | 0:0:1 | S45 满分; **2026-04-26 PQCat re-test: H:O:S = 1:1:1, all 37/37 PERFECT** | ✅ |
| #132 | dirty-gap-momentum-aapl | Jiahao-Xie-86 | 1:1:1 | 干净无区分度 | |
| #139 | mtm-xccy-basis-desk | Jingyi-Jia | 0:0:0 → Sonnet 138/145 | **2026-04-26 PQCat re-test (Sonnet alone, solo run, 28:23): 138/145 — only 7 failures, ALL spec/convention issues, no methodology errors.** First 3 confusing parts (out of 7): (1) **`par_basis_bps` definition**: Sonnet=5.65, expected=35.65 — off by *exactly* 30bp = contractual GBP spread. Instruction doesn't pin whether `par_basis_bps` is "incremental spread above contract" or "total par-equivalent spread". (2) **`accrued_usd` sign convention**: Sonnet=+230,791.67, expected=−230,791.67 (same magnitude, opposite sign). Trader-vs-accountant sign convention divergence; instruction doesn't pin. (3) **`forward_points` output unit**: Sonnet=0.00032076 (decimal), expected=3.207644 (pips) — exact 10,000× factor. Instruction says *"forward_points_pips are pips; divide by 10000 before adding to spot"* (telling agent to use decimal **internally**) but doesn't pin what to write in the OUTPUT `forward_points` column. Sonnet's underlying math is correct; it just missed the output convention. Other 4 failures of similar shape (sort key, FRA raw vs adjusted quote semantics, par_basis cascades). Once these 3 conventions are pinned, this becomes a strong dealer-style XCCY task. | 🟡 |
| #140 | localvol-barrier | Jingyi-Jia | 0:0:0 | Hard task, Opus 27/34 but local vol off by 17-21% | |
| #141 | swap-curve-bootstrap-ois | YoutingWang | 0:1:1 | 好 debug 格式 | ✅ |
| #151 | fomc-tone-event-study | gem-mint | 0:1:0 | ⭐ NLP+固收，Opus-only | |
| #152 | american-binomial-tree | Dongzhikang | 1:1:1 | 干净无区分度 | ✅ |
| #153 | asian-option-levy-curran | Dongzhikang | 0:1:0 | 好区分度 | |
| #154 | barone-adesi-whaley | Dongzhikang | 0:1:1 | BAW 正确; **2026-04-26 PQCat re-test: H:O:S = 1:1:1, all 36/36 PERFECT.** Extended the agent timeout at harbor/docker level via `--timeout-multiplier 3.0` (600s default → 1800s) — the harbor 600s default is too short for heavy derivatives calculations on this task. Task content unchanged. | ✅ |
| #156 | bs-greeks-pde | Dongzhikang | 0:1:1 | PDE 残差优秀 | |
| #159 | cir-bond-pricing | Dongzhikang | 1:1:1 | 建议改 hard→medium | ✅ |
| #160 | cliquet-ratchet-pricing | Dongzhikang | 0:1:0 | Opus 17/17, good discrimination | |
| #161 | compound-option-geske | Dongzhikang | 0:1:0 | Pushed type label fix, parity check catches Sonnet bivariate normal error. Needs re-run | ✅ |
| #162 | digital-barrier-options | Dongzhikang | 0:1:1 | 干净 | |
| #163 | double-barrier-options | Dongzhikang | 0:1:0 | Kunitomo-Ikeda 正确 | |
| #165 | first-passage-time | Dongzhikang | 0:1:1 | 反射原理正确 | |
| #167 | geometric-mean-reverting-jd | Dongzhikang | 0:1:0 | OU+jump 正确 | ✅ |
| #168 | heston-cf-pricing | Dongzhikang | 0:1:0 | 74 tests, Opus 73/74 trivial K rounding | |
| #169 | implied-vol-approximations | Dongzhikang | 0:1:0 → 0.9:0.9:0.9 | Fixed rtol 1e-6→0.02, awaiting re-trial; **2026-04-26 PQCat re-test: H/S/O each 9/10 — different ATM method fails per agent** (Haiku & Sonnet on Brenner-Subrahmanyam, Opus on Li ATM). Cites Brenner-Subrahmanyam (1988) ATM, **Li (2005) trigonometric**, **Corrado-Miller-Hallerbach** rational approximation — Li and CMH are **post-1994** (after Dupire local-vol). Less universally taught than classical BS; this task **tests how well the agent has learned recent IV-approximation literature**. Each agent picks a different variant from training memory on different methods → empirical confirmation that training-data depth on post-1994 references varies. | ✅ |
| #170 | kou-double-exponential | Dongzhikang | 0:1:0 | Fixed boundary <→<=, awaiting re-trial | |
| #171 | lookback-options | Dongzhikang | 0:1:1 | 区分度好 | ✅ |
| #173 | ou-jump-commodity | Dongzhikang | 1:1:0 | 合理 | |
| #175 | rainbow-option-pricing | Dongzhikang | 0:0:0 | 全挂但反映真正难度; **PQCat file-level review found 2 typos in instruction that likely cause the 0:0:0**: (1) **Wrong prose payoff for call-on-min**: instruction says *"Call on minimum: max(S1_T, S2_T) − K (but prices the minimum)"* — the `max(S1, S2)` is the call-on-MAX payoff, should be `max(min(S1, S2) − K, 0)`. **Misleads agents** who try to verify via MC or who read prose before formula. (2) **Undefined `d+` in pricing formulas**: the "Define" block defines `d`, `d1+`, `d1-`, `d2+`, `d2-`, but the C_max/C_min formulas use `d+` (which is not defined; should be `d` per Stulz 1982 standard notation). **Forces agents to think too long / guess** what `d+` means — different agents pick different reasonable interpretations (`d`, `d + σ√τ`, `d + σ²τ/2`, etc.) and produce different numbers. With 3 independent agents, P(all guess correctly) is small → empirically observed 0:0:0. Both typos are trivial 1-line fixes; once corrected, this is a strong rainbow-options task with closed-form Stulz-Johnson formulas + decomposition identity sanity check. | 🟡 |
| #177 | spread-option-kirk-margrabe | Dongzhikang | 0:1:1 | ⭐ 设计优秀 | |
| #178 | variance-swap-pricing | Dongzhikang | 1:0:1 | Opus 失败合理; **2026-04-26 PQCat re-test (Opus): 36/37 — single failure on `test_parameters_in_reasonable_range` with `kappa=50.0`** (test asserts `kappa ≤ 20`). Methodology valid: model-free Carr-Madan replication formula and Heston closed-form `K_var = θT + (v_0−θ)/κ·(1−e^{−κT})` both explicitly written. **Spec ambiguity (the failure cause)**: Step 4 instruction allows EITHER "use default Heston parameters as initial guess: kappa=2.0, theta=0.04, v0=0.02" OR "fit the three parameters to minimize squared error" — but doesn't specify **fit constraints**. Opus chose to fit and converged to kappa=50 (a valid local optimum given SPY's term structure but outside the test's "typical range" check). The test asserts `0.01 < kappa ≤ 20.0` without telling the agent. **Fix**: instruction should pin bounds on the fit, e.g. *"fit with `kappa ∈ [0.01, 20]`, `theta ∈ [0.0001, 1]`, `v0 ∈ [0.0001, 1]`"*, or specify a regularized calibration (e.g. estimate θ from long-end then fit κ, v0 to short-end). Also recommended: pin extrapolation strategy for deep-OTM strikes ("set option price to zero outside the available strike range"). Once fit-constraints are pinned, Opus would pass and #178 becomes solid (complementary to #109 — practitioner cleaning vs theoretical Heston comparison). **Once this is fixed, this is a good test.** | 🟡 |
| #179 | sma-crossover-spy | PQCat | 1:1:1 | Fix PR，干净 | ✅ |
| --- | --- *PQCat 2026-04-26 re-test additions (appended below)* | --- | --- | --- | --- |
| #119 | option-put-call-parity-forward-audit | Runder-sun | 1:1:1 | (PQCat 2026-04-26 re-test) Docker SHA-pin fix only, content untouched; H/S/O all pass 5/5; PCP arb on bid-ask, no other task covers this | |
| #125 | bl-regime-hmm | GinkgoGao | 1:1:1 | (PQCat 2026-04-26 re-test) All 3 PERFECT after `bl: changeV2`; only Baum-Welch HMM task in entire bench | |
| #172 | merton-jump-diffusion | Dongzhikang | 1:1:1 | (PQCat 2026-04-26 re-test) All 3 pass 28/28, bit-identical MLE; only Merton 1976 jump-diffusion task | |
| **#211** | **(Docker fix for #119)** | **PQCat** | **1:1:1*** | **(PQCat 2026-04-26) Removes obsolete `sha256:709847...` SHA pin from #119's Dockerfile — purely infrastructure, no instruction/solution edits.** ⚠️ **Must be merged BEFORE #119**: #119 cannot build on any machine other than the original author's until this lands. H/S/O 1:1:1 reflects post-fix runs on the merged `feat/human_review_beta` branch. | |

### ✅ 新增 PR#180-209 — Haiku 满分 (2026-04-26 added)

| PR | Task | Author | H:O:S | 备注 | Final Approval |
|---|---|---|---|---|---|
| #185 | gaussian-copula-credit | Dongzhikang | 1:?:? | ✅ Haiku 34/34 满分 | |
| #187 | delta-gamma-option-var | Dongzhikang | 1:?:? | ✅ Haiku 23/23 满分 | |
| #188 | vasicek-portfolio-credit | Dongzhikang | 1:?:? | ✅ Haiku 24/24 满分 | |
| #189 | geometric-spacings-test | Dongzhikang | 1:?:? | ✅ Haiku 29/29 满分 | |
| #190 | ewma-correlation-sensitivity | Dongzhikang | 1:?:? | ✅ Haiku 22/22 满分 | |
| #191 | rolling-correlation-indices | Dongzhikang | 1:?:? | ✅ Haiku 24/24 满分 | |
| #192 | pca-equity-returns | Dongzhikang | 1:?:? | ✅ Haiku 37/37 满分 | |
| #194 | var-es-coherence | Dongzhikang | 1:?:? | ✅ Haiku 49/49 满分 | |
| #197 | one-factor-equity-model | Dongzhikang | 1:?:? | ✅ Haiku 32/32 满分 | |
| #198 | ljung-box-serial-dependence | Dongzhikang | 1:?:? | ✅ Haiku 27/27 满分 | |
| #199 | single-loss-approximation | Dongzhikang | 1:?:? | ✅ Haiku 24/24 满分 | |
| #200 | merton-structural-credit | Dongzhikang | 1:?:? | ✅ Haiku 21/21 满分 | |
| #202 | intensity-credit-model | Dongzhikang | 1:?:? | ✅ Haiku 35/35 满分 | |
| #203 | block-maxima-gev | Dongzhikang | 1:?:? | ✅ Haiku 16/16 满分 | |
| #206 | gh-distribution-fitting | Dongzhikang | 1:?:? | ✅ Haiku 43/43 满分 | |
| #207 | jarque-bera-normality-test | Dongzhikang | 1:?:? | ✅ Haiku 36/36 满分 | |
| #209 | weekly-garch-vol-proxy | Dongzhikang | 1:?:? | ✅ Haiku 35/35 满分 | |

### ✅ 三模型深度 Review 确认 Merge (2026-04-27 added)

> 以下 14 tasks 经 Haiku 4.5 + Sonnet 4.5 + Opus 4.6 三模型 trial 验证，确认为好 benchmark item。Failures 均为 agent 能力差异，非 task/oracle 问题。

| PR | Task | Author | H:S:O | 备注 | Final Approval |
|---|---|---|---|---|---|
| #180 | smith-tail-index | Dongzhikang | TO:33/33:33/33 | S/O 满分，Haiku timeout。新 task | |
| #181 | copula-equity-fitting | Dongzhikang | 27/28:28/28:28/28 | S/O 满分，Haiku nu 收敛差 1。新 task | |
| #184 | fft-compound-poisson | Dongzhikang | 14/18:14/18:18/18 | Opus-only 满分，连 S/H 都区分。新 task | |
| #193 | creditmetrics-portfolio-var | Dongzhikang | 25/26:26/26:26/26 | S/O 满分。新 task | |
| #195 | standard-var-methods | Dongzhikang | 22/25:25/25:25/25 | S/O 满分。新 task | |
| #201 | copula-sampling-rank-correlation | Dongzhikang | 25/31:31/31:31/31 | Haiku Gumbel copula 实现错误，好区分度。新 task | |
| #204 | panjer-recursion | Dongzhikang | 18/22:22/22:22/22 | S/O 满分，Haiku 推导不出 (a,b)。新 task | |
| #205 | var-es-estimation | Dongzhikang | 0/47:46/47:46/47 | **极好区分度**，Haiku 完全不会。新 task | |
| #161 | compound-option-geske | Dongzhikang | 34/34:33/34:34/34 | H/O 满分，S MLE 差 1。补充 H:S:O | |
| #170 | kou-double-exponential | Dongzhikang | 12/12:11/12:12/12 | H/O 满分，S 差 1。补充 H:S:O | |
| #172 | merton-jump-diffusion | Dongzhikang | 22/22:22/22:22/22 | 三模型满分。从 🟡→✅ | |
| #174 | power-options | Dongzhikang | 33/36:36/36:36/36 | 修复后 S/O 满分。从 ❌→✅ | |
| #164 | dupire-local-vol | Dongzhikang | 62/67:65/67:0/67 | O 的 0/67 是 subagent 路径问题非 task 问题。从 🟡→✅ | |
| #176 | realized-vol-estimators | Dongzhikang | 29/33:29/33:30/33 | 三模型一致 ~30/33，agent 能力问题。从 ❌→✅ | |

## ❌ 不建议 Merge (35)

| PR | Task | Author | Blocker 类型 |
|---|---|---|---|
| #45 | heston-mc-pricing | oyzh888 | 缺 Dockerfile |
| #46 | ou-pairs-trading | oyzh888 | 缺 Dockerfile + 无 oracle |
| #47 | merton-jump-diffusion | oyzh888 | 缺 Dockerfile |
| #48 | cir-calibration | Dongzhikang | 缺 Dockerfile |
| #49 | rough-vol-rbgergomi | oyzh888 | 缺 Dockerfile + instruction 含糊 |
| #53 | equity-vendor-restatement-break-audit | Runder-sun | Spec 歧义 |
| #61 | pairs-trading-cointegration | Dongzhikang | 2 个 verifier bug |
| #64 | cta-ewma-cvar | Dongzhikang | Oracle bug (num_valid_obs) |
| #66 | portfolio-risk-attribution | Dongzhikang | Sharpe 未说明 excess vs raw |
| #72 | treasury-curve-pca-butterfly | Dongzhikang | PCA 符号 + P&L 有误 |
| #75 | var-ebacktest-coverage | Dongzhikang | e-backtest 公式缺失 |
| #77 | cds-curve-stripping | Dongzhikang | 全模型同样失败 → spec 问题 |
| #81 | lmm-markov-representation | PQCat | 关键词匹配 verifier 太脆弱 |
| #88 | event-study-earnings | harvenstar | Oracle bug (KP t-stat) |
| #89 | lob-pc-signal | owen8877 | Docker base image 错误 |
| #91 | polars-api-migration | owen8877 | Docker 错误 + 非 QF task |
| #92 | sec-10k-report-long | owen8877 | Docker base image 错误 |
| #97 | factor-momentum-spanning | wshi83 | 全挂，oracle 校准问题 |
| #99 | 13f-amendment-aware-crowding | Minxuan-Hu | Docker base image 错误 |
| #104 | form4-cross-sectional-sale-pressure | Minxuan-Hu | Docker base image 错误 |
| #106 | etf-overlap-redemption-pressure | Minxuan-Hu | Docker base image 错误 |
| #124 | pairs-cointegration-kalman | GinkgoGao | 非标准 ADF + 不合理经济学 |
| #127 | crypto-funding-rate-basis-carry | xinlan-technology | 16-32 test 失败，值硬编码 |
| #136 | quantamental-earnings-jumpfilter | xushenbo | Docker build 失败 |
| #137 | multimodal-alpha-fusion | xushenbo | 0/0/0 零区分度 |
| #144 | double-sort/residual-momentum/stable-residual | mingjun-sun | Verifier broken |
| #148 | futures-carry/insider-buy/post-earnings | judy12345 | Docker image broken |
| #149 | liquidity-var-backtest | gem-mint | Verifier broken |
| #155 | barrier-gbm-analytics | Dongzhikang | test_mean_fpt_down crash |
| #157 | cev-option-pricing | Dongzhikang | Oracle 值有误 (β=0.9) |
| #158 | chooser-option-pricing | Dongzhikang | Oracle discount factor bug |

| #174 | ~~power-options~~ | ~~Dongzhikang~~ | ~~Moved to ✅ (2026-04-27)~~ |
| #176 | ~~realized-vol-estimators~~ | ~~Dongzhikang~~ | ~~Moved to ✅ (2026-04-27)~~ |

## 🟡 需要 Human Review (20)

| PR | Task | Author | 原因 |
|---|---|---|---|
| #28 | data-cleaning | oyzh888 | 太简单，test 自引用 |
| #65 | bond-portfolio-analytics | Dongzhikang | Trial 旧版需重跑 |
| #76 | fama-macbeth-risk-premia | Dongzhikang | Opus 59/60，GRS 容差 |
| #78 | fx-carry-trade-backtest | Dongzhikang | Opus 差 1 test |
| #79 | execution-is-vwap | Dongzhikang | Sonnet 差 1 test |
| #95 | fixed-income-market-stress | wshi83 | 区分度反转 |
| #100 | minimum-cost-equity-etf-hedger | liup3424 | 全过零区分度 |
| #164 | ~~dupire-local-vol~~ | ~~Dongzhikang~~ | ~~Moved to ✅ (2026-04-27)~~ |
| #118 | perpetual-funding-ledger-reconciliation | Runder-sun | 硬编码风险，无 trial |
| #120a | barra-cne6-risk | GinkgoGao | 所有模型 ≤0.31 |
| #126 | merton-cds-copula | GinkgoGao | 全部 0.9，差 1 checkpoint |
| #128 | etf-cross-asset-lead-lag | xinlan-technology | 全有全无计分浪费区分度 |
| #131 | garch-vecm-cointegration | bochencs | 区分度反转 |
| #150 | earnings-news-event-alpha | gem-mint | 0/0/0 零区分度 |
### 🟡 新增 PR#180-209 — Convention/Parameterization 歧义 (2026-04-26 added)

| PR | Task | Author | 原因 |
|---|---|---|---|
| #183 | pca-yield-curve | Dongzhikang | Haiku 22/26, PCA eigenvector sign convention 歧义，test pin exact VaR 值 |
| #186 | pot-gpd-bitcoin | Dongzhikang | Haiku 25/46, GPD shape xi 符号: scipy genpareto c = -xi convention 未在 instruction 说明 |
| #208 | garch-sp500-fit | Dongzhikang | Haiku 33/47, GARCH-t parameterization: 不同库的 Student-t nu 定义不同，instruction 未指定库 |

### 🟡 三模型深度 Review — Oracle/Tolerance 疑问 (2026-04-27 added)

> 以下 3 tasks 经三模型验证后发现 oracle 精度或约定可能有问题。

| PR | Task | Author | H:S:O | 原因 |
|---|---|---|---|---|
| #196 | copula-garch-portfolio | Dongzhikang | 35/38:35/38:37/38 | `test_gs_alpha_value` 三模型全挂，oracle alpha≈0.073 vs agent 0.10-0.12，tolerance 可能太紧 |
| #182 | creditrisk-plus-model | Dongzhikang | TO:25/30:25/30 | S4.5/O4.6 VaR **完全一致** (5.9/7.7/10.2) 但与 oracle (6.5/9.0/12.6) 系统偏差，Panjer 离散化约定疑问 |
| #169 | implied-vol-approximations | Dongzhikang | 9/10:9/10:TO | 三模型都 fail 同一个 RMSE tolerance test，公式变体或 tolerance 问题。从 ✅→🟡 |

---

## Blocker 模式分析

| 模式 | 数量 | 涉及 PR |
|---|---|---|
| **Docker/基础设施问题** | 13 | #45,46,47,48,49,89,91,92,99,104,106,136,148 |
| **Oracle/Verifier bug** | 10 | #61,64,88,97,98,103,105,155,157,170 |
| **Instruction under-specification** | 8 | #53,66,72,75,77,107,169,174 |
| **答案泄露/硬编码** | 4 | #127,137,169 |
| **设计问题** | 5 | #81,124,125,176 |
| **零区分度（需重新评估）** | 2 | #91,149 |

## 按作者统计

| Author | Total | ✅ | ❌ | 🟡 | Merge率 |
|---|---|---|---|---|---|
| Dongzhikang | 45 | 21 | 16 | 8 | 47% |
| GinkgoGao | 6 | 2 | 2 | 2 | 33% |
| oyzh888 | 5 | 0 | 4 | 1 | 0% |
| wshi83 | 5 | 2 | 2 | 1 | 40% |
| Runder-sun | 5 | 1 | 1 | 3 | 20% |
| YoutingWang | 4 | 3 | 0 | 1 | 75% |
| boqiny | 3 | 2 | 0 | 1 | 67% |
| yyu56253 | 3 | 2 | 1 | 0 | 67% |
| Minxuan-Hu | 3 | 0 | 3 | 0 | 0% |
| owen8877 | 3 | 0 | 3 | 0 | 0% |
| Jingyi-Jia | 3 | 0 | 2 | 1 | 0% |
| xinlan-technology | 3 | 1 | 1 | 1 | 33% |
| bochencs | 2 | 1 | 0 | 1 | 50% |
| liup3424 | 2 | 1 | 0 | 1 | 50% |
| gem-mint | 3 | 1 | 1 | 1 | 33% |
| pangjacque | 2 | 0 | 0 | 2 | 0% |
| Others | 5 | 3 | 1 | 1 | 60% |
