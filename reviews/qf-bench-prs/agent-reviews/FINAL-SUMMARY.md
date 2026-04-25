# QF-Bench PR Review — Complete Summary

**Date:** 2026-04-23 | **Reviewed:** 105 PRs (excluding #4 mega-PR and #145 docs-only)
**Total:** ✅ 建议Merge: 40 (38%) | ❌ 不建议Merge: 38 (36%) | 🟡 需要Human Review: 27 (26%)

---

## ✅ 建议 Merge (40)

| PR | Task | Author | H:O:S | 备注 |
|---|---|---|---|---|
| #38 | zero-coupon-bootstrapping | Dongzhikang | 1:1:1 | 正确，无区分度 |
| #39 | corporate-action-adjustment | Dongzhikang | 1:1:1 | 正确，无区分度 |
| #40 | earnings-surprise-calculator | Dongzhikang | 1:1:1 | 过于简单 |
| #41 | interest-rate-cap-floor | Dongzhikang | 0:1:1 | ⭐ fixing-time convention 真正quant难度 |
| #42 | pca-factor-portfolio | Dongzhikang | 1:1:1 | 建议改 hard→medium |
| #51 | binance-btc-participation-tca | Runder-sun | N/A | 设计优秀，修 Docker sha256 |
| #52 | ust-carry-roll-down-attribution | Runder-sun | 0:1:1 | 好区分度 |
| #62 | cross-sectional-momentum | Dongzhikang | 1:1:1 | 建议改 hard→medium |
| #63 | markowitz-efficient-frontier | Dongzhikang | 0:1:0 | ⭐ ERC portfolio 区分度好 |
| #84 | cme-hdd-option-pricing | xinlan-technology | 0:1:1 | 好设计 |
| #87 | yield-curve-bootstrap-immunization | harvenstar | 0:1:1 | 优秀多步固收 task |
| #93 | yield-curve-pca-dynamics | wshi83 | 1:1:0 | 好 PCA task |
| #96 | credit-spread-decomposition | wshi83 | 0:1:1 | 优秀信用分析 |
| #101 | sec-8k-event-alpha | boqiny | 0.96:1:0.54 | ⭐ 优秀区分度，partial credit |
| #102 | intraday-volume-fitting | liup3424 | 0:1:1 | 好校准 |
| #108 | delta-hedging-pnl-simulation | yyu56253 | 0:1:1 | 干净衍生品 task |
| #109 | variance-swap-replication | yyu56253 | 1:1:1 | Carr-Madan 正确 |
| #110 | evt-pot-var | boqiny | 0.71:1:0.92 | ⭐ 全面尾部风险，partial credit |
| #111 | historical-var-data-prep | YoutingWang | 1:1:1 | 干净，标 easy 诚实 |
| #112 | ewma-portfolio-risk-decomposition | YoutingWang | 0:1:1 | ⭐ 优秀 debug task，verifier 重算 |
| #120b | ipca-latent-factors | GinkgoGao | 0.33:0.69:0.29 | 好区分度，partial credit |
| #121 | alpha-hedge-strategy | GinkgoGao | 0.64:1:1 | O+S 过 H 挂 |
| #129 | fx-forward-cross-rate | bochencs | 0:0:1 | S45 满分 |
| #132 | dirty-gap-momentum-aapl | Jiahao-Xie-86 | 1:1:1 | 干净无区分度 |
| #139 | mtm-xccy-basis-desk | Jingyi-Jia | 0:0:0 | Hard task, agents substantively wrong |
| #140 | localvol-barrier | Jingyi-Jia | 0:0:0 | Hard task, Opus 27/34 but local vol off by 17-21% |
| #141 | swap-curve-bootstrap-ois | YoutingWang | 0:1:1 | 好 debug 格式 |
| #151 | fomc-tone-event-study | gem-mint | 0:1:0 | ⭐ NLP+固收，Opus-only |
| #152 | american-binomial-tree | Dongzhikang | 1:1:1 | 干净无区分度 |
| #153 | asian-option-levy-curran | Dongzhikang | 0:1:0 | 好区分度 |
| #154 | barone-adesi-whaley | Dongzhikang | 0:1:1 | BAW 正确 |
| #156 | bs-greeks-pde | Dongzhikang | 0:1:1 | PDE 残差优秀 |
| #159 | cir-bond-pricing | Dongzhikang | 1:1:1 | 建议改 hard→medium |
| #162 | digital-barrier-options | Dongzhikang | 0:1:1 | 干净 |
| #163 | double-barrier-options | Dongzhikang | 0:1:0 | Kunitomo-Ikeda 正确 |
| #165 | first-passage-time | Dongzhikang | 0:1:1 | 反射原理正确 |
| #167 | geometric-mean-reverting-jd | Dongzhikang | 0:1:0 | OU+jump 正确 |
| #171 | lookback-options | Dongzhikang | 0:1:1 | 区分度好 |
| #173 | ou-jump-commodity | Dongzhikang | 1:1:0 | 合理 |
| #175 | rainbow-option-pricing | Dongzhikang | 0:0:0 | 全挂但反映真正难度 |
| #177 | spread-option-kirk-margrabe | Dongzhikang | 0:1:1 | ⭐ 设计优秀 |
| #178 | variance-swap-pricing | Dongzhikang | 1:0:1 | Opus 失败合理 |
| #179 | sma-crossover-spy | PQCat | 1:1:1 | Fix PR，干净 |

## ❌ 不建议 Merge (42)

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
| #98 | nelson-siegel-yield-curve-fit | wshi83 | outlier count window 太紧 |
| #99 | 13f-amendment-aware-crowding | Minxuan-Hu | Docker base image 错误 |
| #103 | fx-carry-forward-hedge | Jingyi-Jia | Verifier 脆弱 (NaN + off-by-one) |
| #104 | form4-cross-sectional-sale-pressure | Minxuan-Hu | Docker base image 错误 |
| #105 | yield-curve-bond-immunization | Jingyi-Jia | KRD key format bug |
| #106 | etf-overlap-redemption-pressure | Minxuan-Hu | Docker base image 错误 |
| #107 | realized-vol-estimators | yyu56253 | 公式未在 instruction 说明 |
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

| #174 | power-options | Dongzhikang | Instruction 缺 closed-form |
| #176 | realized-vol-estimators | Dongzhikang | Trial 跑的旧版 task |

## 🟡 需要 Human Review (23)

| PR | Task | Author | 原因 |
|---|---|---|---|
| #28 | data-cleaning | oyzh888 | 太简单，test 自引用 |
| #65 | bond-portfolio-analytics | Dongzhikang | Trial 旧版需重跑 |
| #76 | fama-macbeth-risk-premia | Dongzhikang | Opus 59/60，GRS 容差 |
| #78 | fx-carry-trade-backtest | Dongzhikang | Opus 差 1 test |
| #79 | execution-is-vwap | Dongzhikang | Sonnet 差 1 test |
| #80 | credit-migration-matrix | pangjacque | 1:1:0→1:1:1 | Updated per reviewer feedback, S4.6+H4.5 63/63 |
| #117 | credit-portfolio-var-cvar | pangjacque | 0:1:0 | Good 3-tier discrimination. Fix: obligor count ~50→991, remove 0.8 multiplier in t-copula tail test |
| #95 | fixed-income-market-stress | wshi83 | 区分度反转 |
| #100 | minimum-cost-equity-etf-hedger | liup3424 | 全过零区分度 |
| #114 | brinson-sector-attribution | boqiny | Knife-edge，隐式约定 |
| #164 | dupire-local-vol | Dongzhikang | Instruction clarified, pushed fix, needs re-trial |
| #118 | perpetual-funding-ledger-reconciliation | Runder-sun | 硬编码风险，无 trial |
| #119 | option-put-call-parity-forward-audit | Runder-sun | 同 #118，无 trial |
| #120a | barra-cne6-risk | GinkgoGao | 所有模型 ≤0.31 |
| #126 | merton-cds-copula | GinkgoGao | 全部 0.9，差 1 checkpoint |
| #128 | etf-cross-asset-lead-lag | xinlan-technology | 全有全无计分浪费区分度 |
| #131 | garch-vecm-cointegration | bochencs | 区分度反转 |
| #150 | earnings-news-event-alpha | gem-mint | 0/0/0 零区分度 |
| #160 | cliquet-ratchet-pricing | Dongzhikang | Forward-start 歧义 |
| #161 | compound-option-geske | Dongzhikang | 区分度反转 |
| #168 | heston-cf-pricing | Dongzhikang | Opus 73/74，K rounding |
| #172 | merton-jump-diffusion | Dongzhikang | 零 trial 数据 |
| #125 | bl-regime-hmm | GinkgoGao | Opus 0.92，放宽 HMM tolerance 即可 |
| #169 | implied-vol-approximations | Dongzhikang | 已修 rtol→0.02，Opus 过 (0:1:0) |
| #170 | kou-double-exponential | Dongzhikang | 已修 boundary <=，待重跑 trial |

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
