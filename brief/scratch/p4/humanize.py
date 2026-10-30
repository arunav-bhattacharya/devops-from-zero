#!/usr/bin/env python3
"""Human-voice edit of content/p4.json (Terraform, d13 to d15).

Loads the current JSON, replaces prose fields only, and writes it back.
Ids, titles, code, commands, refs, sources, answers, options and diagrams
are left exactly as they are. Do not rerun build.py after this: it would
overwrite these edits.
"""
import json
import pathlib

PATH = pathlib.Path("/home/user/devops-from-zero/content/p4.json")
P = json.loads(PATH.read_text())
L = {x["id"]: x for x in P["lessons"]}

# ---------------------------------------------------------------- part level

P["intro"] = (
    "Up to now you made containers by typing commands. From here on you describe infrastructure in files, "
    "and Terraform makes the real world match them. You start with Docker on your laptop. Then, if you want, "
    "you create a real AWS bucket and run Terraform from GitHub Actions."
)

P["recap"] = [
    "IaC keeps infrastructure in reviewed, versioned files, and Terraform makes reality match them.",
    "The loop is init, plan, apply and destroy. Read the plan every time before you approve it.",
    "Variables, outputs, locals and modules make Terraform code reusable.",
    "State links code to real objects and can hold secrets, so it belongs in a locked remote backend.",
    "`plan -refresh-only` shows drift, and `import` blocks adopt things that already exist.",
    "On AWS, do the safety steps first: root MFA, a non-root login and a budget alert. Destroy everything when you finish.",
    "CI checks and plans on pull requests, and applies on main after approval. It logs in with OIDC, so no keys are stored.",
]

FB = {
    3: "HashiCorp moved Terraform to the BSL in 2023, so the community forked the last open source version.",
    5: "No. It only hides the value on screen. The state file still stores it in plain text.",
    8: "Removing one key affects only that copy. With count, the later copies shift and get replaced.",
    10: "It writes a .tflock file next to the state, so only one run can change the state at a time.",
}
for i, back in FB.items():
    P["flashcards"][i]["back"] = back

QW = {
    0: "Terraform cannot change that attribute on the existing object, so it destroys the object and creates a new one.",
    1: "State stores resource attributes, passwords and tokens included, so protect it and keep it in a proper backend.",
    7: "It copies your current state into the backend you just configured, so Terraform still knows what exists.",
}
for i, why in QW.items():
    P["quiz"][i]["why"] = why

# ---------------------------------------------------------------- d13

d = L["d13"]
d["sections"][0]["body"] = """Build a server by clicking through a cloud web page and it works. Six months later you need a second one, exactly the same. Which boxes did you tick? Nobody remembers.

Doing it by hand goes wrong in a few ways:
- You cannot repeat it. There is no exact copy for testing or for another region.
- Nobody reviews it. A change happens without anyone looking first, and nothing records it.
- It drifts. Someone changes a setting by hand, and reality slowly moves away from what everyone believes.

**Infrastructure as Code** (IaC) means you describe your infrastructure in text files, and a tool makes the real world match them. The files live in git, so your infrastructure gets the same treatment as your Kotlin code:
- `git log` shows every change and who made it.
- A pull request lets a teammate review a change before it happens.
- Reverting a commit and applying again rolls a change back."""

d["sections"][1]["body"] = """You can tell a computer what to do in two ways:
- Imperative: you list the steps. "Start this container, then open this port." A shell script works this way.
- Declarative: you describe the result. "There is one nginx container on port 8090." The tool works out the steps.

Terraform is declarative, and you see why that matters the second time you run it. Run a "start a container" script twice and it either fails or makes a duplicate. A Terraform file only says what should exist. If it already exists, Terraform does nothing. A command that gives the same result however many times you run it is called idempotent.

You used this idea on Day 7. `compose.yaml` describes services, and `docker compose up` makes them exist. Terraform does the same for almost anything that has an API, whether that is Docker on your laptop or a whole cloud account."""

