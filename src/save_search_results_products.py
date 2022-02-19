# scrapes the data from the downloaded html files and saves it in a csv
import csv
import os
import shutil
from datetime import date, timedelta
from pathlib import Path
import glob
import links

from bs4 import BeautifulSoup

rows = []
today = str(date.today() - timedelta(days=0))


def append_details(objects):
    for ind, i in enumerate(objects):
        try:
            id = i["href"]
        except Exception:
            id = None
        try:
            name = (
                BeautifulSoup(f"{i}", "html.parser")
                    .select("div > div:last-of-type > p")[0]
                    .string
            )
        except Exception:
            name = None
        try:
            price = (
                BeautifulSoup(f"{i}", "html.parser")
                    .select(
                    "div > div:last-of-type > div > div:last-of-type > div:last-of-type > h4"
                )[0]
                    .string
            )
        except Exception:
            price = None
        rows.append([id, name, price, today])


def main():
    files_processed = glob.glob(links.TRG_PATH_FULL + f"{today}_*.html")
    if files_processed:
        return True
    else:
        files_to_process = glob.glob(links.SRC_PATH_FULL + f"{today}_*.html")
        file_count = len(files_to_process)
        if file_count:
            for file_num in range(1, file_count + 1):
                file_path = f"../html_to_process/{today}_{file_num}.html"
                with open(file_path, "r") as html:
                    bs = BeautifulSoup(html, "html.parser")
                    objects = (
                        bs.div.div.section.div.div.contents[1].contents[0].main.contents[5].div.contents
                    )
                    append_details(objects)

            with open(f"../csv files/ricardo_{today}.csv", "w") as csv_file:
                writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
                for row in rows:
                    writer.writerow(row)

            for src_file in Path(links.SRC_PATH_FULL).glob("*.html"):
                shutil.move(
                    os.path.join(links.SRC_PATH_FULL, os.path.basename(src_file)),
                    os.path.join(links.TRG_PATH_FULL, os.path.basename(src_file)),
                )
            return True
        else:
            print("No files to process, aborting")
            return False


if __name__ == "__main__":
    main()
