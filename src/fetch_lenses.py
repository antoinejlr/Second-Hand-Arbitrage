# Fetches all Canon EF Lenses products feature today on the retail website and saves them to a csv
from datetime import date

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import csv

options = webdriver.FirefoxOptions()
options.headless = True

# instantiate driver
DRIVER_PATH = Service(
    "/Users/Shared/github_projects/Second-Hand-Arbitrage/exec/geckodriver"
)
driver = webdriver.Firefox(service=DRIVER_PATH, options=options)

today = str(date.today())
rows = [("url", "product_title", "price", today)]

i = 0

current_scroll_position, new_height = 0, 1
speed = 20
driver.get(
    "https://www.digitec.ch/en/search?filter=t_pt%3D59%2Ct_bra%3D94&q=canon%20ef&take=200"
)
pageSource = driver.page_source
bs = BeautifulSoup(pageSource, "html.parser")
while current_scroll_position <= new_height:
    try:
        # /html/body/div[1]/div/div[2]/div[1]/main/div/div[2]/div[4]/article[1]/a
        url = (
            bs.html.body.contents[1]
            .contents[1]
            .contents[2]
            .contents[0]
            .main.div.contents[2]
            .contents[-2]
            .contents[i]
            .contents[2]["href"]
        )
        price = (
            bs.html.body.contents[1]
            .contents[1]
            .contents[2]
            .contents[0]
            .main.div.contents[2]
            .contents[-2]
            .contents[i]
            .contents[1]
            .contents[1]
            .contents[0]
            .contents[1]
            .contents[0]
            .contents[1]
            .span.strong.text
        )
        title_head = (
            bs.html.body.contents[1]
            .contents[1]
            .contents[2]
            .contents[0]
            .main.div.contents[2]
            .contents[-2]
            .contents[i]
            .contents[1]
            .contents[1]
            .contents[0]
            .contents[1]
            .contents[0]
            .contents[2]
            .strong.text
        )
        title_body = (
            bs.html.body.contents[1]
            .contents[1]
            .contents[2]
            .contents[0]
            .main.div.contents[2]
            .contents[-2]
            .contents[i]
            .contents[1]
            .contents[1]
            .contents[0]
            .contents[1]
            .contents[0]
            .contents[2]
            .span.text
        )
        title = "".join([title_head, title_body])
        rows.append((url, title, price, today))
        i += 1
    except Exception:
        current_scroll_position += speed
        driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
        new_height = driver.execute_script("return document.body.scrollHeight")
        bs = BeautifulSoup(driver.page_source, "html.parser")
        pass

csvFile = open(f"../product_prices/retail_{today}.csv", "w")
writer = csv.writer(csvFile, quoting=csv.QUOTE_NONNUMERIC)
for row in rows:
    writer.writerow(row)
csvFile.close()
driver.quit()

nb_articles = len(
    bs.html.body.contents[1]
    .contents[1]
    .contents[2]
    .contents[0]
    .main.div.contents[2]
    .contents[-2]
    .contents
)
nb_articles_saved = len(rows) - 1
if nb_articles_saved == nb_articles:
    print(f"Successfully captured {nb_articles_saved} products")
else:
    print(f"Scrapping incomplete: gathered {nb_articles_saved}/{nb_articles}")
