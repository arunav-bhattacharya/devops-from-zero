from common import *
from svg import D29

V_DD_CI = ref("Complete Terraform course: AWS and GitHub Actions (DevOps Directive)", V_DD, "watch")

SECTIONS = [
    {
        "h": "Before any cloud: make the account safe",
        "body": (
            "Everything on AWS today is optional. The rest of the course runs on your laptop, and the worked example below needs no account. Day 10 explained cloud costs and free plans. This is the checklist to finish before your first apply, in order:\n"
            "1. Sign up and choose the Free plan. Accounts created since July 15, 2025 pick a plan. The Free plan gives up to $200 in credits for six months and cannot charge your card. When the credits or the six months run out, the account closes, and you have 90 days to upgrade if you want it back.\n"
            "2. Protect the root user, the email login you signed up with. It can do anything, even close the account. Turn on MFA for it and never use it for daily work.\n"
            "3. In Billing and Cost Management, open Budgets and create a zero spend budget from a template. It emails you as soon as you spend anything.\n"
            "4. Make an everyday login that is not root (next section).\n\n"
            "Older accounts stay on the previous free tier and can be billed, so the budget matters even more there. Also, do not create an AWS Organization on a learning account: AWS lists joining Organizations among the actions that move a Free plan account to the Paid plan.\n\n"
            "A budget alert only sends email. It stops nothing, and its numbers can lag by hours. Destroying what you create is what protects you, and it is the last step today. IAM roles and the OIDC provider cost nothing. S3 charges per gigabyte stored each month plus a little per request, and a state file is a few kilobytes, so today's bucket costs close to nothing. Check the S3 pricing page for your Region anyway."
        ),
        "refs": [
            ref("Choosing an AWS Free Tier plan", "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html", "docs"),
            ref("Root user best practices", "https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html", "docs"),
            ref("Control your AWS costs with budgets (AWS tutorial)", "https://docs.aws.amazon.com/hands-on/latest/control-your-costs-free-tier-budgets/control-your-costs-free-tier-budgets.html", "docs"),
        ],
    },
    {
        "h": "A login for your laptop that is not root",
        "body": (
            "Terraform's AWS provider finds credentials the same way as the AWS CLI. Its docs list the order: arguments in the provider block, then environment variables such as `AWS_PROFILE`, then the shared files in `~/.aws`, and finally the credentials of a container or a machine in AWS. Install the CLI with `brew install awscli`, and check the current AWS docs if anything differs.\n\n"
            "You have two common ways to get a login that is not root:\n"
            "- IAM Identity Center, AWS's single sign-on. You sign in through the browser and get short-lived credentials. Run `aws configure sso` once, then `aws sso login` each day.\n"
            "- An IAM user with MFA and an access key, saved with `aws configure`. It is simpler, but the key is a long-lived password on your disk. Delete it when you finish.\n\n"
            "Identity Center is the better habit, with one catch. It is built on AWS Organizations, which would move a Free plan account to the Paid plan. To stay on the Free plan, use the IAM user today and delete its key tonight.\n\n"
            "Then run `aws sts get-caller-identity`. It should print your 12-digit account ID and a user or role that is not root. If that works, Terraform will work too, because it reads the same credentials. Never put an access key into a `.tf` file or a `.tfvars` file."
        ),
        "refs": [
            ref("AWS provider: authentication and configuration (docs source)", "https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/index.html.markdown", "docs"),
            ref("Configure IAM Identity Center authentication with the AWS CLI", "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html", "docs"),
        ],
    },
    {
        "h": "A private, versioned bucket, then state inside it",
        "body": (
            "The lab's `infra/aws` folder creates one S3 bucket. A bucket name must be unique across every AWS account in the world, so the code adds your 12-digit account ID to it. It reads that ID with the data source `aws_caller_identity`. A data source reads something that exists without managing it.\n\n"
            "In the AWS provider, a bucket's settings are separate resources that sit next to `aws_s3_bucket`:\n"
            "- `aws_s3_bucket_versioning` keeps every old version of every file, so you can undo a bad write.\n"
            "- `aws_s3_bucket_public_access_block` stops anything in the bucket from becoming public.\n"
            "- `aws_s3_bucket_server_side_encryption_configuration` encrypts files with keys that S3 manages.\n\n"
            "New buckets already block public access and encrypt files by default. Write it down anyway, so reviewers and scanners can see it. The provider's `default_tags` block adds tags such as `Project` and `ManagedBy` to every resource, so you can always tell what something is for.\n\n"
            "This bucket also stores its own state, which sounds impossible at first: Terraform needs the bucket to store state, but the bucket does not exist until Terraform creates it. You solve it in two steps:\n"
            "1. Apply with local state. This creates the bucket.\n"
            "2. Uncomment the `backend \"s3\"` block, put in the bucket name, and run `terraform init -migrate-state`. Terraform copies the state into S3 and uses it from then on.\n\n"
            "The block sets `use_lockfile = true`, which you met on Day 27. Each run writes a small `.tflock` file next to the state, and a second run that finds it stops with a lock error."
        ),
        "refs": [
            ref("Backend type: s3 (Terraform docs)", HC + "language/backend/s3", "docs"),
            V_FCC_AWS,
        ],
    },
    {
        "h": "GitHub Actions logs in to AWS with OIDC",
        "body": (
            "On Day 21 you met OIDC: a workflow gets a short-lived token from GitHub instead of storing cloud keys. The lab's `github-oidc.tf` builds the AWS side:\n"
            "1. An OIDC identity provider for `token.actions.githubusercontent.com` with the audience `sts.amazonaws.com`.\n"
            "2. An IAM role whose **trust policy** checks the token's `sub` (subject) claim. It names your repo and the context, such as `pull_request` or `environment:production`.\n"
            "3. A permissions policy that says what the role may do.\n\n"
            "The `sub` has to match exactly, character for character. Repos created after July 15, 2026 put numeric IDs in it, like `repo:you@123456/hello-devops@456789:pull_request`. Older repos use `repo:you/hello-devops:pull_request`. The lab trusts both forms, for your repo only. When the login fails with \"Not authorized to perform sts:AssumeRoleWithWebIdentity\", check the `sub` first.\n\n"
            "Keep the role small. The lab's role may manage only buckets whose names start with `hello-devops-`, and read its own IAM setup so that plan works. It cannot change IAM, so a pull request cannot give the pipeline more power. You apply IAM changes from your laptop."
        ),
        "refs": [
            ref("Configuring OpenID Connect in Amazon Web Services (GitHub docs)", "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws", "docs"),
            ref("Immutable subject claims for GitHub Actions OIDC tokens", "https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/", "read"),
            ref("aws-actions/configure-aws-credentials", "https://github.com/aws-actions/configure-aws-credentials", "docs"),
        ],
    },
    {
        "h": "The pipeline: checks, plan on pull requests, apply on main",
        "body": (
            "The lab's `.github/workflows/terraform.yml` runs when anything under `infra/` changes. It has three jobs:\n"
            "1. `checks` runs on every pull request and push, with no cloud login. It runs `terraform fmt -check`, tflint, a trivy scan, `terraform validate` for `infra/local` and `infra/aws`, and the hello-stack module's tests with the mock provider from Day 28.\n"
            "2. `plan` runs on pull requests once the checks pass. It logs in to AWS with OIDC, runs `terraform plan -out=tfplan`, and puts the plan on the run's summary page for reviewers.\n"
            "3. `apply` runs after a merge to main. It waits in the `production` environment until a required reviewer approves, then plans and applies.\n\n"
            "The cheap checks run first, so a formatting slip fails before anything logs in to AWS. The AWS jobs also have `vars.AWS_ROLE_ARN != ''` in their `if`. Until you save the role ARN as a repository variable, they are skipped, so a repo without an AWS account still gets green checks.\n\n"
            "A few more settings are worth spotting:\n"
            "- `concurrency` with `cancel-in-progress: false` on the AWS jobs, so a second run waits and never stops an apply halfway.\n"
            "- `TF_VAR_` environment variables filled from the `github` context, so CI passes your owner, repo and their IDs without any secrets.\n"
            "- `id-token: write` only on the two jobs that log in to AWS. The checks job can only read the repo.\n"
            "- Third-party actions pinned to full commit SHAs, as on Day 21."
        ),
        "refs": [
            ref("hashicorp/setup-terraform", "https://github.com/hashicorp/setup-terraform", "docs"),
            ref("OpenID Connect in GitHub Actions (GitHub docs)", "https://docs.github.com/en/actions/concepts/security/openid-connect", "docs"),
            V_DD_CI,
        ],
    },
    {
        "h": "Linters and scanners, and trusting the scanner",
        "body": (
            "Plan tells you what will change. It does not tell you whether the change is wise. Three free tools help:\n"
            "- tflint, from Day 28, finds mistakes that `validate` misses. The lab's `infra/aws/.tflint.hcl` turns on its AWS plugin, which knows real AWS values.\n"
            "- `trivy config` looks for security problems, such as public buckets, missing encryption, or IAM policies that allow too much. It took over from tfsec, whose README asks users to move to Trivy.\n"
            "- checkov does a similar job with over 1000 built-in policies, and it can scan GitHub Actions workflows too.\n\n"
            "Scanners are strict on purpose, and you decide what to fix. To accept a finding, put a comment such as `# trivy:ignore:AWS-0132` above the resource, followed by your reason. A reviewer can then read the decision and question it.\n\n"
            "A scanner is also software that runs with access to your code, and sometimes to your secrets. In March 2026 attackers moved most version tags of `aquasecurity/trivy-action` to malicious code, tracked as CVE-2026-33634. Any workflow that used the action through one of those tags ran the attacker's code. The lab's Terraform workflow runs the trivy image pinned to a digest, and its release workflow pins trivy-action to a full commit SHA. Day 52 tells the whole story."
        ),
        "refs": [
            ref("Trivy", "https://github.com/aquasecurity/trivy", "docs"),
            ref("Checkov", "https://github.com/bridgecrewio/checkov", "docs"),
            ref("Trivy GitHub Actions supply chain compromise (Snyk)", "https://snyk.io/articles/trivy-github-actions-supply-chain-compromise/", "read"),
        ],
    },
]

