
#!/usr/bin/env bash
set -euo pipefail
# Usage: GITHUB_TOKEN=... ./scripts/apply_branch_protection_curl.sh owner repo [branch=main]
OWNER="${1:?owner required}"
REPO="${2:?repo required}"
BRANCH="${3:-main}"
TOKEN="${GITHUB_TOKEN:?GITHUB_TOKEN required}"

PAYLOAD=$(cat <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["CI - Python", "CI - Docker", "CodeQL"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null
}
JSON
)

curl -sS -X PUT   -H "Authorization: Bearer $TOKEN"   -H "Accept: application/vnd.github+json"   -d "$PAYLOAD"   "https://api.github.com/repos/$OWNER/$REPO/branches/$BRANCH/protection"

echo
echo "Applied protection to $OWNER/$REPO:$BRANCH"
