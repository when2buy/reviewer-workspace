# QF-Bench FINAL-SUMMARY clean tables (2026-05-02)
Source: reviewer-workspace `FINAL-SUMMARY.md` on `review/zhikang-full-review-2026-04-23`; live check against `QF-Bench/QuantitativeFinance-Bench` `origin/main` (`04a83d6`) and GitHub PR state.
- Main branch tasks now: **65**
- Pending ✅ merge candidates after removing already-main/outdated rows: **35**
- Pending ❌ do-not-merge rows: **24**
- Pending 🟡 human-review rows: **25**

## 1) Already merged on main
| Task |
|---|
| `13f-amendment-aware-crowding` |
| `alpha-hedge-strategy` |
| `american-option-fd-new` |
| `asian-option-levy-curran` |
| `barrier-garch-var` |
| `bl-regime-hmm` |
| `bollinger-backtest-aapl` |
| `brinson-sector-attribution` |
| `bs-greeks-pde` |
| `cliquet-ratchet-pricing` |
| `cme-hdd-option-pricing` |
| `compound-option-geske` |
| `copula-equity-fitting` |
| `copula-sampling-rank-correlation` |
| `credit-portfolio-var-cvar` |
| `credit-spread-decomposition` |
| `creditmetrics-portfolio-var` |
| `crypto-funding-rate-basis-carry` |
| `cta-basel-capital` |
| `delta-hedging-pnl-simulation` |
| `digital-barrier-options` |
| `etf-cross-asset-lead-lag` |
| `evt-pot-var` |
| `ewma-portfolio-risk-decomposition` |
| `fama-french-factor-model-new` |
| `fft-compound-poisson` |
| `first-passage-time` |
| `fomc-tone-event-study` |
| `fx-carry-forward-hedge` |
| `geometric-mean-reverting-jd` |
| `hull-white-swaption` |
| `implied-vol-approximations` |
| `interest-rate-cap-floor` |
| `intraday-volume-fitting-and-execution-scheduling` |
| `ipca-latent-factors` |
| `kelly-var-sizing` |
| `lob-pc-signal` |
| `localvol-barrier` |
| `lookback-options` |
| `mc-greek-surface-1` |
| `mc-greeks-surface` |
| `merton-jump-diffusion` |
| `momentum-backtest` |
| `mtm-xccy-basis-desk` |
| `ohlc-realized-vol-estimators` |
| `option-put-call-parity-forward-audit` |
| `ou-jump-commodity` |
| `pairs-cointegration-kalman` |
| `polars-api-migration` |
| `realized-vol-estimators` |
| `regime-cta-vol-target` |
| `regime-riskparity-cvar` |
| `sec-10k-report-long` |
| `sec-8k-event-alpha` |
| `sentiment-factor-alpha` |
| `sma-crossover-spy` |
| `smith-tail-index` |
| `spread-option-kirk-margrabe` |
| `standard-var-methods` |
| `stochvol-implied-surface-new` |
| `structured-note-risk` |
| `swap-curve-bootstrap-ois` |
| `yield-curve-bond-immunization` |
| `yield-curve-bootstrap-immunization` |
| `yield-curve-pca-dynamics` |

