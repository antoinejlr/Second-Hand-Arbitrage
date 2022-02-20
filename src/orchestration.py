import fetch_search_results_pages
import save_search_results_products
import fetch_product_pages
import save_product_pages_details
import listings_cleansing
import listings_feature_engineering
from model_training import FEATURES, PandasLabelEncoder
import listings_with_prediction
import listings_summary
import socket
import time
import send_email


def isConnected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            sock.close
        return True
    except OSError:
        pass
    return False


if __name__ == "__main__":
    # try 5 times to connect
    flow = False
    try:
        for test in range(5):
            if isConnected():
                flow = True
                break
            print("Failed to connect, trying again in 10s")
            time.sleep(10)

        if flow:
            print("Connection successful, starting script")
            flow = fetch_search_results_pages.main()
        else:
            print('Failed to connect: aborting script')
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

    except Exception:
        flow = False
    send_email.send_email(flow)
