"""Tests for aws-report. moto plays AWS inside this process: nothing leaves your laptop."""

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from python_ops import aws_report

REGION = "eu-central-1"


@pytest.fixture
def aws(monkeypatch):
    """Fake credentials first, then moto. Real keys in your shell can never be used."""
    for name in ("AWS_PROFILE", "AWS_ENDPOINT_URL", "AWS_SESSION_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", REGION)
    with mock_aws():
        yield


def make_bucket(s3, name, versioning=None):
    s3.create_bucket(Bucket=name, CreateBucketConfiguration={"LocationConstraint": REGION})
    if versioning:
        s3.put_bucket_versioning(Bucket=name, VersioningConfiguration={"Status": versioning})


def make_instance(ec2, tags):
    image = ec2.describe_images(Owners=["amazon"])["Images"][0]["ImageId"]
    answer = ec2.run_instances(
        ImageId=image,
        InstanceType="t4g.micro",
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {"ResourceType": "instance", "Tags": [{"Key": k, "Value": v} for k, v in tags.items()]}
        ],
    )
    instance_id = answer["Instances"][0]["InstanceId"]
    # The waiter polls describe_instances until the state is "running".
    ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
    return instance_id


def test_buckets_without_versioning(aws):
    s3 = boto3.client("s3", region_name=REGION)
    make_bucket(s3, "never-versioned")
    make_bucket(s3, "versioned", versioning="Enabled")
    make_bucket(s3, "paused", versioning="Suspended")
    findings = aws_report.buckets_without_versioning(s3)
    assert findings == [
        {"bucket": "never-versioned", "problem": "versioning disabled"},
        {"bucket": "paused", "problem": "versioning suspended"},
    ]


def test_instances_without_owner(aws):
    ec2 = boto3.client("ec2", region_name=REGION)
    make_instance(ec2, {"Name": "web-1", "owner": "ana"})
    lost = make_instance(ec2, {"Name": "test-box"})
    shouting = make_instance(ec2, {"Name": "db-1", "Owner": "li"})  # tag keys differ in case
    findings = aws_report.instances_without_owner(ec2)
    assert [f["instance"] for f in findings] == [lost]
    assert shouting not in [f["instance"] for f in findings]


def test_terminated_instances_are_ignored(aws):
    ec2 = boto3.client("ec2", region_name=REGION)
    gone = make_instance(ec2, {"Name": "old"})
    ec2.terminate_instances(InstanceIds=[gone])
    ec2.get_waiter("instance_terminated").wait(InstanceIds=[gone])
    assert aws_report.instances_without_owner(ec2) == []


def test_unreadable_bucket_is_reported_not_fatal(aws, monkeypatch):
    s3 = boto3.client("s3", region_name=REGION)
    make_bucket(s3, "locked")

    def access_denied(**kwargs):
        raise ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}, "GetBucketVersioning"
        )

    monkeypatch.setattr(s3, "get_bucket_versioning", access_denied)
    findings = aws_report.buckets_without_versioning(s3)
    assert findings == [{"bucket": "locked", "problem": "cannot read versioning (AccessDenied)"}]


def test_main_exit_codes_and_output(aws, capsys):
    assert aws_report.main(["--region", REGION]) == 0  # an empty account is clean
    make_bucket(boto3.client("s3", region_name=REGION), "shop-logs")
    assert aws_report.main(["--region", REGION]) == 1
    out, err = capsys.readouterr()
    assert "S3 buckets without versioning: 1" in out
    assert "account 123456789012" in err  # moto's pretend account number


def test_no_credentials_exits_2(monkeypatch, tmp_path, capsys):
    for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE"):
        monkeypatch.delenv(name, raising=False)
    # Point boto3 at empty config files, and stop it from asking EC2's metadata service.
    monkeypatch.setenv("AWS_CONFIG_FILE", str(tmp_path / "config"))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(tmp_path / "credentials"))
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    assert aws_report.main(["--region", REGION]) == 2
    assert "Unable to locate credentials" in capsys.readouterr().err
