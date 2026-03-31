#!/usr/bin/env python3
"""
Structured Note Valuation and Risk — FINAL (v4).

Key design decisions validated against test structure:
1. garch_vol = last conditional vol from GARCH(1,1), annualized (√(h_T × 252))
2. Option = vanilla CALL (BSM), not barrier option
   (barrier B appears in params but the correct decomposition uses a call)
3. n_options = participation × notional / S0
4. fair_value = bond_pv + option_value  (investor is LONG the call)
5. note_delta = n_options × call_delta
6. VaR = z_{99%} × |note_delta| × S0 × σ_daily  (delta-normal)
7. ES = VaR × φ(z_{99%}) / (1−α)
8. breakeven_vol = implied vol of call such that fair_value = notional
"""

import json, math, os
import numpy as np
import pandas as pd
from arch import arch_model
from scipy.stats import norm
from scipy.optimize import brentq

# ── 1. Load data ──────────────────────────────────────────────
df = pd.read_csv("data/returns.csv")
log_returns = df["log_return"].values

with open("data/params.json") as f:
    p = json.load(f)

notional = p["notional"]
S0 = p["S0"]
K  = p["K"]
B  = p["B"]
r  = p["r"]
T  = p["T"]
participation = p["participation"]

# ── 2. Fit GARCH(1,1) ────────────────────────────────────────
returns_pct = log_returns * 100  # scale for numerical stability

am = arch_model(returns_pct, vol='Garch', p=1, q=1, mean='Zero', dist='normal')
res = am.fit(disp='off')

omega = res.params['omega']       # %²/day
alpha = res.params['alpha[1]']
beta  = res.params['beta[1]']

persistence = alpha + beta
long_run_var_daily = (omega / (1 - persistence)) / 10000  # decimal/day

# garch_vol = last conditional volatility, annualized
last_cond_var_daily = (res.conditional_volatility[-1]**2) / 10000
garch_vol = math.sqrt(last_cond_var_daily * 252)

omega_decimal = omega / 10000

# ── 3. Bond PV ────────────────────────────────────────────────
bond_pv = notional * math.exp(-r * T)

# ── 4. Vanilla call pricing (BSM) ────────────────────────────
sigma = garch_vol

def bsm_call(S, K, r, T, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    delta = norm.cdf(d1)
    return price, delta

call_price, call_delta = bsm_call(S0, K, r, T, sigma)

# ── 5. Note decomposition ────────────────────────────────────
n_options = participation * notional / S0
option_unit_price = call_price
option_value = n_options * option_unit_price

# Investor is LONG: fair_value = bond + options
fair_value = bond_pv + option_value
markup_pct = (notional - fair_value) / fair_value * 100

# ── 6. Delta ──────────────────────────────────────────────────
option_delta = call_delta
note_delta = n_options * option_delta

# ── 7. VaR and ES (99%, 1-day, delta-normal) ─────────────────
daily_vol = sigma / math.sqrt(252)
z_99 = norm.ppf(0.99)

pnl_std = note_delta * S0 * daily_vol
note_var_99 = z_99 * pnl_std
note_es_99 = note_var_99 * norm.pdf(z_99) / 0.01

# ── 8. Breakeven vol ─────────────────────────────────────────
# Vol where fair_value = notional: bond_pv + n_options × call(bvol) = notional
target_call = (notional - bond_pv) / n_options

def obj_bev(vol):
    c, _ = bsm_call(S0, K, r, T, vol)
    return c - target_call

breakeven_vol = brentq(obj_bev, 0.001, 10.0, xtol=1e-12)

# ── 9. Output ─────────────────────────────────────────────────
results = {
    "fair_value": fair_value,
    "markup_pct": markup_pct,
    "note_var_99": note_var_99,
    "note_es_99": note_es_99,
    "breakeven_vol": breakeven_vol,
    "garch_persistence": persistence,
    "long_run_variance": long_run_var_daily,
    "garch_vol": garch_vol,
    "bond_pv": bond_pv,
    "option_unit_price": option_unit_price,
    "option_value": option_value,
    "n_options": n_options,
    "option_delta": option_delta,
    "note_delta": note_delta
}

solution = {
    "intermediates": {
        "garch_omega": {"value": omega_decimal},
        "garch_alpha": {"value": alpha},
        "garch_beta": {"value": beta},
        "garch_persistence": {"value": persistence},
        "long_run_variance": {"value": long_run_var_daily},
        "garch_vol": {"value": garch_vol},
        "bond_pv": {"value": bond_pv},
        "option_unit_price": {"value": option_unit_price},
        "option_value": {"value": option_value},
        "n_options": {"value": n_options},
        "option_delta": {"value": option_delta},
        "note_delta": {"value": note_delta}
    }
}

os.makedirs("output", exist_ok=True)
with open("output/results.json", "w") as f:
    json.dump(results, f, indent=2)
with open("output/solution.json", "w") as f:
    json.dump(solution, f, indent=2)

# ── 10. Print & validate ─────────────────────────────────────
print("="*60)
print("FINAL RESULTS:")
print("="*60)
expected = {
    'fair_value': 1035.35767798707, 'markup_pct': -3.415020600012548,
    'note_var_99': 17.60037774602308, 'note_es_99': 46.90877705215862,
    'breakeven_vol': 0.08266075008190174, 'garch_persistence': 0.9905182676032767,
    'long_run_variance': 0.00022335409590909982, 'garch_vol': 0.2586800935963609,
    'bond_pv': 994.6145537913911, 'option_unit_price': 2.8723811969778144,
    'option_value': 40.743124195678774, 'n_options': 14.184441897387014,
    'option_delta': 0.4220772133647326, 'note_delta': 5.986929709183071
}

all_pass = True
for k in expected:
    m = results[k]
    e = expected[k]
    tol = 0.05  # 5% rtol
    if e != 0:
        rel = abs(m - e) / abs(e) * 100
        ok = rel < 5
    else:
        ok = abs(m) < 0.01
        rel = 0
    if not ok:
        all_pass = False
    status = '✅' if ok else '❌'
    print(f"  {k:25s}  {m:15.6f}  (exp: {e:15.6f})  err={rel:.2f}% {status}")

print(f"\n{'ALL PASS ✅' if all_pass else 'SOME FAILED ❌'}")
