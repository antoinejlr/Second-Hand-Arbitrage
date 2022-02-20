import glob
import pandas as pd
from pathlib import Path
import sys

sys.path.append('..')

from src.links import PRODUCT_IMAGES, LISTINGS_WITH_SUMMARY


def missing_pictures():
    """
    Checks if each product has an associated picture
    :return:
    """
    unique_products = pd.read_csv(LISTINGS_WITH_SUMMARY) \
        .drop_duplicates("model_product")["model_product"].to_list()

    pictures = map(lambda x: Path(x).absolute().stem, glob.glob(PRODUCT_IMAGES + "*"))

    missing_pictures = set(unique_products) - set(pictures)
    return missing_pictures

def redundant_pictures():
    """
    Checks if each product has an associated picture
    :return:
    """
    unique_products = pd.read_csv(LISTINGS_WITH_SUMMARY) \
        .drop_duplicates("model_product")["model_product"].to_list()

    pictures = map(lambda x: Path(x).absolute().stem, glob.glob(PRODUCT_IMAGES + "*"))

    redundant_pictures = set(pictures) - set(unique_products)
    return redundant_pictures


print(redundant_pictures())
