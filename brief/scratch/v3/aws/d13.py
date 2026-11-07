"""Day 13: Hands-on AWS 1: your account, IAM and the AWS CLI. Imported by build_p3_aws.py."""

from labfiles import lab

AWS_CONFIG_EXAMPLE = """# ~/.aws/config after "aws login --profile learn" (Day 13).
# The CLI writes this file for you. No keys are stored in it.
# Your account ID and user name will differ.
[profile learn]
login_session = arn:aws:iam::123456789012:user/learner
region = us-east-1

# For comparison: what "aws configure sso" writes at a company
# that uses IAM Identity Center.
[profile work-admin]
sso_session = work
sso_account_id = 111122223333
sso_role_name = AdministratorAccess
region = eu-central-1
output = json

[sso-session work]
sso_start_url = https://d-xxxxxxxxxx.awsapps.com/start
sso_region = eu-central-1
sso_registration_scopes = sso:account:access
"""

DIAGRAM = (
    '<svg viewBox="0 0 560 270" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="You sign in through the browser with MFA, aws login turns that into temporary keys, '
    'every API call is checked against IAM policies, and the result is allow or deny">'
    '<rect x="8" y="24" width="128" height="44" rx="10" class="bx"/>'
    '<text x="72" y="51" font-size="13" text-anchor="middle" class="t">Browser + MFA</text>'
    '<rect x="162" y="24" width="104" height="44" rx="10" class="bxo"/>'
    '<text x="214" y="51" font-size="13" text-anchor="middle" class="tk">aws login</text>'
    '<rect x="292" y="24" width="140" height="44" rx="10" class="bxt"/>'
    '<text x="362" y="51" font-size="13" text-anchor="middle" class="tk">temporary keys</text>'
    '<rect x="454" y="24" width="98" height="44" rx="10" class="bx"/>'
    '<text x="503" y="51" font-size="13" text-anchor="middle" class="t">API call</text>'
    '<line x1="138" y1="46" x2="159" y2="46" class="ln" marker-end="url(#ar)"/>'
    '<line x1="268" y1="46" x2="289" y2="46" class="ln" marker-end="url(#ar)"/>'
    '<line x1="434" y1="46" x2="451" y2="46" class="ln" marker-end="url(#ar)"/>'
    '<text x="72" y="92" font-size="11" text-anchor="middle" class="ts">your IAM user</text>'
    '<text x="214" y="92" font-size="11" text-anchor="middle" class="ts">no key on disk</text>'
    '<text x="362" y="92" font-size="11" text-anchor="middle" class="ts">expire on their own</text>'
    '<rect x="376" y="120" width="176" height="44" rx="10" class="bxg"/>'
    '<text x="464" y="147" font-size="13" text-anchor="middle" class="tk">IAM checks policies</text>'
    '<line x1="503" y1="70" x2="503" y2="117" class="ln" marker-end="url(#ar)"/>'
    '<rect x="300" y="200" width="120" height="44" rx="10" class="bxt"/>'
    '<text x="360" y="227" font-size="13" text-anchor="middle" class="tk">Allow: read</text>'
    '<rect x="432" y="200" width="120" height="44" rx="10" class="bxo"/>'
    '<text x="492" y="227" font-size="13" text-anchor="middle" class="tk">Deny: delete</text>'
    '<line x1="430" y1="166" x2="378" y2="197" class="ln" marker-end="url(#ar)"/>'
    '<line x1="494" y1="166" x2="492" y2="197" class="ln" marker-end="url(#ar)"/>'
    '<text x="150" y="160" font-size="11" text-anchor="middle" class="ts">everything starts denied</text>'
    '<text x="150" y="180" font-size="11" text-anchor="middle" class="ts">a matching Allow opens a call</text>'
    '<text x="150" y="200" font-size="11" text-anchor="middle" class="ts">any Deny wins</text>'
    '</svg>'
)