d["sections"][2]["body"] = """Terraform is made by HashiCorp, which IBM bought in 2025. Until August 2023 it was open source under the MPL licence. Then [HashiCorp moved it to the Business Source License](https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license) (BSL). You may still use Terraform for free at work. What you may not do is build a competing hosted product with it.

Many companies disliked the change, so they forked the last open source version and called it OpenTofu. It lives at the Linux Foundation and joined the CNCF in 2025. You type `tofu` instead of `terraform`, and `tofu plan` behaves like `terraform plan`. Everything you learn this week works with both, so if your team already uses one, stay with it.

You will also hear about these tools:
- CloudFormation: AWS's own IaC service, with YAML or JSON templates. It only works for AWS.
- Pulumi: IaC written in normal programming languages such as Python, TypeScript, Go or Java.
- Ansible: logs in to servers that already exist and sets them up (packages, files, services).

Teams often split the work between them. Terraform creates the machines, and Ansible or a container image sets up what runs on them."""

d["sections"][3]["body"] = """Terraform files end in `.tf` and use HCL, the HashiCorp Configuration Language. You need three pieces of it:
- A block has a type, labels and braces: `resource "docker_container" "web" { }`.
- An argument sets a value inside a block: `name = "tf-web"`.
- A reference reads a value from another block: `docker_image.nginx.image_id`.

A resource block has two labels. The first is the resource type, such as `docker_container`, and it always starts with the provider's name. The second is your own name for it, such as `web`. Together they make the address `docker_container.web`, which must be unique in the folder.

References also set the order. The container refers to the image, so Terraform pulls the image first. You never write "do this first", because Terraform works the order out from the references.

A provider is a plugin that talks to one platform's API. You list providers in the `terraform` block with a source and a version, much like a dependency in a Gradle file. This lesson uses `kreuzwerker/docker`, which talks to the same Docker engine as the `docker` command."""

d["sections"][4]["body"] = """You use four commands, in this order:
1. `terraform init` downloads the providers into a hidden `.terraform` folder. It also writes `.terraform.lock.hcl`, which pins the exact provider versions.
2. `terraform plan` compares your files, the state and the real world. It prints what it would do and changes nothing.
3. `terraform apply` shows the plan again, waits for you to type `yes`, makes the changes and updates the state.
4. `terraform destroy` removes everything this folder manages.

Read every plan before you approve it. Each resource in it starts with a symbol:
- `+` create a new resource.
- `~` update in place: the same resource stays, one setting changes.
- `-/+` replace: destroy the old one, then create a new one.
- `-` destroy.

Replacement is where people get caught. Some settings cannot change on a running resource, such as a container's port. A small edit to one of them becomes `-/+`, and the line shows `# forces replacement`. For a container that is harmless. For a database it can mean lost data. So check the summary line as well, such as `Plan: 1 to add, 0 to change, 1 to destroy.`"""

d["sections"][5]["body"] = """After an apply, Terraform writes `terraform.tfstate`. It links each address in your code, such as `docker_container.web`, to a real object ID. Without it, Terraform could not tell "create a container" from "this container already exists".

Day 14 goes deeper into state. Until then, follow these rules:
- Never edit the state file by hand.
- Do not commit it to git. The lab's `.gitignore` already blocks `*.tfstate`.
- Do commit `.terraform.lock.hcl`, so everyone gets the same provider versions."""

d["analogy"] = (
    "Terraform works like a thermostat. You set the temperature you want, and it turns the heating on or off "
    "until the room matches. You never tell it \"heat for ten minutes\". The comparison fails in one place: a "
    "thermostat checks the room all the time, while Terraform only checks when you run plan or apply."
)

ws = d["worked"]["steps"]
ws[0]["say"] = ("Make a practice folder outside your repo and save the `main.tf` from the Files section in it. "
                "Then run init, which downloads the Docker provider the file asks for.")
ws[1]["say"] = ("Preview the change. Nothing exists yet, so the plan has two creates and no changes or destroys. "
                "The real output also lists every attribute; these lines are trimmed.")
ws[2]["say"] = ("Apply. Terraform shows the plan again and waits for `yes`. The image comes first because the "
                "container refers to it. Then check that nginx answers.")
ws[3]["say"] = ("Now set `restart = \"unless-stopped\"`. Docker can change that on a running container, so the plan "
                "shows `~` and keeps the same container. Apply it.")
ws[4]["say"] = ("Change `external = 8090` to `8091`. Docker cannot move a running container to a new port, so "
                "Terraform has to replace it. Look for `forces replacement`.")
ws[5]["say"] = ("Clean up. Destroy removes the container and also the image Terraform pulled, so `docker ps -a` "
                "no longer lists `tf-web`.")

