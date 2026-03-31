# MEMORY.md — Grim Reviewer Agent

This is the persistent memory index for the reviewer workspace.
Detailed entries live in `memory/YYYY-MM-DD.md` and `memory/*.md`.

---

## Identity

- **Name:** Grim
- **Role:** Senior code reviewer for finbench / QuantitativeFinance-Bench
- **Workspace:** `workspace-reviewer`
- **Emoji:** 🔍

---

## People

- **Steve (Zhihao Ouyang)** — Telegram: 7373369713 — Primary owner, full authority
- **Hui H.** — Telegram: 7378618680 — Admin, full authority
- **Darren Carbox** — Telegram: 8262676934 — Co-owner, domain team lead

---

## Project

- **Project:** finance-bench / QuantitativeFinance-Bench — state-aware financial agent benchmark
- **Primary repo:** oyzh888/QuantitativeFinance-Bench (personal, was Dongzhikang fork)
- **Upstream:** joyceHe703/finance-bench (ignore per Steve)
- **Infra:** DigitalOcean droplet finance-bench-v3 (159.65.5.105)

---

## GitHub Access

- **Primary token (`$GITHUB_TOKEN`):** Fine-grained PAT for `when2buy` org — full push/admin
- **Secondary (oyzh888 personal):** classic PAT `github_pat_11AD3X2HQ0zT31YIuqCzlk_...` — full repo scope, works for PR reviews on personal repos
- **Dongzhikang's token:** Fine-grained PAT for `QF-Bench` org — admin/push
- Full details: `memory/github-tokens.md`
- `gh` CLI v2.65.0+ at `~/bin/gh`
- **All GitHub PR reviews must be written in English** (per Steve, 2026-03-27)

---

## Review Preferences (set by Steve)

- Run code to verify: **YES**
- Multi-agent parallel review: **YES**
- Push reviews to GitHub: **YES** (preferred over Telegram)
- Severity labels: `[CRITICAL]`, `[MAJOR]`, `[MINOR]`, `[NIT]`

---

## Review History

### 2026-03-22 — oyzh888/QuantitativeFinance-Bench#1 (merton-credit-model)
- Oracle: 13/13 tests pass ✅
- Verdict: **REQUEST CHANGES** — 2 blockers
  1. Missing `environment/Dockerfile` — task can't run in benchmark
  2. DD formula bug: divides by `sigma_a` instead of `sigma_a * sqrt(T)` (masked because T=1 in tests)
- Also: circular test, dead scipy dep, no canary in CSVs
- Review posted to GitHub ✅

---

## Key Learnings

- Fine-grained PATs do NOT inherit permissions when user joins new orgs
- `x-oauth-scopes` absent for fine-grained PATs (only classic tokens show it)
- `permissions: {admin: true}` in GET response does NOT guarantee write access — fine-grained scope must explicitly include the org
- Can't use `--request-changes` on own PR; use `--comment` instead

---

## Workspace Repo

- Pushed to: https://github.com/when2buy/reviewer-workspace (private)
- First push: 2026-03-31
