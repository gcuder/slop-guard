#!/bin/sh
# Every language pack exposes its checks here, so the root runner needs no per-language knowledge.
set -e
cd "$(dirname "$0")"
PYTHONPATH=src:tests python3 -m unittest discover -s tests -t tests
PYTHONPATH=src python3 -m slop_guard src tests
