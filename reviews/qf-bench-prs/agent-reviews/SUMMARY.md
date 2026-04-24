# Dongzhikang PR Review Summary

**Reviewer:** Agent (automated) | **Date:** 2026-04-23
**Total PRs:** 45 | ✅ 建议Merge: 21 | ❌ 不建议Merge: 16 | 🟡 需要Human Review: 8

## ✅ 建议 Merge (21)

| PR | Task | H:O:S | 备注 |
|---|---|---|---|
| #38 | zero-coupon-bootstrapping | 1:1:1 | 正确，无区分度 |
| #39 | corporate-action-adjustment | 1:1:1 | 正确，无区分度 |
| #40 | earnings-surprise-calculator | 1:1:1 | 过于简单 |
| #41 | interest-rate-cap-floor | 0:1:1 | ⭐ Haiku在fixing-time挂，真正quant难度 |
| #42 | pca-factor-portfolio | 1:1:1 | 建议改标签 hard→medium |
| #62 | cross-sectional-momentum | 1:1:1 | 建议改标签 hard→medium |
| #63 | markowitz-efficient-frontier | 0:1:0 | ⭐ ERC portfolio区分度好，solve.py需更新 |
| #152 | american-binomial-tree | 1:1:1 | 干净，无区分度 |
| #153 | asian-option-levy-curran | 0:1:0 | 好区分度 |
| #154 | barone-adesi-whaley | 0:1:1 | BAW正确 |
| #156 | bs-greeks-pde | 0:1:1 | PDE残差检验优秀 |
| #159 | cir-bond-pricing | 1:1:1 | Verifier好，"hard"标签偏高 |
| #162 | digital-barrier-options | 0:1:1 | 干净 |
| #163 | double-barrier-options | 0:1:0 | Kunitomo-Ikeda正确 |
| #165 | first-passage-time | 0:1:1 | 反射原理正确 |
| #167 | geometric-mean-reverting-jd | 0:1:0 | OU+jump正确 |
| #171 | lookback-options | 0:1:1 | 区分度好 |
| #173 | ou-jump-commodity | 1:1:0 | 合理 |
| #175 | rainbow-option-pricing | 0:0:0 | 全挂但反映真正难度 |
| #177 | spread-option-kirk-margrabe | 0:1:1 | ⭐ 设计优秀 |
| #178 | variance-swap-pricing | 1:0:1 | Opus失败合理 |

## ❌ 不建议 Merge (16)

| PR | Task | H:O:S | Blocker |
|---|---|---|---|
| #48 | cir-calibration | N/A | 缺Dockerfile，无trial |
| #61 | pairs-trading-cointegration | 0:0:0 | 2个verifier bug：signed shares + drawdown符号 |
| #64 | cta-ewma-cvar | 0:0:0 | Oracle bug（num_valid_obs 57 vs 58） |
| #66 | portfolio-risk-attribution | 0:0:0 | OOS Sharpe未说明excess vs raw |
| #72 | treasury-curve-pca-butterfly | 0:0:0 | PCA符号未指定 + butterfly P&L可能有误 |
| #75 | var-ebacktest-coverage | 0:0:0 | e-backtest公式缺失 |
| #77 | cds-curve-stripping | 0:0:0 | 所有模型同样失败→spec问题 |
| #155 | barrier-gbm-analytics | 0:0:0 | test_mean_fpt_down在无穷FPT上crash |
| #157 | cev-option-pricing | 0:0:0 | Oracle值有误：β=0.9 ATM应≈53.6非45.34 |
| #158 | chooser-option-pricing | 0:0:0 | 简单chooser公式可能有误 + 答案泄露 |
| #164 | dupire-local-vol | 0:0:0 | 所有模型全挂，spec太脆弱 |
| #166 | fx-quanto-options | 0:0:0 | compo公式可能错（缺composite vol） |
| #169 | implied-vol-approximations | 0:0:0 | Oracle值硬编码到1e-6 |
| #170 | kou-double-exponential | 0:0:0 | Verifier边界bug + ATM容差太窄 |
| #174 | power-options | 0:0:0 | Instruction缺显式closed-form |
| #176 | realized-vol-estimators | 1:0:0 | Trial跑的是旧版task |

## 🟡 需要 Human Review (8)

| PR | Task | H:O:S | 原因 |
|---|---|---|---|
| #65 | bond-portfolio-analytics | 1:1:1 | Trial跑的是旧版test，需重跑 |
| #76 | fama-macbeth-risk-premia | 0:0:0 | Opus 59/60，GRS容差 |
| #78 | fx-carry-trade-backtest | 0:0:0 | Opus差1个test，小修可过 |
| #79 | execution-is-vwap | 0:0:0 | Sonnet差1个test，区分度好 |
| #160 | cliquet-ratchet-pricing | 0:1:0 | Forward-start公式有歧义 |
| #161 | compound-option-geske | 1:0:0 | 区分度反转（Haiku过Opus挂） |
| #168 | heston-cf-pricing | 0:0:0 | Opus 73/74过，被K rounding卡住 |
| #172 | merton-jump-diffusion | N/A | 零trial数据 |

## 关键发现

1. **最佳 tasks（⭐）：** #41 interest-rate-cap-floor, #63 markowitz-efficient-frontier, #177 spread-option-kirk-margrabe — 真正的quant区分度
2. **常见问题模式：** instruction under-specification（#66, #72, #75, #174）、oracle值有误（#64, #157）、verifier bug（#61, #155, #170）
3. **难度标签问题：** #42, #62 标hard但全过应改medium；#159 标hard但全过
4. **0:0:0 不一定是坏事：** #175 rainbow-option-pricing 全挂但反映真实难度，值得保留
