import fetch_search_results_pages
import save_search_results_products
import fetch_product_pages
import save_product_pages_details
import listings_cleansing
import listings_feature_engineering
from model_training import FEATURES, PandasLabelEncoder
import listings_with_prediction
import listings_summary

flow = fetch_search_results_pages.main()
if flow:
    print("All search result pages fetched successfully")
    flow = save_search_results_products.main()
if flow:
    print("Full search product pages saved to csv")
    fetch_product_pages.main()
    print("Product pages fetched successfully")
    save_product_pages_details.main()
    print("Unique listings fetched")
    listings_cleansing.main()
    print("Unique listings cleaned")
    listings_feature_engineering.main()
    print("Unique listing features created")
    listings_with_prediction.main()
    print("Unique listing products predicted")
    listings_summary.main()
    print("Unique listing with summary statistics saved")