d["mistake"] = (
    "Typing `yes` without reading the plan. A one-word edit can turn into `-/+`, and replacing a database means "
    "losing its data. Read the summary line and look for `forces replacement` every time, even when you are sure "
    "the change is small."
)
d["real_world"] = (
    "Take PayLoop, a payments company made up for this course. Nobody there creates production infrastructure by "
    "clicking. Every change is a pull request with the Terraform plan attached, and a second engineer reads that "
    "plan before anyone applies it. People open the cloud web console to look around, or in an emergency."
)

d["task"]["steps"][2] = "Run `terraform fmt`, `terraform init` and `terraform plan`. Count the creates in the plan before you apply."
d["task"]["steps"][5] = "Change the container's name and plan again. Find the line that forces replacement, then change the name back."

d["explain_back"]["prompt"] = (
    "A teammate has never used Terraform. In 3 to 4 sentences, tell them what happens when you run "
    "`terraform plan` and then `terraform apply`. Mention the state file and what `-/+` means."
)
d["explain_back"]["answer"] = (
    "Plan reads my .tf files, the state file and the real world, then prints the difference without changing "
    "anything. Apply shows that plan again, asks me to confirm, and calls the provider to make the changes. Then "
    "it updates the state file, so next time it knows what already exists. A `-/+` means a setting cannot change "
    "on the existing resource, so Terraform destroys it and creates a new one."
)

d["recap"][3] = "init downloads providers, plan previews, apply makes the changes, destroy cleans up."
d["recap"][5] = "OpenTofu is the open source fork of Terraform, with nearly identical commands."

d["check"][1]["why"] = ("Plan reads the real world, sees the container is missing, and proposes to create it again "
                        "so reality matches the code.")
d["check"][2]["why"] = ("Ansible is built to set up software on machines that already exist; Terraform and "
                        "CloudFormation mainly create infrastructure.")

d["interview"][0]["a"] = (
    "Infrastructure as Code means describing infrastructure, such as servers, networks and permissions, in text "
    "files that a tool applies. The files live in git, so every change gets reviewed and leaves a history. You can "
    "rebuild the same setup in another region or account, which helps with testing and disaster recovery. It also "
    "reduces drift: the code is the source of truth, and a plan shows any difference."
)
d["interview"][1]["a"] = (
    "Terraform is declarative. It mainly creates infrastructure through APIs and keeps track of it in a state file. "
    "Ansible is mainly for configuration: it connects to existing machines over SSH and runs tasks such as "
    "installing packages. Those tasks run in order, so Ansible feels more step by step. Many teams use both: "
    "Terraform creates the machines, and Ansible or a container image sets up what runs on them."
)

d["deeper"]["body"] = """Version constraints and the lock file decide which provider code runs on your machine. Give them ten minutes, because a surprise upgrade can break a plan that worked yesterday.

The `version` argument in `required_providers` is a constraint. Three forms cover most needs:
- `= 4.6.0` allows exactly one version.
- `~> 4.6` allows 4.6 and newer, but stays below 5.0. This is the usual choice.
- `~> 4.6.0` allows 4.6.x patch releases only.

`~>` is called the pessimistic constraint: only the rightmost number may grow. Major versions can remove or rename things, so move to a new major version on purpose, after reading the upgrade guide.

`terraform init` picks the newest version that fits and records it in `.terraform.lock.hcl`, together with checksums of the provider files. From then on, init installs that exact version, even when a newer one exists. To move forward, run `terraform init -upgrade` and commit the new lock file.

Mac users run into one edge case here. Checksums are per platform: your Mac is `darwin_arm64`, while GitHub's runners are `linux_amd64`. Terraform usually records checksums for every platform. When providers come from a local cache or mirror, though, it may record only yours, and init in CI then fails with a checksum error. Fix it once with `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64`, which records both.

The `terraform` block can also hold `required_version`, which sets the Terraform CLI versions allowed to run this code. The lab's `infra/aws` asks for `>= 1.11`, because the S3 lock file you meet on Day 15 needs a recent version.

OpenTofu reads the same blocks but downloads providers from its own registry. Read the OpenTofu migration guide before you switch one state between `terraform` and `tofu`."""

# ---------------------------------------------------------------- d14

