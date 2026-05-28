#!/usr/bin/env bash
set -e

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate

python3 -m pip install -r requirements.txt
python3 -m pip install nonebot2[fastapi]
python3 -m playwright install chromium

python3 main.py
