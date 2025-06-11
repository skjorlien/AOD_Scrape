from config import RAW_DATA_DIR, ED_TOKEN
from urllib.parse import quote
import subprocess
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import date
import sys

# Define the CMR API endpoint and California bounding box coordinates

ENDPOINTS = {
    "products": "measurements/products",
    "regions": "measurements/regions",
    "details": "content/details",
    "archive": "content/archives",
}


class BBox:
    def __init__(self, north, east, south, west):
        self.north = north
        self.east = east
        self.south = south
        self.west = west

    def __str__(self):
        return f"[BBOX]W{self.west} N{self.north} E{self.east} S{self.south}"

    @classmethod
    def from_str(cls, data):
        try:
            datalist = data.split(",")
            if len(datalist) != 4:
                raise ValueError
            return cls(*datalist)
        except ValueError:
            print("Must provide a string of the form 'N,E,S,W'")


class DateRange:
    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end

    def __str__(self):
        return f"{self.start}" if self.end == "" else f"{self.start}..{self.end}"


def generate_month_daterange(start: date) -> DateRange:
    year = start.year + (start.month // 12)
    month = start.month % 12 + 1
    day = start.day
    end = date(year, month, day)
    return DateRange(start, end)


class AODUrl:
    def __init__(self, bbox: BBox, daterange: DateRange, product="MCD19A2", endpoint="archive"):
        self.BASE_URL = "https://ladsweb.modaps.eosdis.nasa.gov/api/v2/"
        self.ENDPOINTS = {
            "products": "measurements/products",
            "regions": "measurements/regions",
            "details": "content/details",
            "archive": "content/archives",
        }
        self.endpoint = self.ENDPOINTS[endpoint]
        self.bbox = bbox
        self.daterange = daterange
        self.product = product
        self.url = self._build_url()

    def _build_query_string(self):
        params = {
            "products": self.product,
            "temporalRanges": self.daterange,
            "regions": self.bbox,
        }
        return "&".join([f"{key}={quote(str(value), safe="[]")}" for key, value in params.items()])

    def _build_url(self):
        q = self._build_query_string()
        url = f"{self.BASE_URL}{self.endpoint}"
        return f"{url}" if q == "" else f"{url}?{q}"

    def __str__(self):
        return self.url


def run_command(aodurl: AODUrl, output_dir: str, token: str) -> None:
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
        "--cut-dirs=3", aodurl.url, "-P", output_dir]

    subprocess.run(command)
    return


def scrape_month_of_data(bbox: BBox, year: int, month: int):
    token = ED_TOKEN
    start_date = date(year, month, 1)
    drange = generate_month_daterange(start_date)

    url = AODUrl(bbox, drange)
    run_command(url, RAW_DATA_DIR, token)
    return


def scrape_year_of_data(bbox: BBox, year: int = 2019) -> None:
    '''
    fetch all files in a year. breaks up queries into 12 months date ranges to take advantage of multithreading
    '''

    print(f"Fetching {year=} Data")
    time.sleep(1)

    months = range(1, 13)

    with ThreadPoolExecutor() as executor:
        executor.map(lambda month: scrape_month_of_data(bbox, year, month), months)

    return


def main():
    args = sys.argv[1:]
    if "--year" not in args:
        print("Usage: scrape_modis.py --year <YEAR> [--month <MONTH>]")

    try:
        year_index = args.index("--year") + 1
        year = int(args[year_index])
    except (IndexError, ValueError):
        print("Error: --year must be followed by an integer")
        sys.exit(1)

    if "--bbox" in args:
        try:
            bbox_index = args.index("--bbox") + 1
            bbox_str = args[bbox_index]
            bbox = BBox.from_str(bbox_str)
        except Exception as e:
            print(f"{e}: --bbox must be followed by a comma-delimited string of floats of the form 'N,E,S,W'")

    else:
        print("No bounding box coordinates provided. Defaulting to California")
        bbox = BBox(32.0, -114.0, 42.0, -125.0)

    if "--month" in args:
        try:
            month_index = args.index("--month") + 1
            month = int(args[month_index])
            if not (1 <= month <= 12):
                raise ValueError
            scrape_month_of_data(bbox, year, month)
        except (IndexError, ValueError):
            print("Error: --month must be followed by an integer between 1 and 12")
            sys.exit(1)
    else:
        scrape_year_of_data(bbox, year)


if __name__ == "__main__":
    main()
