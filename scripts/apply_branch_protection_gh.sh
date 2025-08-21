
#!/usr/bin/env bash
set -euo pipefail
# Usage: ./scripts/apply_branch_protection_gh.sh owner repo [branch=main]
OWNER="${1:?owner required}"
REPO="${2:?repo required}"
BRANCH="${3:-main}"

echo "Applying branch protection to $OWNER/$REPO:$BRANCH via gh..."
# Require PR reviews, dismiss stale, and required status checks
gh api -X PUT   -H "Accept: application/vnd.github+json"   "/repos/$OWNER/$REPO/branches/$BRANCH/protection"   -f required_status_checks.strict=true   -f required_status_checks.contexts[]="CI - Python"   -f required_status_checks.contexts[]="CI - Docker"   -f enforce_admins=true   -f required_pull_request_reviews.required_approving_review_count=1   -f required_pull_request_reviews.dismiss_stale_reviews=true   -f required_pull_request_reviews.require_code_owner_reviews=false   -f restrictions=
echo "Done."
