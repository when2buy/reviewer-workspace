# QF-Bench PR Review — Complete Summary

**Date:** 2026-04-23 | **Reviewed:** 105 PRs (excluding #4 mega-PR and #145 docs-only)
**Total:** ✅ 建议Merge: 72 (56%) | ❌ 不建议Merge: 37 (29%) | 🟡 需要Human Review: 17 (13%) | ❌ 待定: 3 (2%)

> **2026-04-26 PQCat re-test:** Promoted #119, #125, #172 from 🟡 Human Review → ✅ Merge after fresh Haiku/Sonnet/Opus runs (all H:O:S = 1:1:1). Also added **PR #211** (Docker SHA-pin fix for #119 — *must be merged before #119*). See `HUMAN-REVIEW-SUMMARY.md` for full re-test details and the Corrado-formula concern that may move #88 from ✅ Merge → 🟡 in a future update.

> **2026-04-26 update:** Added 17 Haiku-pass tasks from PR#180-209 to ✅ Merge. Added 3 tasks needing human review (convention/parameterization issues). 3 tasks (var-es-estimation, smith-tail-index, creditrisk-plus-model) pending Sonnet/Opus trials.

---

## ✅ 建议 Merge (55)

| PR | Task | Author | H:O:S | 备注 | Final Approval |
|---|---|---|---|---|---|
| #38 | zero-coupon-bootstrapping | Dongzhikang | 1:1:1 | 正确，无区分度 | |
| #39 | corporate-action-adjustment | Dongzhikang | 1:1:1 | 正确，无区分度 | |
| #40 | earnings-surprise-calculator | Dongzhikang | 1:1:1 | 过于简单 | |
| #41 | interest-rate-cap-floor | Dongzhikang | 0:1:1 | ⭐ fixing-time convention 真正quant难度 | |
| #42 | pca-factor-portfolio | Dongzhikang | 1:1:1 | 建议改 hard→medium | |
| #51 | binance-btc-participation-tca | Runder-sun | N/A | 设计优秀，修 Docker sha256 | |
| #52 | ust-carry-roll-down-attribution | Runder-sun | 0:1:1 | 好区分度 | |
| #62 | cross-sectional-momentum | Dongzhikang | 1:1:1 | 建议改 hard→medium | |
| #63 | markowitz-efficient-frontier | Dongzhikang | 0:1:0 | ⭐ ERC portfolio 区分度好 | |
| #80 | credit-migration-matrix | pangjacque | 1:1:0→1:1:1 | Updated per reviewer feedback, S4.6+H4.5 63/63 | |
| #84 | cme-hdd-option-pricing | xinlan-technology | 0:1:1 | 好设计 | |
| #87 | yield-curve-bootstrap-immunization | harvenstar | 0:1:1 | 优秀多步固收 task | |
| #93 | yield-curve-pca-dynamics | wshi83 | 1:1:0 | 好 PCA task | |
| #96 | credit-spread-decomposition | wshi83 | 0:1:1 | 优秀信用分析 | |
| #98 | nelson-siegel-yield-curve-fit | wshi83 | 应该是easy outlier count window 太紧 | |
| #101 | sec-8k-event-alpha | boqiny | 0.96:1:0.54 | ⭐ 优秀区分度，partial credit | |
| #102 | intraday-volume-fitting | liup3424 | 0:1:1 | 好校准 | |
| #103 |fx-carry-forward-hedge|	Jingyi-Jia	|
| #105 | yield-curve-bond-immunization | Jingyi-Jia | KRD key format bug |
| #107 | realized-vol-estimators | yyu56253 | 公式未在 instruction 说明 需要改instruction, 应该是easy | |
| #108 | delta-hedging-pnl-simulation | yyu56253 | 0:1:1 | 干净衍生品 task | |
| #109 | variance-swap-replication | yyu56253 | 1:1:1 | Carr-Madan 正确 | |
| #110 | evt-pot-var | boqiny | 0.71:1:0.92 | ⭐ 全面尾部风险，partial credit | |
| #111 | historical-var-data-prep | YoutingWang | 1:1:1 | 干净，标 easy 诚实 | |
| #112 | ewma-portfolio-risk-decomposition | YoutingWang | 0:1:1 | ⭐ 优秀 debug task，verifier 重算 | |
| #114 | brinson-sector-attribution | boqiny | 0:1:0 | Reviewer-iterated, full BF framework with drift+rebalance, 3-tier discrimination | |
| #117 | credit-portfolio-var-cvar | pangjacque | 0:1:0 | Good 3-tier discrimination. Fix: obligor count ~50→991, remove 0.8 multiplier in t-copula tail test | |
| #120b | ipca-latent-factors | GinkgoGao | 0.33:0.69:0.29 | 好区分度，partial credit | |
| #121 | alpha-hedge-strategy | GinkgoGao | 0.64:1:1 | O+S 过 H 挂 | |
| #129 | fx-forward-cross-rate | bochencs | 0:0:1 | S45 满分 | |
| #132 | dirty-gap-momentum-aapl | Jiahao-Xie-86 | 1:1:1 | 干净无区分度 | |
| #139 | mtm-xccy-basis-desk | Jingyi-Jia | 0:0:0 | Hard task, agents substantively wrong | |
| #140 | localvol-barrier | Jingyi-Jia | 0:0:0 | Hard task, Opus 27/34 but local vol off by 17-21% | |
| #141 | swap-curve-bootstrap-ois | YoutingWang | 0:1:1 | 好 debug 格式 | |
| #151 | fomc-tone-event-study | gem-mint | 0:1:0 | ⭐ NLP+固收，Opus-only | |
| #152 | american-binomial-tree | Dongzhikang | 1:1:1 | 干净无区分度 | |
| #153 | asian-option-levy-curran | Dongzhikang | 0:1:0 | 好区分度 | |
| #154 | barone-adesi-whaley | Dongzhikang | 0:1:1 | BAW 正确 | |
| #156 | bs-greeks-pde | Dongzhikang | 0:1:1 | PDE 残差优秀 | |
| #159 | cir-bond-pricing | Dongzhikang | 1:1:1 | 建议改 hard→medium | |
| #160 | cliquet-ratchet-pricing | Dongzhikang | 0:1:0 | Opus 17/17, good discrimination | |
| #161 | compound-option-geske | Dongzhikang | 0:1:0 | Pushed type label fix, parity check catches Sonnet bivariate normal error. Needs re-run | |
| #162 | digital-barrier-options | Dongzhikang | 0:1:1 | 干净 | |
| #163 | double-barrier-options | Dongzhikang | 0:1:0 | Kunitomo-Ikeda 正确 | |
| #165 | first-passage-time | Dongzhikang | 0:1:1 | 反射原理正确 | |
| #167 | geometric-mean-reverting-jd | Dongzhikang | 0:1:0 | OU+jump 正确 | |
| #168 | heston-cf-pricing | Dongzhikang | 0:1:0 | 74 tests, Opus 73/74 trivial K rounding | |
| #169 | implied-vol-approximations | Dongzhikang | 0:1:0 | Fixed rtol 1e-6→0.02, awaiting re-trial | |
| #170 | kou-double-exponential | Dongzhikang | 0:1:0 | Fixed boundary <→<=, awaiting re-trial | |
| #171 | lookback-options | Dongzhikang | 0:1:1 | 区分度好 | |
| #173 | ou-jump-commodity | Dongzhikang | 1:1:0 | 合理 | |
| #175 | rainbow-option-pricing | Dongzhikang | 0:0:0 | 全挂但反映真正难度 | |
| #177 | spread-option-kirk-margrabe | Dongzhikang | 0:1:1 | ⭐ 设计优秀 | |
| #178 | variance-swap-pricing | Dongzhikang | 1:0:1 | Opus 失败合理 | |
| #179 | sma-crossover-spy | PQCat | 1:1:1 | Fix PR，干净 | |
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

## ❌ 不建议 Merge (37)

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

| #174 | power-options | Dongzhikang | Output path spec bug: instruction never mentions /app/output/, Opus/Sonnet wrote to /app/ (all correct), Haiku guessed /app/output/ (luck). Needs instruction fix + re-run |
| #176 | realized-vol-estimators | Dongzhikang | Trial ran wrong task version (141-test intraday microstructure task vs current 33-test daily OHLCV). Trial data invalid. Needs re-run on current PR version |

## 🟡 需要 Human Review (14)

| PR | Task | Author | 原因 |
|---|---|---|---|
| #28 | data-cleaning | oyzh888 | 太简单，test 自引用 |
| #65 | bond-portfolio-analytics | Dongzhikang | Trial 旧版需重跑 |
| #76 | fama-macbeth-risk-premia | Dongzhikang | Opus 59/60，GRS 容差 |
| #78 | fx-carry-trade-backtest | Dongzhikang | Opus 差 1 test |
| #79 | execution-is-vwap | Dongzhikang | Sonnet 差 1 test |
| #95 | fixed-income-market-stress | wshi83 | 区分度反转 |
| #100 | minimum-cost-equity-etf-hedger | liup3424 | 全过零区分度 |
| #164 | dupire-local-vol | Dongzhikang | Instruction clarified, pushed fix, needs re-trial |
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