LESSON = {
    "id": "d13",
    "title": "Hands-on AWS 1: your account, IAM and the AWS CLI",
    "minutes": 50,
    "goal": "By the end you can open an AWS account that cannot surprise you with a bill, sign in to the AWS CLI without a stored key, read an IAM policy line by line, and create, share and delete an S3 bucket from your terminal.",
    "guess": {
        "q": "You create an access key for an IAM user and save it in ~/.aws/credentials. When does that key stop working?",
        "options": [
            "After 12 hours, like a console session",
            "When you sign out of the AWS console",
            "Only when someone deactivates or deletes it",
            "After 90 days, when AWS rotates it for you",
        ],
        "answer": 2,
        "why": "An access key is long-lived: it works until someone deactivates or deletes it, for you and for anyone who copies it. Today's login uses `aws login` instead, whose credentials expire on their own.",
    },
    "terms": [
        {"term": "Root user", "plain": "The email login an AWS account was opened with. It can do anything, including close the account."},
        {"term": "IAM user", "plain": "A named identity inside one account for one person, with its own password, MFA and permissions."},
        {"term": "Access key", "plain": "An ID and a secret that sign API calls. A long-lived one works until someone deletes it."},
        {"term": "Temporary credentials", "plain": "An access key, a secret and a session token that stop working by themselves after a set time."},
        {"term": "IAM Identity Center", "plain": "AWS's single sign-on for people: one browser login gives short-lived access to each account and role."},
        {"term": "ARN", "plain": "Amazon Resource Name: the full unique name of an AWS resource, such as arn:aws:s3:::my-bucket."},
        {"term": "Trust policy", "plain": "The part of an IAM role that says who may assume the role."},
        {"term": "Presigned URL", "plain": "A link to one private S3 object that works without a login until it expires."},
    ],
    "sections": [
        {
            "h": "Open the account on the Free plan",
            "body": (
                "Today you get a real AWS account, and the first choice comes during sign-up. Since July 15, 2025, every new account picks one of two plans:\n\n"
                "- The Free plan gives you $100 in credits, plus up to $100 more for trying five services. It ends after six months or when the credits are used up, whichever comes first. It never charges your card.\n"
                "- The Paid plan starts with the same credits, but once they are gone, you pay for what you use.\n\n"
                "Pick the Free plan for this course. When it ends, the account closes instead of sending a bill. AWS keeps your data for 90 days after that, and upgrading in that window brings the account back.\n\n"
                "Sign-up asks for an email address, a password, a card and a phone number for a verification code. AWS does not charge the card while you stay on the Free plan; it is there in case you upgrade later.\n\n"
                "A few actions move a Free plan account to the Paid plan automatically, and your Free Tier credits end at once. Two of them are joining AWS Organizations and setting up an AWS Control Tower landing zone. This course needs neither. Accounts opened before July 15, 2025 stay on the older 12-month free tier, which can bill you, so the budget in the next section matters even more there.\n\n"
                "The extra $100 comes from five tasks in the Explore AWS panel on the console's home page, worth $20 each. One of them is creating a cost budget, which costs nothing, so start with that one. Some of the others, such as launching a server, spend a little of your credits."
            ),
            "refs": [
                {"title": "Choosing a Free plan or Paid plan (AWS Billing docs)", "url": "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html", "kind": "docs"},
                {"title": "Earning additional credits (AWS Billing docs)", "url": "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans-activities.html", "kind": "docs"},
                {"title": "AWS Free Tier now offers $200 in credits and a 6-month free plan (AWS What's New)", "url": "https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/", "kind": "read"},
            ],
        },
        {
            "h": "Lock the root user, then set a zero-spend budget",
            "body": (
                "The email address you signed up with is the **root user**. It can do anything in the account, including closing it, and no IAM policy can limit it. You protect it once and then put it away:\n\n"
                "1. Turn on MFA for it. AWS now requires MFA for the root user of every account. A passkey (Touch ID on your Mac) or an authenticator app both work. You can register up to eight devices, so add a spare.\n"
                "2. Never create access keys for it.\n"
                "3. Create your everyday IAM user (next section), sign out, and keep root for the rare account-level task, such as changing the plan.\n\n"
                "Then, before you create anything else, set a budget. In the console, open Billing and Cost Management, then Budgets, and pick the template called Zero spend budget. AWS describes it as a budget that notifies you once your spending exceeds the AWS Free Tier limits. Give it your email address and create it. That is also the $20 task from the Explore AWS panel.\n\n"
                "A budget is an alarm, not a brake. As Day 12 said, it sends an email and stops nothing. Its numbers lag too: AWS refreshes budget data up to three times a day, so an alert can arrive hours after the spending. What protects you is deleting things the same day, which is why both AWS lessons end with a cleanup script. Budgets without actions cost nothing, so a second one from the Monthly cost budget template, set to $5, is a cheap extra alarm."
            ),
            "refs": [
                {"title": "Root user best practices for your AWS account (IAM docs)", "url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html", "kind": "docs"},
                {"title": "Using a budget template (AWS Cost Management docs)", "url": "https://docs.aws.amazon.com/cost-management/latest/userguide/budget-templates.html", "kind": "docs"},
                {"title": "AWS IAM now enforces MFA for root users across all account types (AWS What's New)", "url": "https://aws.amazon.com/about-aws/whats-new/2025/06/aws-iam-mfa-root-users-across-all-account-types", "kind": "read"},
            ],
        },
        {
            "h": "People and programs get credentials in different ways",
            "body": (
                "AWS checks every API call against credentials: an access key ID, a secret and, for temporary credentials, a session token. The safe rule is about where they come from:\n\n"
                "- People sign in through a browser and get short-lived credentials.\n"
                "- Programs, such as a server or a CI job, assume an IAM role and never hold a stored key.\n"
                "- A long-lived access key is the last resort. It works for whoever holds it, copied from a laptop, a log or a git repo, until someone deletes it.\n\n"
                "At work you will meet IAM Identity Center, AWS's single sign-on. Your company login opens a portal with every account and role you may use. You connect the CLI once with `aws configure sso`, which asks for, in order:\n\n"
                "1. A session name of your choice.\n"
                "2. The start URL of the portal, shaped like `https://d-xxxxxxxxxx.awsapps.com/start`.\n"
                "3. The SSO region, then the registration scopes (keep the default).\n"
                "4. Your approval in the browser window it opens.\n"
                "5. The account, the role, a default region and an output format.\n"
                "6. A profile name. It suggests the role and account, such as `AdministratorAccess-123456789012`.\n\n"
                "After that, `aws sso login --profile NAME` signs you in for the day.\n\n"
                "On your own Free plan account there is a catch. Identity Center gives access to AWS accounts only through an organization instance, which needs AWS Organizations, and that ends the Free plan. Its smaller account instance cannot give access to accounts at all.\n\n"
                "So today you make an IAM user with a console password, MFA and the AdministratorAccess policy. It is your own sandbox, so admin rights are reasonable. Then `aws login`, in CLI 2.32.0 or later, signs the CLI in through the browser with that same login. It stores temporary credentials and refreshes them every 15 minutes, and no key ever lands on your disk. A user without admin rights needs the AWS managed policy `SignInLocalDevelopmentAccess` for it.\n\n"
                "Programs get roles: Day 14 gives a server one through an instance profile, and Days 27 and 35 give GitHub Actions one through OIDC."
            ),
            "refs": [
                {"title": "Login for AWS local development using console credentials (AWS CLI docs)", "url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html", "kind": "docs"},
                {"title": "Configuring IAM Identity Center authentication with the AWS CLI", "url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html", "kind": "docs"},
                {"title": "Account instances of IAM Identity Center (AWS docs)", "url": "https://docs.aws.amazon.com/singlesignon/latest/userguide/account-instances-identity-center.html", "kind": "docs"},
            ],
        },
        {
            "h": "The CLI: profiles, regions and shaping the output",
            "body": (
                "Install the CLI with `brew install awscli`, which is version 2, and check it with `aws --version`. AWS also publishes a Mac installer package; check its install page if Homebrew is not an option. If you only have a browser, AWS CloudShell is a terminal inside the console, already signed in as you. It is free, keeps 1 GB of files per region, and deletes them after 120 days without a visit.\n\n"
                "Settings live in named profiles in `~/.aws/config`. `aws login --profile learn` creates one called learn. Pick it for one command with `--profile learn`, or for the whole terminal with `export AWS_PROFILE=learn`.\n\n"
                "Three habits prevent most confusion:\n\n"
                "- Ask who you are. `aws sts get-caller-identity` prints the account and identity the CLI is using right now. If the ARN ends in `:root`, stop and sign in as your IAM user.\n"
                "- Know your region. Each command works in one region, taken from `--region`, then `AWS_REGION`, then the profile. A bucket or server in another region is invisible from this one, and it still bills.\n"
                "- Shape the output. The `--output` option takes json, yaml, text or table. The `--query` option takes JMESPath, a small language for picking fields out of JSON, and runs on your laptop after the answer arrives.\n\n"
                "For example, `--query Account --output text` prints only the 12-digit number, ready for a shell variable. The jq tool from Day 5 works too, and it is better at heavy reshaping. The `--query` option needs nothing installed, so it also works in CloudShell and on servers.\n\n"
                "Some EC2 commands accept `--dry-run`. AWS checks your permissions and the request, then refuses with `DryRunOperation` if the call would have worked. Day 14 launches its server that way first. When AWS returns an error, the CLI exits with 254, so a script with `set -e` (Day 7) stops at the failing line."
            ),
            "refs": [
                {"title": "Filtering output in the AWS CLI (--query)", "url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-filter.html", "kind": "docs"},
                {"title": "Controlling command output in the AWS CLI", "url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-output.html", "kind": "docs"},
                {"title": "Service quotas and restrictions for AWS CloudShell", "url": "https://docs.aws.amazon.com/cloudshell/latest/userguide/limits.html", "kind": "docs"},
            ],
        },
        {
            "h": "Reading an IAM policy, and a role's two policies",
            "body": (
                "An IAM policy is a JSON document. Open `policies/reports-reader-permissions.json` from the lab and read it next to this list:\n\n"
                "- `Version` is always `\"2012-10-17\"`, the version of the policy language. You never change it.\n"
                "- `Statement` is a list of rules, each with an optional `Sid`, a label for humans.\n"
                "- `Effect` is Allow or Deny.\n"
                "- `Action` names API calls as `service:Action`, such as `s3:GetObject`.\n"
                "- `Resource` names what the call acts on, by ARN.\n"
                "- `Condition` is optional and narrows the rule further.\n\n"
                "An **ARN** has the shape `arn:aws:service:region:account:resource`. S3 bucket names are global, so bucket ARNs leave the region and account empty: `arn:aws:s3:::hello-devops-lab-123456789012`. Objects add their key, as in `.../reports/*`.\n\n"
                "The file's first statement allows `s3:ListBucket` on the bucket, but its Condition only matches listings whose prefix starts with `reports/`. The second allows `s3:GetObject` on objects under `reports/`. Nothing allows `s3:DeleteObject`. AWS decides every call the same way: it starts from deny, a matching Allow opens the call, and an explicit Deny anywhere beats every Allow. So a delete fails.\n\n"
                "A role carries two policies. The permissions policy, like this one, says what the role may do. The trust policy says who may assume it. In `reports-reader-trust.json` the Principal is `arn:aws:iam::ACCOUNT_ID:root`, which means the whole account: any identity in it whose own policy allows `sts:AssumeRole`. It does not mean the root user.\n\n"
                "`aws sts assume-role` hands back temporary credentials that last an hour by default. Their access key ID starts with ASIA, while long-lived keys start with AKIA, so you can tell them apart in a log.\n\n"
                "Two AWS tools check a policy before it bites. IAM Access Analyzer's policy validation runs over 100 checks on grammar and good practice (`aws accessanalyzer validate-policy`). The policy simulator answers \"would this call be allowed?\" without making the call (`aws iam simulate-custom-policy`)."
            ),
            "refs": [
                {"title": "Policy evaluation logic (IAM docs)", "url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html", "kind": "docs"},
                {"title": "IAM policy validation with IAM Access Analyzer", "url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_policy-validator.html", "kind": "docs"},
                {"title": "IAM policy power hour, re:Inforce 2024 (AWS Events)", "url": "https://www.youtube.com/watch?v=MKhkLqN0AyY", "kind": "watch"},
            ],
        },
        {
            "h": "S3: buckets, versions, sharing and deleting",
            "body": (
                "S3 (Simple Storage Service) keeps files, which it calls objects, in buckets. An object's name is its key, such as `reports/2026-11-06.csv`. The slashes only look like folders. S3 has none; the console draws key prefixes as if they were.\n\n"
                "Four rules shape what you do with it:\n\n"
                "- Bucket names are unique across every AWS account in the world, so the lab puts your account ID in the name. Since March 2026 you can also create buckets in your account regional namespace. Their names end with your account ID, the region and `-an`, and no other account can ever take them.\n"
                "- Block Public Access has four settings, and every bucket created since April 2023 starts with all four on. Leave them on. `s3-lab.sh` sets them anyway, so anyone reading the script sees the intent.\n"
                "- Versioning keeps every old version of an object. Once it is on, you can suspend it but never turn it fully off. A delete then only adds a delete marker on top, and removing the marker brings the object back.\n"
                "- A lifecycle rule deletes objects on a schedule. The lab's rule removes reports after 30 days, replaced versions 7 days later, and unfinished uploads after a day.\n\n"
                "To share one private object, make a presigned URL: a link that carries a signature made with your credentials. Anyone who has the link can read that object until it expires, and from the CLI it can last up to 7 days. It also dies when the credentials that signed it expire, so a link signed with `aws login` or a role can stop working long before the time you asked for.\n\n"
                "Deleting a versioned bucket needs one more step. The command `aws s3 rb --force` removes the current objects, but old versions and delete markers stay, and the bucket refuses to go. The lab's `cleanup.sh` deletes every version first. The few kilobytes you store today cost a tiny fraction of a cent."
            ),
            "refs": [
                {"title": "Download and upload objects with presigned URLs (S3 docs)", "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html", "kind": "docs"},
                {"title": "Access control in Amazon S3 (S3 docs)", "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-management.html", "kind": "docs"},
                {"title": "Amazon S3 security and access control best practices, re:Invent 2025 (AWS Events)", "url": "https://www.youtube.com/watch?v=UfGW7RoaNhc", "kind": "watch"},
            ],
        },
        {
            "h": "No account yet? Practise on an emulator",
            "body": (
                "You can learn every command from today without an account. moto is a free program that pretends to be AWS on your laptop. Install it in a virtual environment, start it with `moto_server -p 5050`, and point the CLI at it: `--endpoint-url http://localhost:5050` for one command, or `export AWS_ENDPOINT_URL=http://localhost:5050` for the whole terminal. Fake keys such as `testing` are fine. The lab README has the exact steps, and every lab script runs there.\n\n"
                "The worked example below ran on moto, and each step says where its output differs from AWS. Some things an emulator cannot teach:\n\n"
                "- It allows every call, so you never see AccessDenied, and the policy simulator does not run.\n"
                "- New buckets have no Block Public Access until you set it, and presigned URLs never expire.\n"
                "- Nothing bills, so you learn nothing about cost.\n"
                "- On Day 14 no server boots and no logs arrive.\n\n"
                "LocalStack is a bigger emulator. Since March 2026 it needs a LocalStack account and an auth token, with a free plan for non-commercial use. moto needs neither, so the course uses it.\n\n"
                "When you go back to real AWS, unset the fake keys and the endpoint, or close that terminal tab. Left behind, they quietly win over your profile, as the common mistake below shows."
            ),
            "refs": [
                {"title": "Non-Python SDKs / Server Mode (moto docs)", "url": "https://moto.readthedocs.io/en/latest/docs/server_mode.html", "kind": "docs"},
                {"title": "Service-specific endpoints and AWS_ENDPOINT_URL (AWS SDKs and Tools guide)", "url": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html", "kind": "docs"},
                {"title": "The road ahead for LocalStack (LocalStack blog)", "url": "https://blog.localstack.cloud/the-road-ahead-for-localstack/", "kind": "read"},
            ],
        },
    ],
    "analogy": (
        "Your AWS account works like an office building with a badge desk. The root user is the owner's master key, so it stays in the safe. "
        "Your IAM user is your staff badge, and `aws login` prints you a day pass from it that stops working by itself. "
        "A role is a contractor's badge: the trust policy lists who may collect it at the desk, and the permissions policy lists the doors it opens. "
        "A real badge reader checks you once at the front door. AWS checks every single request against the current policies, so when a badge loses a door, even someone already inside notices within seconds."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "aws login turns your browser sign-in into temporary keys; IAM then checks each API call and allows it or denies it.",
    "worked": {
        "title": "An S3 bucket from creation to deletion, on the emulator",
        "steps": [
            {
                "say": "Ask who you are first. On real AWS this prints your 12-digit account ID and `user/learner`; on moto every account is 123456789012 and the user is moto. Keep the ID in a variable, because the bucket name needs it.",
                "code": (
                    "$ aws sts get-caller-identity\n{\n    \"UserId\": \"AKIAIOSFODNN7EXAMPLE\",\n    \"Account\": \"123456789012\",\n    \"Arn\": \"arn:aws:sts::123456789012:user/moto\"\n}\n"
                    "$ BUCKET=hello-devops-lab-$(aws sts get-caller-identity --query Account --output text)"
                ),
                "lang": "console",
            },
            {
                "say": "Create the bucket and ask for its Block Public Access settings. Here moto differs from AWS: real S3 answers with all four settings on, while moto has none until you set them. Setting them explicitly is a good habit either way, and it prints nothing when it works.",
                "code": (
                    "$ aws s3 mb s3://$BUCKET\nmake_bucket: hello-devops-lab-123456789012\n"
                    "$ aws s3api get-public-access-block --bucket $BUCKET\n"
                    "aws: [ERROR]: An error occurred (NoSuchPublicAccessBlockConfiguration) when calling the GetPublicAccessBlock operation: The public access block configuration was not found\n"
                    "$ aws s3api put-public-access-block --bucket $BUCKET --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
                ),
                "lang": "console",
            },
            {
                "say": "Upload a small CSV straight from a pipe: the `-` means read from standard input (Day 5). `--summarize` adds the totals to the listing.",
                "code": (
                    "$ printf 'date,orders,failed\\n2026-11-06,1520,12\\n' | aws s3 cp - s3://$BUCKET/reports/2026-11-06.csv\n"
                    "$ aws s3 ls s3://$BUCKET --recursive --human-readable --summarize\n"
                    "2026-11-07 17:43:24   38 Bytes reports/2026-11-06.csv\n\nTotal Objects: 1\n   Total Size: 38 Bytes"
                ),
                "lang": "console",
            },
            {
                "say": "Share it for five minutes. Our test ran moto on port 5013, while yours runs on 5050. The presigned URL works with no login at all, while the plain URL gets 403. On real AWS the URL starts with `https://hello-devops-lab-...s3.amazonaws.com`, and after five minutes it returns 403 too; moto never checks the expiry.",
                "code": (
                    "$ URL=$(aws s3 presign s3://$BUCKET/reports/2026-11-06.csv --expires-in 300)\n"
                    "$ echo \"$URL\" | cut -c1-90\nhttp://localhost:5013/hello-devops-lab-123456789012/reports/2026-11-06.csv?X-Amz-Algorithm\n"
                    "$ curl -s \"$URL\"\ndate,orders,failed\n2026-11-06,1520,12\n"
                    "$ curl -s -o /dev/null -w \"%{http_code}\\n\" \"http://localhost:5013/$BUCKET/reports/2026-11-06.csv\"\n403"
                ),
                "lang": "console",
            },
            {
                "say": "Turn on versioning, overwrite the report, then delete it by mistake. The listing shows two versions and a delete marker on top. The first upload came before versioning, so its version ID is `null`, on AWS too. moto's other IDs look like UUIDs; real ones are longer random strings.",
                "code": (
                    "$ aws s3api put-bucket-versioning --bucket $BUCKET --versioning-configuration Status=Enabled\n"
                    "$ printf 'date,orders,failed\\n2026-11-06,1520,9\\n' | aws s3 cp - s3://$BUCKET/reports/2026-11-06.csv\n"
                    "$ aws s3 rm s3://$BUCKET/reports/2026-11-06.csv\ndelete: s3://hello-devops-lab-123456789012/reports/2026-11-06.csv\n"
                    "$ aws s3api list-object-versions --bucket $BUCKET --query '{versions: Versions[].VersionId, markers: DeleteMarkers[].VersionId}' --output json\n"
                    "{\n    \"versions\": [\n        \"a17e311f-6caf-4db2-bbc6-170305906a82\",\n        \"null\"\n    ],\n    \"markers\": [\n        \"eb390243-307e-439d-8fde-fcce59f94990\"\n    ]\n}"
                ),
                "lang": "console",
            },
            {
                "say": "Undo the delete by deleting the marker, and the newest version is back. Then add the lifecycle rule from the lab and read it back as a table.",
                "code": (
                    "$ MARKER=$(aws s3api list-object-versions --bucket $BUCKET --query 'DeleteMarkers[?IsLatest].VersionId' --output text)\n"
                    "$ aws s3api delete-object --bucket $BUCKET --key reports/2026-11-06.csv --version-id $MARKER > /dev/null\n"
                    "$ aws s3 cp s3://$BUCKET/reports/2026-11-06.csv -\ndate,orders,failed\n2026-11-06,1520,9\n"
                    "$ aws s3api put-bucket-lifecycle-configuration --bucket $BUCKET --lifecycle-configuration file://s3/lifecycle.json\n"
                    "$ aws s3api get-bucket-lifecycle-configuration --bucket $BUCKET --query 'Rules[].{id:ID,prefix:Filter.Prefix,days:Expiration.Days}' --output table"
                ),
                "lang": "console",
            },
            {
                "say": "Now try to remove the bucket the quick way. The `--force` flag deletes the current object, which in a versioned bucket only adds one more marker, and the old versions keep the bucket alive. The lab's `cleanup.sh` lists every version and marker, deletes them, and then the bucket goes.",
                "code": (
                    "$ aws s3 rb s3://$BUCKET --force\ndelete: s3://hello-devops-lab-123456789012/reports/2026-11-06.csv\n"
                    "remove_bucket failed: s3://hello-devops-lab-123456789012 An error occurred (BucketNotEmpty) when calling the DeleteBucket operation: The bucket you tried to delete is not empty\n"
                    "$ ./cleanup.sh\n...\n== 5. The buckets, with every old version inside them\nbucket hello-devops-lab-123456789012: deleting 3 object versions\nremove_bucket: hello-devops-lab-123456789012"
                ),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "bash", "title": "labs/aws/env.sh", "src": lab("env.sh"), "run": "source ./env.sh && echo \"$CALLER_ARN\""},
        {"lang": "bash", "title": "labs/aws/s3-lab.sh", "src": lab("s3-lab.sh"), "run": "./s3-lab.sh"},
        {"lang": "json", "title": "labs/aws/s3/lifecycle.json", "src": lab("s3/lifecycle.json"), "run": "jq . s3/lifecycle.json"},
        {"lang": "json", "title": "labs/aws/policies/reports-reader-trust.json", "src": lab("policies/reports-reader-trust.json"), "run": "sed \"s/ACCOUNT_ID/$ACCOUNT_ID/g\" policies/reports-reader-trust.json"},
        {"lang": "json", "title": "labs/aws/policies/reports-reader-permissions.json", "src": lab("policies/reports-reader-permissions.json"), "run": "aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://policies/reports-reader-permissions.json"},
        {"lang": "ini", "title": "~/.aws/config (written by the CLI, shown for reading)", "src": AWS_CONFIG_EXAMPLE, "run": "aws configure list --profile learn"},
        {"lang": "bash", "title": "labs/aws/cleanup.sh (Days 13 and 14)", "src": lab("cleanup.sh"), "run": "./cleanup.sh"},
    ],
    "commands": [
        {"cmd": "brew install awscli", "what": "Install the AWS CLI version 2 on your Mac."},
        {"cmd": "aws login --profile learn", "what": "Sign the CLI in through the browser with your console login; stores temporary credentials, no key."},
        {"cmd": "export AWS_PROFILE=learn", "what": "Use the learn profile for every command in this terminal."},
        {"cmd": "aws sts get-caller-identity", "what": "Show which account and identity the CLI is using right now."},
        {"cmd": "aws configure list", "what": "Show where the CLI found its credentials and region (environment, profile, file)."},
        {"cmd": "aws configure sso", "what": "At work: connect a profile to IAM Identity Center once."},
        {"cmd": "aws sso login --profile work-admin", "what": "At work: sign in through Identity Center for the day."},
        {"cmd": "aws s3 mb s3://hello-devops-lab-123456789012", "what": "Make a bucket in the current region."},
        {"cmd": "aws s3 ls s3://BUCKET --recursive --human-readable", "what": "List every object in a bucket with readable sizes."},
        {"cmd": "aws s3 presign s3://BUCKET/reports/2026-11-06.csv --expires-in 300", "what": "Print a link that reads one private object for 5 minutes."},
        {"cmd": "aws s3api put-bucket-versioning --bucket BUCKET --versioning-configuration Status=Enabled", "what": "Keep every old version of every object."},
        {"cmd": "aws s3api list-object-versions --bucket BUCKET --query 'DeleteMarkers[?IsLatest].VersionId' --output text", "what": "Find the delete markers that hide deleted objects."},
        {"cmd": "aws sts assume-role --role-arn ROLE_ARN --role-session-name test", "what": "Get temporary credentials for a role (they start with ASIA)."},
        {"cmd": "aws iam simulate-custom-policy --policy-input-list file://policy.json --action-names s3:DeleteObject --resource-arns ARN", "what": "Ask whether a policy would allow a call, without making it."},
        {"cmd": "aws s3 ls --endpoint-url http://localhost:5050", "what": "Send one command to the moto emulator instead of AWS."},
        {"cmd": "aws logout --profile learn", "what": "Delete the cached login credentials for a profile."},
    ],
    "mistake": (
        "Leaving old keys in environment variables after an emulator session. With `export AWS_PROFILE=learn`, a leftover `AWS_ACCESS_KEY_ID` still wins, so real calls fail with InvalidAccessKeyId or reach the wrong account. "
        "`aws configure list` shows it: the key's TYPE column says `env`. Unset the variables or open a fresh terminal tab."
    ),
    "real_world": (
        "A company with dozens of AWS accounts, one per team and environment, never hands out IAM users. "
        "Engineers sign in once through IAM Identity Center with the company login, pick an account and a permission set such as ReadOnly, and get credentials that expire within hours. "
        "Secret scanning watches every repo for anything shaped like an AKIA key (Day 64), because a pushed key is treated as leaked the moment it lands."
    ),
    "task": {
        "title": "Your account, your login, and a role that can only read",
        "steps": [
            "No account yet? Start moto as the lab README shows and do steps 6 to 10 there; the AccessDenied results in step 8 only appear on real AWS.",
            "Sign up on the Free plan. Turn on MFA for the root user with a passkey or an authenticator app, and add a spare device.",
            "Create the zero-spend budget from its template with your email, then check that the Explore AWS panel shows the $20 credit task as done.",
            "Still as root, create an IAM user called `learner` with console access, the AdministratorAccess policy and its own MFA. Sign out of root and sign in at your account's sign-in URL as learner.",
            "Install the CLI, run `aws login --profile learn`, export `AWS_PROFILE`, and check that `aws sts get-caller-identity` shows `user/learner`, not root.",
            "Copy `labs/aws` to `~/code/aws-lab` and run `./s3-lab.sh`. Open the presigned URL in a browser, then open the plain object URL and read the AccessDenied page.",
            "Create the role `hello-devops-reports-reader` from the two `reports-reader` policy files (put your account ID in place of ACCOUNT_ID). Assume it and export its three values in a new terminal tab.",
            "In that tab, list `reports/`, list the whole bucket, download the report and try to delete it. Write down which calls work, and look at the first four letters of the key ID.",
            "Back in your first tab, run `aws iam simulate-custom-policy` for `s3:GetObject` and `s3:DeleteObject`, and `aws accessanalyzer validate-policy` on the permissions file.",
            "Close the role tab, run `./cleanup.sh`, and check its last four counts.",
        ],
        "hints": [
            "`aws sts assume-role` returns AccessKeyId, SecretAccessKey and SessionToken; they go into AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN.",
            "Listing the whole bucket sends an empty prefix, and the Condition only matches prefixes like `reports/*`.",
            "Your sign-in URL is `https://ACCOUNT_ID.signin.aws.amazon.com/console`, with your 12-digit ID.",
        ],
        "done_when": "You are done when the role reads reports/2026-11-06.csv but gets AccessDenied on the delete, and ./cleanup.sh ends with four zeros.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how a nightly job can read one S3 folder without any stored key. Mention the trust policy, the permissions policy and temporary credentials.",
        "answer": (
            "The job runs with an IAM role instead of an access key. The role's trust policy says who may assume it, for example identities in my account or the EC2 service. "
            "Its permissions policy allows only `s3:ListBucket` with a `reports/` prefix and `s3:GetObject` on `reports/*`, so everything else stays denied. "
            "When the job assumes the role, STS returns temporary credentials that start with ASIA and expire after about an hour, so a copied credential is useless soon after."
        ),
    },
    "recap": [
        "Pick the Free plan: when credits or six months run out, the account closes instead of billing.",
        "Lock the root user with MFA, give it no keys, and set a zero-spend budget before anything else.",
        "People sign in for short-lived credentials (`aws login`, or `aws configure sso` at work); programs use roles.",
        "A policy is Effect, Action, Resource and Condition; calls start denied and any Deny wins.",
        "A role has a trust policy (who may assume it) and a permissions policy (what it may do).",
        "Versioned buckets keep old versions and delete markers; delete them all before the bucket.",
    ],
    "check": [
        {
            "q": "A policy allows `s3:ListBucket` on `arn:aws:s3:::team-exports` with the condition `s3:prefix` like `2026/*`. Which command fails?",
            "options": [
                "`aws s3 ls s3://team-exports/2026/`",
                "`aws s3 ls s3://team-exports`",
                "`aws s3 ls s3://team-exports/2026/11/`",
                "None of them, because ListBucket is allowed",
            ],
            "answer": 1,
            "why": "Listing the whole bucket sends an empty prefix, which does not match `2026/*`, so the call falls back to the default deny.",
        },
        {
            "q": "Yesterday you exported test keys for moto in this terminal. Today you run `aws login --profile learn` and `export AWS_PROFILE=learn`, and `aws s3 ls` fails with InvalidAccessKeyId. Why?",
            "options": [
                "aws login needs a day before it works",
                "The learn profile has no region set",
                "The bucket list is empty on a new account",
                "The leftover AWS_ACCESS_KEY_ID beats the profile",
            ],
            "answer": 3,
            "why": "Key variables in the environment come before the profile set by AWS_PROFILE; `aws configure list` shows their TYPE as env.",
        },
        {
            "q": "You presign a report with `--expires-in 604800` (7 days) while signed in with `aws login`. A colleague says the link already returns 403 the next morning. What is the likely cause?",
            "options": [
                "The credentials that signed the link expired first",
                "Presigned links never work from another network",
                "Block Public Access turned itself off overnight",
                "S3 deletes presigned objects after 24 hours",
            ],
            "answer": 0,
            "why": "A presigned URL stops working when the credentials that signed it expire, even if its own expiry is later.",
        },
    ],
    "interview": [
        {
            "q": "How should engineers and applications get AWS credentials?",
            "a": (
                "Engineers sign in through single sign-on such as IAM Identity Center, and the CLI gets short-lived credentials from that login with `aws configure sso` and `aws sso login`. "
                "Applications use IAM roles: an instance profile on EC2, a task role on ECS, or OIDC federation for CI such as GitHub Actions. "
                "Long-lived access keys are a last resort, scoped tightly and rotated, because they work for whoever holds them until someone deletes them. "
                "The root user gets MFA, no access keys, and almost no use."
            ),
        },
        {
            "q": "What is the difference between a role's trust policy and its permissions policy?",
            "a": (
                "The trust policy is a resource policy on the role that names who may assume it. That can be a service like ec2.amazonaws.com, an account, or an OIDC provider with conditions on the token. "
                "The permissions policy says what the role may do once someone has assumed it. "
                "Both must allow: a principal also needs `sts:AssumeRole` in its own policy unless the trust policy names it directly. "
                "When a CI login fails with 'not authorized to perform sts:AssumeRoleWithWebIdentity', I look at the trust policy first."
            ),
        },
        {
            "q": "How do you make sure an S3 bucket never becomes public?",
            "a": (
                "I keep all four Block Public Access settings on, at the account and on each bucket, and leave ACLs disabled, which is the default for new buckets. "
                "Access goes through IAM policies on named roles, and single objects are shared with short-lived presigned URLs. "
                "A scanner in the pipeline, such as trivy on the Terraform code, fails a change that weakens those settings. "
                "IAM Access Analyzer reports any bucket that is shared outside the account."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Every AWS CLI command, and every SDK such as boto3 on Day 16, looks for credentials in a fixed order and stops at the first it finds. Simplified:\n\n"
            "1. Options on the command line, such as `--profile`.\n"
            "2. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN`.\n"
            "3. The chosen profile in `~/.aws/config` and `~/.aws/credentials`: a login session, an SSO session, a role to assume, or stored keys.\n"
            "4. On AWS itself, the container's or the server's role (Day 14).\n\n"
            "`aws configure list` shows what the CLI would use and where each value came from. We tried it with test keys left in the environment and a profile called learn that held a different key. With `AWS_PROFILE=learn` exported, the access key's TYPE column said `env`: the leftover variables won. With `--profile learn` on the command line, the TYPE said `config-file`. The CLI treats a profile named on the command line as an explicit choice and skips the key variables, while `AWS_PROFILE` gets no such priority. That difference explains a lot of confusing \"but I logged in\" moments.\n\n"
            "Some tools, especially older ones, do not understand `aws login` or SSO profiles yet. For them, `aws configure export-credentials --profile learn --format env` prints `export` lines with the profile's current temporary keys. Run it inside `eval \"$(...)\"` and that terminal has plain variables the old tool can read. They expire like any temporary credentials, so you repeat it later. Another way is a profile with a `credential_process` line, which tells a tool to run a command whenever it needs credentials.\n\n"
            "The CLI caches temporary credentials in `~/.aws/login/cache` for `aws login` and in `~/.aws/sso/cache` for SSO. They expire, but until then they are as powerful as your login. Keep the folder private and out of container images, and remember that `aws logout` clears the login cache.\n\n"
            "Last, the habit that ties this together: run `aws sts get-caller-identity` before anything that changes your account. It costs nothing and answers the only question that matters before a delete: which account, and as whom."
        ),
    },
    "sources": [
        {"title": "Choosing a Free plan or Paid plan (AWS Billing docs)", "url": "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html"},
        {"title": "Login for AWS local development using console credentials (AWS CLI docs)", "url": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html"},
        {"title": "Policy evaluation logic (IAM docs)", "url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html"},
        {"title": "Download and upload objects with presigned URLs (S3 docs)", "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html"},
    ],
}
