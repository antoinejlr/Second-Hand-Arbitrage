# fetches the description a product page
import csv
import glob
import os
import dateparser

from datetime import date
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from tqdm import tqdm
from pathlib import Path
import regex as re

options = webdriver.FirefoxOptions()
options.headless = True
DRIVER_PATH = Service(
    "/Users/Shared/github_projects/Second-Hand-Arbitrage/exec/geckodriver"
)


def fetch_page_source(url: str, branch=True) -> str:
    """
    fetches the html product page
    :param branch: True by default, if url is a full url enter False
    :param url: ricardo product page url
    :return: html string
    """
    if not branch:
        full_url = url
    else:
        root_url = "https://www.ricardo.ch"
        full_url = root_url + url
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
        prod_quality = (bs.div.div.section.contents[-4]
                        .div.div.div.contents[3]
                        .div.div.div.section.contents[0]
                        .contents[-1].contents[-1].text
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

    return header_description, body_description, prod_quality


def append_to_product_details(
        url: str, file_name: str, header_description: str, body_description: str, prod_quality: str
) -> None:
    """
    Adds a row to the product_details csv containing
    :param url: branch url of the product page
    :param file_name: valid file_name based on url
    :param header_description: product description header (sometimes does not exist)
    :param body_description: product description body (always exists)
    :param prod_quality: product quality
    :return: None
    """
    with open(
            "/metadata/listings_unique.csv",
            "a",
    ) as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([url, file_name, header_description, body_description, prod_quality])


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


def product_urls_needing_update() -> list:
    '''
    scans the existing product pages in html_products and
    checks if any product pages have ad end dates prior to today
    if so, the function checks if the information whether the product was sold or not
    if that information is missing it adds it to the list of urls needing an update
    :return: list of urls needing an update
    '''
    today = date.today()
    file_path_list = glob.glob("/Users/Shared/github_projects/Second-Hand-Arbitrage/html_product/*")
    urls_to_fetch = []

    for file in file_path_list:
        with open(file, "r") as f:
            bs = BeautifulSoup(f, "html.parser")

            try:
                end_date_str = (bs.html.body.contents[1].contents[0].section.contents[1]
                                .contents[0].contents[0].contents[0].contents[2]
                                .contents[0].contents[0].span.text
                                )

                end_date_str_re = re.sub(r'(.*\|\s)?', r'', end_date_str)
                end_date = dateparser.parse(end_date_str_re).date()

                if end_date < today:
                    urls_to_fetch.append((Path(file).stem, bs.html.head.find_all('link')[4].get('href')))

            except Exception:
                pass
    return urls_to_fetch


def remove_bid_only_product_pages() -> None:
    """
    It can happen that updated product page are now bid-only which is out of scope
    This function checks for these pages and removes them from the html_product folder
    :return: None
    """
    today = date.today()
    file_path_list = glob.glob("/Users/Shared/github_projects/Second-Hand-Arbitrage/html_product/*")
    pages_to_remove = []
    for file in file_path_list:
        with open(file, "r") as f:
            bs = BeautifulSoup(f, "html.parser")

            try:
                end_date_str = (bs.html.body.contents[1].contents[0].section.contents[1]
                                .contents[0].contents[0].contents[0].contents[2]
                                .contents[0].contents[0].span.text
                                )

                end_date_str_re = re.sub(r'(.*\|\s)?', r'', end_date_str)
                end_date = dateparser.parse(end_date_str_re).date()

                if end_date > today:
                    try:
                        (bs.html.body.contents[1].contents[0].section.contents[1]
                         .contents[0].contents[0].contents[0].contents[2]
                         .contents[0].contents[0].contents[3].a.text
                         )
                    except Exception:
                        pages_to_remove.append(file)
                        pass

            except Exception:
                pass

    for page in pages_to_remove:
        os.remove(page)
    print(f'{len(pages_to_remove)} pages removed')

    with open("/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/urls_to_ignore.txt", "a") as ignored_urls:
        for url in pages_to_remove:
            ignored_urls.write(re.search(r"-(\d*).html$", url)[1] + '\n')


def ad_status() -> None:
    '''
    fetches all product page htmls on disk and outputs to file a csv containing
    the file url, the ad status (whether the product was sold), the price it went for, the end date
    :return: None
    '''
    date.today()
    file_path_list = glob.glob("/Users/Shared/github_projects/Second-Hand-Arbitrage/html_product/*")
    urls_to_fetch = []

    for file in file_path_list:
        with open(file, "r") as f:
            bs = BeautifulSoup(f, "html.parser")

            try:
                end_date_str = (bs.html.body.contents[1].contents[0].contents[3]
                    .contents[2].contents[0].contents[0].contents[0]
                    .contents[2].contents[0].contents[0].contents[1].contents[1]
                    )

                end_status = (bs.html.body.contents[1].contents[0].contents[3]
                              .contents[0].contents[0].contents[0].contents[0]
                              .contents[0].contents[0].contents[1].contents[0].text
                              )

                price = (bs.html.body.contents[1].contents[0].section.contents[2]
                         .contents[0].contents[0].contents[0].contents[2]
                         .contents[0].contents[0].contents[3].contents[0]
                         .contents[1].text
                         )

                end_date = dateparser.parse(end_date_str).date()

                urls_to_fetch.append((Path(file).stem, end_status, price, end_date))

            except Exception:
                end_date_str = (bs.html.body.contents[1].contents[0].section.contents[1]
                                .contents[0].contents[0].contents[0].contents[2]
                                .contents[0].contents[0].span.text
                                )

                price = (bs.html.body.contents[1].contents[0].section.contents[1]
                         .contents[0].contents[0].contents[0].contents[2]
                         .contents[0].contents[0].contents[3].contents[-2]
                         .contents[1].text
                         )

                end_date_str_re = re.sub(r'(.*\|\s)?', r'', end_date_str)
                end_date = dateparser.parse(end_date_str_re).date()

                urls_to_fetch.append((Path(file).stem, "Live", price, end_date))

    with open("/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/ad_status.csv", "w") as file:
        csv_out = csv.writer(file)
        csv_out.writerow(['file_url', 'end_status', 'price', 'end_date'])
        for row in urls_to_fetch:
            csv_out.writerow(row)


def main():
    unique_urls = fetch_unique_product_urls()  # get unique product urls by scanning all csv files
    urls = fetch_new_product_urls(unique_urls)  # keep the url of product pages absent in html_product
    with open("/Users/Shared/github_projects/Second-Hand-Arbitrage/metadata/urls_to_ignore.txt", "r") as urls_to_ignore:
        urls_to_ignore_list = list((url_to_ignore_in_file.strip() for url_to_ignore_in_file in urls_to_ignore))

    # scrape page by page the product urls and save them to html_product
    for url in tqdm(urls):
        if not any(ignore_url in url for ignore_url in urls_to_ignore_list):
            page_source = fetch_page_source(url)
            valid_name = url_to_file_name(url)
            save_page_source(valid_name, page_source)

    # save the product descriptions and quality to disk
    try:
        os.remove("/metadata/listings_unique.csv")
    except FileNotFoundError:
        pass
    for url in tqdm(unique_urls):
        if not any(ignore_url in url for ignore_url in urls_to_ignore_list):
            valid_name = url_to_file_name(url)
            header_description, body_description, product_quality = fetch_product_desc_from_file(
                valid_name
            )
            append_to_product_details(url, valid_name, header_description, body_description, product_quality)

    # update the product pages for which the ads are now closed
    urls_to_update_list = product_urls_needing_update()
    for url_to_update_filename, url_to_update in tqdm(urls_to_update_list):
        page_source = fetch_page_source(url_to_update, branch=False)
        save_page_source(url_to_update_filename, page_source)
    remove_bid_only_product_pages()
    ad_status()


if __name__ == "__main__":
    main()
