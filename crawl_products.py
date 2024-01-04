import urllib3, clients, utils, os, json, config, csv, processor
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS_QUEUE_LENGTH = None
current_crawled_count = 0
current_errors_count = 0


def crawl_product(ASIN):
    global current_crawled_count, current_errors_count

    if os.path.exists(f'./data/items/{ASIN}.json'):
        current_crawled_count += 1  
        return "Cached"

    s = clients.generate_new_client("DATA_CENTER")
    s = clients.add_default_headers(s)

    r = utils.try_and_fetch(s, f'https://www.amazon.com/gp/product/ajax/ref=aod_f_new?asin={ASIN}&pc=dp&filters={{"all":true,"primeEligible":true,"new":true}}&experienceId=aodAjaxMain', 'GET', None, 10, [200, 404], "Captcha", None, 30, 0)

    fetch_status = "SUCCESS"
    if r == None:
        fetch_status = "FAILED"
    elif r.status_code == 404:
        fetch_status = "NLA"
        with open(f'./data/items/{ASIN}.json', 'w', encoding='utf8') as fwriter:
            fwriter.write(json.dumps({"ASIN": ASIN, "NLA": True}))
    else: 
        with open(f'./data/items/{ASIN}.json', 'w', encoding='utf8') as fwriter:
            fwriter.write(processor.process_record(r.text, ASIN))

    current_crawled_count += 1  
    utils.log(f"[{fetch_status}] - Net Bandwidth [{utils.ALL_BANDWIDTH/1024/1024:.2f} MBs] - Fetched [{ASIN}]. Queue: [{current_crawled_count}/{URLS_QUEUE_LENGTH}], errors: [{utils.ALL_ERRORS}]")
    return r


if __name__ == "__main__":
    if not os.path.exists('./data'):
        os.mkdir('./data')
    if not os.path.exists('./data/items'):
        os.mkdir('./data/items')

if not os.path.exists('./asins.xlsx'):
    utils.die("Please make sure the ASIN list is an XLSX file [asins.xlsx] within the same directory.")

ASIN_QUEUE = []
d = pd.read_excel('asins.xlsx', converters={'ASIN': str})
for asin in d['ASIN'].values:
    if asin: # Ensure not empty ASINs
        ASIN_QUEUE.append(asin)

URLS_QUEUE_LENGTH = len(ASIN_QUEUE)


# TEST
# ASIN="B01GW8XTXS"
# s = clients.generate_new_client("DATA_CENTER")
# s = clients.add_default_headers(s)
# r = utils.try_and_fetch(s, f'https://www.amazon.com/gp/product/ajax/ref=aod_f_new?asin={ASIN}&pc=dp&filters={{"all":true,"primeEligible":true,"new":true}}&experienceId=aodAjaxMain', 'GET', None, 10, [200, 404], "Captcha", None, 30, 0)

# with open('test.html', 'w', encoding='utf8') as fwriter:
#     fwriter.write(r.text)


# with open('test.html', 'r', encoding='utf8') as freader:
#     pprint(processor.process_record(freader.read(), "B01GW8XTXS"))

utils.log(f'Loaded [{URLS_QUEUE_LENGTH}] ASINs')

with ThreadPoolExecutor(max_workers=config.WORKERS) as executor:
    results = executor.map(crawl_product, ASIN_QUEUE)
    # We don't care about the returned results, but we need to iterate through them to crawl them.
    for result in results:
        pass