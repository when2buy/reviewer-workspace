---
name: github-access
description: GitHub 代码库访问和管理。配置 GitHub 认证、访问 Aitist 代码库、管理 repos。包含实际 token 和常用操作。
---

# GitHub Access

访问和管理 oyzh888 / when2buy 下的 GitHub 代码库。

## Token 清单

### 当前主力 Token（推荐使用）

**Token**: `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`

- 类型：Fine-grained PAT
- 权限：When2Buy org 全权限（push / maintain / admin）
- ✅ 可创建 repo（when2buy 组织）
- 环境变量：`GITHUB_TOKEN`（已注入所有 bot 容器）

### 旧 Token（已废弃）

- `github_pat_11AD3X2HQ0Hz7vceF7y3lG_...` — 仅 selected repos，已弃用
- `github_pat_11AD3X2HQ0zT31YIuqCzlk_...` — 全权限 classic，已替换

## 认证配置

```bash
# 方式 1：直接使用环境变量（推荐，已自动注入）
git clone https://oyzh888:${GITHUB_TOKEN}@github.com/oyzh888/<repo>.git

# 方式 2：配置 git credentials store
git config --global credential.helper store
echo "https://oyzh888:${GITHUB_TOKEN}@github.com" > ~/.git-credentials

# 方式 3：gh CLI
echo "$GITHUB_TOKEN" | gh auth login --with-token
```

## 重要代码库

| Repo | 用途 | 权限 |
|------|------|------|
| `oyzh888/aitist_infru_openclaw` | Aitist 基础设施配置 | private |
| `oyzh888/openclaw-fleet` | Bot fleet 部署配置 | private |
| `when2buy/*` | When2Buy 项目 repos | org admin |

## 常用操作

### Clone 私有 repo

```bash
git clone https://oyzh888:${GITHUB_TOKEN}@github.com/oyzh888/aitist_infru_openclaw.git
git clone https://oyzh888:${GITHUB_TOKEN}@github.com/oyzh888/openclaw-fleet.git
```

### 创建新 repo

```bash
# 在 oyzh888 个人账号下
curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"<repo-name>","private":true}'

# 在 when2buy 组织下
curl -s -X POST https://api.github.com/orgs/when2buy/repos \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"<repo-name>","private":true}'
```

### Push 更新

```bash
cd <repo>
git add -A
git commit -m "message"
git push
```

### GitHub API

```bash
# 列出所有 repo
curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/user/repos?per_page=100" | python3 -c "import sys,json; [print(r['full_name']) for r in json.load(sys.stdin)]"

# 列出 when2buy org repos
curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/orgs/when2buy/repos" | python3 -c "import sys,json; [print(r['full_name']) for r in json.load(sys.stdin)]"

# 验证 token
curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/user | python3 -c "import sys,json; d=json.load(sys.stdin); print('User:', d.get('login'), '| Plan:', d.get('plan',{}).get('name','unknown'))"
```

## 在 Bot 中使用

`GITHUB_TOKEN` 已注入所有 bot 容器环境变量，可直接使用：

```bash
# 验证是否已注入
echo $GITHUB_TOKEN | cut -c1-20  # 应显示 github_pat_11AD3X2HQ0...

# 如未注入，手动设置
export GITHUB_TOKEN="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"
```
