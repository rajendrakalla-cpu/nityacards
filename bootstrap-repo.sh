#!/usr/bin/env bash
# One-shot: create the GitHub repo and push this project to it.
#
#   ./bootstrap-repo.sh                # -> rajendrakalla-cpu/nityacards
#   ./bootstrap-repo.sh other-name
#
# Works whether or not the repo already exists: if it does, this just pushes.
#
# The repo must be PUBLIC: Instagram fetches each card by URL from
# raw.githubusercontent.com, and it cannot authenticate to a private repo.
#
# Needs the GitHub CLI (`gh auth login`) or a GITHUB_TOKEN with `repo` scope.
set -euo pipefail

REPO="${1:-nityacards}"
DESC="Automated daily eight-language Panchang and scripture carousels for @nityasankalpa"

command -v git >/dev/null || { echo "git is required"; exit 1; }

if [ ! -d .git ]; then
  git init -q -b main
fi
git add -A
git diff --cached --quiet || git commit -qm "Nitya Panchang: panchang + scripture carousel pipeline"

if command -v gh >/dev/null; then
  OWNER="$(gh api user --jq .login)"
  if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
    echo "Repo $OWNER/$REPO already exists — pushing to it."
  else
    gh repo create "$OWNER/$REPO" --public --description "$DESC"
  fi
  git remote get-url origin >/dev/null 2>&1 \
    || git remote add origin "https://github.com/$OWNER/$REPO.git"
  git push -u origin main --force-with-lease
elif [ -n "${GITHUB_TOKEN:-}" ]; then
  OWNER="$(curl -fsSL -H "Authorization: Bearer $GITHUB_TOKEN" \
            https://api.github.com/user | python3 -c 'import json,sys;print(json.load(sys.stdin)["login"])')"
  curl -fsSL -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
       -H "Accept: application/vnd.github+json" https://api.github.com/user/repos \
       -d "{\"name\":\"$REPO\",\"description\":\"$DESC\",\"private\":false}" >/dev/null 2>&1 || true
  git remote get-url origin >/dev/null 2>&1 \
    || git remote add origin "https://${GITHUB_TOKEN}@github.com/$OWNER/$REPO.git"
  git push -u origin main --force-with-lease
else
  echo "Install the GitHub CLI (gh) or export GITHUB_TOKEN, then re-run." >&2
  exit 1
fi

echo
echo "Pushed to https://github.com/$OWNER/$REPO"
echo
echo "Next, add these under Settings -> Secrets and variables -> Actions:"
echo "  IG_USER_ID        your Instagram user id"
echo "  IG_ACCESS_TOKEN   long-lived Instagram token"
echo "  GH_IMAGE_TOKEN    fine-grained PAT with Contents: read and write on this repo"
echo
echo "Then run it once by hand:"
echo "  Actions -> Daily Nitya Panchang -> Run workflow -> dry_run = true"