d = L["d14"]
d["guess"]["why"] = ("`sensitive` only hides the value in Terraform's output. The state file still holds it in plain "
                     "text, so protect state like a secret.")

d["sections"][0]["body"] = """Hard-coded values make code hard to reuse. Terraform gives you three kinds of named values:
- Input variables are the folder's parameters. A `variable` block gives a type, a description and an optional default. You read one with `var.host_port`.
- Outputs are the folder's return values. Apply prints them, and `terraform output` shows them again later.
- Locals are named expressions inside the folder, read with `local.name`. Use one when you would otherwise repeat a long expression.

A variable without a default is required, and Terraform asks you for it. A value can come from several places. From weakest to strongest:
1. The `default` in the variable block.
2. An environment variable such as `TF_VAR_host_port=8081`.
3. A `terraform.tfvars` file in the folder, which Terraform loads automatically.
4. The `-var host_port=8081` flag.

The `-var` flag has a trap: Terraform does not remember it between runs. Apply with `-var` today, plan without it tomorrow, and Terraform wants to go back to the default. Put values you always want in `terraform.tfvars`."""

d["sections"][1]["body"] = """Every reference adds an edge to a graph. In the lab, the app container refers to the Redis container's name, and Redis refers to the network. So Terraform builds the network first, then Redis, then the app. Things with no link between them are built in parallel. `terraform graph` prints this graph as text that tools such as Graphviz can draw.

A data source reads something that already exists, without managing it. You write a `data` block and read it with a `data.` prefix. On Day 15 you use `data.aws_caller_identity.current` to read your AWS account ID. Terraform reads data sources during every plan, so the value is always fresh.

Sometimes a dependency is invisible. A program inside one container may need another container that the code never mentions. For that case there is `depends_on`. Reach for it last, only when a reference cannot express the link."""

d["sections"][2]["body"] = """The state file links each address in your code to a real object and stores every attribute Terraform read. Plan uses it to know what already exists. Some things about it are easy to get wrong:
- It can contain secrets in plain text, even values marked `sensitive`.
- You never edit it by hand. Commands such as `terraform state list`, `state show` and `state rm` exist for that.
- One laptop is a bad home for it. Two people with two copies will overwrite each other's work.

The **backend** decides where state lives. The default is a local file. Teams use a remote backend, such as an S3 bucket or HCP Terraform, HashiCorp's hosted service (it has a free tier with limits). A good backend also locks the state: while one run changes things, any other run is refused until it finishes.

With the S3 backend, `use_lockfile = true` turns on locking with a small lock file next to the state. Older guides use a DynamoDB table for this, and Terraform now marks that option as deprecated. You set up an S3 backend on Day 15."""

d["sections"][3]["body"] = """Drift happens when someone changes real infrastructure outside Terraform, for example by deleting a container or editing a setting in a web console. Every plan starts with a refresh, which reads the real state of each resource, so the next plan notices.

You then decide which side wins:
- The code wins: run a normal apply, and Terraform puts things back the way the code says.
- Reality wins: change your code to match. `terraform apply -refresh-only` writes the real values into the state without touching any infrastructure, but your code still decides the next normal plan.

To look without any risk, run `terraform plan -refresh-only`. It reports only what changed outside Terraform.

The opposite problem is something real that Terraform does not manage yet, such as a network someone made by hand. An `import` block adopts it. You write a resource block that describes it, plus an `import` block with two arguments: `to` (the address) and `id` (the real object's ID). The plan says "will be imported", and apply adds it to the state without recreating it."""

d["sections"][4]["body"] = """A module is a folder of .tf files. The folder where you run Terraform is the root module. When it calls another folder with a `module` block, that folder is a child module. You know functions from Kotlin, so think of a child module as one: its variables are the parameters and its outputs are the return values.

A `module` block needs a `source`. It can be:
- A local path, such as `./modules/site`.
- A registry address, such as `terraform-aws-modules/s3-bucket/aws`, with a `version` constraint.
- A git URL.

Public registry modules save a lot of work, but read one before you use it, because it runs with your permissions. Pin the version, and run `terraform init` after adding or changing a module.

To make several similar things, use a meta-argument. The `count = 3` argument makes three numbered copies. The `for_each` argument takes a map or a set and makes one copy per key, such as `module.site["blue"]`. Prefer `for_each`. If you remove one key, only that copy goes away. With `count`, the copies after it shift by one and get replaced."""

