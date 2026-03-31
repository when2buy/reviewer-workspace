# GitHub Token Reference

## Available Tokens

### 1. Primary Fine-grained PAT (oyzh888) — `GITHUB_TOKEN` env var
- **Prefix:** `github_pat_11AD3X2HQ0XVRGt2bF7RsS_...`
- **Type:** Fine-grained PAT
- **Scope:** `oyzh888` personal repos + `when2buy` org
- **Permissions:** Full (push/maintain/admin) within scoped repos
- **Limitation:** Does NOT cover `QF-Bench` org — cannot write PR reviews, comments, or issues there
- **Source:** `~/.config/gh/hosts.yml`, injected as `$GITHUB_TOKEN`

### 2. Secondary Fine-grained PAT (oyzh888)
- **Prefix:** `github_pat_11AD3X2HQ0zT31YIuqCzlk_...`
- **Type:** Fine-grained PAT (previously thought to be classic — it is NOT)
- **Scope:** Similar to primary, does NOT cover `QF-Bench` org
- **Source:** `~/.git-credentials`
- **Note:** Labeled "deprecated" in skill docs but still active. Same org limitation as primary.

### 3. Dongzhikang's PAT ✅ USE FOR QF-Bench
- **Prefix:** `github_pat_11AKM7ZZI0x9c9K1QWu3RW_...`
- **Type:** Fine-grained PAT
- **Scope:** `QF-Bench` org (admin/push/maintain/triage/pull)
- **Permissions:** Can write PR reviews, issue comments, push code to `QF-Bench/QuantitativeFinance-Bench`
- **Source:** `~/.git-credentials`
- **Use for:** All write operations on `QF-Bench/QuantitativeFinance-Bench`

## Decision Tree

1. **Reading any repo** → any token works (all have read access)
2. **Writing to `oyzh888/*` or `when2buy/*`** → use `$GITHUB_TOKEN` (primary)
3. **Writing to `QF-Bench/*`** → use Dongzhikang's token
4. **PR reviews on QF-Bench** → Dongzhikang's token (tested and confirmed 2026-03-27)

## Key Learnings

- Fine-grained PATs do NOT inherit permissions when user joins new orgs
- `x-oauth-scopes` header is absent for fine-grained PATs (only present for classic tokens)
- Having `admin: true` in repo permissions (read API) does NOT mean the token can write — the token's fine-grained scope must explicitly include the org
- PR review API (`POST /pulls/{id}/reviews`) requires write access; issue comment API (`POST /issues/{id}/comments`) also requires write access
- Both oyzh888 tokens return `permissions: {admin: true}` for QF-Bench repo on GET but fail on POST — misleading

## Language Policy

- **All GitHub PR reviews and comments must be written in English** (per Steve, 2026-03-27)

## Installed Tools

- `gh` CLI v2.67.0 installed at `~/bin/gh` (add `$HOME/bin` to PATH before use)
