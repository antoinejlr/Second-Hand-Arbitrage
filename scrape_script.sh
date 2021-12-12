#!/bin/bash

# activate virtual python environment
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
conda activate arbitrage

cd src

# run the two python scripts sequentially
# 1st one downloads all the html pages for the searched keyword (here: 'Canon EF')
# 2nd one scrapes specific data points from all the pages and adds them to a csv

Python3 fetch_pages.py
Python3 page_scraper.py