## 2) ✅ Clean merge candidates / not yet on main
| PR | Task | Author | Evidence/Note | PR state |
|---|---|---|---|---|
| #38 | `zero-coupon-bootstrapping` | Dongzhikang | 1:1:1; 正确，无区分度 | OPEN |
| #39 | `corporate-action-adjustment` | Dongzhikang | 1:1:1; 正确，无区分度 | OPEN |
| #40 | `earnings-surprise-calculator` | Dongzhikang | 1:1:1; 过于简单 | OPEN |
| #42 | `pca-factor-portfolio` | Dongzhikang | 1:1:1; 建议改 hard→medium | OPEN |
| #51 | `binance-btc-participation-tca` | Runder-sun | N/A; 设计优秀，修 Docker sha256 | OPEN |
| #62 | `cross-sectional-momentum` | Dongzhikang | 1:1:1; 建议改 hard→medium | OPEN |
| #80 | `credit-migration-matrix` | pangjacque | 1:1:0→1:1:1; Updated per reviewer feedback, S4.6+H4.5 63/63 | OPEN |
| #109 | `variance-swap-replication` | yyu56253 | 1:1:1; Carr-Madan 正确 | OPEN |
| #111 | `historical-var-data-prep` | YoutingWang | 1:1:1; 干净，标 easy 诚实 | OPEN |
| #129 | `fx-forward-cross-rate` | bochencs | 0:0:1; S45 满分; 2026-04-26 PQCat re-test: H:O:S = 1:1:1, all 37/37 PERFECT | OPEN |
| #152 | `american-binomial-tree` | Dongzhikang | 1:1:1; 干净无区分度 | OPEN |
| #154 | `barone-adesi-whaley` | Dongzhikang | 0:1:1; BAW 正确; 2026-04-26 PQCat re-test: H:O:S = 1:1:1, all 36/36 PERFECT. Extended the agent timeout at harbor/docker level via `--timeout-multiplier 3.0` (600s default → 1800s) — the harbor 600s default is too short fo | OPEN |
| #159 | `cir-bond-pricing` | Dongzhikang | 1:1:1; 建议改 hard→medium | OPEN |
| #163 | `double-barrier-options` | Dongzhikang | 0:1:0; Kunitomo-Ikeda 正确 | OPEN |
| #182 | `var-es-estimation` | Dongzhikang | 0/47:46/47:46/47; 极好区分度，Haiku 完全不会。新 task | OPEN |
| #183 | `pca-yield-curve` | Dongzhikang | Haiku 22/26, PCA eigenvector sign convention 歧义，test pin exact VaR 值; ✅ Root cause confirmed. Added 1 sentence to the `eigenvalues.csv` output schema in `instruction.md`: "`var_explained` and `cumulative_var_explained` a | OPEN |
| #185 | `gaussian-copula-credit` | Dongzhikang | 1:?:?; ✅ Haiku 34/34 满分 | OPEN |
| #186 | `pot-gpd-bitcoin` | Dongzhikang | Haiku 25/46, GPD shape xi 符号: scipy genpareto c = -xi convention 未在 instruction 说明; ✅ scipy sign concern does not hold. Task formula is correct, no changes needed. Note: the concern originated from R's `ismev` package (S | OPEN |
| #187 | `delta-gamma-option-var` | Dongzhikang | 1:?:?; ✅ Haiku 23/23 满分 | OPEN |
| #188 | `vasicek-portfolio-credit` | Dongzhikang | 1:?:?; ✅ Haiku 24/24 满分 | OPEN |
| #189 | `geometric-spacings-test` | Dongzhikang | 1:?:?; ✅ Haiku 29/29 满分 | OPEN |
| #190 | `ewma-correlation-sensitivity` | Dongzhikang | 1:?:?; ✅ Haiku 22/22 满分 | OPEN |
| #191 | `rolling-correlation-indices` | Dongzhikang | 1:?:?; ✅ Haiku 24/24 满分 | OPEN |
| #192 | `pca-equity-returns` | Dongzhikang | 1:?:?; ✅ Haiku 37/37 满分 | OPEN |
| #194 | `var-es-coherence` | Dongzhikang | 1:?:?; ✅ Haiku 49/49 满分 | OPEN |
| #195 | `creditrisk-plus-model` | Dongzhikang | TO:25/30:25/30; S4.5/O4.6 VaR 完全一致 (5.9/7.7/10.2) 但与 oracle (6.5/9.0/12.6) 系统偏差，Panjer 离散化约定疑问 | OPEN |
| #197 | `one-factor-equity-model` | Dongzhikang | 1:?:?; ✅ Haiku 32/32 满分 | OPEN |
| #198 | `ljung-box-serial-dependence` | Dongzhikang | 1:?:?; ✅ Haiku 27/27 满分 | OPEN |
| #199 | `single-loss-approximation` | Dongzhikang | 1:?:?; ✅ Haiku 24/24 满分 | OPEN |
| #200 | `merton-structural-credit` | Dongzhikang | 1:?:?; ✅ Haiku 21/21 满分 | OPEN |
| #202 | `intensity-credit-model` | Dongzhikang | 1:?:?; ✅ Haiku 35/35 满分 | OPEN |
| #203 | `block-maxima-gev` | Dongzhikang | 1:?:?; ✅ Haiku 16/16 满分 | OPEN |
| #206 | `gh-distribution-fitting` | Dongzhikang | 1:?:?; ✅ Haiku 43/43 满分 | OPEN |
| #207 | `jarque-bera-normality-test` | Dongzhikang | 1:?:?; ✅ Haiku 36/36 满分 | OPEN |
| #209 | `weekly-garch-vol-proxy` | Dongzhikang | 1:?:?; ✅ Haiku 35/35 满分 | OPEN |

