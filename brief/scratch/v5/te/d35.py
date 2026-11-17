from common import apply

S0 = """
Everything on AWS today is optional. AWS (Amazon Web Services) is Amazon's cloud, and the rest of the course runs on your laptop. The worked example below needs no account at all.

If you want to follow along on AWS and skipped Day 13, do it first. That lesson opens the account safely, in four moves:
- It opens the account on the Free plan.
- It protects the root user, the all-powerful first login, with MFA: a second proof such as a code from your phone.
- It sets a zero-spend budget, which emails you as soon as anything costs money.
- It gives you an everyday IAM user (a login with limited rights) that signs in with `aws login`.

Today adds nothing to that list. One warning from it matters again here: do not create an AWS Organization on a learning account, because joining one moves a Free plan account to the Paid plan.

If you ran Day 14's `cleanup.sh`, nothing from those lessons is still running, so today's bill starts from zero. Today's resources are cheap too, because almost nothing here bills by the hour:
- IAM roles and the OIDC provider cost nothing. You will meet both shortly.
- S3, Amazon's file storage, charges per gigabyte stored each month plus a little per request. A state file is a few kilobytes, so the bucket costs close to nothing. Check the S3 pricing page for your Region (the part of the world your resources live in) anyway.

A budget alert only sends email. It stops nothing, and its numbers can lag by hours. Destroying what you create is what protects you, and it is the last step today. With the account safe, the first question is how Terraform proves who you are.
"""

S1 = """
On your laptop, Docker trusted Terraform because they ran on the same machine. AWS is far away, so Terraform needs credentials: the proof of who you are, like a key and a password together. Terraform's AWS provider finds credentials the same way as the AWS CLI (the `aws` command), and its docs list the order:
1. Arguments in the provider block.
2. Environment variables, such as `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`.
3. The shared files in `~/.aws`.
4. The credentials of a container or a machine running in AWS, such as Day 14's instance role.

So the login from Day 13 works as it is. Run `aws login --profile learn`, then `export AWS_PROFILE=learn` in the same terminal. `aws sts get-caller-identity` should print your 12-digit account ID and your IAM user, not root. Inside Terraform, the `aws_caller_identity` data source asks the same question. A data source reads something that already exists without managing it, and the next section uses its answer to name the bucket.

`aws login` is newer than many tools. If Terraform, or any other tool, says it found no credentials while `aws sts get-caller-identity` works, run `eval "$(aws configure export-credentials --profile learn --format env)"`. It copies the profile's short-lived credentials into your terminal's environment variables, which every tool checks. Leftover `AWS_ACCESS_KEY_ID` variables beat `AWS_PROFILE` (Day 13), so when a plan shows the wrong account, run `aws configure list`.

Leave a `profile` argument out of the provider block. A profile name ties the code to your laptop, while an environment variable keeps the same code working in CI. Never put an access key into a `.tf` file or a `.tfvars` file either. In CI, the same provider block finds the short-lived variables that the `configure-aws-credentials` action exports, which is step 2 in the list above. They come with no stored key, and we build that a little later. First, something for Terraform to build.
"""

S2 = """
The lab's `infra/aws` folder creates one S3 bucket, a named storage place for files. A bucket name must be unique across every AWS account in the world, so the code adds your 12-digit account ID to it, read with the data source `aws_caller_identity`.

In the AWS provider, a bucket's settings are separate resources that sit next to `aws_s3_bucket`. Each one matches its own request in the S3 API, so changing one setting leaves the others alone:
- `aws_s3_bucket_versioning` keeps every old version of every file, so you can undo a bad write.
- `aws_s3_bucket_public_access_block` stops anything in the bucket from becoming public.
- `aws_s3_bucket_server_side_encryption_configuration` encrypts files with keys that S3 manages.

New buckets already block public access and encrypt files by default. Write it down anyway, so reviewers and scanners can see it. The provider's `default_tags` block adds tags (labels such as `Project` and `ManagedBy`) to every resource, so you can always tell what something is for.

This bucket also stores its own state, which sounds impossible at first. It is like needing a toolbox to build the shed you will keep the toolbox in. Terraform needs the bucket to store the state, but the bucket does not exist until Terraform creates it. You solve it in two steps:
1. Apply with local state. This creates the bucket.
2. Uncomment the `backend "s3"` block, put in the bucket name, and run `terraform init -migrate-state`. Terraform copies the state into S3 and uses it from then on.

The block sets `use_lockfile = true`, which you met in the state lesson. Each run writes a small `.tflock` file next to the state, and a second run that finds it stops with a lock error.

Leaving needs the same care in reverse. If you run `terraform destroy` while the state still lives in the bucket you are destroying, the bucket goes away and Terraform has nowhere to save the final state. So first comment out the backend block and run `terraform init -migrate-state` to bring the state home, then destroy. Now the bucket exists, and the pipeline needs a way in.
"""

