import re
import subprocess
import eventlet, datetime, sys, time, clients

DEBUG = False
ALL_ERRORS = 0
ALL_SUCCESS = 0
ALL_BANDWIDTH = 0

def log(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

def die(msg):
    log(msg)
    exit(0)

def rgx_find(rgx, data, all = False):
    results = re.findall(rgx, data, re.IGNORECASE | re.DOTALL)
    if len(results) > 0 and not all:
        return results[0]
    elif len(results) > 0 and all:
        return results
    elif all:
        return []
    else:
        return None

def extract_arr_key(arr, key):
    for i in arr:
        if key in i:
            return i[key]
    return None


def process_command(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out, err


def try_and_fetch(client, url, method = 'GET', data = None, retries = 3, allowed_rcs = [200], invalidation_regex = None, validation_regex = None, timeout = 30, wait_duration = 0):
    global ALL_SUCCESS, ALL_ERRORS, ALL_BANDWIDTH

    curr_retries = 0
    while True:
        if DEBUG: log(f"Fetching [{url}] - Retries {curr_retries}/{retries}")
        try:
            with eventlet.Timeout(timeout):
                if method == 'GET':
                    response = client.get(url, allow_redirects=False)
                elif method == 'POST':
                    response = client.post(url, data=data, allow_redirects=False)

                # Manually calculate Content-Length
                if 'Content-Length' not in response.headers:
                    response.headers['Content-Length'] = len(response.content)

                ALL_BANDWIDTH +=  int(response.headers['Content-Length'])

                if response.status_code not in allowed_rcs:
                    raise Exception(f"URL [{url}] returned an unexpected status code: [{response.status_code}]")
                
                if validation_regex != None and not rgx_find(validation_regex, response.text):
                    raise Exception(f"Validation regex [{validation_regex}] not found, retrying.")

                if invalidation_regex != None and rgx_find(invalidation_regex, response.text):
                    raise Exception(f"Invalidation regex [{validation_regex}] was found, retrying.")
                
                if wait_duration > 0:
                    time.sleep(wait_duration)

                ALL_SUCCESS += 1
                return response
        except:
            if DEBUG: log(sys.exc_info()[1])
            ALL_ERRORS += 1
            
            curr_retries += 1
            if curr_retries >= retries:
                if DEBUG: log(f"Max retries reached, wasn't able to fetch [{url}]")
                break
            
            if DEBUG: log("Generating a new session.")
            client = clients.generate_new_client(client.proxy_type)
            client = clients.add_default_headers(client)


    return None