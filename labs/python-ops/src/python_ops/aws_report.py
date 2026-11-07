"""aws-report: find S3 buckets without versioning and EC2 instances without an owner tag.

Examples:
  aws login --profile learn          # the sign-in from Day 13
  uv run aws-report --profile learn --region us-east-1
  AWS_ENDPOINT_URL=http://localhost:5050 uv run aws-report   # a local moto server

The report only reads: it calls List, Get and Describe APIs and changes nothing.
Exit codes: 0 nothing found, 1 findings, 2 could not ask AWS.
"""

import argparse
import json
import logging
import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError

log = logging.getLogger("aws-report")

# Instances in these states still exist (and stopped ones can still cost money for disks).
LIVE_STATES = ["pending", "running", "stopping", "stopped"]


def buckets_without_versioning(s3) -> list[dict]:
    findings = []
    # list_buckets returns pages too; a paginator asks for every page for you.
    for page in s3.get_paginator("list_buckets").paginate():
        for bucket in page.get("Buckets", []):
            name = bucket["Name"]
            try:
                answer = s3.get_bucket_versioning(Bucket=name)
            except ClientError as err:
                # One bucket we may not read should not hide the rest of the report.
                code = err.response["Error"]["Code"]
                findings.append({"bucket": name, "problem": f"cannot read versioning ({code})"})
                continue
            # "Enabled", "Suspended", or no Status at all (never turned on).
            status = answer.get("Status", "Disabled")
            if status != "Enabled":
                findings.append({"bucket": name, "problem": f"versioning {status.lower()}"})
    return findings


def instances_without_owner(ec2, tag_key: str = "owner") -> list[dict]:
    findings = []
    pages = ec2.get_paginator("describe_instances").paginate(
        Filters=[{"Name": "instance-state-name", "Values": LIVE_STATES}]
    )
    # search() runs a JMESPath expression (as in --query on Day 13) over every page.
    for instance in pages.search("Reservations[].Instances[]"):
        tags = {t["Key"].lower(): t["Value"] for t in instance.get("Tags", [])}
        if not tags.get(tag_key.lower()):
            findings.append(
                {
                    "instance": instance["InstanceId"],
                    "state": instance["State"]["Name"],
                    "name": tags.get("name", "-"),
                    "problem": f"no {tag_key} tag",
                }
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aws-report", description=__doc__.splitlines()[0])
    parser.add_argument("--profile", help="profile from ~/.aws/config (default: AWS_PROFILE)")
    parser.add_argument("--region", help="region for EC2 (default: from the profile)")
    parser.add_argument("--owner-tag", default="owner", help="tag every instance needs")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    # Our own messages at INFO; other libraries (botocore) only from WARNING up.
    logging.basicConfig(format="%(name)s: %(message)s", stream=sys.stderr, force=True)
    log.setLevel(logging.INFO)

    try:
        # A session holds one set of credentials and one region; clients come from it.
        session = boto3.Session(profile_name=args.profile, region_name=args.region)
        who = session.client("sts").get_caller_identity()
        log.info("account %s, region %s, as %s", who["Account"], session.region_name, who["Arn"])
        buckets = buckets_without_versioning(session.client("s3"))
        instances = instances_without_owner(session.client("ec2"), args.owner_tag)
    except ClientError as err:
        error = err.response["Error"]
        log.error("AWS said %s: %s", error["Code"], error["Message"])
        return 2
    except BotoCoreError as err:
        # No credentials, an unknown profile, an expired sign-in, no region, no network
        log.error("%s", err)
        return 2

    if args.format == "json":
        print(json.dumps({"buckets": buckets, "instances": instances}, indent=2))
    else:
        print(f"S3 buckets without versioning: {len(buckets)}")
        for f in buckets:
            print(f"  {f['bucket']:<40} {f['problem']}")
        print(f"EC2 instances missing the {args.owner_tag} tag: {len(instances)}")
        for f in instances:
            print(f"  {f['instance']:<22} {f['state']:<9} {f['name']}")
    return 1 if buckets or instances else 0


if __name__ == "__main__":
    sys.exit(main())