d["sections"][5]["body"] = """A `lifecycle` block inside a resource changes how Terraform treats it. You will meet these settings:
- `prevent_destroy = true` makes any plan that would destroy the resource fail with "Instance cannot be destroyed".
- `create_before_destroy = true` makes the new copy first and removes the old one after. It only works if two copies can exist at once.
- `ignore_changes` lists attributes that Terraform should stop correcting, because another system owns them.

Put `prevent_destroy` on anything that would hurt to lose, such as databases and state buckets. Know its gap, though: if you delete the whole resource block from your code, the guard goes with it."""

d["analogy"] = (
    "State is like the ticket book in a theatre cloakroom. When you hand in a coat, the attendant writes your "
    "ticket number next to the hook. Without the book, there is a room full of coats and no way to know which one "
    "is yours. The comparison has a limit: the book only notes the hook, while Terraform's state copies every "
    "detail of each resource, secrets included."
)

ws = d["worked"]["steps"]
ws[0]["say"] = ("In a practice folder, create `modules/site/main.tf`. It takes three inputs and returns a URL. The "
                "`terraform` block is there because a child module that uses a non-HashiCorp provider must name it "
                "in its own `required_providers`.")
ws[1]["say"] = ("Next to the `modules` folder, write `main.tf`. Copy the `terraform` and `provider` blocks from Day "
                "13's file to the top, then add this. `for_each` calls the module once per map entry.")
ws[2]["say"] = "Run init, which now also installs the module, then apply. The output holds both URLs."
ws[3]["say"] = "List the state. Each copy has its own address, with the map key in square brackets."
ws[4]["say"] = ("Now cause drift on purpose by deleting one container behind Terraform's back. A refresh-only plan "
                "reports it and changes nothing. You may also see small \"has changed\" notes for the other site; "
                "that is the provider filling in empty default values.")
ws[5]["say"] = ("A normal plan offers to fix the drift by creating the missing container again. Apply it, check "
                "both sites, then clean up.")

d["mistake"] = (
    "Committing `terraform.tfstate` to git, or pasting it into a chat. State can hold passwords and tokens in plain "
    "text, and shared copies soon disagree. Keep `*.tfstate` in `.gitignore` (the lab already does). Move to a "
    "remote backend with locking as soon as a second person or a pipeline runs Terraform."
)
d["real_world"] = (
    "PayLoop, the made-up payments company from Day 13, gives each environment its own small root folder. Each "
    "folder calls shared child modules, such as a `service` module every team reuses. State lives in a versioned "
    "S3 bucket with locking, and only the pipeline may write to it. Every night a job runs "
    "`terraform plan -refresh-only` and posts any drift to the team chat."
)

d["task"]["steps"][5] = "Run fmt, validate, plan and apply. Open the URL and reload it a few times."
d["task"]["steps"][7] = "Plan with `-var host_port=8081` and read the plan before you apply. What gets replaced, and why?"
d["task"]["hints"][2] = "Look at the Files section only after you have tried it yourself."

d["explain_back"]["prompt"] = (
    "A teammate wants to commit `terraform.tfstate` so everyone can share it. In 3 to 4 sentences, explain what "
    "state contains, why it matters, and where it should live instead."
)
d["explain_back"]["answer"] = (
    "The state file is Terraform's record of what it manages: it links each resource in our code to a real object "
    "and stores its attributes. Plan uses it to decide what to create, change or destroy, so losing or corrupting "
    "it causes real damage. It can also hold secrets in plain text, which rules out git. It belongs in a remote "
    "backend, such as a versioned S3 bucket, with locking so two runs cannot change it at once."
)

d["recap"][2] = ("References build the dependency graph. That gives Terraform the order, and lets it run "
                 "independent work in parallel.")
d["recap"][5] = "Modules are reusable folders. For copies, prefer `for_each` over `count`."

d["interview"][1]["a"] = (
    "Drift is a difference between real infrastructure and Terraform's state, usually caused by manual changes or "
    "another tool. You find it with `terraform plan`, or with `terraform plan -refresh-only` to see only the outside "
    "changes. Then you decide: apply to restore what the code says, or change the code to match reality. To prevent "
    "it, limit write access in the console and run plans on a schedule, so drift shows up early."
)

