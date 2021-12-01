# Fetches all product pages and saves them

import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

options = webdriver.FirefoxOptions()
options.headless = True

# instantiate driver
DRIVER_PATH = Service('/Users/antoinejlr/Documents/5 Data Science/github_projects/Second-Hand-Arbitrage/exec/geckodriver')
driver = webdriver.Firefox(service=DRIVER_PATH, options=options)
driver.get('https://www.ricardo.ch/fr/s/canon%20ef?offer_type=fixed_price')
pageSource = driver.page_source
driver.quit()

# save page source
i = 1
file1 = open(f"../html files/{i}.html", "a")
file1.writelines(pageSource)
file1.close()

# find first link
bs = BeautifulSoup(pageSource, 'html.parser')
objects = bs.div.div.section.div.div.contents[1].contents[0].main.contents[6].div.contents[-1]['href']
print(objects)

# loop until all product pages are iterated over
while objects:
    try:
        time.sleep(5)
        # fetch new webpage using last link
        link = "".join(['https://www.ricardo.ch', objects])
        DRIVER_PATH = Service(
           '/Users/antoinejlr/Documents/5 Data Science/github_projects/Second-Hand-Arbitrage/exec/geckodriver')
        driver = webdriver.Firefox(service=DRIVER_PATH, options=options)
        driver.get(link)
        pageSource = driver.page_source
        driver.quit()

        # save page source
        i += 1
        file1 = open(f"../html files/{i}.html", "a")
        file1.writelines(pageSource)
        file1.close()

        # find next link
        bs = BeautifulSoup(pageSource, 'html.parser')
        objects = bs.div.div.section.div.div.contents[1].contents[0].main.contents[6].div.contents[-1]['href']
    except:
        break

print(f'operation complete: {i} pages saved')

