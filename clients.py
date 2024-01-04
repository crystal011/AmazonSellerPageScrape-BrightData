import requests, random

def get_random_user_agent():
    ua = []
    with open('./data/user-agent-list.txt', 'r') as freader:
        ua = [l.strip() for l in freader.readlines()]
    
    return ua[random.randrange(0, len(ua))]

def generate_new_client(PROXY):
    client = requests.Session()
    
    if PROXY == "UNBLOCKER":
        client.proxies = { 
            'http': 'lum-customer-hl_827f1a13-zone-unblocker:8e4e9o9na6ep@zproxy.lum-superproxy.io:22225',
            'https': 'lum-customer-hl_827f1a13-zone-unblocker:8e4e9o9na6ep@zproxy.lum-superproxy.io:22225'
        }
    if PROXY == "DATA_CENTER":
        client.proxies = {
            'http': 'lum-customer-c_827f1a13-zone-data_center-country-us:zti4y8s6e957@zproxy.lum-superproxy.io:22225',
            'https': 'lum-customer-c_827f1a13-zone-data_center-country-us:zti4y8s6e957@zproxy.lum-superproxy.io:22225'
        }
    if PROXY == "RESIDENTIAL":
        client.proxies = {
            'http': 'lum-customer-c_827f1a13-zone-residential:vh0ofog5pmxw@zproxy.lum-superproxy.io:22225',
            'https': 'lum-customer-c_827f1a13-zone-residential:vh0ofog5pmxw@zproxy.lum-superproxy.io:22225'
        }
    client.verify = False
    client.headers = {
        "User-Agent": get_random_user_agent(),
    }
    client.proxy_type = PROXY
    
    return client

def add_default_headers(client):

    r0 = random.randrange(100, 1000)
    r1 = random.randrange(1000000, 10000000)
    r2 = random.randrange(1000000, 10000000)

    client.headers["Cookie"] = f"i18n-prefs=USD; ubid-acbus={r0}-{r1}-{r2};x-requested-with=XMLHttpRequest;"

    return client