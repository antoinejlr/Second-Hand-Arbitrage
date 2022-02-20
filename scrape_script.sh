#!/bin/bash

# activate virtual python environment
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
conda activate arbitrage

# shellcheck disable=SC2164
cd src

Python3 orchestration.py

today=$(date +%x)
git add ../arbitrage/data/listings_with_summary.csv
git commit -m "$today update"
git push