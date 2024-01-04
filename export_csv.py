from asyncio import start_server
import glob
import json
import csv
import html
import utils
import pandas as pd

data = []

data.append([
    'ASIN',
    'URL',
    'Title',
    'Price',
    'ShipsFrom',
    'SoldBy',
    'Stars',
    'Rating',
    'Condition',
    'NLA',
])

curr = 0
all_items = glob.glob('./data/items/*.json')
for path in all_items:
    curr += 1
    print(f'{curr}/{len(all_items)} - {path}')
    with open(path, 'r', encoding='utf8') as file:
        try:
            js = json.loads(file.read())
        except:
            print(f"ERROR PARSING: {path}")
            continue

        if js['NLA'] == True:
            data.append([js['ASIN'], "", "", "", "", "", "", "", "", "Yes"])
            continue

        price = float('inf')
        shipsFrom = ""
        soldBy = ""
        condition = ""
        stars = ""
        rating = ""


        for offer in js['offers']:
            if offer['Price'] == '':
                continue
            if offer['Condition'] != "New":
                continue

            if float(offer['Price'].replace('$', '').replace(',', '')) < price:
                price = float(offer['Price'].replace('$', '').replace(',', ''))
                shipsFrom = offer['ShipsFrom']
                soldBy = offer['SoldBy']
                condition = offer['Condition']
                stars = offer['Stars']
                rating = offer['Ratings']

        if price == float('inf'):
            data.append([js['ASIN'], "", "", "", "", "", "", "", "", "Yes"])
            continue

        data.append([
            js['ASIN'],
            js['url'],
            js['title'],
            price,
            shipsFrom,
            soldBy,
            stars.replace("-", ".") if stars != None else "",
            rating,
            condition,
            "No"
        ])

df = pd.DataFrame(data=data)
df.to_excel('./items.xlsx', index=False, header=False)
print('Saved to [items.xlsx]')
        