# scrapes the data from the saved html
import os
from bs4 import BeautifulSoup
from datetime import date
import csv

def append_details(objects):
    for ind, i in enumerate(objects):
        try:
            id = i['href']
        except:
            pass
        try:
            name = BeautifulSoup(f'{i}', 'html.parser').select('div > div:last-of-type > p')[0].string
        except:
            pass
        try:
            price = BeautifulSoup(f'{i}', 'html.parser').select('div > div:last-of-type > div > div:last-of-type > div:last-of-type > h4')[0].string
        except:
            pass
        rows.append([id, name, price, today])
        print(rows[-1])


today = str(date.today())
path, dirs, files = next(os.walk("../html files"))
file_count = len(files)
rows = []

for i in range(1, file_count + 1):
    file_path = f"../html files/{i}.html"
    html = open(file_path, "r")
    bs = BeautifulSoup(html, 'html.parser')
    objects = bs.div.div.section.div.div.contents[1].contents[0].main.contents[5].div.contents
    append_details(objects)
    print(len(rows))


#save data to csv
csvFile = open(f'../csv files/ricardo_{today}.csv', 'w')
writer = csv.writer(csvFile, quoting=csv.QUOTE_NONNUMERIC)
for row in rows:
    writer.writerow(row)
csvFile.close()

