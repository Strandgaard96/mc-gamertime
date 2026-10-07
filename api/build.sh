#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
rm -rf dist lambda.zip
mkdir dist
# The Lambda dependency set is exported from uv.lock (core + the `aws` group),
# hash-pinned, so the zip carries exactly what the tests ran against.
# --locked fails the build if pyproject.toml changed without a re-lock.
uv export --locked --no-default-groups --group aws --format requirements-txt --quiet \
  --output-file dist/.requirements.txt
uv pip install -r dist/.requirements.txt --require-hashes --target dist/ --quiet \
  --python-version 3.12 \
  --python-platform x86_64-manylinux_2_28 \
  --only-binary :all:
rm dist/.requirements.txt
cp -r main.py lib routes dist/
cd dist && zip -qr ../lambda.zip . -x "*.pyc" -x "*/__pycache__/*"
echo "Built lambda.zip ($(du -sh ../lambda.zip | cut -f1))"
