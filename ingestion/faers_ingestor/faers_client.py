import urllib.request
import urllib.error
import json
import logging
import boto3
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://api.fda.gov/drug/event.json"
MAX_LIMIT = 1000
MAX_PAGES = 3

def get_api_key():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId="pharma-pipeline/faers-api-key")
    secret = json.loads(response["SecretString"])
    return secret["api_key"]

def build_date_filter(start_date, end_date):
    """

    :param start_date: str
    :param end_date: str
    :return: str
    """
    return f"receivedate:[{start_date}+TO+{end_date}]"

def fetch_page(search_filter, skip, api_key):
    """

    :param search_filter: str
    :param skip: int
    :return: response.json() (dict)
    """
    params = {
        "search": search_filter,
        "limit": MAX_LIMIT,
        "skip": skip
    }

    url = f"{BASE_URL}?search={search_filter}&limit={MAX_LIMIT}&skip={skip}&api_key={api_key}"
    logger.info(f"Calling URL: {url.replace(api_key, '***')}")

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP {e.code} for URL: {url}")
        logger.error(f"Response body: {e.read().decode()}")
        raise

def fetch_adverse_events(start_date, end_date):
    """

    :param start_date: (str)
    :param end_date: (str)
    :return: (list[dict])
    """
    api_key = get_api_key()
    search_filter = build_date_filter(start_date, end_date)
    all_pages = []
    skip = 0

    for page_num in range(MAX_PAGES):
        logger.info(f"Fetching page {page_num + 1}, skip={skip}")

        try:
            data = fetch_page(search_filter, skip, api_key)
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                logger.info(f"Got {e.code} - no data available for this date range, stopping")
                break
            raise

        results = data.get("results", [])
        if not results:
            logger.info("Empty results page, stopping pagination")
            break

        all_pages.append({
            "page_number": page_num + 1,
            "fetched_at": datetime.utcnow().isoformat(),
            "results": results
        })

        total = data["meta"]["results"]["total"]
        skip += MAX_LIMIT

        if skip >= total:
            logger.info(f"Fetched all available records, total={total}")
            break

        logger.info(f"Fetched page {page_num + 1} of ~{total // MAX_LIMIT + 1}")

    return all_pages