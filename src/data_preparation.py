# outcome 3 csv files
# best_ads_today_stats.csv
# hist_ads_stats_agg.csv
# hist_ads_stats_by_prod.csv


# Challenge: comparing historical product ads requires
# linking ads selling the same product together.
# However, the second-hand website input field for the product title is free-hand
# and there is no directory of lens products.
#
# Solution: Use machine learning on a feature set derived from the product titles
# to classify products


# Part 1 - Build historical set by
# - combining ad listing csv files into a pandas dataframe
# - removing duplicate ads
# - merge the dataframe with the ad details
# - remove defective products
# - remove ads that are out of scope (via regular expression)


# Part 2 - Add product labels
# - harmonize title structure (via regex)
# - create product features (via regex)
# - label the data
# ### in parallel ###
# - iterate over several machine learning models (using k-folds)
# --- to get the most relevant features
# --- to get the best performing model
# -> Best performing model is Gaussian Naive Bayes with 10 features (out of 17)
# ###################
# - encode selected features
# - fit a gaussian Naive Bayes model (>80% accuracy during the iterative analysis) to the whole historical data set
# - add the product prediction to the historical dataset


# Part 3 - Create DataSets
# 


















