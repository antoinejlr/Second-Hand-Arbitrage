# fetches the description a product page
import csv
import glob
import dateparser

from bs4 import BeautifulSoup
from tqdm import tqdm
import regex as re
from pathlib import Path
import links


def fetch_page_url(bs: BeautifulSoup) -> str:
    page_url = None
    try:
        page_url = bs.html.head.find_all('link')[4].get('href')
    except Exception:
        pass
    return page_url


def fetch_product_title(bs: BeautifulSoup) -> str:
    product_title = None
    try:
        product_title = (bs.html.body.contents[1].contents[0].contents[3]
                 .contents[2].contents[0].contents[0].contents[0]
                 .contents[2].contents[0].contents[0].contents[0].h1.text
                 )
    except Exception:
        pass
    try:
        product_title = (bs.html.body.contents[1].contents[0].section.contents[1]
                 .contents[0].contents[0].contents[0].contents[2]
                 .contents[0].contents[0].h1.text
                 )
    except Exception:
        pass
    return product_title


def fetch_body_desc(bs: BeautifulSoup) -> str:
    body_description = None
    try :
        body_description = (
            bs.div.div.section.contents[-4]
                .div.div.div.contents[3]
                .div.div.div.section.contents[-1] # 3 divs
                .div.div.contents[-1]
                .article.get_text(separator="\n", strip=True)
        )
    except Exception:
        pass
    try:
        body_description = (
            bs.div.div.section.contents[-4]
                .div.div.div.contents[3]
                .div.div.section.contents[-1] # 2 divs
                .div.div.contents[-1]
                .article.get_text(separator="\n", strip=True)
        )
    except Exception:
        pass
    return body_description


def fetch_head_desc(bs: BeautifulSoup) -> str:
    header_description = None
    try:
        header_description = (
            bs.div.div.section.contents[-4]
                .div.div.div.contents[3]
                .div.div.section.contents[-1]
                .div.div.h2.text
        )
    except Exception:
        pass
    try:
        header_description = (
            bs.div.div.section.contents[-4]
                .div.div.div.contents[3]
                .div.div.div.section.contents[-1]
                .div.div.h2.text
        )
    except Exception:
        pass
    return header_description


def fetch_quality_desc(bs: BeautifulSoup) -> str:
    prod_quality = None
    try:
        prod_quality = (bs.div.div.section.contents[-4]
                        .div.div.div.contents[3]
                        .div.div.div.section.contents[0]
                        .contents[-1].contents[-1].text
                        )
    except Exception:
        pass
    try:
        prod_quality = (bs.div.div.section.contents[-4]
                        .div.div.div.contents[3]
                        .div.div.section.contents[0]
                        .contents[-1].contents[-1].text
                        )
    except Exception:
        pass
    return prod_quality


def fetch_end_date_desc(bs: BeautifulSoup) -> str:
    try:
        end_date_str = (bs.html.body.contents[1].contents[0].contents[3]
            .contents[2].contents[0].contents[0].contents[0]
            .contents[2].contents[0].contents[0].contents[1].contents[1]
            )
        end_date = dateparser.parse(end_date_str).date()
    except Exception:
        end_date_str = (bs.html.body.contents[1].contents[0].section.contents[1]
                        .contents[0].contents[0].contents[0].contents[2]
                        .contents[0].contents[0].span.text
                        )
        end_date_str_re = re.sub(r'(.*\|\s)?', r'', end_date_str)
        end_date = dateparser.parse(end_date_str_re).date()
    return end_date


def fetch_status_desc(bs: BeautifulSoup) -> str:
    status = "Live"
    try:
        status = (bs.html.body.contents[1].contents[0].contents[3]
                  .contents[0].contents[0].contents[0].contents[0]
                  .contents[0].contents[0].contents[1].contents[0].text
                  )
    except Exception:
        pass
    return status


def fetch_price_desc(bs: BeautifulSoup) -> str:
    price = None
    try:
        price = (bs.html.body.contents[1].contents[0].section.contents[2]
                 .contents[0].contents[0].contents[0].contents[2]
                 .contents[0].contents[0].contents[3].contents[0]
                 .contents[1].text
                 )
    except Exception:
        pass
    try:
        price = (bs.html.body.contents[1].contents[0].section.contents[1]
             .contents[0].contents[0].contents[0].contents[2]
             .contents[0].contents[0].contents[3].contents[-2]
             .contents[1].text
             )
    except Exception:
        pass

    return price


def main():
    product_pages = glob.glob(
        "/Users/Shared/github_projects/Second-Hand-Arbitrage/html_product/*"
    )
    with open(links.LISTINGS_UNIQUE, "w") as product_details:

        writer = csv.writer(product_details, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['file_url', 'page_url', 'product_title', 'end_date', 'end_status',
                         'price', 'product_quality', 'header_description', 'body_description'])

        for product_page in tqdm(product_pages):
            with open(product_page, "r") as f:
                bs = BeautifulSoup(f, "html.parser")

                product_page_stem = Path(product_page).stem
                page_url = fetch_page_url(bs)
                product_title = fetch_product_title(bs)
                end_date = fetch_end_date_desc(bs)
                end_status = fetch_status_desc(bs)
                price = fetch_price_desc(bs)
                product_quality = fetch_quality_desc(bs)
                header_description = fetch_head_desc(bs)
                body_description = fetch_body_desc(bs)

                writer.writerow([product_page_stem, page_url, product_title, end_date, end_status,
                                 price, product_quality, header_description, body_description])


if __name__ == "__main__":
    main()
