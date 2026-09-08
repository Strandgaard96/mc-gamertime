#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
rm -rf dist lambda.zip
mkdir dist
uv pip install -r requirements.txt --target dist/ --quiet \
  --python-version 3.12 \
  --python-platform x86_64-manylinux_2_28 \
  --only-binary :all:
cp -r main.py lib routes handlers dist/
cd dist && zip -r ../lambda.zip . -x "*.pyc" -x "*/__pycache__/*"
echo "Built lambda.zip ($(du -sh ../lambda.zip | cut -f1))"
