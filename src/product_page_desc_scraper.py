# fetches the description a product page
import csv
import glob
import os

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from tqdm import tqdm
from pathlib import Path

options = webdriver.FirefoxOptions()
options.headless = True
DRIVER_PATH = Service(
    "/Users/Shared/github_projects/Second-Hand-Arbitrage/exec/geckodriver"
)

# URL Quick Access for Tests
root_url = "https://www.ricardo.ch"
branch_url = "/fr/a/objektiv-canon-ef-100mm-1-2.-8l-makro-1193871126/"
branch_url_2 = "/fr/a/canon-50mm-1.8-ef-1193903100/"
# full url = 'https://www.ricardo.ch/fr/a/objektiv-canon-ef-100mm-1-2.-8l-makro-1193871126/'
full_url = root_url + branch_url
# full url 2 = 'https://www.ricardo.ch/fr/a/canon-50mm-1.8-ef-1193903100/'
full_url_2 = root_url + branch_url_2


def fetch_page_source(branch_url: str) -> str:
    """
    fetches the html product page
    :param branch_url: ricardo product page url
    :return: html string
    """
    root_url = "https://www.ricardo.ch"
    full_url = root_url + branch_url
    driver = webdriver.Firefox(service=DRIVER_PATH, options=options)
    driver.get(full_url)
    pageSource = driver.page_source
    driver.close()
    return pageSource


def url_to_file_name(url: str) -> str:
    """
    changes url into a valid file name
    :param url: branch url
    :return: branch url as a valid file name
    """
    file_name_string = "".join(i for i in url if i not in "/:*?<>|\\")
    return file_name_string


def save_page_source(file_name: str, content: str) -> None:
    """
    saves content with file_name in the html_product folder
    :param file_name: valid file name
    :param content: page source
    :return: None
    """
    file = f"../html_product/{file_name}.html"
    with open(file, "w") as f:
        f.write(content)


def fetch_product_desc_from_file(file_name: str) -> tuple:
    """
    fetches the product description if given the html path
    :param file_name: html product page path
    :return: product description string
    """
    file = f"../html_product/{file_name}.html"
    with open(file, "r") as f:
        bs = BeautifulSoup(f, "html.parser")
        body_description = (
            bs.div.div.section.contents[-4]
                .div.div.div.contents[3]
                .div.div.div.section.contents[-1]
                .div.div.contents[-1]
                .article.get_text(separator="\n", strip=True)
        )
        try:
            header_description = (
                bs.div.div.section.contents[-4]
                    .div.div.div.contents[3]
                    .div.div.div.section.contents[-1]
                    .div.div.h2.text
            )
        except AttributeError:
            header_description = None

    return header_description, body_description


def append_to_url_filename_description_mapping(
        url: str, file_name: str, header_description: str, body_description: str
) -> None:
    """
    Adds a row to the url_filename_description_mapping csv containing
    :param url: branch url of the product page
    :param file_name: valid file_name based on url
    :param header_description: product description header (sometimes does not exist)
    :param body_description: product description body (always exists)
    :return: None
    """
    with open(
            "/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/url_filename_description_mapping.csv",
            "a",
    ) as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([url, file_name, header_description, body_description])


def fetch_unique_product_urls() -> list:
    """
    isolates unique urls from all the csv files captured to date
    :return: list of all product urls
    """
    # fetch all csv file paths
    csv_file_path_list = glob.glob(
        "/Users/Shared/github_projects/Second-Hand-Arbitrage/csv files/*"
    )

    # create dataframe shell and append all csv contents
    csv_df = pd.DataFrame(columns=["url", "title", "price", "date"])

    for csv_path in csv_file_path_list:
        csv = pd.read_csv(csv_path, names=["url", "title", "price", "date"])
        csv_df = csv_df.append(csv)

    # remove data for dates where entries are under 100 (these are outliers where scrapping did not fully complete)
    csv_df_reject = csv_df.groupby(csv_df["date"]).count() < 100
    rejected_dates = csv_df_reject.index[csv_df_reject["url"] is True].tolist()
    csv_df_valid_dates = csv_df[~csv_df["date"].isin(rejected_dates)]

    unique_product_urls = list(set(csv_df_valid_dates.url.tolist()))
    return unique_product_urls


def fetch_new_product_urls(unique_product_urls: list) -> list:
    """
    checks the list of urls for which a product page exists
    against the latest list of urls and fetches all the product pages not yet captured
    :return: None
    """
    csv_file_path_list = glob.glob(
        "/Users/Shared/github_projects/Second-Hand-Arbitrage/html_product/*"
    )
    product_urls = [Path(full_path).stem for full_path in csv_file_path_list]
    product_page_urls_df = pd.DataFrame(product_urls, columns=["file_url"])
    unique_file_urls = list(map(url_to_file_name, unique_product_urls))
    latest_file_df = pd.DataFrame(zip(unique_product_urls, unique_file_urls), columns=["url", "file_url"])
    new_product_urls = list(
        set(
            pd.merge(latest_file_df, product_page_urls_df, how="outer", on='file_url', indicator=True)
                .query('_merge == "left_only"')
                .drop(columns=["_merge"])["url"]
                .to_list()
        )
    )
    return new_product_urls


def main():
    unique_urls = fetch_unique_product_urls()  # get unique product urls by scanning all csv files
    urls = fetch_new_product_urls(unique_urls)  # keep the url of product pages absent in html_product
    for url in tqdm(urls):  # scrape page by page the product urls and save them to html_product
        page_source = fetch_page_source(url)
        valid_name = url_to_file_name(url)
        save_page_source(valid_name, page_source)
    os.remove("/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/url_filename_description_mapping.csv")
    for url in tqdm(unique_urls):  # keep the
        valid_name = url_to_file_name(url)
        header_description, body_description = fetch_product_desc_from_file(
            valid_name
        )
        append_to_url_filename_description_mapping(url, valid_name, header_description, body_description)


if __name__ == "__main__":
    main()

    # merge the original dataframe with the one with descriptions
    # use the descriptions to identify the language of the ad
    # harmonize the language of the ads
    # save a list of all Canon products New and used on sale on official websites
    # manually label the different ads
    # feature engineer the product titles
    # train a machine learning model to predict the product from the title of the ad
    #
