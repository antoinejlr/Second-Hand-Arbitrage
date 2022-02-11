#!/bin/bash

# activate virtual python environment
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
conda activate arbitrage

cd src

# run the two python scripts sequentially
# 1st one downloads all the html pages for the searched keyword (here: 'Canon EF' with buy it now option)
# 2nd one scrapes specific data points from all the search pages and adds them to a csv
# 3rd one downloads all the unique html product pages
# 4th one scrapes specific data points from all the product pages and adds them to a csv

Python3 fetch_search_results_pages.py
Python3 save_search_results_products.py
Python3 fetch_product_pages.py
Python3 save_product_pages_details.py