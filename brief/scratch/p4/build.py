#!/usr/bin/env python3
"""Build content/p4.json (Part 4: Infrastructure as Code with Terraform)."""
import json
import pathlib

import svg

ROOT = pathlib.Path(__file__).resolve().parents[3]
LAB = ROOT / "labs/hello-devops"
OUT = ROOT / "content/p4.json"


def lab(path):
    return (LAB / path).read_text()


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


# Links found and checked during research for this part.
U = {
    "tf_docker": "https://developer.hashicorp.com/terraform/tutorials/docker-get-started",
    "tf_docker_build": "https://developer.hashicorp.com/terraform/tutorials/docker-get-started/docker-build",
    "tf_docker_change": "https://developer.hashicorp.com/terraform/tutorials/docker-get-started/docker-change",
    "tf_docker_vars": "https://developer.hashicorp.com/terraform/tutorials/docker-get-started/docker-variables",
    "tf_docker_outputs": "https://developer.hashicorp.com/terraform/tutorials/docker-get-started/docker-outputs",
    "tf_files": "https://developer.hashicorp.com/terraform/language/files",
    "tf_providers": "https://developer.hashicorp.com/terraform/tutorials/configuration-language/configure-providers",
    "tf_lock": "https://developer.hashicorp.com/terraform/language/files/dependency-lock",
    "tf_init": "https://developer.hashicorp.com/terraform/cli/commands/init",
    "tf_plan": "https://developer.hashicorp.com/terraform/cli/commands/plan",
    "tf_apply": "https://developer.hashicorp.com/terraform/cli/commands/apply",
    "tf_graph": "https://developer.hashicorp.com/terraform/cli/commands/graph?optInFrom=terraform-io",
    "tf_vars": "https://developer.hashicorp.com/terraform/language/values/variables",
    "tf_vars_tut": "https://developer.hashicorp.com/terraform/tutorials/configuration-language/variables",
    "tf_outputs": "https://developer.hashicorp.com/terraform/language/values/outputs",
    "tf_sensitive": "https://developer.hashicorp.com/terraform/language/manage-sensitive-data",
    "tf_backends": "https://developer.hashicorp.com/terraform/language/state/backends",
    "tf_s3": "https://developer.hashicorp.com/terraform/language/backend/s3",
    "tf_drift": "https://developer.hashicorp.com/terraform/tutorials/state/resource-drift",
    "tf_refresh": "https://developer.hashicorp.com/terraform/tutorials/state/refresh",
    "tf_import": "https://developer.hashicorp.com/terraform/language/import",
    "tf_import_gen": "https://developer.hashicorp.com/terraform/language/import/generating-configuration",
    "tf_modules": "https://developer.hashicorp.com/terraform/language/modules",
    "tf_module_use": "https://developer.hashicorp.com/terraform/tutorials/modules/module-use",
    "tf_meta": "https://developer.hashicorp.com/terraform/language/meta-arguments",
    "tf_lifecycle": "https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle",
    "tf_lifecycle_tut": "https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle",
    "bsl_blog": "https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license",
    "tofu_manifesto": "https://opentofu.org/manifesto/",
    "tofu_migration": "https://opentofu.org/docs/intro/migration/",
    "tofu_cncf": "https://www.cncf.io/projects/opentofu/",
    "kreuzwerker": "https://github.com/kreuzwerker/terraform-provider-docker",
    "aws_plans": "https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html",
    "aws_root": "https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html",
    "aws_budget_tpl": "https://docs.aws.amazon.com/cost-management/latest/userguide/budget-templates.html",
    "aws_iam_bp": "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
    "aws_sso_cli": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html",
    "aws_s3_defaults": "https://aws.amazon.com/about-aws/whats-new/2023/04/amazon-s3-security-best-practices-buckets-default",
    "gh_oidc_aws": "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws",
    "gh_oidc": "https://docs.github.com/en/actions/concepts/security/openid-connect",
    "gh_immutable": "https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/",
    "configure_aws": "https://github.com/aws-actions/configure-aws-credentials",
    "setup_tf": "https://github.com/hashicorp/setup-terraform",
    "tflint": "https://github.com/terraform-linters/tflint",
    "tflint_aws": "https://github.com/terraform-linters/tflint-ruleset-aws",
    "trivy_tf": "https://trivy.dev/docs/latest/tutorials/misconfiguration/terraform/",
}

NGINX_TF = '''terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

# Talk to Docker on your laptop. No cloud account needed.
provider "docker" {}

# Pull an image, like `docker pull nginx:1.30-alpine`.
resource "docker_image" "nginx" {
  name = "nginx:1.30-alpine"
}

# Run a container from it, like `docker run -d -p 8090:80 nginx`.
resource "docker_container" "web" {
  name    = "tf-web"
  image   = docker_image.nginx.image_id
  restart = "no"

  ports {
    internal = 80
    external = 8090
  }
}
'''