## 3) ❌ Clean do-not-merge / blockers
| PR | Task | Author | Blocker | PR state |
|---|---|---|---|---|
| #45 | `heston-mc-pricing` | oyzh888 | 缺 Dockerfile | OPEN |
| #46 | `ou-pairs-trading` | oyzh888 | 缺 Dockerfile + 无 oracle | OPEN |
| #48 | `cir-calibration` | Dongzhikang | 缺 Dockerfile | OPEN |
| #49 | `rough-vol-rbgergomi` | oyzh888 | 缺 Dockerfile + instruction 含糊 | OPEN |
| #53 | `equity-vendor-restatement-break-audit` | Runder-sun | Spec 歧义 | CLOSED |
| #61 | `pairs-trading-cointegration` | Dongzhikang | 2 个 verifier bug | OPEN |
| #64 | `cta-ewma-cvar` | Dongzhikang | Oracle bug (num_valid_obs) | OPEN |
| #66 | `portfolio-risk-attribution` | Dongzhikang | Sharpe 未说明 excess vs raw | OPEN |
| #72 | `treasury-curve-pca-butterfly` | Dongzhikang | PCA 符号 + P&L 有误 | OPEN |
| #75 | `var-ebacktest-coverage` | Dongzhikang | e-backtest 公式缺失 | OPEN |
| #77 | `cds-curve-stripping` | Dongzhikang | 全模型同样失败 → spec 问题 | OPEN |
| #81 | `lmm-markov-representation` | PQCat | 关键词匹配 verifier 太脆弱 | OPEN |
| #88 | `event-study-earnings` | harvenstar | Oracle bug (KP t-stat) | OPEN |
| #97 | `factor-momentum-spanning` | wshi83 | 全挂，oracle 校准问题 | OPEN |
| #104 | `form4-cross-sectional-sale-pressure` | Minxuan-Hu | Docker base image 错误 | OPEN |
| #106 | `etf-overlap-redemption-pressure` | Minxuan-Hu | Docker base image 错误 | OPEN |
| #136 | `quantamental-earnings-jumpfilter` | xushenbo | Docker build 失败 | OPEN |
| #137 | `multimodal-alpha-fusion` | xushenbo | 0/0/0 零区分度 | OPEN |
| #144 | `double-sort/residual-momentum/stable-residual` | mingjun-sun | Verifier broken | OPEN |
| #148 | `futures-carry/insider-buy/post-earnings` | judy12345 | Docker image broken | OPEN |
| #149 | `liquidity-var-backtest` | gem-mint | Verifier broken | OPEN |
| #155 | `barrier-gbm-analytics` | Dongzhikang | test_mean_fpt_down crash | OPEN |
| #157 | `cev-option-pricing` | Dongzhikang | Oracle 值有误 (β=0.9) | OPEN |
| #158 | `chooser-option-pricing` | Dongzhikang | Oracle discount factor bug | OPEN |

