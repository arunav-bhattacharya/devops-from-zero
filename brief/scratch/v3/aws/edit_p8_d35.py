#!/usr/bin/env python3
"""Day 35 (content/p8.json): replace the AWS account, CLI and credential setup that
Days 13 and 14 now teach with short pointers. Re-runnable: each edit checks
whether it was already applied. Touches only lesson d35.
Run: python3 brief/scratch/v3/aws/edit_p8_d35.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
P8 = ROOT / "content" / "p8.json"

SEC1 = {
    "h": "Before any cloud: the account from Day 13, and what today costs",
    "body": (
        "Everything on AWS today is optional. The rest of the course runs on your laptop, and the worked example below needs no account.\n\n"
        "If you skipped Day 13, do it first. It opens the account on the Free plan, puts MFA on the root user, sets a zero-spend budget and gives you an everyday IAM user with `aws login`. Today adds nothing to that list. One warning from it matters again here: do not create an AWS Organization on a learning account, because joining one moves a Free plan account to the Paid plan.\n\n"
        "If you ran Day 14's `cleanup.sh`, nothing from those lessons is still running, so today's bill starts from zero. Today's resources are cheap too, because almost nothing here bills by the hour:\n"
        "- IAM roles and the OIDC provider cost nothing.\n"
        "- S3 charges per gigabyte stored each month plus a little per request. A state file is a few kilobytes, so the bucket costs close to nothing. Check the S3 pricing page for your Region anyway.\n\n"
        "A budget alert only sends email. It stops nothing, and its numbers can lag by hours. Destroying what you create is what protects you, and it is the last step today."
    ),
}

SEC2 = {
    "h": "How Terraform finds your AWS credentials",
    "body": (
        "Terraform's AWS provider finds credentials the same way as the AWS CLI. Its docs list the order:\n"
        "1. Arguments in the provider block.\n"
        "2. Environment variables, such as `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`.\n"
        "3. The shared files in `~/.aws`.\n"
        "4. The credentials of a container or a machine running in AWS, such as Day 14's instance role.\n\n"
        "So the login from Day 13 works as it is. Run `aws login --profile learn`, then `export AWS_PROFILE=learn` in the same terminal. `aws sts get-caller-identity` should print your 12-digit account ID and your IAM user, not root. Inside Terraform, the `aws_caller_identity` data source asks the same question, and the next section uses its answer to name the bucket.\n\n"
        "The provider is built on the AWS SDK for Go, whose default credential chain has read `aws login` profiles since late 2025. If a tool still finds no credentials, `aws configure export-credentials --profile learn --format env` prints short-lived variables for it. Leftover `AWS_ACCESS_KEY_ID` variables beat `AWS_PROFILE` (Day 13), so when a plan shows the wrong account, run `aws configure list`.\n\n"
        "Leave a `profile` argument out of the provider block. A profile name ties the code to your laptop, while an environment variable keeps the same code working in CI. Never put an access key into a `.tf` file or a `.tfvars` file either. In CI the same provider block finds the short-lived variables that the `configure-aws-credentials` action exports, which is step 2 in the list above. They come from OIDC with no stored key, and the next sections build that."
    ),
    "refs": [
        {"title": "AWS provider: authentication and configuration (docs source)", "url": "https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/index.html.markdown", "kind": "docs"},
        {"title": "Login for AWS local development using console credentials (AWS CLI docs)", "url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html", "kind": "docs"},
    ],
}

OLD_SEC1_H = "Before any cloud: make the account safe"
OLD_SEC2_H = "A login for your laptop that is not root"


def main() -> None:
    part = json.loads(P8.read_text())
    L = next(x for x in part["lessons"] if x["id"] == "d35")
    secs = L["sections"]

    for i, s in enumerate(secs):
        if s["h"] in (OLD_SEC1_H, SEC1["h"]):
            secs[i] = {"h": SEC1["h"], "body": SEC1["body"], "refs": s["refs"]}
        elif s["h"] in (OLD_SEC2_H, SEC2["h"]):
            secs[i] = dict(SEC2)

    # Worked example, last step: point to the Day 13 login.
    for st in L["worked"]["steps"]:
        st["say"] = st["say"].replace(
            "and your laptop needs `aws sso login` or your IAM user's profile.",
            "and your laptop needs the `aws login` profile from Day 13.",
        )

    # Commands: the SSO pair becomes the Day 13 login and the export helper.
    for c in L["commands"]:
        if c["cmd"] == "aws configure sso":
            c["cmd"] = "aws login --profile learn"
            c["what"] = "Sign the CLI in with your console login and get short-lived credentials (Day 13)."
        elif c["cmd"] == "aws sso login":
            c["cmd"] = "aws configure export-credentials --profile learn --format env"
            c["what"] = "Print a profile's temporary credentials as variables, for a tool that cannot read the profile."

    steps = L["task"]["steps"]
    for i, s in enumerate(steps):
        if s.startswith("Secure the account:"):
            steps[i] = "Sign in as on Day 13 (`aws login --profile learn` and `export AWS_PROFILE=learn`). `aws sts get-caller-identity` must show your IAM user, not root."
        elif s.startswith("Delete the `AWS_ROLE_ARN` variable"):
            steps[i] = "Delete the `AWS_ROLE_ARN` variable so the AWS jobs skip again, run `aws logout --profile learn` if you are done for the day, and keep the budget."

    P8.write_text(json.dumps(part, ensure_ascii=False, indent=1) + "\n")
    print("d35 sections:", [s["h"] for s in secs])


if __name__ == "__main__":
    main()