WORKED = {
    "title": "Run the pipeline's checks on your laptop first",
    "steps": [
        step("Start in `infra/aws`. Formatting and validation need no AWS account. `-backend=false` skips the S3 backend, which does not exist yet, and `fmt -check` prints nothing when every file is tidy.",
             """$ cd ~/code/hello-devops/infra/aws
$ terraform fmt -check -recursive
$ terraform init -backend=false
Terraform has been successfully initialized!
$ terraform validate
Success! The configuration is valid."""),
        step("Run the module tests the way CI does. The mock provider means no Docker and no cloud.",
             """$ terraform -chdir=../modules/hello-stack init
$ terraform -chdir=../modules/hello-stack test
tests/hello_stack.tftest.hcl... in progress
  run "names_start_with_the_stack_name"... pass
  run "app_talks_to_its_own_redis"... pass
  run "greeting_is_optional"... pass
  run "url_uses_the_host_port"... pass
  run "rejects_privileged_ports"... pass
tests/hello_stack.tftest.hcl... tearing down
tests/hello_stack.tftest.hcl... pass

Success! 5 passed, 0 failed."""),
        step("Scan with trivy (`brew install trivy`, or the `aquasec/trivy` image as CI does). Before the ignore comments were added, it reported three findings. These are its headline lines.",
             """$ trivy config .
github-oidc.tf (terraform)
Failures: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 1, CRITICAL: 0)
AWS-0345 (HIGH): IAM role uses a policy that allows 's3:*' action
main.tf (terraform)
Failures: 2 (UNKNOWN: 0, LOW: 1, MEDIUM: 0, HIGH: 1, CRITICAL: 0)
AWS-0089 (LOW): Bucket has logging disabled
AWS-0132 (HIGH): Bucket does not encrypt data with a customer managed key."""),
        step("Decide on each one. Access logs need a second bucket, and a customer managed KMS key costs money every month, so for a lab you accept both. `s3:*` is limited to this project's buckets. Write each decision above the block it is about.",
             """# trivy:ignore:AWS-0089 Access logs need a second bucket. Not worth it for a lab.
resource "aws_s3_bucket" "state" {

# trivy:ignore:AWS-0132 A customer managed KMS key costs money each month.
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {

# trivy:ignore:AWS-0345 s3:* is limited to this project's buckets.
data "aws_iam_policy_document" "permissions" {""", "hcl"),
        step("Scan again the way CI does. `--exit-code 1` fails the job on HIGH or CRITICAL findings. Now every file shows 0, and the exit code is 0. Without the comments the same command exits with 1.",
             """$ trivy config --severity HIGH,CRITICAL --exit-code 1 .
│ .              │ terraform │         0         │
│ github-oidc.tf │ terraform │         0         │
│ main.tf        │ terraform │         0         │
$ echo $?
0"""),
        step("Give the variables values. `gh api` returns the numeric IDs of your user and your repo. Nothing in `terraform.tfvars` is secret, so you may commit it. Your numbers will differ.",
             """$ gh api users/YOUR_USER --jq .id
$ gh api repos/YOUR_USER/hello-devops --jq .id
$ cat terraform.tfvars
github_owner    = "YOUR_USER"
github_owner_id = "123456"
github_repo_id  = "456789\""""),
        step("Try a plan with no credentials at all. It stops at the provider. CI logs in with OIDC at exactly this point, and your laptop needs `aws sso login` or your IAM user's profile.",
             """$ terraform plan
Planning failed. Terraform encountered an error while generating this plan.

Error: No valid credential sources found

  with provider["registry.terraform.io/hashicorp/aws"],
  on versions.tf line 22, in provider "aws":
  22: provider "aws" {"""),
    ],
}

