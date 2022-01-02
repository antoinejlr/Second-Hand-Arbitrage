# fetches the description a product page
import csv
import glob
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from tqdm import tqdm

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


def fetch_product_desc_from_str(html: str) -> str:
    """
    fetches the product description if given the html as string
    :param html: product page html as string
    :return: product description string
    """
    bs = BeautifulSoup(html, "html.parser")
    description = (
        bs.div.div.section.contents[-4]
        .div.div.div.contents[3]
        .div.div.div.section.contents[2]
        .div.div.contents[2]
        .article.p.text
    )
    return description


def fetch_product_desc_from_file(file_name: str) -> tuple:
    """
    fetches the product description if given the html path
    :param file_name: html product page path
    :return: product description string
    """
    file = f"../html_product/{file_name}.html"
    with open(file, "r") as f:
        bs = BeautifulSoup(f, "html.parser")
        body_description = bs.div.div.section.contents[
            1
        ].div.div.div  # .contents[3].div.div.div.section.contents[
        # 2].div.div.contents[-1].article.get_text(separator="\n", strip=True)
        header_description = (
            bs.div.div.section.contents[1]
            .div.div.div.contents[3]
            .div.div.div.section.contents[2]
            .div.div.contents[-2]
            .text
        )

    return header_description, body_description


def url_to_file_name(url):
    # changes url into a valid file name
    file_name_string = "".join(i for i in url if i not in "/:*?<>|\\")
    return file_name_string


def save_page_source(file_name, content):
    file = f"../html_product/{file_name}.html"
    with open(file, "w") as f:
        f.write(content)


def append_to_url_filename_description_mapping(
    url, file_name, header_description, body_description
):
    with open(
        "/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/url_filename_description_mapping.csv",
        "a",
    ) as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([url, file_name, header_description, body_description])


def append_url_to_list_of_urls(url):
    with open(
        "/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/product_page_urls.csv",
        "a",
    ) as file:
        writer = csv.writer(
            file, delimiter="\n", escapechar=" ", quoting=csv.QUOTE_NONE
        )
        writer.writerow([url])


def load_product_pages(product_page_urls: list) -> None:
    """
    Step 1:
    fetches all the product pages in list of urls

    Step 2:
    saves the html files

    Step 3:
    appends url, filename and product description to the mapping csv

    Step 4:
    append the newly capture product page urls to the list of urls for which a product page exist

    :return: None
    """
    for product_page_url in tqdm(product_page_urls):
        # Step 2
        pageSource = fetch_page_source(product_page_url)
        product_file_name = url_to_file_name(product_page_url)
        save_page_source(product_file_name, pageSource)

        # Step 3
        header_description, body_description = fetch_product_desc_from_file(
            product_file_name
        )
        append_to_url_filename_description_mapping(
            product_page_url, product_file_name, header_description, body_description
        )

        # Step 4
        append_url_to_list_of_urls(product_page_url)
        time.sleep(2)


def fetch_all_product_urls() -> list:
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

    urls = list(set(csv_df_valid_dates.url.tolist()))
    return urls


def fetch_new_product_urls() -> list:
    """
    checks the list of urls for which a product page exists
    against the latest list of urls and fetches all the product pages not yet captured
    :return: None
    """
    # Step 1
    product_page_urls_path = "/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/product_page_urls.csv"
    product_page_urls_df = pd.read_csv(product_page_urls_path, names=["url"])
    latest_file_df = pd.DataFrame(fetch_all_product_urls(), columns=["url"])
    new_product_page_urls = list(
        set(
            pd.merge(latest_file_df, product_page_urls_df, how="outer", indicator=True)
            .query('_merge == "left_only"')
            .drop(columns=["_merge"])["url"]
            .to_list()
        )
    )
    return new_product_page_urls


def main():
    urls = fetch_new_product_urls()
    load_product_pages(urls)


if __name__ == "__main__":
    # main()
    print(fetch_product_desc_from_file("fracanon-ef-50mm-f-1.2l-usm-1187571954"))

    # to do --> clean up the Beautiful Soup selectors
    # clean up the mapping file as a result and rerun
    # merge the original dataframe with the one with descriptions
    # use the descriptions to identify the language of the ad
    # harmonize the language of the ads
    # save a list of all Canon products New and used on sale on official websites
    # manually label the different ads
    # feature engineer the product titles
    # train a machine learning model to predict the product from the title of the ad
    #