d["deeper"]["body"] = """Import and rename are the two state moves you will need most. You do both with blocks in your code, so they go through review like any other change.

Try an import on your laptop:
1. Create a network by hand: `docker network create legacy-net`.
2. Get its ID: `docker network inspect -f '{{.Id}}' legacy-net`.
3. In a Terraform folder, add an `import` block with two arguments: `to = docker_network.legacy` and `id` set to that ID.
4. Run `terraform plan -generate-config-out=generated.tf`. The plan says the network "will be imported", and Terraform writes a resource block into `generated.tf`.
5. Read `generated.tf`. It lists every attribute, including defaults. Keep what matters (here, `name = "legacy-net"`), move it into `main.tf`, and delete the file.
6. Plan again. You want `Plan: 1 to import, 0 to add, 0 to change, 0 to destroy.` Then apply.

Terraform warns that config generation is experimental. For a first draft that is fine.

Always read the plan line for the imported resource. It must say "will be imported". If it says "must be replaced", your resource block does not match reality, and apply would delete the real object and make a new one. It happens often. Import a Docker container, for example, and the provider cannot read back some settings, such as published ports, so the plan wants to replace the container. Fix the block, or manage that thing a different way, before you apply.

Renaming is the other move. Rename `docker_container.web` to `docker_container.app` in the code, and Terraform sees one resource gone and a new one wanted, so it plans a destroy and a create. A `moved` block with `from = docker_container.web` and `to = docker_container.app` fixes this. Plan then shows a move and no replacement. The same works when you move a resource into a module, from `docker_container.web` to `module.site["blue"].docker_container.this`.

The older commands `terraform import` and `terraform state mv` still exist. They change state right away, with no plan and no review. Prefer the blocks, because a teammate can read them in a pull request."""

# ---------------------------------------------------------------- d15

d = L["d15"]

d["sections"][0]["body"] = """Everything on AWS today is optional. The rest of the course runs on your laptop, and the CI checks in the worked example need no account. If you do use AWS, do these steps first, in this order:
1. Sign up. Accounts created since July 15, 2025 choose a plan. The free plan gives $100 in credits, plus up to $100 more for trying services, for six months. You are not charged while you stay on it.
2. Protect the root user, the email login you signed up with. It can do anything, even close the account. Turn on MFA for it, and do not use it for daily work.
3. Create a budget alert. In Billing and Cost Management, open Budgets, choose Create budget, use a template, and pick the zero spend budget with your email. Budgets without actions are free.
4. Make an everyday login that is not root (next section).

When the free plan's credits or six months run out, the account closes unless you upgrade within 90 days. Older accounts are on the old free tier and can be billed, so the alert matters even more there.

A budget alert only sends email. It stops nothing, and its numbers can be hours old. Destroying what you create is what actually protects you, and that is the last step today. Today's resources should cost about nothing: a few small files and requests."""

d["sections"][1]["body"] = """Terraform's AWS provider finds credentials the same way as the AWS CLI: from environment variables such as `AWS_PROFILE`, or from the files in `~/.aws`. Install the CLI with `brew install awscli`, and check the current AWS docs if anything differs. You have two common ways to get a non-root login:
- IAM Identity Center, AWS's single sign-on. You sign in through the browser and get short-lived credentials. Run `aws configure sso` once, then `aws sso login` each day.
- An IAM user with MFA and an access key, saved with `aws configure`. It is simpler, but the key is a long-lived password on your disk. Delete it when you finish.

Identity Center is the better habit, with one catch. It is built on AWS Organizations, and some Organizations actions move a free-plan account to the paid plan. To stay on the free plan, use the IAM user today.

Then run `aws sts get-caller-identity`. It should print your account ID and a user or role that is not root. If that works, Terraform will work too."""

