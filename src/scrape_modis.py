from threading import Thread
import requests
from settings import *
from dataclasses import dataclass
from urllib.parse import quote
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor
import time

# NASA Earthdata login credentials
username = ED_user
password = ED_pass
token = ED_token

# Define the CMR API endpoint and California bounding box coordinates
base_url = 'https://ladsweb.modaps.eosdis.nasa.gov/api/v2/'


@dataclass
class EndPoint:
    products: str = "measurements/products"
    regions: str = "measurements/regions"
    details: str = "content/details"
    archive: str = "content/archives"
    

def custom_quote(value: str) -> str:
    '''
    A wrapper around urllib's quote function to escape brackets for ladsweb

    Args:
    value (str): the text to quote

    Returns:
    str: the quoted string for building the url
    '''
    return quote(value, safe="[]")


def build_bbox(west:float, north:float, east:float, south:float) -> str:
    '''
    Build the bounding box url query string for the ladsweb api call

    Args:
    west (float): west in longitude
    north (float): north in longitude
    east (float): east in longitude
    south (float): south in longitude

    Returns:
    str: query string 
    '''
    return f"[BBOX]W{west} N{north} E{east} S{south}"


def build_date_range(start: str, end: str = "") -> str:
    '''
    Build the date range url query string for ladsweb api call

    Args:
    start (str): Start date of query in YYYY-MM-DD format
    end (str): End date of query in YYYY-MM-DD format

    Returns 
    str: query string for api call 
    '''
    date = start
    if end != "":
        date = f"{date}..{end}"
    return date


def build_query_string(params: dict) -> str:
    '''
    Builds the quoted query string for the api call.

    Args:
    params (dict): key value pairs for building the get str

    Returns:
    (str) full formatted query string.
    '''
    return "&".join([f"{key}={custom_quote(str(value))}" for key, value in params.items()])


def build_url(url: str, params: dict = {}) -> str:
    '''
    Takes a url and a dictionary of parameters and builds a full url for get api

    Args:
    url (str): the base url
    params (dict): a dictionary of parameters to include after the '?'

    Returns:
    str: the full url
    '''
    q = build_query_string(params)
    if q != "":
        url = f"{url}?{q}"
    return url


def fetch_json_from_api(base_url: str, endpoint: str = "", params: dict={}):
    url = build_url(f"{base_url}{endpoint}", params)

    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError(f"query failed: {response.text =}, {response.url =}")

    out = response.json()
    return out


def get_all_links(url:str) -> list[str]:
    json = fetch_json_from_api(url) 

    downloads = [x['downloadsLink'] for x in json['content']]
    
    nextpage = json.get('nextPageLink')
    if nextpage:
        future_downloads = get_all_links(nextpage)
        return downloads + future_downloads

    return downloads


def run_command(url: str, output_dir: str, token: str) -> None:
    '''
    runs the ladsweb api call using wget.

    Args:
    url (str): the full url to call
    output_dir (str): a path where we'd like to save the files that match this query.
    token (str): the api token for my EarthData account
    '''
    command = [
        "wget", "-e", "robots=off", "-m", "-np", "-R", ".html,.tmp",
        "-nH", "--header", "X-Requested-With: XMLHttpRequest", 
        "--header", f"Authorization: Bearer {token}",  
        "--cut-dirs=3", url, "-P", output_dir]      
    
    subprocess.run(command)
    return


def fetch_year_of_data(year: int = 2019) -> None:
    '''
    fetch all files in a year. breaks up queries into 12 months date ranges to take advantage of multiprocessing
    '''
    
    print(f"Fetching {year = } Data")
    time.sleep(1)
    ## WARNING: running this on a two day query downloaded 200 mb of data. recommend processing in batches.  
    token = ED_token
    product = 'MCD19A2'  # MCD19A2 is the MAIAC AOD product for MODIS Terra + Aqua
    ca_box = [-125.0, 32.0, -114.0, 42.0]  # Bounding box for California
    

    start_dates = [f"{year}-{i:02}-01" for i in range(1,13)]
    end_dates = [f"{year}-{i:02}-01" for i in range(2, 13)] + [f"{year + 1}-01-01"]
    date_ranges = [build_date_range(start, end) for start, end in zip(start_dates, end_dates)]

    params_list = [{
        "products": product,
        "temporalRanges": drange,
        "regions": build_bbox(*ca_box),
    } for drange in date_ranges]
    
    urls = [build_url(f"{base_url}{EndPoint.archive}", params=params) for params in params_list]
    output_dir = Paths.raw_data
    
    with ThreadPoolExecutor() as executor:
        executor.map(lambda url: run_command(url, output_dir, token), urls)

    return

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        year = int(sys.argv[1])
        fetch_year_of_data(year)

    else:
        print("You must provide a year")