## 4) 🟡 Clean human-review / fix-before-merge
| PR | Task | Author | Reason | PR state |
|---|---|---|---|---|
| #28 | `data-cleaning` | oyzh888 | 太简单，test 自引用 | OPEN |
| #52 | `ust-carry-roll-down-attribution` | Runder-sun | 0:1:1; 好像还没有finish？ It says This PR remains in draft while validation evidence is being collected. | OPEN |
| #63 | `markowitz-efficient-frontier` | Dongzhikang | 0:1:0; 很好的设计，但最新的状态是REQUEST CHANGES？好像还有bug没有来得及修完 | OPEN |
| #65 | `bond-portfolio-analytics` | Dongzhikang | Trial 旧版需重跑 | OPEN |
| #76 | `fama-macbeth-risk-premia` | Dongzhikang | Opus 59/60，GRS 容差 | OPEN |
| #78 | `fx-carry-trade-backtest` | Dongzhikang | Opus 差 1 test | OPEN |
| #79 | `execution-is-vwap` | Dongzhikang | Sonnet 差 1 test | OPEN |
| #95 | `fixed-income-market-stress` | wshi83 | 区分度反转 | OPEN |
| #98 | `nelson-siegel-yield-curve-fit` | wshi83 | 🟡看起来没问题，但缺最新的结果; 应该是easy outlier count window 太紧 | OPEN |
| #100 | `minimum-cost-equity-etf-hedger` | liup3424 | 全过零区分度 | OPEN |
| #118 | `perpetual-funding-ledger-reconciliation` | Runder-sun | 硬编码风险，无 trial | OPEN |
| #120 | `barra-cne6-risk` | GinkgoGao | 所有模型 ≤0.31 | CLOSED |
| #126 | `merton-cds-copula` | GinkgoGao | 全部 0.9，差 1 checkpoint | OPEN |
| #131 | `garch-vecm-cointegration` | bochencs | 区分度反转 | OPEN |
| #132 | `dirty-gap-momentum-aapl` | Jiahao-Xie-86 | 1:1:1; Very easy task with no discrimination. Keep? | OPEN |
| #150 | `earnings-news-event-alpha` | gem-mint | 0/0/0 零区分度 | OPEN |
| #164 | `dupire-local-vol` | Dongzhikang | 62/67:65/67:0/67; Instruction says valuation date is 2024-03-15, but the oracle uses the last daily close from 2025-12-30 as S0 (687.06); the actual 2024-03-15 close is 509.82. So the option filtering and surface are built with future information. | OPEN |
| #168 | `heston-cf-pricing` | Dongzhikang | 0:1:0; 想法很好！最后的小问题是关于浮点计算的rounding error的要求是否需要明确？目前agent的做法应该是对的，但因为rounding error被判错了。 | OPEN |
| #170 | `kou-double-exponential` | Dongzhikang | 12/12:11/12:12/12; The oracle moment-matches double-exponential jumps into normal components rather than implementing the Kou density/series, and the sigma optimizer bound still allows 1.0 despite the spec/test bound of 0.50. | OPEN |
| #174 | `power-options` | Dongzhikang | 33/36:36/36:36/36; Now the verifier grades based on self-reported MC errors/parity booleans. Will agents lie? Use independent recomputation instead? | OPEN |
| #175 | `rainbow-option-pricing` | Dongzhikang | 0:0:0; 全挂但反映真正难度; PQCat file-level review found 2 typos in instruction that likely cause the 0:0:0: (1) Wrong prose payoff for call-on-min: instruction says *"Call on minimum: max(S1_T, S2_T) − K (but prices the minimum)"* — the `max(S1, S2)` is the call-on-MA | OPEN |
| #178 | `variance-swap-pricing` | Dongzhikang | 1:0:1; Opus 失败合理; 2026-04-26 PQCat re-test (Opus): 36/37 — single failure on `test_parameters_in_reasonable_range` with `kappa=50.0` (test asserts `kappa ≤ 20`). Methodology valid: model-free Carr-Madan replication formula and Heston closed-form `K_var = θT +  | OPEN |
| #196 | `copula-garch-portfolio` | Dongzhikang | 35/38:35/38:37/38; `test_gs_alpha_value` 三模型全挂，oracle alpha≈0.073 vs agent 0.10-0.12，tolerance 可能太紧 | OPEN |
| #204 | `panjer-recursion` | Dongzhikang | 18/22:22/22:22/22; Statement "Starting from P(S = 0) = P(N = 0) (evaluated using the appropriate frequency distribution), use the Panjer recursion..." is wrong. Should be “P(S = 0) = P_N(f_X(0))” instead. | OPEN |
| #208 | `garch-sp500-fit` | Dongzhikang | Haiku 33/47, GARCH-t parameterization: 不同库的 Student-t nu 定义不同，instruction 未指定库; ✅ Root cause confirmed. The instruction's Step 3 formula defines `z_t = X_t / σ_t` but omits the `scale = sqrt((ν−2)/ν)` factor — both in the z definition and the log-likelihood su | OPEN |

## Removed as outdated/noise
- Removed struck-through “Moved to …” rows.
- Removed rows whose task is already present on `origin/main` (including old ❌ rows for `lob-pc-signal`, `polars-api-migration`, `sec-10k-report-long`, `13f-amendment-aware-crowding`).
- Corrected stale row: `standard-var-methods` is PR #205, not #195; #195 is `creditrisk-plus-model`.
- Corrected stale row: #176 merged as `ohlc-realized-vol-estimators` to avoid duplicate #107 `realized-vol-estimators`.