d["sections"][2]["body"] = """The lab's `infra/aws` folder creates one S3 bucket. A bucket name must be unique across all AWS accounts, so the code adds your 12-digit account ID to it. It reads the ID with the data source `aws_caller_identity`.

In the AWS provider, a bucket's settings are separate resources that sit next to `aws_s3_bucket`:
- `aws_s3_bucket_versioning` keeps every old version of every file, so you can undo a bad write.
- `aws_s3_bucket_public_access_block` stops anything in the bucket from becoming public.
- `aws_s3_bucket_server_side_encryption_configuration` encrypts files with keys that S3 manages.

New buckets already block public access and encrypt files by default. Write it down anyway, so reviewers and scanners can see it. The provider's `default_tags` block adds tags such as `Project` and `ManagedBy` to everything, so you can always tell what a resource is for.

This bucket also stores its own state. That sounds impossible at first: Terraform needs the bucket to store state, but the bucket does not exist until Terraform creates it. You solve it in two steps:
1. Apply with local state. This creates the bucket.
2. Uncomment the `backend "s3"` block, add the bucket name, and run `terraform init -migrate-state`. Terraform copies the state into S3 and uses it from then on.

The block sets `use_lockfile = true`, so each run writes a small `.tflock` file next to the state. A second run that finds it stops with a lock error and leaves the state alone."""

d["sections"][3]["body"] = """On Day 12 you met OIDC: a workflow gets a short-lived token from GitHub instead of storing AWS keys. The lab's `github-oidc.tf` builds the AWS side:
1. An OIDC identity provider for `token.actions.githubusercontent.com` with the audience `sts.amazonaws.com`. You no longer need a certificate thumbprint.
2. An IAM role whose **trust policy** checks the token's `sub` (subject) claim. It names the repo and the context, such as `pull_request` or `environment:production`.
3. A permissions policy that says what the role may do.

The `sub` has to match exactly, character for character. Repos created after July 15, 2026 put numeric IDs in it, like `repo:you@123456/hello-devops@456789:pull_request`. Older repos use `repo:you/hello-devops:pull_request`. The lab trusts both forms, for your repo only. When the login fails with "Not authorized to perform sts:AssumeRoleWithWebIdentity", a `sub` mismatch is the first thing to check.

Keep the role small. The lab's role may manage only buckets whose names start with `hello-devops-`, and read its own IAM setup so that plan works. It cannot change IAM, so a pull request cannot give itself more power. You apply IAM changes from your laptop."""

d["sections"][4]["body"] = """The lab's `.github/workflows/terraform.yml` runs only when files in `infra/aws` change. On a pull request, the plan job:
1. Checks formatting with `terraform fmt -check`.
2. Runs `terraform init -backend=false` and `terraform validate`, which need no AWS login.
3. Scans the code with `trivy config` and fails on HIGH or CRITICAL findings.
4. Logs in with OIDC, runs `terraform plan`, and puts the plan on the run's summary page for reviewers.

The cheap checks run first, so a formatting slip fails the job before it ever logs in to AWS.

After the merge to main, the apply job runs in the `production` environment. Like the release job on Day 12, it waits until a required reviewer approves. Then it plans and applies.

Look for these settings in the file as well:
- `concurrency` with `cancel-in-progress: false`, so a second run waits and never stops an apply halfway.
- `TF_VAR_` environment variables filled from the `github` context, so CI passes your owner, repo and their IDs without secrets.
- The role ARN in a repository variable, `AWS_ROLE_ARN`, because it is not secret."""

d["sections"][5]["body"] = """Plan tells you what will change. It does not tell you whether the change is wise. Two free tools help with that:
- tflint finds mistakes that `validate` misses, such as unused variables. Its AWS plugin, turned on in a `.tflint.hcl` file and installed with `tflint --init`, also catches things like invalid instance types.
- `trivy config` looks for security problems, such as public buckets, missing encryption, or IAM policies that allow too much. Checkov is a similar tool.

Scanners are strict on purpose, and you decide what to fix. To accept a finding, put a comment such as `# trivy:ignore:AWS-0132` above the resource, followed by the reason. A reviewer can then read the decision and question it."""

d["analogy"] = (
    "OIDC works like a hotel key card. At the front desk (GitHub) you prove who you are, and you get a card that "
    "opens one room (the IAM role) and stops working at checkout. Nobody carries a master key that works forever. "
    "The hotel picture misses one thing: a hotel checks your passport in person, while AWS only trusts GitHub's "
    "signature. That is why the trust policy must name exactly which repo may get a card."
)

ws = d["worked"]["steps"]
ws[0]["say"] = ("Copy the lab's `infra/aws` files into your repo. Format and validate need no AWS account, so start "
                "there. `-backend=false` skips the S3 backend, which does not exist yet, and `fmt -check` prints "
                "nothing when every file is tidy.")
