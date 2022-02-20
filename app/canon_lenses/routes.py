import pandas as pd
import numpy as np
from flask import render_template, Blueprint
import glob
import os
from datetime import datetime, timedelta


routes = Blueprint('routes', __name__)

# constants
today = datetime.today()
today_date = str(today.date())
today_minus_3_months = str((today - timedelta(days=90)).date())
today_plus_1_month = str((today + timedelta(days=30)).date())

# data imports and transformation

all_ads = pd.read_csv('app/data/listings_with_summary.csv')

all_ads.loc[:, "price":"price_sold_mean_dif"] = all_ads.loc[:, "price":"price_sold_mean_dif"]\
                                                .apply(lambda x: np.floor(x)).astype('Int64')
all_ads = all_ads.astype(object).where(all_ads.notna(), None)


all_ads['end_date'] = pd.to_datetime(all_ads['end_date']).apply(lambda x: str(x.date()))


best_ads = all_ads.loc[(all_ads['price_sold_max_dif'] > 50) 
                     & (all_ads['price_not_sold_min_dif'] > 30) 
                     & (all_ads['price_sold_mean_dif'] > -100) 
                     & (all_ads['end_date'] > today_date), :]
best_ads = best_ads[best_ads['end_status'] == 'live'].sort_values(by="price", ascending=False)


live_ads = all_ads[all_ads['end_status'] == 'live']

ads_summary = all_ads.drop_duplicates(subset=['model_product'])
ads_summary = ads_summary.sort_values(by='model_product')

# routes


def return_path(paths, product):
    for path in paths:
        if product in path:
            return os.path.split(path)[-1]
    return ""


@routes.route("/")
@routes.route("/home")
def home():
    return render_template('home.html')


@routes.route("/deals")
def deals():
    return render_template('deals.html', tables=best_ads, titles=[''])


@routes.route("/product_index")
def product_index():
    return render_template('product_index.html', tables=ads_summary, titles=[''])


@routes.route("/product/<string:product>")
def product(product):
    product_image_paths = glob.glob('app/static/products/*')
    filename = return_path(product_image_paths, product)
    
    product_all_ads = all_ads[all_ads['model_product'] == product]

    product_live_ads = product_all_ads[product_all_ads['end_status'] == 'live']\
        .sort_values(by='price_sold_max_dif', ascending=False)
    product_sold_ads = product_all_ads[product_all_ads['end_status'] == 'sold']
    product_not_sold_ads = product_all_ads[product_all_ads['end_status'] == 'not sold']

    return render_template('product.html', filename=filename,
                           product_all_ads=product_all_ads,
                           product_live_ads=product_live_ads,
                           product_not_sold_ads=product_not_sold_ads,
                           product_sold_ads=product_sold_ads,
                           today_date=today_date,
                           today_minus_3_months=today_minus_3_months,
                           today_plus_1_month=today_plus_1_month)





