# Performs basic statistical computations on the listings with prediction dataframe
# and saves the resulting dataframe to the flask app's data repository

import pandas as pd
import links


def main():
    source_df = pd.read_csv(links.LISTINGS_WITH_PREDICTIONS)

    summary_stats_uf = source_df[['model_product', 'price', 'end_status']]\
                       .groupby(['model_product', 'end_status'], as_index=False) \
                       .agg({'price': ['mean', 'min', 'max', 'count']})

    summary_stats_uf.columns = ['_'.join([a, b]) if b
                                else ' '.join([a, b]).strip()
                                for a, b in summary_stats_uf.columns]

    summary_stats_uf = summary_stats_uf[~summary_stats_uf['end_status'].str.contains('deleted')]

    summary_stats_pivot = summary_stats_uf.pivot(index='model_product', columns='end_status',
                                                 values=['price_mean', 'price_min',
                                                         'price_max', 'price_count'])\
                                          .reset_index().sort_values(('price_count', 'sold'), ascending=False)

    summary_stats_pivot.columns = ['_'.join([a, b]).replace(' ', '_') if b
                                   else ' '.join([a, b]).strip()
                                   for a, b in summary_stats_pivot.columns]

    summary_stats_pivot.iloc[:, 1:] = summary_stats_pivot.iloc[:, 1:].astype(float)

    all_products = source_df[
        ['page_url', 'title_upper', 'model_product', 'end_date', 'product_quality', 'end_status', 'price']]
    all_products = all_products[all_products['model_product'] != 'Other']

    all_products_with_stats = pd.merge(all_products,
                                       summary_stats_pivot,
                                       how='left',
                                       on='model_product'
                                       )

    all_products_with_stats['price_sold_max_dif'] = all_products_with_stats['price_max_sold'] - all_products_with_stats[
        'price']
    all_products_with_stats['price_not_sold_min_dif'] = all_products_with_stats['price_min_not_sold'] - \
                                                        all_products_with_stats['price']
    all_products_with_stats['price_sold_mean_dif'] = all_products_with_stats['price_mean_sold'] - all_products_with_stats[
        'price']

    all_products_with_stats.to_csv(links.LISTINGS_WITH_SUMMARY, index=False)


if __name__ == "__main__":
    main()