S3 = """
Back to the doormat. An AWS access key saved as a GitHub secret works until someone deletes it, so a leaked key stays useful for months. On Day 27 you met the hotel desk instead: OIDC (OpenID Connect). A workflow asks GitHub for a short-lived token, a signed pass that expires soon. The pass holds claims, named fields such as the repo and branch the job runs for.

AWS never sees the job in person. It only trusts GitHub's signature, so it must be told exactly which repo may get a card. The lab's `github-oidc.tf` builds the AWS side in three parts:
1. An OIDC identity provider for `token.actions.githubusercontent.com`, so AWS can check GitHub's signature. Its audience, `sts.amazonaws.com`, is the `aud` claim a token must carry.
2. An IAM role (a set of permissions a program can borrow for a while) whose trust policy checks the token's `sub` (subject) claim. It names your repo and the context, such as `pull_request` or `environment:production`.
3. A permissions policy that says what the role may do.

The `sub` has to match exactly, character for character. Repos created after July 15, 2026 put numeric IDs in it, like `repo:you@123456/hello-devops@456789:pull_request`. Older repos use `repo:you/hello-devops:pull_request`. The lab trusts both forms, for your repo only. When the login fails with "Not authorized to perform sts:AssumeRoleWithWebIdentity", check the `sub` first.

Keep the role small. The lab's role may manage only buckets whose names start with `hello-devops-`, and read its own IAM setup so that plan works. It cannot change IAM, so a pull request cannot give the pipeline more power. You apply IAM changes from your laptop.

**A key that never expires is a key under the doormat. Let the pipeline borrow one that does.**

The key card is ready. Next comes the pipeline that carries it.
"""

S4 = """
The lab's `.github/workflows/terraform.yml` runs whenever anything under `infra/` changes. It has three jobs, each a group of steps that GitHub runs on a fresh machine:
1. `checks` runs on every pull request and push, with no cloud login. It runs `terraform fmt -check`, tflint, a trivy scan, `terraform validate` for `infra/local` and `infra/aws`, and the hello-stack module's tests with the mock provider from Day 34.
2. `plan` runs on pull requests once the checks pass. It logs in to AWS with OIDC, runs `terraform plan -out=tfplan`, and puts the plan on the run's summary page for reviewers.
3. `apply` runs after a merge to main. It waits in the `production` environment until a required reviewer approves, then plans and applies.

The cheap checks run first, so a formatting slip fails before anything logs in to AWS. The AWS jobs also have `vars.AWS_ROLE_ARN != ''` in their `if`. An ARN is the full AWS name of a resource, here the role. Until you save the role's ARN as a repository variable, those jobs are skipped, so a repo without an AWS account still gets green checks.

Look for these settings in the file as well:
- `concurrency` with `cancel-in-progress: false` on the AWS jobs, so a second run waits and never stops an apply halfway.
- `TF_VAR_` environment variables filled from the `github` context, so CI passes your owner, repo and their IDs without any secrets.
- `id-token: write` only on the two jobs that log in to AWS. The checks job can only read the repo.
- Third-party actions pinned to full commit SHAs, as on Day 27. A SHA is the long fingerprint that names one exact commit.

Picture a team where auditors check every production change. Engineers there get read-only access to production. Changes go through a pull request with the plan posted for review, and only the pipeline's role can apply, after a second person approves. The pipeline also runs scanners, and a scanner deserves a closer look of its own.
"""