ws[1]["say"] = ("Scan with trivy (`brew install trivy`, or run the `aquasec/trivy` image as CI does). Before the "
                "ignore comments were added, it reported three findings. These are its headline lines.")
ws[2]["say"] = ("Decide on each one. Access logs need a second bucket, and a customer managed KMS key costs money "
                "every month, so for a lab you accept both. `s3:*` is limited to this project's buckets. Write each "
                "decision above the block it is about.")
ws[3]["say"] = ("Scan again the way CI does. `--exit-code 1` makes trivy fail the job when it finds HIGH or "
                "CRITICAL problems. This time there are zero findings, and the exit code is 0.")
ws[4]["say"] = ("Give the variables values. `gh api` returns the numeric IDs of your user and your repo. Nothing in "
                "`terraform.tfvars` is secret, so you may commit it.")
ws[5]["say"] = ("Try a plan. Without AWS credentials it stops at the provider. CI logs in with OIDC at exactly this "
                "point, and your laptop needs `aws sso login` or your IAM user's profile.")

d["mistake"] = (
    "Running `terraform destroy` while the state still lives in the bucket you are destroying. The bucket goes away, "
    "and Terraform has nowhere to save the final state. First comment out the backend block and run "
    "`terraform init -migrate-state` to bring the state home, then destroy."
)
d["real_world"] = (
    "At PayLoop (still made up), engineers have read-only access to production. Every infrastructure change goes "
    "through a pull request with its plan posted for review. Only the pipeline's role can apply, and only after a "
    "second person approves. When the team accepts a scanner finding, they write it down with a reason, so auditors "
    "can see each decision."
)

d["task"]["steps"][6] = "Read the plan on the run's summary page. Then merge, approve the apply job, and watch it finish."

d["explain_back"]["answer"] = (
    "Because the workflow has `id-token: write`, the job can ask GitHub for a signed OIDC token. The "
    "configure-aws-credentials action sends that token to AWS and asks to use our IAM role. AWS checks the "
    "signature through the OIDC provider for token.actions.githubusercontent.com, and the role's trust policy "
    "checks the `aud` and `sub` claims. The `sub` names our repo and the context, such as a pull request or the "
    "production environment, so no other repo can use the role. If everything matches, AWS returns credentials "
    "that expire after a short time."
)

d["recap"][0] = "Cloud work starts with safety: root MFA, a non-root login and a budget alert. It ends with destroy."

d["interview"][1]["a"] = (
    "Access keys last until someone deletes them, so a key that leaks through a log or a bad action can be used "
    "for months. With OIDC, the job gets a signed token from GitHub and swaps it for AWS credentials that expire "
    "within hours. The role's trust policy limits which repo, branch or environment may get them. You also have "
    "nothing to store or rotate."
)

d["deeper"]["body"] = """The lab's pipeline leaves three gaps that real teams usually close.

First, the plan you reviewed is not exactly the plan that runs. The pull request's plan is made from the branch, before the merge. The apply job makes a fresh plan from main, which may include other merged changes or new drift. Teams handle this in a few ways:
- Require pull request branches to be up to date with main before merging, so the reviewed plan is closer to what runs.
- Split the work on main into two jobs. One plans and saves the plan file as an artifact. The next one, behind the environment gate, applies exactly that file, so the approver can read it first.
- Use a tool built for this. Atlantis is open source and runs plan and apply from pull request comments. HCP Terraform and similar services do the same as a hosted product.

Second, one role for both jobs gives a pull request more power than it needs. A cleaner design has two roles. The plan role trusts only `pull_request` and gets read-only permissions, plus access to the state and lock files. The apply role trusts only `environment:production` and may change things. This matters because anyone who can push a branch could edit the workflow in a pull request to run apply.

Third, access to state is a permission in itself. Anyone who can write the state bucket can change what Terraform believes exists. Big teams keep state buckets in a separate account. They turn on versioning and `prevent_destroy`, and only a few roles may write. Each environment gets its own state file, and often its own account, so a mistake in the dev state cannot touch production.

Teams also use destroy outside labs. They run short-lived test environments and destroy them automatically each night. Because the code describes everything, one apply brings them back in the morning."""

with PATH.open("w", encoding="utf-8") as f:
    json.dump(P, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("wrote", PATH)