# ---------------------------------------------------------------- Day 13
d13 = {
    "id": "d13",
    "title": "Infrastructure as Code and your first Terraform",
    "minutes": 35,
    "goal": "By the end you can explain why teams write infrastructure as code, and use Terraform to create, change and destroy a container on your laptop.",
    "guess": {
        "q": "You run `terraform apply`, it succeeds, and then you run `terraform apply` again without changing any file. What happens the second time?",
        "options": [
            "It creates a second copy of everything",
            "It reports no changes and does nothing",
            "It deletes everything and creates it again",
            "It fails because the things already exist",
        ],
        "answer": 1,
        "why": "Terraform compares your files with what already exists. When they match there is nothing to do, so running it again is safe.",
    },
    "terms": [
        {"term": "Infrastructure as Code (IaC)", "plain": "Describing servers, networks and other infrastructure in text files that a tool turns into real things."},
        {"term": "Declarative", "plain": "You describe the end result you want, and the tool works out the steps to get there."},
        {"term": "Provider", "plain": "A Terraform plugin that knows how to talk to one platform, such as Docker or AWS."},
        {"term": "Resource", "plain": "One thing Terraform creates and looks after, such as a container, a network or a storage bucket."},
        {"term": "Plan", "plain": "Terraform's preview of what it will create, change or destroy, shown before anything happens."},
        {"term": "State", "plain": "Terraform's record of the real things it manages, kept in a file called terraform.tfstate."},
    ],
    "sections": [
        {
            "h": "Why clicking in a console does not scale",
            "body": (
                "Imagine you set up a server by clicking through a cloud web page. It works. Six months later you need a second, identical one. Which boxes did you tick? Nobody remembers.\n\n"
                "Setting things up by hand causes three problems:\n"
                "- No repeatability: you cannot make an exact copy for testing or for another region.\n"
                "- No review: nobody sees a change before it happens, and there is no history.\n"
                "- Drift: someone changes a setting by hand, and reality slowly moves away from what everyone believes.\n\n"
                "**Infrastructure as Code** (IaC) fixes this. You describe your infrastructure in text files, and a tool makes the real world match them. "
                "The files live in git, so you get the same benefits as with application code:\n"
                "- A history of every change, and who made it.\n"
                "- Review in a pull request before anything happens.\n"
                "- Rollback by reverting a commit and applying again."
            ),
            "refs": [ref("Terraform tutorials: get started with Docker", U["tf_docker"], "docs")],
        },
        {
            "h": "Declarative: describe the result, not the steps",
            "body": (
                "There are two ways to tell a computer what to do:\n"
                "- Imperative: you list the steps. \"Start this container, then open this port.\" A shell script is imperative.\n"
                "- Declarative: you describe the result. \"There is one nginx container on port 8090.\" The tool works out the steps.\n\n"
                "Terraform is declarative, and this matters more than it sounds. A script that says \"start a container\" fails or makes a duplicate when you run it twice. "
                "A declarative file says what should exist. If it already exists, Terraform does nothing. "
                "Getting the same result no matter how many times you run something is called being idempotent.\n\n"
                "You already met this idea on Day 7. `compose.yaml` describes services, and `docker compose up` makes them exist. "
                "Terraform applies the same idea to almost anything that has an API, from Docker on your laptop to a whole cloud account."
            ),
            "refs": [ref("Build infrastructure (Terraform and Docker tutorial)", U["tf_docker_build"], "docs")],
        },
        {
            "h": "Terraform, OpenTofu and the other tools",
            "body": (
                "Terraform is made by HashiCorp, which IBM bought in 2025. Until August 2023 it was open source under the MPL licence. "
                "Then [HashiCorp moved it to the Business Source License](" + U["bsl_blog"] + ") (BSL). "
                "You may still use Terraform for free at work. You may not build a competing hosted product with it.\n\n"
                "Many companies disliked the change. They forked the last open source version and called it OpenTofu. "
                "It lives at the Linux Foundation and joined the CNCF in 2025. "
                "The command is `tofu` instead of `terraform`, so `tofu plan` behaves like `terraform plan`. "
                "Everything you learn this week works with both.\n\n"
                "You will hear about three other tools:\n"
                "- CloudFormation: AWS's own IaC service, with YAML or JSON templates. It only works for AWS.\n"
                "- Pulumi: IaC written in normal programming languages such as Python, TypeScript, Go or Java.\n"
                "- Ansible: logs in to servers that already exist and sets them up (packages, files, services).\n\n"
                "A common split is Terraform to create the machines and Ansible, or a container image, to set up what runs on them."
            ),
            "refs": [
                ref("HashiCorp adopts Business Source License", U["bsl_blog"], "read"),
                ref("The OpenTofu manifesto", U["tofu_manifesto"], "read"),
                ref("Migrating to OpenTofu from Terraform", U["tofu_migration"], "docs"),
            ],
        },
        {
            "h": "HCL: blocks, arguments and references",
            "body": (
                "Terraform files end in `.tf` and use HCL, the HashiCorp Configuration Language. HCL has three main parts:\n"
                "- A block has a type, labels and braces: `resource \"docker_container\" \"web\" { }`.\n"
                "- An argument sets a value inside a block: `name = \"tf-web\"`.\n"
                "- A reference reads a value from another block: `docker_image.nginx.image_id`.\n\n"
                "A resource block has two labels. The first is the resource type, such as `docker_container`. It always starts with the provider's name. "
                "The second is your own name for it, such as `web`. Together they make the address `docker_container.web`, which must be unique in the folder.\n\n"
                "References also decide the order. The container refers to the image, so Terraform pulls the image first. "
                "You never write \"do this first\". Terraform works it out.\n\n"
                "A provider is a plugin that talks to one platform's API. You list providers in the `terraform` block with a source and a version, much like a dependency in a Gradle file. "
                "The Docker provider used here is `kreuzwerker/docker`. It talks to the same Docker engine as the `docker` command."
            ),
            "refs": [
                ref("Files and directories in the Terraform language", U["tf_files"], "docs"),
                ref("Configure Terraform providers", U["tf_providers"], "docs"),
                ref("kreuzwerker/terraform-provider-docker on GitHub", U["kreuzwerker"], "read"),
            ],
        },
        {
            "h": "The workflow: init, plan, apply, destroy",
            "body": (
                "You use four commands, in this order:\n"
                "1. `terraform init` downloads the providers into a hidden `.terraform` folder. It also writes `.terraform.lock.hcl`, which pins the exact provider versions.\n"
                "2. `terraform plan` compares your files, the state and the real world. It prints what it would do and changes nothing.\n"
                "3. `terraform apply` shows the plan again, waits for you to type `yes`, makes the changes and updates the state.\n"
                "4. `terraform destroy` removes everything this folder manages.\n\n"
                "Read every plan before you approve it. The symbols tell you what will happen:\n"
                "- `+` create a new resource.\n"
                "- `~` update in place: the same resource stays, one setting changes.\n"
                "- `-/+` replace: destroy the old one, then create a new one.\n"
                "- `-` destroy.\n\n"
                "This trips most people up. Some settings cannot change on a living resource, like a container's port. "
                "Then a small edit becomes `-/+`, and the line shows `# forces replacement`. "
                "For a container that is harmless. For a database it can mean lost data. "
                "Always check the summary line, such as `Plan: 1 to add, 0 to change, 1 to destroy.`"
            ),
            "refs": [
                ref("terraform plan command reference", U["tf_plan"], "docs"),
                ref("terraform apply command reference", U["tf_apply"], "docs"),
                ref("Change infrastructure (Terraform and Docker tutorial)", U["tf_docker_change"], "docs"),
            ],
        },
        {
            "h": "State: Terraform's memory",
            "body": (
                "After an apply, Terraform writes `terraform.tfstate`. It links each address in your code, such as `docker_container.web`, to a real object ID. "
                "Without it, Terraform could not tell \"create a container\" from \"this container already exists\". Day 14 covers state in depth.\n\n"
                "For now, remember three rules:\n"
                "- Never edit the state file by hand.\n"
                "- Do not commit it to git. The lab's `.gitignore` already blocks `*.tfstate`.\n"
                "- Do commit `.terraform.lock.hcl`, so everyone gets the same provider versions."
            ),
            "refs": [ref("Dependency lock file", U["tf_lock"], "docs")],
        },
    ],
    "analogy": (
        "Terraform works like a thermostat. You set the temperature you want, and it turns the heating on or off until the room matches. "
        "You never say \"heat for ten minutes\". "
        "Where it breaks: a thermostat checks the room all the time, while Terraform only checks when you run plan or apply."
    ),
    "diagram": svg.d13(),
    "diagram_caption": "Plan compares your code with the state and the real world. Apply makes the changes through a provider and updates the state.",
    "worked": {
        "title": "Run nginx from Terraform, change it, destroy it",
        "steps": [
            {
                "say": "Make a practice folder outside your repo and save the `main.tf` from the Files section in it. Then run init. It downloads the Docker provider that the file asks for.",
                "code": "$ mkdir -p ~/code/tf-first && cd ~/code/tf-first\n$ terraform init\nInitializing provider plugins...\n- Finding kreuzwerker/docker versions matching \"~> 4.6\"...\n- Installing kreuzwerker/docker v4.6.0...\nTerraform has been successfully initialized!",
                "lang": "console",
            },
            {
                "say": "Preview the change. Nothing exists yet, so you see two creates and no changes or destroys. These lines are trimmed from a longer listing of every attribute.",
                "code": "$ terraform plan\n  # docker_container.web will be created\n  # docker_image.nginx will be created\nPlan: 2 to add, 0 to change, 0 to destroy.",
                "lang": "console",
            },
            {
                "say": "Apply. Terraform shows the plan again and waits for `yes`. The image is created first because the container refers to it. Then check that nginx answers.",
                "code": "$ terraform apply\n  Enter a value: yes\ndocker_image.nginx: Creating...\ndocker_image.nginx: Creation complete after 3s\ndocker_container.web: Creating...\ndocker_container.web: Creation complete after 0s\nApply complete! Resources: 2 added, 0 changed, 0 destroyed.\n$ curl -s localhost:8090 | grep title\n<title>Welcome to nginx!</title>",
                "lang": "console",
            },
            {
                "say": "Change a setting that Docker can update on a running container: set `restart = \"unless-stopped\"`. The `~` means the same container is kept. Apply it.",
                "code": "$ terraform plan\n  ~ update in-place\n  # docker_container.web will be updated in-place\n      ~ restart = \"no\" -> \"unless-stopped\"\nPlan: 0 to add, 1 to change, 0 to destroy.",
                "lang": "console",
            },
            {
                "say": "Now change `external = 8090` to `8091`. Docker cannot move a running container to a new port, so Terraform must replace it. Look for `forces replacement`.",
                "code": "$ terraform apply\n-/+ destroy and then create replacement\n  # docker_container.web must be replaced\n          ~ external = 8090 -> 8091 # forces replacement\nPlan: 1 to add, 0 to change, 1 to destroy.\n  Enter a value: yes\ndocker_container.web: Destroying...\ndocker_container.web: Creating...\nApply complete! Resources: 1 added, 0 changed, 1 destroyed.",
                "lang": "console",
            },
            {
                "say": "Clean up. Destroy removes the container and also the image that Terraform pulled. `docker ps -a` no longer lists `tf-web`.",
                "code": "$ terraform destroy\nPlan: 0 to add, 0 to change, 2 to destroy.\n  Enter a value: yes\nDestroy complete! Resources: 2 destroyed.",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "hcl", "title": "~/code/tf-first/main.tf (practice folder)", "src": NGINX_TF, "run": "terraform init && terraform apply"},
        {"lang": "hcl", "title": "infra/local/versions.tf (in hello-devops)", "src": lab("infra/local/versions.tf"), "run": "cd ~/code/hello-devops/infra/local && terraform init"},
    ],
    "commands": [
        {"cmd": "terraform version", "what": "Show the Terraform version and the providers this folder uses."},
        {"cmd": "terraform init", "what": "Download the providers for this folder and write the lock file."},
        {"cmd": "terraform fmt", "what": "Rewrite the .tf files in this folder in the standard style."},
        {"cmd": "terraform validate", "what": "Check the files for syntax errors and broken references, without touching anything."},
        {"cmd": "terraform plan", "what": "Show what would change. Changes nothing."},
        {"cmd": "terraform apply", "what": "Show the plan, ask for yes, then make the changes and update the state."},
        {"cmd": "terraform apply -auto-approve", "what": "Apply without asking. Fine for practice, risky for anything real."},
        {"cmd": "terraform show", "what": "Print what the state says exists right now."},
        {"cmd": "terraform destroy", "what": "Remove everything this folder manages."},
    ],
    "mistake": (
        "Typing `yes` without reading the plan. A one-word edit can turn into `-/+`, and replacing a database means losing its data. "
        "Read the summary line and look for `forces replacement` every time, even when you are sure."
    ),
    "real_world": (
        "At PayLoop, a made-up payments company, nobody creates production infrastructure by clicking. "
        "Every change is a pull request with the Terraform plan attached, and a second engineer reads the plan before anyone applies it. "
        "The cloud web console is for looking, and for emergencies."
    ),
    "task": {
        "title": "Run Redis for hello-devops with Terraform",
        "steps": [
            "In your hello-devops repo, create the folder `infra/local` and add `versions.tf` from the Files section.",
            "Add a `main.tf` with two resources: a `docker_image` for `redis:8-alpine`, and a `docker_container` named `hello-redis` that uses it.",
            "Run `terraform fmt`, `terraform init` and `terraform plan`. Count the creates before you apply.",
            "Apply, then check that Redis answers with `docker exec hello-redis redis-cli ping`.",
            "Add `restart = \"unless-stopped\"` to the container and plan. Is it `~` or `-/+`?",
            "Change the container's name, plan again, and find the line that forces replacement. Then change the name back.",
            "Run `terraform destroy` and check with `docker ps -a` that the container is gone.",
            "Commit `versions.tf`, `main.tf` and `.terraform.lock.hcl`. Check that `git status` lists no state file.",
        ],
        "hints": [
            "The container's `image` argument should be a reference to the image resource's `image_id`, like in the nginx example.",
            "Redis needs no published port today. `docker exec` runs `redis-cli` inside the container.",
            "If Terraform cannot connect to Docker but `docker ps` works, run `docker context inspect` to find your socket and set `DOCKER_HOST` to it.",
        ],
        "done_when": "`docker exec hello-redis redis-cli ping` prints PONG, and after `terraform destroy` the container is gone from `docker ps -a`.",
    },
    "explain_back": {
        "prompt": "Explain to a teammate what happens when you run `terraform plan` and then `terraform apply`, in 3 to 4 sentences. Mention the state file and what `-/+` means.",
        "answer": (
            "Plan reads my .tf files, the state file and the real world, and prints the difference without changing anything. "
            "Apply shows that plan again, asks me to confirm, and then calls the provider to make the changes. "
            "Afterwards it updates the state file, so next time it knows what already exists. "
            "A `-/+` means a setting cannot change on the existing resource, so Terraform destroys it and creates a new one."
        ),
    },
    "recap": [
        "IaC means describing infrastructure in files, so you get review, history and repeatable setups.",
        "Terraform is declarative: you describe the result, and it works out the steps.",
        "A resource address such as `docker_container.web` is the type plus your own name.",
        "init downloads providers, plan previews, apply changes, destroy cleans up.",
        "Plan symbols: `+` create, `~` update in place, `-/+` replace, `-` destroy.",
        "OpenTofu is the open source fork of Terraform, and its commands are nearly identical.",
    ],
    "check": [
        {
            "q": "You change only the `image` of a `docker_container` and run plan. The container shows `-/+`. What will apply do?",
            "options": [
                "Edit the running container in place",
                "Stop because the file has an error",
                "Destroy the container and create a new one",
                "Pull the new image but keep the old container",
            ],
            "answer": 2,
            "why": "`-/+` means replace: the image of a running container cannot change, so Terraform removes it and creates a new one.",
        },
        {
            "q": "A teammate deletes the `tf-web` container by hand. You run `terraform plan` without changing any file. What will the plan most likely show?",
            "options": [
                "A create, to bring the container back",
                "Nothing, because your files did not change",
                "An error saying the state is broken",
                "A destroy, to remove it from your files",
            ],
            "answer": 0,
            "why": "Plan reads the real world, notices the container is missing, and proposes to create it again so reality matches the code.",
        },
        {
            "q": "Your team must install packages and edit config files on 50 Linux servers that already exist. Which tool fits best?",
            "options": ["Terraform", "CloudFormation", "kind", "Ansible"],
            "answer": 3,
            "why": "Ansible is built to set up software on existing machines; Terraform and CloudFormation mainly create infrastructure.",
        },
    ],
    "interview": [
        {
            "q": "What is Infrastructure as Code, and why would a team use it?",
            "a": (
                "Infrastructure as Code means describing infrastructure, such as servers, networks and permissions, in text files that a tool applies. "
                "The files live in git, so every change goes through review and has a history. "
                "You can rebuild the same setup in another region or account, which helps testing and disaster recovery. "
                "It also reduces drift, because the code is the source of truth and a plan shows any difference."
            ),
        },
        {
            "q": "What is the difference between Terraform and Ansible?",
            "a": (
                "Terraform is declarative and mainly creates infrastructure through APIs, keeping track of it in a state file. "
                "Ansible is mainly for configuration: it connects to existing machines over SSH and runs tasks such as installing packages. "
                "Ansible runs its tasks in order, so it feels more step by step. "
                "Many teams use both: Terraform creates the machines, and Ansible or a container image sets up what runs on them."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Version constraints and the lock file decide which provider code runs on your machine. They are worth ten minutes, because a surprise upgrade can break a plan that worked yesterday.\n\n"
            "The `version` argument in `required_providers` is a constraint. Three forms cover most needs:\n"
            "- `= 4.6.0` allows exactly one version.\n"
            "- `~> 4.6` allows 4.6 and newer, but stays below 5.0. This is the usual choice.\n"
            "- `~> 4.6.0` allows 4.6.x patch releases only.\n\n"
            "The `~>` operator is called the pessimistic constraint. It lets the rightmost number grow. "
            "Major versions can remove or rename things, so you move to a new major version on purpose, after reading the upgrade guide.\n\n"
            "`terraform init` picks the newest version that fits, then records it in `.terraform.lock.hcl`. "
            "The lock file stores the exact version and checksums of the provider files. "
            "Next time, init installs that exact version, even if a newer one exists. To move forward on purpose, run `terraform init -upgrade` and commit the new lock file.\n\n"
            "Here is an edge case that often affects Mac users. Checksums are per platform. "
            "Your Mac is `darwin_arm64`, while GitHub's runners are `linux_amd64`. "
            "Terraform usually records checksums for every platform. When providers come from a local cache or mirror, it may record only yours, and init in CI then fails with a checksum error. "
            "Fix it once with `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64`, which records both.\n\n"
            "There is also `required_version` in the `terraform` block. It sets which Terraform CLI versions may run this code. "
            "The lab's `infra/aws` asks for `>= 1.11`, because the S3 lock file you meet on Day 15 needs a recent version.\n\n"
            "OpenTofu reads the same blocks and downloads providers from its own registry. "
            "Do not switch one state between `terraform` and `tofu` without reading the OpenTofu migration guide first."
        ),
    },
    "sources": [
        {"title": "Terraform tutorials: get started with Docker", "url": U["tf_docker"]},
        {"title": "terraform plan command reference", "url": U["tf_plan"]},
        {"title": "Dependency lock file", "url": U["tf_lock"]},
        {"title": "The OpenTofu manifesto", "url": U["tofu_manifesto"]},
    ],
}

# ---------------------------------------------------------------- Day 14
MODULE_TF = '''terraform {
  required_providers {
    docker = { source = "kreuzwerker/docker" }
  }
}
variable "name" { type = string }
variable "image" { type = string }
variable "port" { type = number }
resource "docker_container" "this" {
  name  = var.name
  image = var.image
  ports {
    internal = 80
    external = var.port
  }
}
output "url" { value = "http://localhost:${var.port}" }'''

ROOT_TF = '''resource "docker_image" "nginx" {
  name = "nginx:1.30-alpine"
}

# One module block, two copies: one per map entry.
module "site" {
  source   = "./modules/site"
  for_each = { blue = 8091, green = 8092 }

  name  = "site-${each.key}"
  image = docker_image.nginx.image_id
  port  = each.value
}

output "sites" { value = module.site }'''

d14 = {
    "id": "d14",
    "title": "Variables, state and modules",
    "minutes": 40,
    "goal": "By the end you can make Terraform code reusable with variables, outputs and modules, explain where state should live, and run the hello-devops stack with Terraform.",
    "guess": {
        "q": "You mark a variable `sensitive = true` and use it as a database password. Where can someone still read the real value?",
        "options": [
            "Nowhere, because Terraform encrypts it",
            "Only in the plan printed on screen",
            "In the state file, in plain text",
            "Only inside the provider's memory",
        ],
        "answer": 2,
        "why": "`sensitive` only hides the value in Terraform's output. The state file still stores it in plain text, so state must be protected like a secret.",
    },
    "terms": [
        {"term": "Input variable", "plain": "A named setting a Terraform folder accepts, with a type and an optional default value."},
        {"term": "Output", "plain": "A value Terraform prints after apply, which other code or people can read."},
        {"term": "Data source", "plain": "A read-only lookup of something that already exists, such as your cloud account ID."},
        {"term": "Backend", "plain": "The place where Terraform keeps the state file, such as your laptop or a storage bucket."},
        {"term": "State locking", "plain": "A guard that lets only one Terraform run change the state at a time."},
        {"term": "Drift", "plain": "A difference between real infrastructure and Terraform's state, usually caused by a change made by hand."},
        {"term": "Module", "plain": "A folder of .tf files that other Terraform code can call, like a function."},
    ],
    "sections": [
        {
            "h": "Variables, outputs and locals",
            "body": (
                "Hard-coded values make code hard to reuse. Terraform has three kinds of named values:\n"
                "- Input variables are the folder's parameters. A `variable` block gives a type, a description and an optional default. You read one with `var.host_port`.\n"
                "- Outputs are the folder's return values. Apply prints them, and `terraform output` shows them again.\n"
                "- Locals are named expressions inside the folder, read with `local.name`. They stop you repeating a long expression.\n\n"
                "A variable without a default is required, and Terraform asks for it. Values can come from several places. From weakest to strongest:\n"
                "1. The `default` in the variable block.\n"
                "2. An environment variable such as `TF_VAR_host_port=8081`.\n"
                "3. A `terraform.tfvars` file in the folder, which is loaded automatically.\n"
                "4. The `-var host_port=8081` flag.\n\n"
                "Terraform does not remember `-var` values between runs. If you apply with `-var` and later plan without it, Terraform wants to go back to the default. "
                "Put values you always want in `terraform.tfvars`."
            ),
            "refs": [
                ref("Input variables", U["tf_vars"], "docs"),
                ref("Output values", U["tf_outputs"], "docs"),
                ref("Customize Terraform configuration with variables", U["tf_vars_tut"], "docs"),
            ],
        },
        {
            "h": "References, data sources and the dependency graph",
            "body": (
                "Every reference adds an edge to a graph. In the lab, the app container refers to the Redis container's name, and Redis refers to the network. "
                "So Terraform builds the network first, then Redis, then the app. Things with no link between them are built in parallel. "
                "`terraform graph` prints this graph as text that tools such as Graphviz can draw.\n\n"
                "A data source reads something that already exists, without managing it. You write a `data` block and read it with a `data.` prefix. "
                "On Day 15 you will use `data.aws_caller_identity.current` to read your AWS account ID. Data sources are read during every plan, so the value is always fresh.\n\n"
                "Sometimes a dependency is invisible. For example, a program inside a container may need another container that the code never mentions. "
                "Then you add `depends_on`. Use it only when a reference cannot express the link."
            ),
            "refs": [ref("terraform graph command reference", U["tf_graph"], "docs")],
        },
        {
            "h": "State: what it holds and where it lives",
            "body": (
                "The state file links each address in your code to a real object, and stores every attribute Terraform read. Plan uses it to know what already exists.\n\n"
                "Three facts about state:\n"
                "- It can contain secrets in plain text, even values marked `sensitive`.\n"
                "- You never edit it by hand. Commands such as `terraform state list`, `state show` and `state rm` exist for that.\n"
                "- One laptop is a bad home for it. Two people with two copies will overwrite each other's work.\n\n"
                "The **backend** decides where state lives. The default is a local file. Teams use a remote backend, such as an S3 bucket or HCP Terraform, HashiCorp's hosted service (it has a free tier with limits). "
                "A good backend also locks the state: while one run changes things, any other run is refused until it finishes.\n\n"
                "With the S3 backend, `use_lockfile = true` turns on locking with a small lock file next to the state. "
                "Older guides use a DynamoDB table for this. Terraform now marks that option as deprecated. You will set up an S3 backend on Day 15."
            ),
            "refs": [
                ref("Backend type: s3", U["tf_s3"], "docs"),
                ref("Backends: state storage and locking", U["tf_backends"], "docs"),
                ref("Manage sensitive data", U["tf_sensitive"], "docs"),
            ],
        },
        {
            "h": "Drift, and adopting what already exists",
            "body": (
                "Drift happens when someone changes real infrastructure outside Terraform, for example by deleting a container or editing a setting in a web console. "
                "Every plan first refreshes: it reads the real state of each resource. So the next plan notices.\n\n"
                "When you see drift, you have two choices:\n"
                "- Undo it: run a normal apply, and Terraform puts things back the way the code says.\n"
                "- Accept it: change your code to match, or run `terraform apply -refresh-only` to record reality in the state without changing anything.\n\n"
                "`terraform plan -refresh-only` is the safe way to look. It only reports what changed outside Terraform.\n\n"
                "The opposite problem is something real that Terraform does not manage yet, such as a network someone made by hand. "
                "An `import` block adopts it. You write a resource block that describes it, and an `import` block with two arguments: `to` (the address) and `id` (the real object's ID). "
                "The plan says \"will be imported\", and apply adds it to the state without recreating it."
            ),
            "refs": [
                ref("Use refresh-only mode to sync Terraform state", U["tf_refresh"], "docs"),
                ref("Manage resource drift", U["tf_drift"], "docs"),
                ref("Import existing resources", U["tf_import"], "docs"),
            ],
        },
        {
            "h": "Modules: reuse with inputs and outputs",
            "body": (
                "A module is a folder of .tf files. The folder where you run Terraform is the root module. "
                "When it calls another folder with a `module` block, that folder is a child module. "
                "Think of a child module as a function: variables are its parameters and outputs are its return values.\n\n"
                "A `module` block needs a `source`. Common sources:\n"
                "- A local path, such as `./modules/site`.\n"
                "- A registry address, such as `terraform-aws-modules/s3-bucket/aws`, with a `version` constraint.\n"
                "- A git URL.\n\n"
                "Public registry modules save a lot of work, but read them first. They run with your permissions. Pin the version, and run `terraform init` after adding or changing one.\n\n"
                "To make several similar things, use a meta-argument. The `count = 3` argument makes three numbered copies. "
                "The `for_each` argument takes a map or a set and makes one copy per key, such as `module.site[\"blue\"]`. "
                "Prefer `for_each`. If you remove one key, only that copy goes away. With `count`, the copies after it shift by one and get replaced."
            ),
            "refs": [
                ref("Modules overview", U["tf_modules"], "docs"),
                ref("Use registry modules in configuration", U["tf_module_use"], "docs"),
                ref("Meta-arguments", U["tf_meta"], "docs"),
            ],
        },
        {
            "h": "Lifecycle rules for risky resources",
            "body": (
                "A `lifecycle` block inside a resource changes how Terraform treats it. Three settings are worth knowing:\n"
                "- `prevent_destroy = true` makes any plan that would destroy the resource fail with \"Instance cannot be destroyed\".\n"
                "- `create_before_destroy = true` makes the new copy first and removes the old one after. It only works if two copies can exist at once.\n"
                "- `ignore_changes` lists attributes that Terraform should stop correcting, because another system owns them.\n\n"
                "Use `prevent_destroy` on things that hurt to lose, such as databases and state buckets. "
                "It has one gap: if you delete the whole resource block from your code, the guard goes with it."
            ),
            "refs": [
                ref("The lifecycle meta-argument", U["tf_lifecycle"], "docs"),
                ref("Manage resource lifecycle", U["tf_lifecycle_tut"], "docs"),
            ],
        },
    ],
    "analogy": (
        "State is like the ticket book in a theatre cloakroom. When you hand in a coat, the attendant writes your ticket number next to the hook. "
        "Without the book, there is a room full of coats and no way to know which one is yours. "
        "Where it breaks: a ticket book only notes the hook, while Terraform's state copies every detail of each resource, secrets included."
    ),
    "diagram": svg.d14(),
    "diagram_caption": "Variables go in and outputs come out. The root module calls child modules, and the state remembers what exists.",
    "worked": {
        "title": "One module, two nginx sites, and some drift",
        "steps": [
            {
                "say": "In a practice folder, create `modules/site/main.tf`. It takes three inputs and returns a URL. A child module that uses a non-HashiCorp provider must name it in its own `required_providers`.",
                "code": MODULE_TF,
                "lang": "hcl",
            },
            {
                "say": "Next to the `modules` folder, write `main.tf`. Copy the `terraform` and `provider` blocks from Day 13's file to the top, then add this. The `for_each` argument calls the module once per map entry.",
                "code": ROOT_TF,
                "lang": "hcl",
            },
            {
                "say": "Run init (it now also installs the module), then apply. The output holds both URLs.",
                "code": "$ terraform init\nInitializing modules...\n- site in modules/site\n$ terraform apply -auto-approve\nApply complete! Resources: 3 added, 0 changed, 0 destroyed.\nOutputs:\nsites = {\n  \"blue\" = {\n    \"url\" = \"http://localhost:8091\"\n  }\n  \"green\" = {\n    \"url\" = \"http://localhost:8092\"\n  }\n}",
                "lang": "console",
            },
            {
                "say": "List the state. Each copy has its own address, with the map key in square brackets.",
                "code": "$ terraform state list\ndocker_image.nginx\nmodule.site[\"blue\"].docker_container.this\nmodule.site[\"green\"].docker_container.this",
                "lang": "console",
            },
            {
                "say": "Cause drift on purpose: delete one container behind Terraform's back. A refresh-only plan reports it and changes nothing. You may also see small \"has changed\" notes for the other site. That is the provider filling in empty default values.",
                "code": "$ docker rm -f site-green\n$ terraform plan -refresh-only\nNote: Objects have changed outside of Terraform\n  # module.site[\"green\"].docker_container.this has been deleted",
                "lang": "console",
            },
            {
                "say": "A normal plan offers to fix the drift by creating the missing container again. Apply it, check both sites, then clean up.",
                "code": "$ terraform plan\n  # module.site[\"green\"].docker_container.this will be created\nPlan: 1 to add, 0 to change, 0 to destroy.\n$ terraform apply -auto-approve\n$ terraform destroy -auto-approve\nDestroy complete! Resources: 3 destroyed.",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "hcl", "title": "infra/local/versions.tf", "src": lab("infra/local/versions.tf"), "run": "terraform init"},
        {"lang": "hcl", "title": "infra/local/variables.tf", "src": lab("infra/local/variables.tf"), "run": "terraform validate"},
        {"lang": "hcl", "title": "infra/local/main.tf", "src": lab("infra/local/main.tf"), "run": "terraform plan"},
        {"lang": "hcl", "title": "infra/local/outputs.tf", "src": lab("infra/local/outputs.tf"), "run": "terraform apply && curl $(terraform output -raw url)"},
    ],
    "commands": [
        {"cmd": "terraform apply -var host_port=8081", "what": "Set one variable for this run only."},
        {"cmd": "terraform output -raw url", "what": "Print one output without quotes, handy inside other commands."},
        {"cmd": "terraform console", "what": "Open a prompt where you can try expressions such as `var.host_port`."},
        {"cmd": "terraform state list", "what": "List every resource address in the state."},
        {"cmd": "terraform state show docker_container.redis", "what": "Show everything the state knows about one resource."},
        {"cmd": "terraform graph", "what": "Print the dependency graph as text that Graphviz can draw."},
        {"cmd": "terraform plan -refresh-only", "what": "Show only drift: changes made outside Terraform."},
        {"cmd": "terraform apply -refresh-only", "what": "Accept drift by writing the real values into the state, changing nothing else."},
        {"cmd": "terraform plan -generate-config-out=generated.tf", "what": "With an import block, write a first draft of the resource block for you."},
        {"cmd": "terraform fmt -recursive", "what": "Format the .tf files in this folder and every subfolder, including modules."},
    ],
    "mistake": (
        "Committing `terraform.tfstate` to git, or pasting it into a chat. State can hold passwords and tokens in plain text, and shared copies soon disagree. "
        "Keep `*.tfstate` in `.gitignore` (the lab already does) and use a remote backend with locking as soon as a second person or a pipeline runs Terraform."
    ),
    "real_world": (
        "At PayLoop, a made-up payments company, each environment has its own small root folder that calls shared child modules, such as a `service` module every team reuses. "
        "State lives in a versioned S3 bucket with locking, and only the pipeline may write to it. "
        "A nightly job runs `terraform plan -refresh-only` and posts any drift to the team chat."
    ),
    "task": {
        "title": "Run hello-devops with Terraform (infra/local)",
        "steps": [
            "Make sure the image exists: from the repo root, run `docker build -t hello-devops:1.0.0 .`.",
            "In `infra/local`, add `variables.tf` with three variables: the app image, the app version, and the host port (default 8080). Give each a type and a description.",
            "In `main.tf`, add a `docker_network` and attach your Redis container to it with a `networks_advanced` block.",
            "Add the app container: use `var.app_image`, set `REDIS_HOST` from the Redis container's name with a reference, and map container port 8000 to `var.host_port`.",
            "Add `outputs.tf` with a `url` output built from `var.host_port`.",
            "Run fmt, validate, plan and apply. Open the URL and reload a few times.",
            "Run `terraform graph` and check the order it implies: network, then Redis, then the app.",
            "Plan with `-var host_port=8081` and read it before you apply. What gets replaced, and why?",
            "Destroy everything, then commit your files.",
        ],
        "hints": [
            "Containers on the same user-defined network find each other by name, just like Compose did on Day 7.",
            "Use `docker_container.redis.name` instead of the plain string, so Terraform knows Redis must exist first.",
            "Compare with the Files section only after you have tried it yourself.",
        ],
        "done_when": "`curl localhost:8080` shows `visits` counting up, and `terraform output -raw url` prints http://localhost:8080.",
    },
    "explain_back": {
        "prompt": "A teammate wants to commit `terraform.tfstate` so everyone can share it. Explain in 3 to 4 sentences what state contains, why it matters, and where it should live instead.",
        "answer": (
            "The state file is Terraform's record of what it manages: it links each resource in our code to a real object and stores its attributes. "
            "Plan uses it to decide what to create, change or destroy, so losing or corrupting it causes real damage. "
            "It can hold secrets in plain text, so it must not go into git. "
            "It belongs in a remote backend, such as a versioned S3 bucket, with locking so two runs cannot change it at the same time."
        ),
    },
    "recap": [
        "Variables are inputs, outputs are return values, and locals are named expressions.",
        "Value order, weakest to strongest: default, `TF_VAR_` environment variable, `terraform.tfvars`, `-var`.",
        "References build the dependency graph, so Terraform knows the order and runs independent work in parallel.",
        "State links code to real objects and can hold secrets. Keep it out of git, in a locked remote backend.",
        "`plan -refresh-only` shows drift, and an `import` block adopts something that already exists.",
        "Modules are reusable folders. Prefer `for_each` over `count` for copies.",
    ],
    "check": [
        {
            "q": "You use `count = 3` to make containers from the list [\"a\", \"b\", \"c\"]. You remove \"a\" from the list. What happens on the next plan?",
            "options": [
                "Only the container for \"a\" is destroyed",
                "The others shift position and may be replaced",
                "Nothing, because count ignores list changes",
                "Terraform refuses until you switch to for_each",
            ],
            "answer": 1,
            "why": "With `count`, copies are numbered, so \"b\" moves from index 1 to 0 and Terraform sees changed copies; `for_each` keys avoid this.",
        },
        {
            "q": "A teammate applied with `-var host_port=9000`. You run `terraform plan` the next day with no flags and no tfvars file. What do you see?",
            "options": [
                "No changes, because Terraform remembers 9000",
                "An error asking you for host_port",
                "A plan to change the port back to the default",
                "A plan to destroy everything",
            ],
            "answer": 2,
            "why": "`-var` values are not saved, so your plan uses the default 8080 and proposes to change the port back.",
        },
        {
            "q": "A colleague created an S3 bucket by hand last year. You want Terraform to manage it without deleting it. What do you add?",
            "options": [
                "An import block plus a matching resource block",
                "A data block that reads the bucket",
                "A lifecycle block with prevent_destroy",
                "A depends_on that points at the bucket",
            ],
            "answer": 0,
            "why": "An import block adopts the existing bucket into state; a data block only reads it and never manages it.",
        },
    ],
    "interview": [
        {
            "q": "How do you manage Terraform state in a team?",
            "a": (
                "Keep state in a remote backend, such as a versioned and encrypted S3 bucket, or HCP Terraform. "
                "Turn on locking so only one run changes it at a time; with S3 that is `use_lockfile = true`. "
                "Limit who can read it, because it can contain secrets. "
                "Split large setups into smaller states, for example one per environment, so a mistake affects less. "
                "Never edit state by hand; use `terraform state` commands and import blocks."
            ),
        },
        {
            "q": "What is drift, and how do you handle it?",
            "a": (
                "Drift is a difference between real infrastructure and Terraform's state, usually caused by manual changes or another tool. "
                "You find it with `terraform plan`, or `terraform plan -refresh-only` to see only the outside changes. "
                "Then you decide: apply to restore what the code says, or change the code (or run `apply -refresh-only`) to accept it. "
                "To prevent it, limit write access in the console and run plans on a schedule so drift shows up early."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "Import and rename are the two state moves you will need most. Both are done with blocks in your code, so they go through review like any other change.\n\n"
            "Try an import on your laptop:\n"
            "1. Create a network by hand: `docker network create legacy-net`.\n"
            "2. Get its ID: `docker network inspect -f '{{.Id}}' legacy-net`.\n"
            "3. In a Terraform folder, add an `import` block with two arguments: `to = docker_network.legacy` and `id` set to that ID.\n"
            "4. Run `terraform plan -generate-config-out=generated.tf`. The plan says the network \"will be imported\", and Terraform writes a resource block into `generated.tf`.\n"
            "5. Read `generated.tf`. It lists every attribute, including defaults. Keep what matters (here, `name = \"legacy-net\"`), move it into `main.tf`, and delete the file.\n"
            "6. Plan again. You want `Plan: 1 to import, 0 to add, 0 to change, 0 to destroy.` Then apply.\n\n"
            "Terraform prints a warning that config generation is experimental. That is fine for a first draft.\n\n"
            "Always read the plan line for the imported resource. It must say \"will be imported\". "
            "If it says \"must be replaced\", your resource block does not match reality, and apply would delete the real object and make a new one. "
            "This is common. For example, when you import a Docker container, the provider cannot read back some settings, such as published ports. "
            "The plan then wants to replace the container. Fix the block, or manage that thing a different way, before you apply.\n\n"
            "Renaming is the other common move. If you rename `docker_container.web` to `docker_container.app` in the code, Terraform sees one resource gone and a new one wanted. "
            "It plans a destroy and a create. A `moved` block with `from = docker_container.web` and `to = docker_container.app` fixes this. "
            "Plan then shows a move and no replacement. The same works when you move a resource into a module, from `docker_container.web` to `module.site[\"blue\"].docker_container.this`.\n\n"
            "The older commands `terraform import` and `terraform state mv` still exist. They change state right away, with no plan and no review. "
            "The blocks are safer, because a teammate can read them in a pull request."
        ),
    },
    "sources": [
        {"title": "Input variables", "url": U["tf_vars"]},
        {"title": "Backend type: s3", "url": U["tf_s3"]},
        {"title": "Import existing resources", "url": U["tf_import"]},
        {"title": "Modules overview", "url": U["tf_modules"]},
    ],
}

# ---------------------------------------------------------------- Day 15
IGNORE_SNIPPET = '''# trivy:ignore:AWS-0089 Access logs need a second bucket. Not worth it for a lab.
resource "aws_s3_bucket" "state" {

# trivy:ignore:AWS-0132 A customer managed KMS key costs money each month.
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {

# trivy:ignore:AWS-0345 s3:* is limited to this project's buckets.
data "aws_iam_policy_document" "permissions" {'''

d15 = {
    "id": "d15",
    "title": "Terraform on a real cloud, and in CI",
    "minutes": 40,
    "goal": "By the end you can set up a safe AWS account, create a private S3 bucket with Terraform, keep state in it, and run plan and apply from GitHub Actions without stored keys.",
    "guess": {
        "q": "You open a new AWS account on the free plan (the one offered since July 2025). What happens when your free credits run out?",
        "options": [
            "Your card is charged for whatever you use next",
            "Nothing, free usage goes on for another year",
            "The account closes unless you upgrade to a paid plan",
            "Everything keeps running, but you cannot create more",
        ],
        "answer": 2,
        "why": "The free plan does not charge you. When the credits or the six months run out, the account closes, and you have 90 days to upgrade to a paid plan to keep it.",
    },
    "terms": [
        {"term": "IAM", "plain": "AWS's service for users, roles and permissions, which decides who can do what."},
        {"term": "IAM role", "plain": "A set of AWS permissions that a person or a program can borrow for a short time."},
        {"term": "OIDC", "plain": "A standard that lets one system, such as GitHub, prove who it is to another with a short-lived signed token."},
        {"term": "Trust policy", "plain": "The part of an IAM role that says who is allowed to use the role."},
        {"term": "S3 bucket", "plain": "A named storage container in AWS that holds files, which S3 calls objects."},
        {"term": "Budget alert", "plain": "An email from AWS Budgets when your spending passes, or is expected to pass, a limit."},
    ],
    "sections": [
        {
            "h": "Before any cloud: make the account safe",
            "body": (
                "This part is optional. The rest of the course runs on your laptop, and the CI checks in the worked example need no account. "
                "If you do use AWS, do these steps first, in this order:\n"
                "1. Sign up. Accounts created since July 15, 2025 choose a plan. The free plan gives $100 in credits, plus up to $100 more for trying services, for six months. You are not charged while you stay on it.\n"
                "2. Protect the root user, the email login you signed up with. It can do anything, even close the account. Turn on MFA for it, and do not use it for daily work.\n"
                "3. Create a budget alert. In Billing and Cost Management, open Budgets, choose Create budget, use a template, and pick the zero spend budget with your email. Budgets without actions are free.\n"
                "4. Make an everyday login that is not root (next section).\n\n"
                "When the free plan's credits or six months run out, the account closes unless you upgrade within 90 days. "
                "Older accounts use the old free tier and can be billed, so the alert matters even more there.\n\n"
                "A budget only sends email. It stops nothing, and its numbers can be hours old. "
                "The real protection is to destroy what you create, which is the last step today. "
                "Today's resources should cost about nothing: a few small files and requests."
            ),
            "refs": [
                ref("Choosing an AWS Free Tier plan", U["aws_plans"], "docs"),
                ref("Root user best practices", U["aws_root"], "docs"),
                ref("Using a budget template", U["aws_budget_tpl"], "docs"),
            ],
        },
        {
            "h": "A login for your laptop that is not root",
            "body": (
                "Terraform's AWS provider finds credentials the same way as the AWS CLI: environment variables such as `AWS_PROFILE`, or the files in `~/.aws`. "
                "Install the CLI with `brew install awscli`, and check the current AWS docs if anything differs. Two common ways to get a non-root login:\n"
                "- IAM Identity Center, AWS's single sign-on. You sign in through the browser and get short-lived credentials. Run `aws configure sso` once, then `aws sso login` each day.\n"
                "- An IAM user with MFA and an access key, saved with `aws configure`. It is simpler, but the key is a long-lived password on your disk. Delete it when you finish.\n\n"
                "Identity Center is the better habit. One catch: it is built on AWS Organizations, and some Organizations actions move a free-plan account to the paid plan. "
                "To stay on the free plan, use the IAM user path today.\n\n"
                "Then run `aws sts get-caller-identity`. It should print your account ID and a user or role that is not root. If that works, Terraform will work too."
            ),
            "refs": [
                ref("Configure IAM Identity Center authentication with the AWS CLI", U["aws_sso_cli"], "docs"),
                ref("Security best practices in IAM", U["aws_iam_bp"], "docs"),
            ],
        },
        {
            "h": "A private, versioned bucket, then state inside it",
            "body": (
                "The lab's `infra/aws` folder creates one S3 bucket. A bucket name must be unique across all AWS accounts, so the code adds your 12-digit account ID to it. "
                "It reads the ID with the data source `aws_caller_identity`.\n\n"
                "In the AWS provider, a bucket's settings are separate resources next to `aws_s3_bucket`:\n"
                "- `aws_s3_bucket_versioning` keeps every old version of every file, so a bad write can be undone.\n"
                "- `aws_s3_bucket_public_access_block` stops anything in the bucket from becoming public.\n"
                "- `aws_s3_bucket_server_side_encryption_configuration` encrypts files with keys that S3 manages.\n\n"
                "New buckets already block public access and encrypt files by default. Writing it down still helps, because reviewers and scanners can see it. "
                "The provider's `default_tags` block adds tags such as `Project` and `ManagedBy` to everything, so you can always tell what a resource is for.\n\n"
                "This bucket also stores its own state. That is a chicken-and-egg problem, solved in two steps:\n"
                "1. Apply with local state. This creates the bucket.\n"
                "2. Uncomment the `backend \"s3\"` block, add the bucket name, and run `terraform init -migrate-state`. Terraform copies the state into S3 and uses it from then on.\n\n"
                "The block sets `use_lockfile = true`, so each run writes a small `.tflock` file next to the state. A second run that finds it stops with a lock error instead of changing the state."
            ),
            "refs": [
                ref("Backend type: s3", U["tf_s3"], "docs"),
                ref("Amazon S3 applies two security best practices to new buckets", U["aws_s3_defaults"], "read"),
            ],
        },
        {
            "h": "GitHub Actions logs in to AWS with OIDC",
            "body": (
                "On Day 12 you met OIDC: a workflow gets a short-lived token from GitHub instead of storing AWS keys. "
                "The lab's `github-oidc.tf` builds the AWS side:\n"
                "1. An OIDC identity provider for `token.actions.githubusercontent.com` with the audience `sts.amazonaws.com`. A certificate thumbprint is no longer needed.\n"
                "2. An IAM role whose **trust policy** checks the token's `sub` (subject) claim. It names the repo and the context, such as `pull_request` or `environment:production`.\n"
                "3. A permissions policy that says what the role may do.\n\n"
                "This trips most people up: the `sub` must match exactly. Repos created after July 15, 2026 put numeric IDs in it, like `repo:you@123456/hello-devops@456789:pull_request`. "
                "Older repos use `repo:you/hello-devops:pull_request`. The lab trusts both forms, for your repo only. "
                "If the login fails with \"Not authorized to perform sts:AssumeRoleWithWebIdentity\", the `sub` does not match.\n\n"
                "Keep the role small. The lab's role may manage only buckets whose names start with `hello-devops-`, and read its own IAM setup so that plan works. "
                "It cannot change IAM, so a pull request cannot give itself more power. You apply IAM changes from your laptop."
            ),
            "refs": [
                ref("Configuring OpenID Connect in Amazon Web Services", U["gh_oidc_aws"], "docs"),
                ref("Immutable subject claims for GitHub Actions OIDC tokens", U["gh_immutable"], "read"),
                ref("aws-actions/configure-aws-credentials", U["configure_aws"], "docs"),
            ],
        },
        {
            "h": "The pipeline: plan on pull requests, apply on main",
            "body": (
                "The lab's `.github/workflows/terraform.yml` runs only when files in `infra/aws` change. On a pull request, the plan job:\n"
                "1. Checks formatting with `terraform fmt -check`.\n"
                "2. Runs `terraform init -backend=false` and `terraform validate`, which need no AWS login.\n"
                "3. Scans the code with `trivy config` and fails on HIGH or CRITICAL findings.\n"
                "4. Logs in with OIDC, runs `terraform plan`, and puts the plan on the run's summary page for reviewers.\n\n"
                "After the merge to main, the apply job runs in the `production` environment. Like the release job on Day 12, it waits until a required reviewer approves. Then it plans and applies.\n\n"
                "Three more details keep it safe:\n"
                "- `concurrency` with `cancel-in-progress: false`, so a second run waits and never stops an apply halfway.\n"
                "- `TF_VAR_` environment variables filled from the `github` context, so CI passes your owner, repo and their IDs without secrets.\n"
                "- The role ARN lives in a repository variable, `AWS_ROLE_ARN`, because it is not secret."
            ),
            "refs": [
                ref("hashicorp/setup-terraform", U["setup_tf"], "docs"),
                ref("OpenID Connect in GitHub Actions", U["gh_oidc"], "docs"),
            ],
        },
        {
            "h": "Linters and scanners",
            "body": (
                "Plan tells you what will change. It does not tell you whether the change is wise. Two free tools help:\n"
                "- tflint finds mistakes that `validate` misses, such as unused variables. Its AWS plugin, turned on in a `.tflint.hcl` file and installed with `tflint --init`, also catches things like invalid instance types.\n"
                "- `trivy config` looks for security problems, such as public buckets, missing encryption, or IAM policies that allow too much. Checkov is a similar tool.\n\n"
                "Scanners are strict on purpose, and you decide what to fix. To accept a finding, put a comment such as `# trivy:ignore:AWS-0132` above the resource, followed by the reason. "
                "A reviewer can then read the decision and question it."
            ),
            "refs": [
                ref("TFLint", U["tflint"], "docs"),
                ref("TFLint ruleset for AWS", U["tflint_aws"], "docs"),
                ref("Trivy: Terraform scanning", U["trivy_tf"], "docs"),
            ],
        },
    ],
    "analogy": (
        "OIDC works like a hotel key card. At the front desk (GitHub) you prove who you are, and you get a card that opens one room (the IAM role) and stops working at checkout. "
        "Nobody carries a master key that works forever. "
        "Where it breaks: a hotel checks your passport in person, while AWS only trusts GitHub's signature, so the trust policy must name exactly which repo may get a card."
    ),
    "diagram": svg.d15(),
    "diagram_caption": "A pull request gets a plan. After merge and approval, the apply job runs. Both jobs swap a GitHub OIDC token for short-lived AWS credentials.",
    "worked": {
        "title": "Run the CI checks on your laptop first",
        "steps": [
            {
                "say": "Copy the lab's `infra/aws` files into your repo. Format and validate need no AWS account, so start there. `-backend=false` skips the S3 backend, which does not exist yet. `fmt -check` prints nothing when every file is tidy.",
                "code": "$ cd ~/code/hello-devops/infra/aws\n$ terraform fmt -check -recursive\n$ terraform init -backend=false\nTerraform has been successfully initialized!\n$ terraform validate\nSuccess! The configuration is valid.",
                "lang": "console",
            },
            {
                "say": "Scan with trivy (`brew install trivy`, or run the `aquasec/trivy` image as CI does). Before the ignore comments existed, it reported three findings. These are its headline lines.",
                "code": "$ trivy config .\nAWS-0345 (HIGH): IAM role uses a policy that allows 's3:*' action\nAWS-0089 (LOW): Bucket has logging disabled\nAWS-0132 (HIGH): Bucket does not encrypt data with a customer managed key.",
                "lang": "console",
            },
            {
                "say": "Decide on each one. Access logs need a second bucket, and a customer managed KMS key costs money every month, so a lab accepts both. `s3:*` is limited to this project's buckets. Record each decision above the block it is about.",
                "code": IGNORE_SNIPPET,
                "lang": "hcl",
            },
            {
                "say": "Scan again the way CI does. `--exit-code 1` makes trivy fail the job when it finds HIGH or CRITICAL problems. Zero findings, exit code 0.",
                "code": "$ trivy config --severity HIGH,CRITICAL --exit-code 1 .\n│ github-oidc.tf │ terraform │         0         │\n│ main.tf        │ terraform │         0         │\n$ echo $?\n0",
                "lang": "console",
            },
            {
                "say": "Give the variables values. `gh api` returns your user's and repo's numeric IDs. `terraform.tfvars` is not secret, so you may commit it.",
                "code": "$ gh api users/YOUR_USER --jq .id\n$ gh api repos/YOUR_USER/hello-devops --jq .id\n$ cat terraform.tfvars\ngithub_owner    = \"YOUR_USER\"\ngithub_owner_id = \"123456\"\ngithub_repo_id  = \"456789\"",
                "lang": "console",
            },
            {
                "say": "Try a plan. Without AWS credentials it stops at the provider. This is exactly the point where CI logs in with OIDC, and where your laptop needs `aws sso login` or your IAM user's profile.",
                "code": "$ terraform plan\nPlanning failed. Terraform encountered an error while generating this plan.\n\nError: No valid credential sources found",
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "hcl", "title": "infra/aws/versions.tf", "src": lab("infra/aws/versions.tf"), "run": "terraform init"},
        {"lang": "hcl", "title": "infra/aws/variables.tf", "src": lab("infra/aws/variables.tf"), "run": "terraform validate"},
        {"lang": "hcl", "title": "infra/aws/main.tf", "src": lab("infra/aws/main.tf"), "run": "terraform plan"},
        {"lang": "hcl", "title": "infra/aws/github-oidc.tf", "src": lab("infra/aws/github-oidc.tf"), "run": "terraform apply"},
        {"lang": "hcl", "title": "infra/aws/outputs.tf", "src": lab("infra/aws/outputs.tf"), "run": "terraform output"},
        {"lang": "yaml", "title": ".github/workflows/terraform.yml", "src": lab(".github/workflows/terraform.yml"), "run": "git add .github/workflows/terraform.yml && git commit -m \"Terraform CI\" && git push"},
    ],
    "commands": [
        {"cmd": "aws configure sso", "what": "Set up a CLI profile that signs in through IAM Identity Center."},
        {"cmd": "aws sso login", "what": "Sign in through the browser and get short-lived credentials for today."},
        {"cmd": "aws sts get-caller-identity", "what": "Show which account and identity your credentials belong to."},
        {"cmd": "terraform init -backend=false", "what": "Install providers without touching the backend, so validate works with no cloud login."},
        {"cmd": "terraform init -migrate-state", "what": "After changing the backend block, copy the existing state to the new place."},
        {"cmd": "terraform fmt -check -recursive", "what": "Fail if any file is not formatted. Good for CI."},
        {"cmd": "terraform plan -out=tfplan", "what": "Save the plan to a file, so apply does exactly what you reviewed."},
        {"cmd": "terraform apply tfplan", "what": "Apply a saved plan without asking again."},
        {"cmd": "tflint --init && tflint", "what": "Install the plugins named in .tflint.hcl, then lint the folder."},
        {"cmd": "trivy config --severity HIGH,CRITICAL .", "what": "Scan Terraform files for risky security settings."},
        {"cmd": "aws s3 ls", "what": "List your S3 buckets, to check what exists before and after cleanup."},
    ],
    "mistake": (
        "Running `terraform destroy` while the state still lives in the bucket you are destroying. The bucket goes away, and Terraform then has nowhere to save the final state. "
        "Comment out the backend block and run `terraform init -migrate-state` to bring the state home first, then destroy."
    ),
    "real_world": (
        "At PayLoop, a made-up payments company, engineers have read-only access to production. "
        "Every infrastructure change goes through a pull request whose plan is posted for review, and only the pipeline's role can apply, after a second person approves. "
        "Scanner findings that the team accepts are written down with a reason, so auditors can see each decision."
    ),
    "task": {
        "title": "Optional: the bucket on AWS, state in S3, CI, then clean up",
        "steps": [
            "No AWS account? Do only step 6. The plan job will pass fmt, validate and trivy, then stop at the AWS login.",
            "Secure the account: root MFA, a zero spend budget with your email, and a non-root login. `aws sts get-caller-identity` must not show root.",
            "In `infra/aws`, create `terraform.tfvars` as in the worked example, then `terraform init` and `terraform apply`. Read the plan first: how many resources, and which are IAM?",
            "Uncomment the backend block, paste the bucket name from `terraform output bucket_name`, and run `terraform init -migrate-state`. Then run `terraform state list` to see it read state from S3.",
            "In GitHub, save `terraform output github_actions_role_arn` as a repository variable named `AWS_ROLE_ARN`. Check that the `production` environment from Day 12 still has you as a required reviewer.",
            "Add `.github/workflows/terraform.yml`. On a branch, add a `tags` argument to the bucket resource only, push, and open a pull request.",
            "Read the plan on the run's summary page. Merge, approve the apply job, and watch it finish.",
            "Clean up from your laptop: comment out the backend block, run `terraform init -migrate-state` to bring the state home, then `terraform destroy`.",
            "Delete the budget if you no longer want it, and delete any IAM access key you created today.",
        ],
        "hints": [
            "If the plan job fails at the AWS login, compare the `sub` values in the role's trust policy with your repo. New repos use the numeric ID form.",
            "Tag the bucket, not `default_tags`. A default tag also changes IAM resources, and the CI role is not allowed to change IAM.",
        ],
        "done_when": "The apply job in GitHub ends with `Apply complete!`, and after cleanup `aws s3 ls` no longer lists your hello-devops bucket.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how your workflow gets permission to change AWS without any stored keys. Mention the OIDC provider, the trust policy and the `sub` claim.",
        "answer": (
            "Because the workflow has `id-token: write`, the job can ask GitHub for a signed OIDC token. "
            "The configure-aws-credentials action sends that token to AWS and asks to use our IAM role. "
            "AWS checks the signature through the OIDC provider for token.actions.githubusercontent.com, and the role's trust policy checks the `aud` and `sub` claims. "
            "The `sub` names our repo and the context, such as a pull request or the production environment, so no other repo can use the role. "
            "AWS then returns credentials that expire after a short time."
        ),
    },
    "recap": [
        "Cloud work starts with safety: root MFA, a non-root login, a budget alert, and destroy at the end.",
        "On the free plan you are not charged; the account closes when the credits or six months run out.",
        "Bucket settings such as versioning and the public access block are separate resources.",
        "Create the state bucket with local state, then move state into it with `terraform init -migrate-state`.",
        "CI checks and plans on pull requests, and applies on main after an environment approval.",
        "OIDC gives CI short-lived credentials, and the trust policy's `sub` check decides who may use the role.",
    ],
    "check": [
        {
            "q": "Your pull request's plan job passes fmt and validate, then fails with \"Not authorized to perform sts:AssumeRoleWithWebIdentity\". What is the most likely cause?",
            "options": [
                "The bucket name is already taken",
                "The token's `sub` does not match the trust policy",
                "terraform fmt changed a file during the run",
                "The budget alert blocked the request",
            ],
            "answer": 1,
            "why": "That error means AWS refused the token for this role, which almost always means the `sub` or `aud` condition did not match.",
        },
        {
            "q": "You want CI to apply only after a person says yes. Where does that gate live in the lab?",
            "options": [
                "In the production environment's required reviewers",
                "In the S3 backend's lock file",
                "In the trust policy's `aud` condition",
                "In the workflow's concurrency group",
            ],
            "answer": 0,
            "why": "A job with `environment: production` waits until a required reviewer of that environment approves it.",
        },
        {
            "q": "A teammate adds `Owner = \"ops\"` to the provider's `default_tags` in a pull request. The plan looks fine, but apply on main fails. Why?",
            "options": [
                "Tags cannot change once a bucket exists",
                "The saved plan expired before apply",
                "Default tags also change the IAM role",
                "S3 buckets do not support tags",
            ],
            "answer": 2,
            "why": "The CI role can read IAM but not change it, so tag updates on the IAM role and OIDC provider are refused at apply time.",
        },
    ],
    "interview": [
        {
            "q": "How would you run Terraform safely in CI/CD?",
            "a": (
                "Run fmt, validate, a linter and a security scanner on every pull request, then a plan that reviewers can read. "
                "Apply only from the main branch, behind an approval such as a protected environment, with one run at a time. "
                "Keep state in a remote backend with locking, and log in with OIDC so there are no long-lived cloud keys. "
                "Give the CI role the smallest permissions it needs, and keep powerful changes such as IAM out of the automatic path."
            ),
        },
        {
            "q": "Why use OIDC instead of AWS access keys stored in GitHub secrets?",
            "a": (
                "Access keys last until someone deletes them, so a key that leaks through a log or a bad action can be used for months. "
                "With OIDC, the job gets a signed token from GitHub and swaps it for AWS credentials that expire within hours. "
                "The role's trust policy limits which repo, branch or environment may get them. "
                "There is also nothing to store or rotate."
            ),
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": (
            "The lab's pipeline is a good start. Real teams usually close three more gaps.\n\n"
            "First, the plan you reviewed is not exactly the plan that runs. The pull request's plan is made from the branch, before the merge. "
            "The apply job makes a fresh plan from main, which may include other merged changes or new drift. Teams handle this in a few ways:\n"
            "- Require pull request branches to be up to date with main before merging, so the reviewed plan is closer to what runs.\n"
            "- Split the work on main into two jobs. One plans and saves the plan file as an artifact. The next one, behind the environment gate, applies exactly that file, so the approver can read it first.\n"
            "- Use a tool built for this. Atlantis is open source and runs plan and apply from pull request comments. HCP Terraform and similar services do the same as a hosted product.\n\n"
            "Second, one role for both jobs is more power than a pull request needs. "
            "A cleaner design has two roles. The plan role trusts only `pull_request` and gets read-only permissions plus access to the state and lock files. "
            "The apply role trusts only `environment:production` and may change things. "
            "Anyone who can push a branch could edit the workflow in a pull request to run apply, so read-only permissions for pull requests matter.\n\n"
            "Third, state access is permission. Anyone who can write the state bucket can change what Terraform believes exists. "
            "Big teams keep state buckets in a separate account. They turn on versioning and `prevent_destroy`, and only a few roles may write. "
            "They give each environment its own state file, and often its own account. "
            "A mistake in the dev state then cannot touch production.\n\n"
            "A last note on cost and cleanup. Destroy is not only for labs. Teams run short-lived test environments and destroy them automatically each night. "
            "Because the code describes everything, recreating them in the morning takes one apply."
        ),
    },
    "sources": [
        {"title": "Backend type: s3", "url": U["tf_s3"]},
        {"title": "Configuring OpenID Connect in Amazon Web Services", "url": U["gh_oidc_aws"]},
        {"title": "Choosing an AWS Free Tier plan", "url": U["aws_plans"]},
        {"title": "Trivy: Terraform scanning", "url": U["trivy_tf"]},
    ],
}

# ---------------------------------------------------------------- Part
part = {
    "part": 4,
    "title": "Infrastructure as Code with Terraform",
    "intro": (
        "So far you created containers by typing commands. In this part you describe infrastructure in files, and Terraform makes the real world match them. "
        "You start on your laptop with Docker, then optionally create a real AWS bucket and run Terraform from GitHub Actions."
    ),
    "lessons": [d13, d14, d15],
    "recap": [
        "IaC keeps infrastructure in reviewed, versioned files, and Terraform makes reality match them.",
        "The loop is init, plan, apply and destroy, and you always read the plan before you approve it.",
        "Variables, outputs, locals and modules make Terraform code reusable.",
        "State links code to real objects, can hold secrets, and belongs in a locked remote backend.",
        "`plan -refresh-only` shows drift, and `import` blocks adopt things that already exist.",
        "On AWS, start with safety: root MFA, a non-root login, a budget alert, and destroy when done.",
        "CI checks and plans on pull requests, applies on main after approval, and logs in with OIDC.",
    ],
    "flashcards": [
        {"front": "What does `-/+` mean in a Terraform plan?", "back": "Replace: destroy the resource, then create a new one."},
        {"front": "What does `terraform init` do?", "back": "Downloads providers and modules, sets up the backend, and writes the lock file."},
        {"front": "Which do you commit: `.terraform.lock.hcl` or `terraform.tfstate`?", "back": "Commit the lock file. Never commit the state file."},
        {"front": "Why does OpenTofu exist?", "back": "HashiCorp moved Terraform to the BSL licence in 2023, so the community forked the last open source version."},
        {"front": "Where can a variable get its value, from weakest to strongest?", "back": "Default, `TF_VAR_` environment variable, `terraform.tfvars`, then the `-var` flag."},
        {"front": "Does `sensitive = true` keep a value out of the state?", "back": "No. It only hides the value on screen; state stores it in plain text."},
        {"front": "How do you look at drift without changing anything?", "back": "`terraform plan -refresh-only`."},
        {"front": "What two arguments does an `import` block need?", "back": "`to`, the resource address, and `id`, the real object's ID."},
        {"front": "Why prefer `for_each` over `count`?", "back": "Removing one key affects only that copy; with count, later copies shift and get replaced."},
        {"front": "What does `prevent_destroy = true` do?", "back": "Makes any plan that would destroy the resource fail."},
        {"front": "What does `use_lockfile = true` do in the S3 backend?", "back": "Writes a .tflock file next to the state so only one run can change it at a time."},
        {"front": "What must a workflow have to ask GitHub for an OIDC token?", "back": "The `id-token: write` permission."},
        {"front": "Which token claims does the lab's role trust policy check?", "back": "`aud` (sts.amazonaws.com) and `sub` (the repo plus pull_request or environment:production)."},
        {"front": "What happens when an AWS free plan account runs out of credits?", "back": "It closes unless you upgrade to a paid plan within 90 days."},
    ],
    "quiz": [
        {
            "q": "A plan line ends with `# forces replacement`. What will apply do to that resource?",
            "options": ["Edit it in place", "Destroy it and create a new one", "Skip it until next time", "Import it into the state"],
            "answer": 1,
            "why": "That attribute cannot change on the existing object, so Terraform replaces it.",
        },
        {
            "q": "Which statement about Terraform state is true?",
            "options": [
                "It is a cache you can delete safely",
                "Terraform encrypts it on your laptop by default",
                "You should commit it so teammates share it",
                "It can contain secrets in plain text",
            ],
            "answer": 3,
            "why": "State stores resource attributes, including passwords and tokens, so it needs protection and a proper backend.",
        },
        {
            "q": "Two pipeline runs try to apply against the same S3-backed state at the same moment. What stops them from corrupting it?",
            "options": ["State locking with the lock file", "The `-refresh-only` flag", "Bucket versioning on its own", "The `.terraform.lock.hcl` file"],
            "answer": 0,
            "why": "With `use_lockfile = true`, the first run holds a lock file and the second is refused; `.terraform.lock.hcl` only pins provider versions.",
        },
        {
            "q": "You want containers named a, b and c, and later to remove b without touching the others. What do you use?",
            "options": ["`count = 3`", "Three copies of the module folder", "`for_each` over a set of names", "`depends_on`"],
            "answer": 2,
            "why": "`for_each` gives each copy a stable key, so removing \"b\" only destroys that copy.",
        },
        {
            "q": "In the lab, the CI role may not change IAM. So how do changes to the role itself get applied?",
            "options": ["By the plan job on pull requests", "By the apply job after approval", "By a nightly drift job", "From your laptop, with your own login"],
            "answer": 3,
            "why": "Keeping IAM changes out of CI means a pull request cannot give the pipeline more power.",
        },
        {
            "q": "In `infra/local`, the app reaches Redis at the host name `hello-redis`. Which Docker feature makes that work?",
            "options": ["DNS on a user-defined network", "Port mapping with `-p`", "A bind mount", "The HEALTHCHECK instruction"],
            "answer": 0,
            "why": "Containers on the same user-defined network can find each other by container name through Docker's built-in DNS.",
            "from": "Part 2",
        },
        {
            "q": "A job uses `environment: production`, and that environment has a required reviewer. What happens when the job is triggered?",
            "options": [
                "It runs, then asks for a review afterwards",
                "It fails, because environments need secrets",
                "It waits until a reviewer approves it",
                "It runs only on pull requests",
            ],
            "answer": 2,
            "why": "Required reviewers are a protection rule: the job pauses before it starts until someone approves.",
            "from": "Part 3",
        },
        {
            "q": "What does `terraform init -migrate-state` do after you add a backend block?",
            "options": [
                "Creates the S3 bucket for you",
                "Copies the existing state into the new backend",
                "Deletes the old state without asking",
                "Upgrades every provider to its newest version",
            ],
            "answer": 1,
            "why": "It moves your current state to the backend you just configured, so Terraform keeps track of what exists.",
        },
    ],
}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