S5 = """
Plan tells you what will change. It does not tell you whether the change is wise. Three free tools help:
- tflint, from Day 34, finds mistakes that `validate` misses. The lab's `infra/aws/.tflint.hcl` turns on its AWS plugin, which knows real AWS values.
- `trivy config` looks for security problems, such as public buckets, missing encryption, or IAM policies that allow too much. It took over from tfsec, whose README asks users to move to Trivy.
- checkov does a similar job with over 1000 built-in policies, and it can scan GitHub Actions workflows too.

Scanners are strict on purpose, and you decide what to fix. To accept a finding, put a comment such as `# trivy:ignore:AWS-0132` above the resource, followed by your reason. A reviewer can then read the decision and question it. When a team accepts a finding, the reason sits next to the code, where anyone checking later can see it.

A scanner is also software that runs with access to your code, and sometimes to your secrets. In March 2026, attackers moved most version tags of `aquasecurity/trivy-action` to malicious code, tracked as CVE-2026-33634 (a public ID for a known security hole). Any workflow that used the action through one of those tags ran the attacker's code. The lab's Terraform workflow runs the trivy image pinned to a digest, a fingerprint of one exact image. Its release workflow pins trivy-action to a full commit SHA. Day 63 tells the whole story.

A scanner runs next to your secrets, so pin it like any other code.

Terraform has now built real things in a real cloud, from a pipeline, with keys that expire. It builds the house well. It is much less good at the work inside a server that already exists: installing programs, writing settings files, restarting services. That is the job of the next part.
"""

