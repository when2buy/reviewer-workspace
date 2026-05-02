# Examples

Worked examples drawn from real PR reviews and the May 2026 50-trial validation. Each shows the trial setup, the relevant agent solution excerpt and task spec excerpt, and the resulting `labels.json` snippet. Examples are paraphrased to fit a small file.

The first three (A/B/C class) cover the original taxonomy. The fourth (A1.d) showcases the structural-deviation sub-rubric added during validation. For all sub-rubrics including the post-validation additions (A1.d, A2.g, A2.h, B1.e, C2.j), see [TAXONOMY.md](TAXONOMY.md). For methodology and validated κ result, see [CALIBRATION.md](CALIBRATION.md).

---

## Example 1 — Class A (Model & Formula): A2 Missing Formula Term

### Trial

- `agent_harness=claude-code`, `model=haiku45`
- `task_name=garch-sp500-fit` (PR #208)
- `solution_kind=claude-code` (multi-step)

### `instruction.md` (excerpt fed to the judge)

> **Step 3 — Estimate GARCH(1,1)-t parameters by maximum likelihood.**
> The Student-t log-likelihood is:
> ```
> L = sum_t [ log f_t(z_t; nu) - 0.5 * log(sigma_t^2) ]
> ```
> where `z_t = X_t / sigma_t`, `sigma_t^2` is the GARCH conditional variance, `f_t(·; nu)` is the Student-t density with ν degrees of freedom, and `X_t` is the centered return.

### Agent solution excerpt

```python
# step 3: GARCH(1,1)-t MLE
from scipy.stats import t as student_t

def neg_loglik(params, X):
    omega, alpha, beta, nu = params
    sigma2 = np.zeros_like(X)
    sigma2[0] = np.var(X)
    for k in range(1, len(X)):
        sigma2[k] = omega + alpha * X[k-1]**2 + beta * sigma2[k-1]
    sigma_t = np.sqrt(sigma2)
    z = X / sigma_t                                       # ← agent follows instruction literally
    ll = np.sum(student_t.logpdf(z, df=nu) - 0.5 * np.log(sigma2))
    return -ll
```

### Failing tests

- `test_nu_in_reasonable_range`: agent_value `nu = 99.999`, expected `nu ∈ [3, 10]`.
- `test_alpha_value`, `test_beta_value`, `test_unconditional_variance` — all cascading from wrong ν.

### `labels.json` snippet (one mode shown)

```json
"missing_extra_formula_term": {
  "match": true,
  "evidence_step_ids": [12, 13],
  "quote": "z = X / sigma_t",
  "confidence": 0.95,
  "notes": "A2.a — t-likelihood missing -log(scale) Jacobian. Reference uses location-scale standardization z = X / (sigma * scale) with scale = sqrt((nu-2)/nu) and L = sum[logpdf(z, nu) - log(sigma) - log(scale)]. Without the Jacobian penalty, optimizer pushes nu to upper bound (99.999). Cascade: 12 downstream test failures from this one root cause."
}
```

(All other modes return `match: false` for this trial.)

---

## Example 2 — Class B (Convention & Units): B2 Sign Convention Error

### Trial

- `agent_harness=gemini-cli`, `model=gemini25pro`
- `task_name=ipca-latent-factors` (PR #123)
- `solution_kind=gemini-cli`

### `instruction.md` (excerpt)

> **Step 4 — Normalize factors via eigendecomposition of `F'F/T`.**
> Report Sharpe ratio per factor in `factor_metrics.csv`.

(Note: instruction does *not* specify a sign-fixing rule for the eigenvectors.)

### Agent solution excerpt

```python
# step 4: factor rotation
M = (F.T @ F) / T
eigvals, eigvecs = np.linalg.eigh(M)
order = np.argsort(eigvals)[::-1]
eigvecs = eigvecs[:, order]

# Heuristic sign convention: make first element positive
for k in range(eigvecs.shape[1]):
    if eigvecs[0, k] < 0:
        eigvecs[:, k] *= -1

F_rot = F @ eigvecs    # rotated factors
sharpes = F_rot.mean(axis=0) / F_rot.std(axis=0) * np.sqrt(252)
```

### Failing tests

- `test_factor_1_sharpe`: agent +0.43, expected −0.43 (ratio = −1).
- `test_factor_3_sharpe`: agent −0.61, expected +0.61.

### `labels.json` snippet

```json
"sign_convention_error": {
  "match": true,
  "evidence_step_ids": [8, 9, 10, 11],
  "quote": "if eigvecs[0, k] < 0: eigvecs[:, k] *= -1",
  "confidence": 0.92,
  "notes": "B2.e — eigenvector sign indeterminacy. Instruction did not specify a sign-fixing rule. Reference uses an implicit anchor (largest-loading positive); agent uses first-element-positive. Factors 1 and 3 come out with flipped signs; factor 2 happens to agree. Sharpes flip sign accordingly. Failure ratio ≈ -1 confirms B2."
}
```

```json
"wrong_parameterization": {
  "match": false,
  "evidence_step_ids": [],
  "quote": "",
  "confidence": 0.7,
  "notes": "Sign-fixing rule choice is a *convention default* for an under-specified spec — could plausibly be A3.c (metric definition) but the magnitude is correct, only the sign flipped. B2 captures this cleanly; not double-classifying."
}
```

---

## Example 3 — Class C (Data & Numerics): C3 Statistical Variant Mismatch (inverse trap)

### Trial

- `agent_harness=claude-code`, `model=sonnet46`
- `task_name=ml-credit-scoring-fairness` (PR #130)
- `solution_kind=claude-code`

### `instruction.md` (excerpt)

> **Step 2 — Bin numerical features into `woe_num_bins` equal-frequency bins. Compute the Weight of Evidence per bin. Use the smoothing constant from `params` to avoid log(0).**
> `params.woe_smoothing = 0.5`

### Agent solution excerpt (textbook implementation, Siddiqi *Credit Risk Scorecards*)

```python
# Step 2: Weight of Evidence
def woe(good_count, bad_count, total_good, total_bad, eps=0.5):
    # standard textbook: smooth the raw counts before computing proportions
    g = (good_count + eps) / total_good
    b = (bad_count  + eps) / total_bad
    return np.log(g / b)
```

### Reference solution (non-canonical variant)

```python
# Reference: smooth proportions, not counts
def woe(good_count, bad_count, total_good, total_bad, eps=0.5):
    g_pct = good_count / total_good
    b_pct = bad_count  / total_bad
    return np.log((g_pct + eps) / (b_pct + eps))   # ← non-standard; dampens WoE 8× toward zero
```

### Failing tests (cascade from one root cause)

- `test_iv_top_feature` — agent reports `num_late_payments` IV ≈ 0.207, expected ≈ 0.0611 (3.4× too high).
- `test_top_3_features_by_iv` — wrong feature ordering due to wrong IVs.
- `test_demographic_parity_ratio`, `test_equalized_odds_difference` — fairness metrics shift because feature selection changed.
- `test_discrimination_metric` × 4 (AUC, Gini, KS-stat, KS-threshold) — all cascading.

### `labels.json` snippet

```json
"statistical_variant_mismatch": {
  "match": true,
  "evidence_step_ids": [22, 23, 24, 25],
  "quote": "g = (good_count + eps) / total_good",
  "confidence": 0.95,
  "notes": "C3.c (inverse trap) — agent applied smoothing to RAW COUNTS before computing proportions, the standard textbook approach (Siddiqi). Reference applies smoothing to PROPORTIONS, which dampens WoE ~8× toward zero. The non-canonical reference variant penalizes the agent for following standard practice. Cascade: 1 root cause → 8 test failures (IV → feature selection → logistic regression → 4 metrics + 2 fairness + 2 IV-ranking). Fix should be in instruction.md (write the exact formula), not in agent code."
}
```

---

## Example 4 — Class A (Model & Formula): A1.d Structural deviation

*Added from the May 2026 validation. Same trial set as the κ=0.89 calibration; this is the case the A1.d sub-rubric was created to capture.*

### Trial

- `agent_harness=claude-code`, `model=haiku-4.5`
- `task_name=hull-white-swaption` (validation set; trial `fb-h45br-r2-hull-white-swaption`)
- `solution_kind=claude-code` (multi-step)

### `instruction.md` (excerpt)

> **Step 7 — Hull-White Trinomial Tree**
> - Time step: `Δt = 1/12` (monthly)
> - Space step: `Δx = σ·√(3·Δt)`
> - Maximum node index: `j_max = ⌈0.184 / (a·Δt)⌉`, minimum 1
> - Stage 2: Arrow-Debreu calibration; `Σ_j Q_n(j)` should match market `P(0, t_n)` to 1e-6.

### Agent solution excerpt

```python
# step 7: "trinomial tree"
dt = 0.5                                                # ← spec says 1/12, agent uses 0.5 (semi-annual)
dx = sigma * np.sqrt(dt)                                # ← spec says σ·√(3·Δt), agent missing the √3
# no j_max boundary; no Arrow-Debreu α_n calibration

for j in range(-20, 21):
    rates[(n_T0, j)] = r0 + j * dx * np.sqrt(T0)        # ← static drift; no per-step calibration

# Backward induction
for n in range(n_T0, -1, -1):
    for j in range(-20, 21):
        cont = disc * 0.25 * (V[(n+1, j-1)]
                              + 2 * V[(n+1, j)]          # ← constant probabilities (1/4, 1/2, 1/4)
                              + V[(n+1, j+1)])
        V[(n, j)] = cont
```

### Reference `solve.py` (canonical Hull-White trinomial)

```python
self.dt = 1.0 / steps_per_year                          # = 1/12
self.dx = sigma * np.sqrt(3.0 * self.dt)
self.j_max = max(int(np.ceil(0.184 / (a * self.dt))), 1)

def _get_probs(self, j):
    eta = self.a * j * self.dt
    if abs(j) < self.j_max:
        pu = 1.0/6.0 + (eta**2 - eta) / 2.0             # drift-dependent probabilities
        pm = 2.0/3.0 - eta**2
        pd = 1.0/6.0 + (eta**2 + eta) / 2.0
    elif j == self.j_max:                                # mirrored boundary
        pu = 7.0/6.0 + (eta**2 + 3*eta) / 2.0
        ...

def _build(self):                                        # Arrow-Debreu calibration
    for n in range(self.n_steps):
        ...
        self.alpha[n] = (1.0/self.dt) * np.log(numerator / P_target)
```

### Failing tests

All 7 file-existence tests fail (no outputs produced — the agent wrote to `./output/` instead of `/output/`). However, the bugs are visible in the code itself per the system prompt's Case-2 instruction.

### `labels.json` snippet

```json
"wrong_model_measure": {
  "match": true,
  "evidence_step_ids": [205, 206, 207, 213, 250],
  "quote": "dt = 0.5; dx = sigma * np.sqrt(dt); cont = disc * 0.25 * (...)",
  "confidence": 0.85,
  "root_cause_class": "agent_conceptual",
  "notes": "A1.d structural deviation: implementation uses HW notation (a, σ, θ(t)) but is not a Hull-White trinomial tree on 4 axes — (i) Δt=0.5 not 1/12; (ii) Δx=σ√Δt not σ√(3·Δt); (iii) constant probabilities (1/4, 1/2, 1/4) not drift-dependent η-based probs with mirrored boundary; (iv) no Arrow-Debreu α_n calibration. Per A1.d threshold of 2+ structural axes wrong, this is a generic 3-pt lattice approximating dr=σ·dW (no mean reversion), not Hull-White."
},
"missing_extra_formula_term": {
  "match": true,
  "evidence_step_ids": [89, 95],
  "quote": "vol_fwd = sigma * B",
  "confidence": 0.85,
  "root_cause_class": "agent_conceptual",
  "notes": "A2.g — caplet vol formula missing time-integration factor √((1−e^{−2aT₁})/(2a)). Canonical Hull-White caplet vol is σ·B(T₁,T₂)·√((1−e^{−2aT₁})/(2a)) (verified vs reference solve.py line 95). Agent's vol_fwd = σ·B is ~45% too large at T₁=0.5, a=0.1. Distinct from A1.d (tree structure) — different code line, separate root cause."
}
```

(Other 7 modes return `match: false`; numerical_optimization_failure correctly returns false because under the Step-0 prerequisite, A1.d/A2.g own the findings.)

---

## Sample report snippet (after batch judging)

After running the LLM judge across all failed trials and aggregating:

```markdown
# QF-Bench Quant Correctness — Failure Mode Report

Trials with labels: **172**. Mode-level judgments aggregated: **1548**.
Rubric source: empirical taxonomy from QF-Bench PR review (~75 PRs).

## Per-class match rate by `agent_harness × model`

| agent_harness | model       | n_trials | A:Model_pct | B:Convention_pct | C:Data_Numerics_pct |
| ------------- | ----------- | -------- | ----------- | ---------------- | ------------------- |
| claude-code   | haiku45     | 24       | 41.7%       | 33.3%            | 29.2%               |
| claude-code   | sonnet46    | 23       | 26.1%       | 21.7%            | 17.4%               |
| claude-code   | opus46      | 22       | 18.2%       | 13.6%            | 13.6%               |
| codex         | o4-mini     | 24       | 33.3%       | 25.0%            | 33.3%               |
| gemini-cli    | gemini25pro | 21       | 28.6%       | 28.6%            | 23.8%               |
| finance-zero  | gpt5        | 27       | 22.2%       | 18.5%            | 51.9%               |
```

The full report includes per-mode breakdowns (which sub-rubric most often triggers each mode), per-task tables (which tasks systematically trigger which mode), agreement-with-human Cohen's-κ if calibration is run, and a stacked bar chart per `(agent, model)` pair.

Note the C3 (Statistical Variant Mismatch) sub-pattern is the dominant signal: across many failing trials, the root cause is that the instruction named a method without pinning the variant, and different agents picked different defensible variants from training memory. This is *both* an agent-correctness signal (some agents pick the variant the test pins more often) *and* a task-design signal (these tasks should pin the formula or widen the test tolerance).
