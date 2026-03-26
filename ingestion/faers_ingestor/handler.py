import json
import logging
import os
from datetime import datetime, timezone

import boto3

from faers_client import fetch_adverse_events

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

def get_quarter_dates():
    """
    Returns the start and end dates for the quarter, with dates structured as YYYYMMDD (per FAERS requirements)

    :return: (tuple[str][str])
    """
    now = datetime.now(timezone.utc)
    quarter = (now.month - 1) // 3                                                                                      # quarter is 0-based

    quarter_ranges = {
        0: ("0101", "0331"),
        1: ("0401", "0630"),
        2: ("0701", "0930"),
        3: ("1001", "1231"),
    }

    start_suffix, end_suffix = quarter_ranges[quarter]
    year = str(now.year)

    return (
        year + start_suffix,
        year + end_suffix,
    )

def save_page_to_s3(bucket, page_data, ingest_date, page_number):
    key = (
        f"bronze/faers/"
        f"ingest_date={ingest_date}/"
        f"page_{page_number:03d}.json"
    )

    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(page_data),
        ContentType="application/json"
    )

    logger.info(f"Saved page {page_number} to s3://{bucket}/key")
    return key

def lambda_handler(event, context):
    bucket_name = os.environ["BUCKET_NAME"]
    ingest_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    #start_date, end_date = get_quarter_dates()
    start_date, end_date = "20230701", "20230930"                                                                       # no recent data, just for testing

    logger.info(f"Ingesting FAERS data from {start_date} to {end_date}")

    pages = fetch_adverse_events(start_date, end_date)

    saved_keys = []
    for page_data in pages:
        key = save_page_to_s3(
            bucket=bucket_name,
            page_data=page_data,
            ingest_date=ingest_date,
            page_number=page_data["page_number"]
        )
        saved_keys.append(key)

    logger.info(f"Ingestion complete. Saved {len(saved_keys)} pages")

    return {
        "statusCode": 200,
        "body": {
            "ingest_date": ingest_date,
            "date_range": {"start": start_date, "end": end_date},
            "pages_ingested": len(saved_keys),
            "s3_keys": saved_keys
        }
    }