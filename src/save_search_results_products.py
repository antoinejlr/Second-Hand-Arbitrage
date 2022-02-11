# scrapes the data from the downloaded html files and saves it in a csv
import csv
import os
import shutil
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

src_path = "../html_to_process/"
src_path_full = "/Users/Shared/github_projects/Second-Hand-Arbitrage/html_to_process/"
trg_path_full = "/Users/Shared/github_projects/Second-Hand-Arbitrage/html_processed/"


def append_details(objects):
    for ind, i in enumerate(objects):
        try:
            id = i["href"]
        except Exception:
            pass
        try:
            name = (
                BeautifulSoup(f"{i}", "html.parser")
                .select("div > div:last-of-type > p")[0]
                .string
            )
        except Exception:
            pass
        try:
            price = (
                BeautifulSoup(f"{i}", "html.parser")
                .select(
                    "div > div:last-of-type > div > div:last-of-type > div:last-of-type > h4"
                )[0]
                .string
            )
        except Exception:
            pass
        rows.append([id, name, price, today])


today = str(date.today())
path, dirs, files = next(os.walk("../html_to_process"))
file_count = len(files)
rows = []

for i in range(1, file_count + 1):
    file_path = f"../html_to_process/{today}_{i}.html"
    html = open(file_path, "r")
    bs = BeautifulSoup(html, "html.parser")
    objects = (
        bs.div.div.section.div.div.contents[1].contents[0].main.contents[5].div.contents
    )
    append_details(objects)


# save data to csv
csvFile = open(f"../csv files/ricardo_{today}.csv", "w")
writer = csv.writer(csvFile, quoting=csv.QUOTE_NONNUMERIC)
for row in rows:
    writer.writerow(row)
csvFile.close()

for src_file in Path(src_path).glob("*.*"):
    shutil.move(
        os.path.join(src_path_full, os.path.basename(src_file)),
        os.path.join(trg_path_full, os.path.basename(src_file)),
    )
