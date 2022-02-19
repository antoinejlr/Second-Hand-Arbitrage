# Fetches all product search results pages and saves them
# to-do ensure it saves all the pages available (not less)

import links
import time
from datetime import date
import glob

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service


def main():
    options = webdriver.FirefoxOptions()
    options.headless = True
    with webdriver.Firefox(service=Service(links.DRIVER), options=options) as driver:
        driver.get("https://www.ricardo.ch/fr/s/canon%20ef?offer_type=fixed_price")
        time.sleep(5)
        pageSource = driver.page_source

    today = str(date.today())

    bs = BeautifulSoup(pageSource, "html.parser")
    pages = int(
        bs.div.div.section.div.div.contents[1]
            .contents[0]
            .main.contents[6]
            .div.contents[-2].button.span.text
    )

    if glob.glob(f"../html_processed/{today}_{pages}.html") or glob.glob(f"../html_to_process/{today}_{pages}.html"):
        return True
    else:
        page_num = 1
        while page_num <= pages:
            with open(f"../html_to_process/{today}_{str(page_num)}.html", "w") as file1:
                file1.writelines(pageSource)
                print(f"{page_num} page loaded")

            if page_num == pages:
                break
            else:
                # fetch new webpage using last link
                next_page = (
                    bs.div.div.section.div.div.contents[1]
                        .contents[0]
                        .main.contents[6]
                        .div.contents[-1]["href"]
                )
                link = "".join(["https://www.ricardo.ch", next_page])
                with webdriver.Firefox(service=Service(links.DRIVER), options=options) as driver:
                    driver.get(link)
                    time.sleep(5)
                    pageSource = driver.page_source

                bs = BeautifulSoup(pageSource, "html.parser")
                page_num += 1

        return True


if __name__ == "__main__":
    main()
