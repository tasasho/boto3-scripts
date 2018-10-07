# coding: utf-8
from __future__ import print_function

import boto3
import json
import time
import urllib

cloudfront = boto3.client("cloudfront")


def lambda_handler(event, context):
    try:
        print("Loading function")

        s3_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        key = urllib.unquote_plus(event["Records"][0]["s3"]["object"]["key"].encode("utf8"))
        print("Bucket: " + s3_bucket_name)
        print("Key: " + key)

        res = cloudfront.list_distributions()
        for distribution in res["DistributionList"]["Items"]:
            if invalidate_cache(distribution, s3_bucket_name, key):
                break

    except Exception as e:
        if e.__class__.__name__ == "InvalidArgument":
            print("Error: The params for calling the CreateInvalidation operation \
                   include Japanese name file or directory.")
        else:
            print(e.message)


def invalidate_cache(distribution, s3_bucket_name, key):
    for origin in distribution["Origins"]["Items"]:
        if origin["DomainName"].find(s3_bucket_name) != 0:
            continue

        params = generate_param(distribution, key)
        res = cloudfront.create_invalidation(
            DistributionId=distribution["Id"],
            InvalidationBatch=params
        )
        print("Success: " + json.dumps(res["Invalidation"]["InvalidationBatch"]))
        return True

    return False

def generate_param(distribution, key):
    cloudfront_name = distribution["DomainName"]

    if distribution["Aliases"]["Quantity"] > 0:
        cloudfront_name = distribution["Aliases"]["Items"][0]

    print("Distribution: " + distribution["Id"] + " (" + cloudfront_name + ")")

    params = {
        "Paths": {"Quantity": 1, "Items": ["/" + key]},
        "CallerReference": str(time.time())
    }
    return params