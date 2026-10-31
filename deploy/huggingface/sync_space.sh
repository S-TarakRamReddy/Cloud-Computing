#!/usr/bin/env bash
# Assemble the Hugging Face Space from this repository and push it.
#
# Required environment:
#   HF_TOKEN   a Hugging Face access token with write access to the Space
# Optional:
#   HF_SPACE   owner/name of the Space (default Tkcy1205/cloud-fraud-detection)
#   HF_REMOTE  full git URL to push to, instead of the Space (used for testing)
set -euo pipefail

SPACE="${HF_SPACE:-Tkcy1205/cloud-fraud-detection}"
OWNER="${SPACE%%/*}"
SRC="$(git rev-parse --show-toplevel)"
SHA="$(git rev-parse --short HEAD)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

if [ -n "${HF_REMOTE:-}" ]; then
  REMOTE="$HF_REMOTE"
else
  : "${HF_TOKEN:?HF_TOKEN is required}"
  REMOTE="https://${OWNER}:${HF_TOKEN}@huggingface.co/spaces/${SPACE}"
fi

export GIT_TERMINAL_PROMPT=0
git lfs install --skip-smudge >/dev/null 2>&1 || true
git clone --quiet "$REMOTE" "$WORK/space"
cd "$WORK/space"
git lfs install --local >/dev/null 2>&1 || true
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# Replace everything except the platform's own .gitattributes (it holds the Git LFS rules)
git ls-files | grep -v '^\.gitattributes$' | xargs -r git rm -q -f --

mkdir -p backend frontend ml/model
cp -r "$SRC/backend/." backend/
cp -r "$SRC/frontend/." frontend/
for f in best_model.pkl feature_names.pkl scaler.pkl threshold.json model_card.json; do
  cp "$SRC/ml/model/$f" ml/model/
done
cp "$SRC/deploy/huggingface/app.py" app.py
cp "$SRC/deploy/huggingface/README.md" README.md
cp "$SRC/deploy/huggingface/requirements.txt" requirements.txt
find . -name __pycache__ -type d -prune -exec rm -rf {} +

git add -A
if git diff --cached --quiet; then
  echo "Space is already up to date with ${SHA}"
  exit 0
fi
git commit --quiet -m "Deploy ${SHA} from GitHub Actions (S-TarakRamReddy/Cloud-Computing)"
git push --quiet origin HEAD:main
echo "Deployed ${SHA} to ${SPACE}"