LESSON = {
    "id": "d29",
    "title": "Terraform on a real cloud, and in CI",
    "minutes": 50,
    "goal": "By the end you can set up a safe AWS account, create a private S3 bucket with Terraform, keep state in it, and run checks, plan and apply from GitHub Actions without stored keys.",
    "guess": mcq(
        "You open a new AWS account on the Free plan. What happens when your free credits run out?",
        ["Your card is charged for whatever you use next", "Nothing: free usage goes on for another year", "The account closes unless you upgrade to a paid plan", "Everything keeps running, but you cannot create more"],
        2,
        "The Free plan does not charge you. When the credits or the six months run out, the account closes, and you have 90 days to upgrade if you want to keep it.",
    ),
    "terms": [
        {"term": "IAM", "plain": "AWS's service for users, roles and permissions, which decides who can do what."},
        {"term": "IAM role", "plain": "A set of AWS permissions that a person or a program can borrow for a short time."},
        {"term": "OIDC", "plain": "A standard that lets one system, such as GitHub, prove who it is to another with a short-lived signed token."},
        {"term": "Trust policy", "plain": "The part of an IAM role that says who may use the role, for example one GitHub repo."},
        {"term": "S3 bucket", "plain": "A named storage container in AWS that holds files, which S3 calls objects."},
        {"term": "Data source", "plain": "A read-only lookup in Terraform, such as your AWS account ID, that manages nothing."},
        {"term": "Budget alert", "plain": "An email from AWS Budgets when your spending passes, or is expected to pass, a limit."},
    ],
    "sections": SECTIONS,
    "analogy": "OIDC works like a hotel key card. At the front desk (GitHub) you prove who you are, and you get a card that opens one room (the IAM role) and stops working at checkout. Nobody carries a master key that works forever. The picture misses one thing: a hotel checks your passport in person, while AWS only trusts GitHub's signature, which is why the trust policy must name exactly which repo may get a card.",
    "diagram": D29,
    "diagram_caption": "Checks and a plan run on pull requests. After merge and approval the apply job runs. Both AWS jobs swap a GitHub OIDC token for short-lived AWS credentials.",
    "worked": WORKED,
    "code": [
        code("hcl", "infra/aws/versions.tf", lab("infra/aws/versions.tf"), "terraform init"),
        code("hcl", "infra/aws/variables.tf", lab("infra/aws/variables.tf"), "terraform validate"),
        code("hcl", "infra/aws/main.tf", lab("infra/aws/main.tf"), "terraform plan"),
        code("hcl", "infra/aws/github-oidc.tf", lab("infra/aws/github-oidc.tf"), "terraform apply"),
        code("hcl", "infra/aws/outputs.tf", lab("infra/aws/outputs.tf"), "terraform output"),
        code("hcl", "infra/aws/.tflint.hcl", lab("infra/aws/.tflint.hcl"), "tflint --init && tflint"),
        code("yaml", ".github/workflows/terraform.yml", lab(".github/workflows/terraform.yml"), "git add .github/workflows/terraform.yml && git commit -m \"Terraform CI\" && git push"),
    ],
    "commands": [
        cmd("aws configure sso", "Set up a CLI profile that signs in through IAM Identity Center."),
        cmd("aws sso login", "Sign in through the browser and get short-lived credentials for today."),
        cmd("aws sts get-caller-identity", "Show which account and identity your credentials belong to."),
        cmd("terraform init -backend=false", "Install providers without touching the backend, so validate works with no cloud login."),
        cmd("terraform init -migrate-state", "After changing the backend block, copy the existing state to the new place."),
        cmd("terraform fmt -check -recursive", "Fail if any file is not formatted. Good for CI."),
        cmd("terraform plan -out=tfplan", "Save the plan to a file, so apply does exactly what you reviewed."),
        cmd("terraform apply tfplan", "Apply a saved plan without asking again."),
        cmd("terraform -chdir=../modules/hello-stack test", "Run the module's tests from another folder."),
        cmd("tflint --init && tflint", "Install the plugins named in .tflint.hcl, then lint the folder."),
        cmd("trivy config --severity HIGH,CRITICAL --exit-code 1 .", "Scan Terraform files for risky settings and fail on serious ones."),
        cmd("checkov -d .", "Scan the folder with checkov's built-in policies."),
        cmd("gh variable set AWS_ROLE_ARN --body ARN", "Save the role ARN as a repository variable, which turns on the AWS jobs."),
        cmd("aws s3 ls", "List your S3 buckets, to check what exists before and after cleanup."),
    ],
    "mistake": "Running `terraform destroy` while the state still lives in the bucket you are destroying. The bucket goes away, and Terraform has nowhere to save the final state. First comment out the backend block and run `terraform init -migrate-state` to bring the state home, then destroy.",
    "real_world": "At PayLoop (still made up), engineers have read-only access to production. Every infrastructure change goes through a pull request with its plan posted for review. Only the pipeline's role can apply, and only after a second person approves. When the team accepts a scanner finding, they write the reason next to it, so auditors can see each decision.",
    "task": {
        "title": "Optional: the bucket on AWS, state in S3, CI, then clean up",
        "steps": [
            "No AWS account? Do only steps 6 and 7 without AWS: push a branch that changes a file under `infra/`, and check that the `checks` job passes while `plan` and `apply` are skipped.",
            "Secure the account: Free plan, root MFA, a zero spend budget with your email, and a login that is not root. `aws sts get-caller-identity` must not show root.",
            "In `infra/aws`, create `terraform.tfvars` as in the worked example, then run `terraform init` and `terraform apply`. Read the plan first: how many resources, and which are IAM?",
            "Uncomment the backend block, paste the bucket name from `terraform output bucket_name`, and run `terraform init -migrate-state`. Then run `terraform state list` to see it read state from S3.",
            "In GitHub, save `terraform output github_actions_role_arn` as a repository variable named `AWS_ROLE_ARN`. Check that the `production` environment from Day 21 still has you as a required reviewer.",
            "Add `.github/workflows/terraform.yml`. On a branch, add a `tags` argument to the bucket resource only, push, and open a pull request.",
            "Read the plan on the run's summary page. Then merge, approve the apply job, and watch it finish.",
            "Clean up from your laptop: comment out the backend block, run `terraform init -migrate-state` to bring the state home, then `terraform destroy`.",
            "Delete the `AWS_ROLE_ARN` variable so the AWS jobs skip again, delete any IAM access key you created today, and keep or delete the budget.",
        ],
        "hints": [
            "If the plan job fails at the AWS login, compare the `sub` values in the role's trust policy with your repo. Repos created after July 15, 2026 use the numeric ID form.",
            "Tag the bucket, not `default_tags`. A default tag also changes the IAM resources, and the CI role may not change IAM.",
            "If `terraform destroy` fails on the bucket, check that `force_destroy = true` is still in `main.tf`; versioned buckets keep old file versions.",
        ],
        "done_when": "The apply job in GitHub ended with `Apply complete!`, and after cleanup `aws s3 ls` no longer lists your hello-devops bucket.",
    },
    "explain_back": {
        "prompt": "In 3 to 4 sentences, explain how your workflow gets permission to change AWS without any stored keys. Mention the OIDC provider, the trust policy and the `sub` claim.",
        "answer": "The job has `id-token: write`, so it can ask GitHub for a signed OIDC token. The configure-aws-credentials action sends that token to AWS and asks to use our IAM role. AWS checks the signature through the OIDC provider for token.actions.githubusercontent.com, and the role's trust policy checks the `aud` and `sub` claims. The `sub` names our repo and the context, such as a pull request or the production environment, so no other repo can use the role. If everything matches, AWS returns credentials that expire after a short time.",
    },
    "recap": [
        "Cloud work starts with safety: Free plan, root MFA, a login that is not root and a budget alert. It ends with destroy.",
        "Bucket settings such as versioning and the public access block are separate resources in the AWS provider.",
        "Create the state bucket with local state, then move state into it with `terraform init -migrate-state`.",
        "CI runs cheap checks first, plans on pull requests, and applies on main after an environment approval.",
        "OIDC gives CI short-lived credentials, and the trust policy's `sub` check decides who may use the role.",
        "Scanners such as trivy, tflint and checkov advise; you decide, and pin the scanner itself by digest or SHA.",
    ],
    "check": [
        mcq("Your pull request's plan job passes the checks, then fails with \"Not authorized to perform sts:AssumeRoleWithWebIdentity\". What is the most likely cause?",
            ["The bucket name is already taken", "The token's `sub` does not match the trust policy", "terraform fmt changed a file during the run", "The budget alert blocked the request"],
            1, "That error means AWS refused the token for this role, which almost always means the `sub` or `aud` condition did not match."),
        mcq("You want CI to apply only after a person says yes. Where does that gate live in the lab?",
            ["In the production environment's required reviewers", "In the S3 backend's lock file", "In the trust policy's `aud` condition", "In the workflow's concurrency group"],
            0, "A job with `environment: production` waits until a required reviewer of that environment approves it."),
        mcq("A teammate adds `Owner = \"ops\"` to the provider's `default_tags` in a pull request. The plan looks fine, but apply on main fails. Why?",
            ["Tags cannot change once a bucket exists", "The saved plan expired before apply", "S3 buckets do not support tags", "Default tags also change the IAM role"],
            3, "The CI role can read IAM but not change it, so tag updates on the IAM role and OIDC provider are refused at apply time."),
    ],
    "interview": [
        {"q": "How would you run Terraform safely in CI/CD?",
         "a": "Run fmt, validate, a linter, module tests and a security scanner on every pull request, then a plan that reviewers can read. Apply only from the main branch, behind an approval such as a protected environment, with one run at a time. Keep state in a remote backend with locking, and log in with OIDC so there are no long-lived cloud keys. Give the CI role the smallest permissions it needs, keep powerful changes such as IAM out of the automatic path, and pin third-party actions to commit SHAs."},
        {"q": "Why use OIDC instead of AWS access keys stored in GitHub secrets?",
         "a": "Access keys last until someone deletes them, so a key that leaks through a log or a compromised action can be used for months. With OIDC, the job gets a signed token from GitHub and swaps it for AWS credentials that expire within hours. The role's trust policy limits which repo, branch or environment may get them. There is also nothing to store or rotate."},
        {"q": "Why pin a GitHub Action to a commit SHA instead of a tag like v4?",
         "a": "A tag is a movable pointer, so whoever controls the action's repo can point it at different code later. In March 2026 attackers did exactly that to most tags of `aquasecurity/trivy-action`, and every workflow that used those tags ran their code. A full commit SHA cannot be moved, so you run the code you reviewed. A version comment next to the SHA and Dependabot keep pinned actions readable and up to date."},
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "The lab's pipeline leaves three gaps that real teams usually close.\n\n"
            "First, the plan you reviewed is not exactly the plan that runs. The pull request's plan is made from the branch, before the merge. The apply job makes a fresh plan from main, which may include other merged changes or new drift. Teams handle this in a few ways:\n"
            "- Require pull request branches to be up to date with main before merging, so the reviewed plan is closer to what runs.\n"
            "- Split the work on main into two jobs. One plans and saves the plan file as an artifact. The next one, behind the environment gate, applies exactly that file, so the approver can read it first.\n"
            "- Use a tool built for this. Atlantis is open source and runs plan and apply from pull request comments. HCP Terraform and similar services do the same as a hosted product.\n\n"
            "Second, one role for both jobs gives a pull request more power than it needs. A cleaner design has two roles. The plan role trusts only `pull_request` and gets read-only permissions, plus access to the state and lock files. The apply role trusts only `environment:production` and may change things. This matters because anyone who can push a branch could edit the workflow in a pull request to run apply.\n\n"
            "Third, access to state is a permission in itself. Anyone who can write the state bucket can change what Terraform believes exists. Big teams keep state buckets in a separate account. They turn on versioning and `prevent_destroy`, and only a few roles may write. Each environment gets its own state file, and often its own account, so a mistake in the dev state cannot touch production.\n\n"
            "Teams also use destroy outside labs. They run short-lived test environments and destroy them automatically each night. Because the code describes everything, one apply brings them back in the morning, and the same `terraform test` suite from Day 28 checks that the modules still build what they promise."
        ),
    },
    "sources": [
        {"title": "Backend type: s3", "url": HC + "language/backend/s3"},
        {"title": "Configuring OpenID Connect in Amazon Web Services", "url": "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws"},
        {"title": "Choosing an AWS Free Tier plan", "url": "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html"},
        {"title": "Trivy", "url": "https://github.com/aquasecurity/trivy"},
    ],
}