new = {
    "goal": "By the end you can set up a safe AWS account, create a private S3 bucket with Terraform, keep the state in it, and run checks, plan and apply from GitHub Actions without stored keys.",
    "opening": """Picture going away for two weeks while a builder works on your house. The quick way is to leave a spare key under the doormat. It works on the first day, and it keeps working for years, for anyone who lifts the mat.

A hotel does it differently. The front desk checks who you are, then hands you a card that opens one room and stops working at checkout. The doormat is tempting because it is quick, and nothing goes wrong until the day it does.

Last time, every stack ran on your laptop, where nothing cost money and nobody else could get in. In this lesson, we'll take the same Terraform to AWS, Amazon's cloud. We'll build a private storage bucket, keep the state inside it, and let a pipeline plan and apply with hotel cards instead of a key under the mat. Everything on AWS today is optional. Before we start, make a guess, and keep it in mind.""",
    "guess": (
        "You open a new AWS account on the Free plan. What happens when your free credits run out?",
        "The Free plan never charges you. When the credits or the six months run out, the account closes, and you have 90 days to upgrade if you want to keep it.",
    ),
    "terms": [
        "AWS's service for users, roles and permissions, which decides who can do what.",
        "A set of AWS permissions that a person or a program can borrow for a short time.",
        "A standard that lets one system, such as GitHub, prove who it is to another with a signed pass that soon expires.",
        "The part of an IAM role that says who may use the role, for example one GitHub repo.",
        "A named storage place in AWS that holds files, which S3 calls objects.",
        "A read-only lookup in Terraform, such as your AWS account ID, that manages nothing.",
        "An email from AWS Budgets when your spending passes, or is expected to pass, a limit.",
    ],
    "sections": [
        ("Before any cloud: a safe account, and what today costs", S0),
        ("How Terraform proves who you are to AWS", S1),
        ("A private bucket, then the state inside it", S2),
        ("A hotel key card for the pipeline: OIDC", S3),
        ("The pipeline: checks, a plan on pull requests, apply on main", S4),
        ("Scanners, and checking the checker", S5),
    ],
    "diagram_caption": "Checks and a plan run on pull requests. After merge and approval the apply job runs. Both AWS jobs swap a GitHub OIDC token for short-lived AWS credentials.",
    "worked": [
        "Start in `infra/aws`. Formatting and validation need no AWS account. `-backend=false` skips the S3 backend, which does not exist yet, and `fmt -check` prints nothing when every file is tidy.",
        "Run the module tests the way CI does. The mock provider means no Docker and no cloud.",
        "Scan with trivy (`brew install trivy`, or the `aquasec/trivy` image as CI does). Before the ignore comments were added, it reported three findings. These are its headline lines.",
        "Decide on each one. Access logs need a second bucket. A customer managed KMS key (an encryption key you own) costs money every month. So for a lab, you accept both. `s3:*` is limited to this project's buckets. Write each decision above the block it is about.",
        "Scan again the way CI does. `--exit-code 1` fails the job on HIGH or CRITICAL findings. Now every file shows 0, and the exit code is 0. Without the comments, the same command exits with 1.",
        "Give the variables values. `gh api` returns the numeric IDs of your user and your repo. Nothing in `terraform.tfvars` is secret, so you may commit it. Your numbers will differ.",
        "Try a plan with no credentials at all. It stops at the provider. CI logs in with OIDC at exactly this point, and your laptop needs the `aws login` profile from Day 13.",
    ],
    "task": {
        "steps": [
            "No AWS account? Do only steps 6 and 7 without AWS: push a branch that changes a file under `infra/`, and check that the `checks` job passes while `plan` and `apply` are skipped.",
            "Sign in as on Day 13 (`aws login --profile learn` and `export AWS_PROFILE=learn`). `aws sts get-caller-identity` must show your IAM user, not root.",
            "In `infra/aws`, create `terraform.tfvars` as in the worked example, then run `terraform init` and `terraform apply`. Read the plan first: how many resources, and which are IAM?",
            "Uncomment the backend block, paste the bucket name from `terraform output bucket_name`, and run `terraform init -migrate-state`. Then run `terraform state list` to see it read the state from S3.",
            "In GitHub, save `terraform output github_actions_role_arn` as a repository variable named `AWS_ROLE_ARN`. Check that the `production` environment from Day 27 still has you as a required reviewer.",
            "Add `.github/workflows/terraform.yml`. On a branch, add a `tags` argument to the bucket resource only, push, and open a pull request.",
            "Read the plan on the run's summary page. Then merge, approve the apply job, and watch it finish.",
            "Clean up from your laptop: comment out the backend block, run `terraform init -migrate-state` to bring the state home, then `terraform destroy`.",
            "Delete the `AWS_ROLE_ARN` variable so the AWS jobs skip again, run `aws logout --profile learn` if you are done for the day, and keep the budget.",
        ],
        "hints": [
            "If the plan job fails at the AWS login, compare the `sub` values in the role's trust policy with your repo. Repos created after July 15, 2026 use the form with numeric IDs.",
            "Tag the bucket, not `default_tags`. A default tag also changes the IAM resources, and the CI role may not change IAM.",
            "If `terraform destroy` fails on the bucket, check that `force_destroy = true` is still in `main.tf`. Versioned buckets keep old file versions.",
        ],
        "done_when": "The apply job in GitHub ended with `Apply complete!`, and after cleanup `aws s3 ls` no longer lists your hello-devops bucket.",
    },
    "explain_back": (
        "In 3 to 4 sentences, explain how your workflow gets permission to change AWS without any stored keys. Mention the OIDC provider, the trust policy and the `sub` claim.",
        "The job has `id-token: write`, so it can ask GitHub for a signed OIDC token. The configure-aws-credentials action sends that token to AWS and asks to use our IAM role. AWS checks the signature through the OIDC provider for token.actions.githubusercontent.com, and the role's trust policy checks the `aud` and `sub` claims. The `sub` names our repo and the context, such as a pull request or the production environment, so no other repo can use the role. If everything matches, AWS returns credentials that expire after a short time.",
    ),
    "recap": [
        "Cloud work starts with safety: Free plan, MFA on root, an everyday login and a budget alert. It ends with destroy.",
        "Bucket settings such as versioning and the public access block are separate resources in the AWS provider.",
        "Create the state bucket with local state, then move the state into it with `terraform init -migrate-state`.",
        "CI runs cheap checks first, plans on pull requests, and applies on main after an environment approval.",
        "OIDC gives CI short-lived credentials, and the trust policy's `sub` check decides who may use the role.",
        "Scanners advise and you decide, so pin the scanner itself. Terraform builds machines well, but setting up software inside them is another job.",
    ],
    "closing": """We started with a key under the doormat and a hotel card that stops at checkout. Today the pipeline got the hotel card: a signed pass from GitHub, checked by a trust policy that names one repo, swapped for keys that expire.

In your repo, search every workflow for `AWS_ACCESS_KEY_ID` and for actions pinned to a tag such as `@v4`. Each one is a key or a door that could still be moved.

Next, we'll step inside a server that already exists. How do you install and set up software on many machines with a checklist that is safe to run twice?""",
    "check": [
        ("Your pull request's plan job passes the checks, then fails with \"Not authorized to perform sts:AssumeRoleWithWebIdentity\". What is the most likely cause?",
         "That error means AWS refused the token for this role, which almost always means the `sub` or `aud` condition did not match."),
        ("You want CI to apply only after a person says yes. Where does that gate live in the lab?",
         "A job with `environment: production` waits until a required reviewer of that environment approves it."),
        ("A teammate adds `Owner = \"ops\"` to the provider's `default_tags` in a pull request. The plan looks fine, but apply on main fails. Why?",
         "The CI role can read IAM but not change it, so tag updates on the IAM role and the OIDC provider are refused at apply time."),
    ],
    "interview": [
        ("How would you run Terraform safely in CI/CD?",
         "Run fmt, validate, a linter, module tests and a security scanner on every pull request, then a plan that reviewers can read. Apply only from the main branch, behind an approval such as a protected environment, with one run at a time. Keep the state in a remote backend with locking, and log in with OIDC so there are no long-lived cloud keys. Give the CI role the smallest permissions it needs, keep powerful changes such as IAM out of the automatic path, and pin third-party actions to commit SHAs."),
        ("Why use OIDC instead of AWS access keys stored in GitHub secrets?",
         "Access keys last until someone deletes them, so a key that leaks through a log or a compromised action can be used for months. With OIDC, the job gets a signed token from GitHub and swaps it for AWS credentials that expire within hours. The role's trust policy limits which repo, branch or environment may get them. There is also nothing to store or rotate."),
        ("Why pin a GitHub Action to a commit SHA instead of a tag like v4?",
         "A tag is a pointer that can be moved, so whoever controls the action's repo can point it at different code later. In March 2026 attackers did exactly that to most tags of `aquasecurity/trivy-action`, and every workflow that used those tags ran their code. A full commit SHA cannot be moved, so you run the code you reviewed. A version comment next to the SHA, and Dependabot, keep pinned actions readable and up to date."),
    ],
    "deeper": """
The lab's pipeline leaves three gaps that real teams usually close.

First, the plan you reviewed is not exactly the plan that runs. The pull request's plan is made from the branch, before the merge. The apply job makes a fresh plan from main, which may include other merged changes or new drift. Teams handle this in a few ways:
- Require pull request branches to be up to date with main before merging, so the reviewed plan is closer to what runs.
- Split the work on main into two jobs. One plans and saves the plan file as an artifact (a file a job keeps for later jobs). The next one, behind the environment gate, applies exactly that file, so the approver can read it first.
- Use a tool built for this. Atlantis is open source and runs plan and apply from pull request comments. HCP Terraform and similar services do the same as a hosted product.

Second, one role for both jobs gives a pull request more power than it needs. A cleaner design has two roles. The plan role trusts only `pull_request` and gets read-only permissions, plus access to the state and lock files. The apply role trusts only `environment:production` and may change things. This matters because anyone who can push a branch could edit the workflow in a pull request to run apply.

Third, access to the state is a permission in itself. Anyone who can write the state bucket can change what Terraform believes exists. Big teams keep state buckets in a separate account. They turn on versioning and `prevent_destroy`, and only a few roles may write. Each environment gets its own state file, and often its own account, so a mistake in the dev state cannot touch production.

Teams also use destroy outside labs. They run short-lived test environments and destroy them automatically each night. Because the code describes everything, one apply brings them back in the morning, and the same `terraform test` suite from Day 34 checks that the modules still build what they promise.
""",
    "drop": ["analogy", "mistake", "real_world"],
}

apply(8, "d35", new)
