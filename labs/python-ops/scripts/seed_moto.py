#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["boto3"]
# ///
"""seed_moto.py: create a few fake resources in a local moto server for aws-report.

Start the server first, in another terminal:
  uvx --from "moto[server]" moto_server -p 5050
Then:
  export AWS_ENDPOINT_URL=http://localhost:5050 AWS_ACCESS_KEY_ID=testing \
         AWS_SECRET_ACCESS_KEY=testing AWS_DEFAULT_REGION=eu-central-1
  uv run scripts/seed_moto.py

It refuses to run unless AWS_ENDPOINT_URL points at your own machine, so it can
never create anything in a real AWS account.
"""

import os
import sys
from urllib.parse import urlparse

import boto3

REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")


def main() -> int:
    endpoint = os.environ.get("AWS_ENDPOINT_URL", "")
    if urlparse(endpoint).hostname not in ("localhost", "127.0.0.1"):
        print("seed_moto: set AWS_ENDPOINT_URL=http://localhost:5050 first", file=sys.stderr)
        return 2

    s3 = boto3.client("s3", region_name=REGION)
    where = {"LocationConstraint": REGION}
    for name in ("shop-invoices", "shop-tmp-exports", "shop-backups"):
        s3.create_bucket(Bucket=name, CreateBucketConfiguration=where)
        # A waiter asks again and again until the bucket exists, or gives up.
        s3.get_waiter("bucket_exists").wait(Bucket=name)
    s3.put_bucket_versioning(Bucket="shop-backups", VersioningConfiguration={"Status": "Enabled"})

    ec2 = boto3.client("ec2", region_name=REGION)
    image = ec2.describe_images(Owners=["amazon"])["Images"][0]["ImageId"]
    tagged = ec2.run_instances(
        ImageId=image,
        InstanceType="t4g.micro",
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": "web-1"}, {"Key": "owner", "Value": "ana"}],
            }
        ],
    )
    untagged = ec2.run_instances(
        ImageId=image,
        InstanceType="t4g.micro",
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": "test-box"}]}
        ],
    )
    ids = [r["Instances"][0]["InstanceId"] for r in (tagged, untagged)]
    ec2.get_waiter("instance_running").wait(InstanceIds=ids)
    print(f"seed_moto: 3 buckets and 2 running instances ({', '.join(ids)}) in {REGION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
