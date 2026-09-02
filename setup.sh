#!/usr/bin/env bash
# One-time setup for the Nitya Panchang pipeline (Debian/Ubuntu).
set -euo pipefail

echo "==> Installing Indic fonts"
sudo apt-get update -qq
sudo apt-get install -y -qq fonts-noto-core fonts-indic fonts-noto-unhinted
fc-cache -f >/dev/null

echo "==> Installing Python packages"
pip install -r requirements.txt

echo "==> Installing Chromium for Playwright"
python3 -m playwright install --with-deps chromium

echo "==> Smoke test"
python3 pipeline.py --dry-run

echo
echo "Setup complete. Copy config.env.example to config.env, fill it in, then:"
echo "  set -a && source config.env && set +a && python3 pipeline.py"
