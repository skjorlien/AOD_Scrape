from scrape_modis import AODUrl
import requests


def fetch_json_from_api(aodurl: AODUrl):
    response = requests.get(aodurl.url)

    if response.status_code != 200:
        raise ValueError(f"query failed: {response.text=}, {response.url=}")

    out = response.json()
    return out


def get_all_links(url: str) -> list[str]:
    json = fetch_json_from_api(url)

    downloads = [x['downloadsLink'] for x in json['content']]

    nextpage = json.get('nextPageLink')
    if nextpage:
        future_downloads = get_all_links(nextpage)
        return downloads + future_downloads

    return downloads
