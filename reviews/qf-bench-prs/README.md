# QF-Bench PR Reviews

Working review drafts and status tracking for open QF-Bench task PRs that Steve (oyzh888) may inspect before posting comments upstream.

Status legend:
- `todo` — not reviewed yet
- `drafted` — local review drafted
- `posted-upstream` — already posted to the upstream PR
- `needs-recheck` — draft exists but should be revisited before posting

Last synchronized: 2026-04-19

Notes:
- `Human Review` excludes `github-actions` CI comments.
- `Reviewer(s)` lists submitted human reviewers first; if none exist, it falls back to requested reviewers.
- `1st Review Label` and `2nd Review Label` reflect the current GitHub labels, not inferred workflow state.

## Open Task PR Tracker

| PR | Title | Reviewer(s) | Last Updated | Human Review | 1st Review Label | 2nd Review Label | Local Status | Summary |
|---|---|---|---|---|---|---|---|---|
| #144 | Add task stable-residual | — | 2026-04-18 | no | no | no | todo | [pr-144.md](./pr-144.md) |
| #143 | Add task residual-momentum | — | 2026-04-18 | no | no | no | todo | [pr-143.md](./pr-143.md) |
| #142 | Add task double-sort | — | 2026-04-18 | no | no | no | todo | [pr-142.md](./pr-142.md) |
| #141 | feat: add swap-curve-bootstrap-ois task (medium, fixed-income) | — | 2026-04-19 | no | no | no | todo | [pr-141.md](./pr-141.md) |
| #140 | feat: add localvol barrier task | PQCat, foxie-huang | 2026-04-19 | no | no | yes | todo | [pr-140.md](./pr-140.md) |
| #139 | Add MTM XCCY basis desk task and improve Finance-Zero extraction | PQCat, foxie-huang | 2026-04-19 | no | no | yes | todo | [pr-139.md](./pr-139.md) |
| #137 | Add task: multimodal-alpha-fusion-edgar-cot-gdelt | yunfei67 | 2026-04-18 | yes | yes | yes | todo | [pr-137.md](./pr-137.md) |
| #136 | Add task: quantamental-earnings-jumpfilter-committee | yunfei67 | 2026-04-18 | yes | yes | yes | todo | [pr-136.md](./pr-136.md) |
| #135 | Add task: prediction-markets-cross-venue-dislocation | Dongzhikang | 2026-04-18 | yes | yes | yes | todo | [pr-135.md](./pr-135.md) |
| #134 | Add task sector-neutral-residual-momentum (hard) | Dongzhikang, Jingyi-Jia | 2026-04-15 | no | yes | yes | todo | [pr-134.md](./pr-134.md) |
| #133 | Add task shrinkage-meanvar-portfolio (medium) | Dongzhikang | 2026-04-16 | yes | yes | yes | todo | [pr-133.md](./pr-133.md) |
| #132 | Add task dirty-gap-momentum-aapl (easy) | yunfei67 | 2026-04-19 | yes | yes | yes | todo | [pr-132.md](./pr-132.md) |
| #131 | feat: add garch-vecm-cointegration task (medium) | PQCat, joyceHe703 | 2026-04-16 | bot only | yes | yes | todo | [pr-131.md](./pr-131.md) |
| #130 | feat: add ml-credit-scoring-fairness task (medium) | Dongzhikang, XiangningLin | 2026-04-18 | yes | yes | yes | todo | [pr-130.md](./pr-130.md) |
| #129 | feat: add fx-forward-cross-rate task (medium) | yunfei67 | 2026-04-16 | yes | yes | yes | todo | [pr-129.md](./pr-129.md) |
| #128 | feat: add etf-cross-asset-lead-lag task (medium, cross-asset-analysis) | yunfei67 | 2026-04-16 | yes | no | yes | todo | [pr-128.md](./pr-128.md) |
| #127 | feat: add crypto-funding-rate-basis-carry task (medium, crypto) | foxie-huang, oyzh888 | 2026-04-16 | no | yes | yes | drafted | [pr-127.md](./pr-127.md) |
| #126 | feat: add merton-cds-copula task (medium, credit risk) | beckybyte, labubububula78-poop | 2026-04-16 | no | yes | yes | todo | [pr-126.md](./pr-126.md) |
| #125 | feat: add bl-regime-hmm task (hard, portfolio optimization) | yunfei67 | 2026-04-14 | yes | yes | yes | todo | [pr-125.md](./pr-125.md) |
| #124 | feat: add pairs-cointegration-kalman task (hard, statistical arbitrage) | yunfei67 | 2026-04-13 | yes | yes | yes | todo | [pr-124.md](./pr-124.md) |
| #123 | feat: add ipca-latent-factors task (hard, latent factor model) | Dongzhikang, GinkgoGao, XiangningLin | 2026-04-18 | yes | no | yes | todo | [pr-123.md](./pr-123.md) |
| #122 | feat: add barra-cne6-risk task (hard, multi-factor risk) | Dongzhikang, XiangningLin | 2026-04-18 | yes | no | yes | todo | [pr-122.md](./pr-122.md) |
| #121 | feat: add alpha-hedge-strategy task (hard, portfolio construction) | PQCat, joyceHe703, labubububula78-poop | 2026-04-16 | no | yes | yes | todo | [pr-121.md](./pr-121.md) |
| #120 | feat: add 6 cross-domain hard tasks (risk, factors, credit, derivatives, portfolio) | foxie-huang, joyceHe703 | 2026-04-15 | no | yes | yes | todo | [pr-120.md](./pr-120.md) |
| #119 | Add option-put-call-parity-forward-audit task | — | 2026-04-08 | no | no | no | todo | [pr-119.md](./pr-119.md) |
| #118 | Add perpetual-funding-ledger-reconciliation task | — | 2026-04-08 | no | no | no | todo | [pr-118.md](./pr-118.md) |
| #117 | add task - credit risk - porfolio var cvar end-to-end ( hard, credit-risk, end-to-end) | XiangningLin, pangjacque | 2026-04-18 | yes | no | yes | todo | [pr-117.md](./pr-117.md) |
| #116 | feat: add cheapest-ETF-creation-basket task(medium) | Dongzhikang, XiangningLin, liup3424 | 2026-04-18 | yes | no | yes | todo | [pr-116.md](./pr-116.md) |
| #115 | feat: add ledoit-wolf-shrinkage task (medium) | Dongzhikang, XiangningLin | 2026-04-18 | yes | no | yes | todo | [pr-115.md](./pr-115.md) |
| #114 | feat: Add brinson-sector-attribution task (Medium) | foxie-huang, yunfei67 | 2026-04-15 | no | yes | yes | todo | [pr-114.md](./pr-114.md) |
| #113 | feat: add execution-ledger-pnl-reconciliation task | Dongzhikang, YoutingWang | 2026-04-19 | yes | yes | yes | todo | [pr-113.md](./pr-113.md) |
| #112 | feat: add ewma-portfolio-risk-decomposition task | labubububula78-poop, oyzh888 | 2026-04-19 | no | yes | yes | drafted | [pr-112.md](./pr-112.md) |
| #111 | feat: add historical-var-data-prep (easy, risk-management) | labubububula78-poop, oyzh888 | 2026-04-19 | no | yes | yes | drafted | [pr-111.md](./pr-111.md) |
| #110 | feat: add evt-pot-var task (Medium) | joyceHe703 | 2026-04-19 | yes | yes | yes | todo | [pr-110.md](./pr-110.md) |
| #109 | feat: add variance-swap-replication task (medium) | yunfei67 | 2026-04-14 | yes | no | yes | todo | [pr-109.md](./pr-109.md) |
| #108 | feat: add delta-hedging-pnl-simulation task (medium) | yunfei67 | 2026-04-14 | yes | no | yes | todo | [pr-108.md](./pr-108.md) |
| #107 | feat: add realized-vol-estimators task (medium) | yunfei67 | 2026-04-10 | yes | no | yes | todo | [pr-107.md](./pr-107.md) |
| #106 | feat: add etf-overlap-redemption-pressure (medium) | PQCat, beckybyte, labubububula78-poop | 2026-04-19 | no | yes | yes | todo | [pr-106.md](./pr-106.md) |
| #105 | feat: add yield-curve-bond-immunization task (hard, fixed-income) | beckybyte, labubububula78-poop | 2026-04-16 | no | yes | yes | todo | [pr-105.md](./pr-105.md) |
| #104 | feat: add form4-cross-sectional-sale-pressure (hard) | Jingyi-Jia, oyzh888 | 2026-04-19 | no | yes | yes | drafted | [pr-104.md](./pr-104.md) |
| #103 | feat: add fx-carry-forward-hedge task (hard, fx-strategy) | PQCat, beckybyte, labubububula78-poop | 2026-04-16 | no | yes | yes | todo | [pr-103.md](./pr-103.md) |
| #102 | feat: add  intraday-volume-fitting-and-execution-scheduling task(Hard) | joyceHe703 | 2026-04-15 | yes | yes | yes | todo | [pr-102.md](./pr-102.md) |
| #101 | feat: add sec-8k-event-alpha task (Medium) | yunfei67 | 2026-04-15 | yes | yes | yes | todo | [pr-101.md](./pr-101.md) |
| #100 | feat: add minimum-cost-equity-etf-hedger task(medium) | — | 2026-04-08 | no | yes | yes | todo | [pr-100.md](./pr-100.md) |
| #99 | feat: add 13f-amendment-aware-crowding (medium) | Jingyi-Jia, beckybyte | 2026-04-06 | no | yes | yes | todo | [pr-099.md](./pr-099.md) |
| #98 | Add task: nelson-siegel-yield-curve-fit (hard) | joyceHe703 | 2026-04-15 | yes | yes | yes | todo | [pr-098.md](./pr-098.md) |
| #97 | Add task: factor-momentum-spanning (hard) | wshi83, yunfei67 | 2026-04-15 | yes | yes | yes | todo | [pr-097.md](./pr-097.md) |
| #96 | Add task: credit-spread-decomposition (hard) | Jingyi-Jia, PQCat, beckybyte | 2026-04-12 | no | yes | yes | todo | [pr-096.md](./pr-096.md) |
| #95 | Add task: fixed-income-market-stress | PQCat, beckybyte | 2026-04-12 | no | yes | yes | todo | [pr-095.md](./pr-095.md) |
| #94 | Add task: trace-rate-flow-analysis | Dongzhikang, PQCat | 2026-04-12 | no | yes | yes | todo | [pr-094.md](./pr-094.md) |
| #93 | Add task: yield-curve-pca-dynamics | wshi83, yunfei67 | 2026-04-14 | yes | no | yes | todo | [pr-093.md](./pr-093.md) |
| #92 | feat: add sec-10k-report-long task (medium) | joyceHe703 | 2026-04-18 | yes | no | yes | todo | [pr-092.md](./pr-092.md) |
| #91 | feat: add polars-api-migration (medium) | PQCat, joyceHe703, oyzh888 | 2026-04-18 | no | yes | yes | drafted | [pr-091.md](./pr-091.md) |
| #89 | feat: add lob-pc-signal task (medium) | PQCat, joyceHe703 | 2026-04-18 | yes | no | no | todo | [pr-089.md](./pr-089.md) |
| #88 | feat: add event-study-earnings task (hard) | joyceHe703 | 2026-04-15 | yes | yes | yes | todo | [pr-088.md](./pr-088.md) |
| #87 | feat: add yield-curve-bootstrap-immunization task (hard) | Jingyi-Jia, joyceHe703 | 2026-04-16 | bot only | yes | yes | todo | [pr-087.md](./pr-087.md) |
| #86 | feat: add dcc-garch-portfolio-var task (hard) | Dongzhikang, harvenstar | 2026-04-06 | yes | yes | yes | drafted | [pr-086.md](./pr-086.md) |
| #84 | feat: add CME HDD option pricing task | PQCat, beckybyte | 2026-04-16 | no | yes | yes | todo | [pr-084.md](./pr-084.md) |
| #81 | Add lmm-markov-representation task to main | foxie-huang | 2026-04-13 | no | yes | yes | todo | [pr-081.md](./pr-081.md) |
| #80 | add task - credit risk - credit transition matrix and markov property (medium, credit-risk, end-to-end) | PQCat, joyceHe703 | 2026-04-15 | no | yes | yes | todo | [pr-080.md](./pr-080.md) |
| #79 | feat: add execution-is-vwap task | foxie-huang | 2026-04-13 | no | yes | yes | todo | [pr-079.md](./pr-079.md) |
| #78 | feat: add fx-carry-trade-backtest task | oyzh888 | 2026-04-16 | no | yes | yes | drafted | [pr-078.md](./pr-078.md) |
| #77 | feat: add cds-curve-stripping task | — | 2026-04-06 | no | yes | yes | todo | [pr-077.md](./pr-077.md) |
| #76 | feat: add fama-macbeth-risk-premia task | — | 2026-04-06 | no | yes | yes | todo | [pr-076.md](./pr-076.md) |
| #75 | feat: add var-ebacktest-coverage task | — | 2026-04-06 | no | yes | yes | todo | [pr-075.md](./pr-075.md) |
| #74 | feat: add black-litterman-allocation task | Dongzhikang | 2026-04-16 | yes | yes | yes | drafted + posted-upstream | [pr-074.md](./pr-074.md) |
| #73 | Feat/cap floor black pricing | Dongzhikang | 2026-04-15 | yes | yes | yes | todo | [pr-073.md](./pr-073.md) |
| #72 | feat: add treasury-curve-pca-butterfly task | foxie-huang | 2026-04-13 | no | yes | yes | todo | [pr-072.md](./pr-072.md) |
| #66 | feat: add portfolio-risk-attribution task | Dongzhikang | 2026-04-14 | yes | yes | yes | todo | [pr-066.md](./pr-066.md) |
| #65 | feat: add bond-portfolio-analytics task | Dongzhikang | 2026-04-16 | yes | yes | yes | todo | [pr-065.md](./pr-065.md) |
| #64 | feat: add cta-ewma-cvar task | Dongzhikang | 2026-04-06 | yes | yes | yes | todo | [pr-064.md](./pr-064.md) |
| #63 | feat: add markowitz-efficient-frontier task | Dongzhikang | 2026-04-06 | yes | yes | yes | todo | [pr-063.md](./pr-063.md) |
| #62 | feat: add cross-sectional-momentum task | — | 2026-04-06 | no | yes | yes | todo | [pr-062.md](./pr-062.md) |
| #61 | feat: add pairs-trading-cointegration task | — | 2026-04-06 | no | yes | yes | todo | [pr-061.md](./pr-061.md) |
| #53 | Add equity-vendor-restatement-break-audit task | — | 2026-04-08 | no | no | no | todo | [pr-053.md](./pr-053.md) |
| #52 | Add ust-carry-roll-down-attribution task | — | 2026-04-08 | no | no | no | todo | [pr-052.md](./pr-052.md) |
| #51 | Add binance-btc-participation-tca task | bot only | 2026-04-08 | bot only | no | no | todo | [pr-051.md](./pr-051.md) |
| #49 | feat: add rough-vol-rbgergomi task (rough Bergomi model IV smile) | — | 2026-04-06 | no | yes | yes | todo | [pr-049.md](./pr-049.md) |
| #48 | feat: add cir-calibration task (CIR interest rate model calibration) | Dongzhikang | 2026-04-06 | yes | yes | yes | todo | [pr-048.md](./pr-048.md) |
| #47 | feat: add merton-jump-diffusion task (Merton jump-diffusion option pricing) | — | 2026-04-06 | no | yes | yes | todo | [pr-047.md](./pr-047.md) |
| #46 | feat: add ou-pairs-trading task (OU process calibration + statistical arbitrage) | — | 2026-04-06 | no | yes | yes | todo | [pr-046.md](./pr-046.md) |
| #45 | feat: add heston-mc-pricing task (Heston stochastic volatility Monte Carlo) | — | 2026-04-06 | no | yes | yes | todo | [pr-045.md](./pr-045.md) |
| #42 | feat: add pca-factor-portfolio task | — | 2026-04-06 | no | yes | yes | todo | [pr-042.md](./pr-042.md) |
| #41 | feat: add interest-rate-cap-floor task | — | 2026-04-06 | no | yes | yes | todo | [pr-041.md](./pr-041.md) |
| #40 | feat: add earnings-surprise-calculator task | — | 2026-04-06 | no | yes | yes | todo | [pr-040.md](./pr-040.md) |
| #39 | feat: add corporate-action-adjustment task | — | 2026-04-06 | no | yes | yes | todo | [pr-039.md](./pr-039.md) |
| #38 | feat: add zero-coupon-bootstrapping task | — | 2026-04-06 | no | yes | yes | todo | [pr-038.md](./pr-038.md) |
| #37 | task proposal | — | 2026-03-21 | no | no | no | todo | [pr-037.md](./pr-037.md) |
| #28 | pq_cat: hull-white-swaption hints + mc-greek-surface-1 task + stochvol benchmark results | foxie-huang, labubububula78-poop | 2026-04-15 | no | no | yes | todo | [pr-028.md](./pr-028.md) |
| #23 | Add stochvol-implied-surface-new task | PQCat | 2026-04-15 | yes | yes | yes | todo | [pr-023.md](./pr-023.md) |
| #4 | Add 15 medium-hard benchmark tasks (fixed-income, derivatives, risk, quant-strategy) | — | 2026-03-06 | no | no | no | todo | [pr-004.md](./pr-004.md) |
| #2 | Add momentum-backtest task | Dongzhikang, foxie-huang, joyceHe703, labubububula78-poop | 2026-04-15 | no | no | no | todo | [pr-002.md](./pr-002.md) |
