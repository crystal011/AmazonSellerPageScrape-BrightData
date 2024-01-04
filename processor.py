import json, utils
from bs4 import BeautifulSoup

def process_record(raw_html, asin):
    '''
    Converts an HTML text to JSON response based on the rules defined.
    '''
    html_parser = BeautifulSoup(raw_html, "lxml")

    url = f"https://www.amazon.com/dp/{asin}"
    title = parse_node(html_parser.select_one('#aod-asin-title-text'))
    all_offers = []
    offers = html_parser.select('#aod-offer')
    pinned_offer = html_parser.select_one('#aod-pinned-offer')

    if offers:
        for offer in offers:
            seller = parse_node(offer.select_one('#aod-offer-soldBy a'))
            all_offers.append({
                "ShipsFrom": parse_node(offer.select_one('#aod-offer-shipsFrom .a-color-base')),
                "SoldBy": "Amazon.com" if seller == "" else seller,
                "Price": parse_node(offer.select_one('.a-price .a-offscreen')),
                "Condition": parse_node(offer.select_one('#aod-offer-heading')),
                "Stars": utils.rgx_find('a-star-mini-([^ ]+)', str(offer.select_one('#aod-offer-seller-rating i'))),
                "Ratings": utils.rgx_find('(\\d+)\\s*rating', parse_node(offer.select_one('#aod-offer-seller-rating #seller-rating-count-\{iter\}'))),
            })

    if pinned_offer:
        pinned_seller = parse_node(pinned_offer.select_one('#aod-offer-soldBy a'))
        all_offers.append({
            "ShipsFrom": parse_node(pinned_offer.select_one('#aod-offer-shipsFrom .a-color-base')),
            "SoldBy": "Amazon.com" if pinned_seller == "" else pinned_seller,
            "Price": parse_node(pinned_offer.select_one('.a-price .a-offscreen')),
            "Condition": parse_node(pinned_offer.select_one('#aod-offer-heading')),
            "Stars": utils.rgx_find('a-star-mini-([^ ]+)', str(pinned_offer.select_one('#aod-offer-seller-rating i'))),
            "Ratings": utils.rgx_find('(\\d+)\\s*rating', parse_node(pinned_offer.select_one('#aod-offer-seller-rating #seller-rating-count-\{iter\}'))),
        })

    return json.dumps({
        "ASIN": asin,
        "url": url,
        "title": title,
        "offers": all_offers,
        "NLA": False
    }, indent=2)

def parse_node(node, arr = False):
    if arr == False:
        if node:
            return node.text.strip()
        return ""
    else:
        r = []
        if node:
            for n in node:
                if n:
                    r.append(n.text.strip())
        return r