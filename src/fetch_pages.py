# Fetches all product pages and saves them
import time
from datetime import date

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

options = webdriver.FirefoxOptions()
options.headless = True

# instantiate driver
DRIVER_PATH = Service(
    "/Users/Shared/github_projects/Second-Hand-Arbitrage/exec/geckodriver"
)
driver = webdriver.Firefox(service=DRIVER_PATH, options=options)
driver.get("https://www.ricardo.ch/fr/s/canon%20ef?offer_type=fixed_price")
time.sleep(8)
pageSource = driver.page_source
driver.quit()

# save page source
today = str(date.today())
i = 1
file1 = open(f"../html_to_process/{today}_{i}.html", "w")
file1.writelines(pageSource)
file1.close()

# find first link
bs = BeautifulSoup(pageSource, "html.parser")
objects = (
    bs.div.div.section.div.div.contents[1]
    .contents[0]
    .main.contents[6]
    .div.contents[-1]["href"]
)
print(f"{i} page loaded")
# loop until all product pages are iterated over
while objects:
    try:
        # fetch new webpage using last link
        link = "".join(["https://www.ricardo.ch", objects])
        DRIVER_PATH = Service(
            "/Users/Shared/github_projects/Second-Hand-Arbitrage/exec/geckodriver"
        )
        driver = webdriver.Firefox(service=DRIVER_PATH, options=options)
        driver.get(link)
        time.sleep(8)
        pageSource = driver.page_source
        driver.quit()

        # save page source
        i += 1
        file1 = open(f"../html_to_process/{today}_{i}.html", "w")
        file1.writelines(pageSource)
        file1.close()
        print(f"{i} page loaded")

        # find next link
        bs = BeautifulSoup(pageSource, "html.parser")
        objects = (
            bs.div.div.section.div.div.contents[1]
            .contents[0]
            .main.contents[6]
            .div.contents[-1]["href"]
        )
    except Exception:
        break

print(f"operation complete: {i} pages saved")
