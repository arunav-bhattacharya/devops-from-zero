from common import *
from svg import D25

SECTIONS = [
    {
        "h": "Why clicking in a console does not scale",
        "body": (
            "Every cloud has a web console. You can click a server, a database and a network into existence in ten minutes, and it works. Six months later you need the same setup again for a test environment. Which boxes did you tick? Nobody remembers, and nobody wrote it down.\n\n"
            "Doing infrastructure by hand goes wrong in three ways:\n"
            "- You cannot repeat it. There is no exact copy for testing, for another region, or for recovery after a disaster.\n"
            "- Nobody reviews it. A change happens without a second pair of eyes, and nothing records who did what.\n"
            "- It drifts. Someone changes a setting by hand during an incident, and reality slowly moves away from what the team believes.\n\n"
            "**Infrastructure as Code** (IaC) means you describe your infrastructure in text files, and a tool makes the real world match them. The files live in git next to your app, so infrastructure gets the same treatment as your Kotlin code:\n"
            "- `git log` shows every change, who made it and why.\n"
            "- A pull request lets a teammate review a change before it reaches anything real.\n"
            "- Reverting a commit and applying again rolls a change back.\n"
            "- The same files build a second, identical environment.\n\n"
            "The short version: your infrastructure gets a pull request. This part of the course uses Terraform, the most widely used IaC tool. You practise on Docker on your laptop for four days, so nothing costs money. Day 29 is the optional trip to a real cloud."
        ),
        "refs": [
            ref("What is Terraform? (Terraform docs)", HC + "intro", "docs"),
            V_INTRO_HC,
        ],
    },
    {
        "h": "Declarative: describe the result, not the steps",
        "body": (
            "You can tell a computer what you want in two ways:\n"
            "- Imperative: you list the steps. \"Pull nginx, then start a container, then publish port 8090.\" A shell script works this way.\n"
            "- Declarative: you describe the result. \"There is one nginx container called tf-web on port 8090.\" The tool works out the steps.\n\n"
            "Terraform is declarative, and you feel the difference the second time you run it. Run a `docker run` script twice and the second run fails, because the name is taken. Run Terraform twice and the second run prints `No changes`. The file only says what should exist, and it already does. A command that gives the same result however many times you run it is called idempotent.\n\n"
            "As a backend engineer you already know this idea from SQL. You write `SELECT ... WHERE status = 'PAID'`, and the database decides whether to use an index or scan the table. Terraform is similar. You write the end state, and Terraform makes a plan of API calls to get there. Under the hood it still runs steps in order. You just do not write them.\n\n"
            "You met the same idea on Day 15. `compose.yaml` describes services, and `docker compose up` makes them exist. Compose only knows Docker on one machine. Terraform talks to almost anything that has an API: Docker, AWS, Google Cloud, Azure, GitHub, Cloudflare and thousands more."
        ),
        "refs": [
            ref("Get started with Terraform and Docker (HashiCorp tutorial)", HC + "tutorials/docker-get-started", "docs"),
            V_NANA,
        ],
    },
    {
        "h": "Terraform, OpenTofu and the other tools",
        "body": (
            "HashiCorp makes Terraform, and IBM bought HashiCorp in February 2025. Terraform was open source under the MPL licence until August 2023. Then [HashiCorp moved it to the Business Source License](https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license) (BSL). You may still use Terraform for free at work. What you may not do is sell a product that competes with HashiCorp's own.\n\n"
            "Part of the community disliked the change and forked the last open source version. The fork is called OpenTofu. It lives at the Linux Foundation and joined the CNCF in 2025. You type `tofu` instead of `terraform`, and `tofu plan` behaves like `terraform plan`. The language is the same, and everything in this part works with both. A few newer features exist in only one of them. If your team already uses one, stay with it.\n\n"
            "You will hear about these tools too:\n"
            "- CloudFormation: AWS's own IaC service, with YAML or JSON templates. It works only for AWS.\n"
            "- Pulumi: IaC written in normal languages such as TypeScript, Python, Go, C# or Java.\n"
            "- Ansible: connects to servers that already exist and sets them up (packages, files, services).\n\n"
            "Teams often combine them. Terraform creates the network, the machines and the Kubernetes cluster. A container image or Ansible decides what runs inside. Terraform can configure servers too, but that is not where it shines."
        ),
        "refs": [
            ref("HashiCorp adopts Business Source License", "https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license", "read"),
            ref("The OpenTofu manifesto", "https://opentofu.org/manifesto/", "read"),
            ref("Migrating from Terraform to OpenTofu (guide source)", "https://github.com/opentofu/opentofu/blob/main/website/docs/intro/migration/migration-guide.mdx", "docs"),
        ],
    },
    {
        "h": "Providers, resources and the shape of a .tf file",
        "body": (
            "Terraform files end in `.tf` and use HCL, the HashiCorp Configuration Language. Terraform reads every `.tf` file in a folder as one configuration, so file names are only for humans. A file is made of blocks:\n"
            "- A block has a type, labels and braces: `resource \"docker_container\" \"web\" { }`.\n"
            "- An argument sets a value inside a block: `name = \"tf-web\"`.\n"
            "- A reference reads a value from another block: `docker_image.nginx.image_id`.\n\n"
            "A **provider** is a plugin that translates your blocks into API calls for one platform. The `terraform` block lists the providers you need, with a source and a version, much like a dependency in `build.gradle.kts`. This lesson uses `kreuzwerker/docker`, which talks to the same Docker engine as the `docker` command. The `provider \"docker\" {}` block then configures it. Empty braces mean \"use the defaults\".\n\n"
            "A resource block has two labels. The first is the resource type, such as `docker_container`, and it always starts with the provider's name. The second is your own name for it, such as `web`. Together they make the address `docker_container.web`. The address must be unique in the folder, and Terraform uses it everywhere: in plans, in state and in commands.\n\n"
            "References also set the order. The container refers to the image, so Terraform pulls the image first. You never write \"do this first\". Resources with no reference between them are created in parallel."
        ),
        "refs": [
            ref("kreuzwerker/docker provider documentation", "https://github.com/kreuzwerker/terraform-provider-docker/blob/master/docs/index.md", "docs"),
            ref("Provider requirements (Terraform docs)", HC + "language/providers/requirements", "docs"),
        ],
    },
    {
        "h": "The workflow: init, plan, apply, destroy",
        "body": (
            "You use the same few commands every day, in this order:\n"
            "1. `terraform init` downloads the providers into a hidden `.terraform` folder and writes `.terraform.lock.hcl`. Run it once per folder, and again after you add a provider or module.\n"
            "2. `terraform fmt` tidies the layout of your files, and `terraform validate` checks for typos and broken references. Neither touches anything real.\n"
            "3. `terraform plan` compares your files, the state and the real world. It prints what it would do and changes nothing.\n"
            "4. `terraform apply` makes a fresh plan, shows it, waits for you to type `yes`, makes the changes and updates the state.\n"
            "5. `terraform destroy` removes everything this folder manages, after the same `yes`.\n\n"
            "Plan is safe to run any time, so run it often. People sometimes worry that plan changes things. It does not. Apply is the only step that does.\n\n"
            "There is one gap to know about. Apply makes a new plan, and the world may have changed since your last plan. For a laptop that does not matter. In a pipeline it does, so you save the plan with `terraform plan -out=tfplan` and later run `terraform apply tfplan`. Terraform then does exactly what you reviewed, or stops if the state moved on. Day 29 uses this.\n\n"
            "`terraform destroy` deletes everything in this folder's state, not only what you added today. It never touches things the folder does not manage, such as a container you started by hand."
        ),
        "refs": [
            ref("terraform plan command reference", HC + "cli/commands/plan", "docs"),
            ref("terraform apply command reference", HC + "cli/commands/apply", "docs"),
            ref("terraform init command reference", HC + "cli/commands/init", "docs"),
        ],
    },
    {
        "h": "Reading a plan",
        "body": (
            "A plan lists every resource it would touch, each with a symbol in front:\n"
            "- `+` create a new resource.\n"
            "- `~` update in place: the same object stays, and a setting changes.\n"
            "- `-/+` replace: destroy the old object, then create a new one.\n"
            "- `-` destroy.\n\n"
            "Three more things show up all the time. `(known after apply)` means the provider will only know the value once the object exists, like a container's ID. That is normal, not an error. `# (50 unchanged attributes hidden)` means Terraform left out the lines that do not change. The last line is the summary, such as `Plan: 1 to add, 0 to change, 1 to destroy.`\n\n"
            "Replacement is where people get hurt. Some settings cannot change on a running object. Docker cannot move a running container to a new host port, or give it new environment variables. A one-character edit to one of those becomes `-/+`, and the line that caused it ends with `# forces replacement`.\n\n"
            "For an nginx container, replacement means a second of downtime. For a database it can mean an empty database. So build one habit now. Before you type `yes`, read the summary line and search the plan for `forces replacement`. If the numbers surprise you, stop and find out why."
        ),
        "refs": [
            ref("Build infrastructure (Terraform and Docker tutorial)", HC + "tutorials/docker-get-started/docker-build", "docs"),
            ref("terraform plan: planning modes and options", HC + "cli/commands/plan", "docs"),
        ],
    },
    {
        "h": "What init and apply leave behind",
        "body": (
            "After your first apply, the folder holds three new things. Each has a different rule for git:\n"
            "- `.terraform/` holds the downloaded provider binaries. It is a cache that `init` can always rebuild. Never commit it.\n"
            "- `.terraform.lock.hcl` records the exact provider version and its checksums. Commit it, so your laptop, your teammates and CI all run the same provider code.\n"
            "- `terraform.tfstate` is the state: Terraform's record of what it created. Never commit it.\n\n"
            "State is how Terraform links the address `docker_container.web` to one real container ID. Without it, Terraform could not tell \"create a container\" from \"this container already exists\". State can also hold passwords in plain text, which is the main reason it stays out of git. Day 27 is all about state.\n\n"
            "Two names sound alike, so keep them apart. The lock file pins provider versions. A state lock, which you meet on Day 27, stops two people from changing the same state at once.\n\n"
            "The lab's `.gitignore` already blocks `.terraform/` and `*.tfstate`. GitHub keeps a [ready-made Terraform .gitignore](https://github.com/github/gitignore/blob/main/Terraform.gitignore) if you start a new repo."
        ),
        "refs": [
            ref("Dependency lock file (Terraform docs)", HC + "language/files/dependency-lock", "docs"),
            ref("GitHub's Terraform.gitignore", "https://github.com/github/gitignore/blob/main/Terraform.gitignore", "read"),
        ],
    },
]

WORKED = {
    "title": "Run nginx from Terraform, change it twice, destroy it",
    "steps": [
        step("Make a practice folder outside your repo and save the `main.tf` from the Files section in it. Then run init. It reads the `terraform` block and downloads the Docker provider. The output is trimmed.",
             """$ mkdir -p ~/code/tf-first && cd ~/code/tf-first
$ terraform init
Initializing the backend...
Initializing provider plugins...
- Finding kreuzwerker/docker versions matching "~> 4.6"...
- Installing kreuzwerker/docker v4.6.0...
Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.
Terraform has been successfully initialized!"""),
        step("Preview. Nothing exists yet, so both resources get a `+`. The real plan lists about 40 attributes for the container; these are the ones worth reading. The ID and image are `(known after apply)` because Docker only knows them later.",
             """$ terraform plan
  # docker_container.web will be created
  + resource "docker_container" "web" {
      + id                                          = (known after apply)
      + image                                       = (known after apply)
      + name                                        = "tf-web"
      + restart                                     = "no"
      + ports {
          + external = 8090
          + internal = 80
        }
    }
  # docker_image.nginx will be created
Plan: 2 to add, 0 to change, 0 to destroy."""),
        step("Apply. Terraform shows the plan again and waits for `yes`. The image comes first because the container refers to it. Then check that nginx answers.",
             """$ terraform apply
  Enter a value: yes

docker_image.nginx: Creating...
docker_image.nginx: Creation complete after 1s [id=sha256:0e52bd054126cdc040b1276c0af347aeb02a41b9cfe305d6094767ac30e97949nginx:1.30-alpine]
docker_container.web: Creating...
docker_container.web: Creation complete after 1s [id=9aa5b0956097591dff522825bbefa5f8a32a44b85eb400f41daed1e8e2fae1c3]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
$ curl -s localhost:8090 | grep title
<title>Welcome to nginx!</title>"""),
        step("Run plan again without touching the file. Terraform refreshes what it knows from Docker, compares, and finds nothing to do. This is idempotence in action: a second `docker run` would have failed.",
             """$ terraform plan
docker_image.nginx: Refreshing state... [id=sha256:0e52bd054126cdc040b1276c0af347aeb02a41b9cfe305d6094767ac30e97949nginx:1.30-alpine]
docker_container.web: Refreshing state... [id=9aa5b0956097591dff522825bbefa5f8a32a44b85eb400f41daed1e8e2fae1c3]

No changes. Your infrastructure matches the configuration."""),
        step("Change `restart = \"no\"` to `\"unless-stopped\"` and plan. Docker can change a restart policy on a running container, so you get `~` and the container keeps its ID. Apply it.",
             """$ terraform plan
  # docker_container.web will be updated in-place
  ~ resource "docker_container" "web" {
        id                                          = "9aa5b0956097591dff522825bbefa5f8a32a44b85eb400f41daed1e8e2fae1c3"
        name                                        = "tf-web"
      ~ restart                                     = "no" -> "unless-stopped"
        # (50 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
$ terraform apply -auto-approve"""),
        step("Now change `external = 8090` to `8091`. Docker cannot move a running container to a new port, so Terraform must replace it. Find `forces replacement`, then notice the new container ID after apply.",
             """$ terraform apply
-/+ destroy and then create replacement
  # docker_container.web must be replaced
      ~ ports {
          ~ external = 8090 -> 8091 # forces replacement
        }
Plan: 1 to add, 0 to change, 1 to destroy.
  Enter a value: yes

docker_container.web: Destroying... [id=9aa5b0956097591dff522825bbefa5f8a32a44b85eb400f41daed1e8e2fae1c3]
docker_container.web: Destruction complete after 1s
docker_container.web: Creating...
docker_container.web: Creation complete after 1s [id=b848c22673139c98159dbab17b13f845edc786a82012082b05fed64a9bfc4d84]
Apply complete! Resources: 1 added, 0 changed, 1 destroyed."""),
        step("Clean up. Destroy removes both resources from Terraform's care. The container is gone. The image stays on your laptop because of `keep_locally = true`.",
             """$ terraform destroy
Plan: 0 to add, 0 to change, 2 to destroy.
  Enter a value: yes

Destroy complete! Resources: 2 destroyed.
$ docker ps -a --filter name=tf-web
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
$ docker image ls nginx:1.30-alpine --format '{{.Repository}}:{{.Tag}}'
nginx:1.30-alpine"""),
    ],
}

LESSON = {
    "id": "d25",
    "title": "Infrastructure as Code and your first Terraform",
    "minutes": 45,
    "goal": "By the end you can explain why teams write infrastructure as code, read a Terraform plan, and create, change and destroy a container with Terraform on your laptop.",
    "guess": mcq(
        "You run `terraform apply`, it succeeds, and then you run `terraform apply` again without changing any file. What happens the second time?",
        ["It creates a second copy of everything", "It reports no changes and does nothing", "It deletes everything and creates it again", "It fails because the things already exist"],
        1,
        "Terraform compares your files with what already exists. When they match there is nothing to do, so running it again is safe.",
    ),
    "terms": [
        {"term": "Infrastructure as Code (IaC)", "plain": "Describing servers, networks and other infrastructure in text files that a tool turns into real things."},
        {"term": "Declarative", "plain": "You describe the end result you want, and the tool works out the steps to get there."},
        {"term": "Idempotent", "plain": "Gives the same result however many times you run it; a second run changes nothing."},
        {"term": "Provider", "plain": "A Terraform plugin that talks to one platform's API, such as Docker or AWS."},
        {"term": "Resource", "plain": "One thing Terraform creates and looks after, such as a container, a network or a storage bucket."},
        {"term": "Plan", "plain": "Terraform's preview of what it would create, change or destroy. Making a plan changes nothing."},
        {"term": "Lock file", "plain": "The file .terraform.lock.hcl, which records the exact provider versions and checksums a folder uses."},
    ],
    "sections": SECTIONS,
    "analogy": "Terraform works like a thermostat. You set the temperature you want, and it turns the heating on or off until the room matches. You never tell it \"heat for ten minutes\", and setting the same temperature twice does nothing. The comparison breaks in one place: a thermostat checks the room all the time, while Terraform only looks when you run plan or apply.",
    "diagram": D25,
    "diagram_caption": "Plan compares your code with the state and the real world. Apply makes the changes through a provider and updates the state.",
    "worked": WORKED,
    "code": [
        code("hcl", "~/code/tf-first/main.tf (practice folder; also in labs/terraform-practice/first)", practice("first/main.tf"), "terraform init && terraform apply"),
        code("hcl", "infra/local/versions.tf (in hello-devops)", day("d25", "infra/local/versions.tf"), "cd ~/code/hello-devops/infra/local && terraform init"),
        code("hcl", "infra/local/main.tf (Day 25 version)", day("d25", "infra/local/main.tf"), "terraform plan && terraform apply"),
    ],
    "commands": [
        cmd("terraform version", "Show the Terraform version, and the providers once a folder is initialized."),
        cmd("terraform init", "Download the providers for this folder and write the lock file."),
        cmd("terraform fmt", "Rewrite the .tf files in this folder in the standard style."),
        cmd("terraform validate", "Check the files for syntax errors and broken references, without touching anything."),
        cmd("terraform plan", "Show what would change. Changes nothing."),
        cmd("terraform apply", "Make a fresh plan, ask for yes, then make the changes and update the state."),
        cmd("terraform apply -auto-approve", "Apply without asking. Fine for practice, risky for anything real."),
        cmd("terraform plan -out=tfplan", "Save the plan to a file, so a later apply does exactly this."),
        cmd("terraform apply tfplan", "Apply a saved plan without asking again."),
        cmd("terraform show", "Print what the state says exists right now."),
        cmd("terraform state list", "List the address of every resource this folder manages."),
        cmd("terraform destroy", "Remove everything this folder manages."),
    ],
    "mistake": "Typing `yes` without reading the plan. A one-word edit can turn into `-/+`, and replacing a database means losing its data. Read the summary line and search for `forces replacement` every time, even when you are sure the change is small.",
    "real_world": "Take PayLoop, a payments company made up for this course. Nobody there creates production infrastructure by clicking. Every change is a pull request with the Terraform plan attached, and a second engineer reads the plan before anyone applies it. People open the cloud console to look around, or during an incident, and the next plan shows whatever they changed by hand.",
    "task": {
        "title": "Run Redis for hello-devops with Terraform",
        "steps": [
            "In your hello-devops repo, create the folder `infra/local` and add `versions.tf` from the Files section.",
            "Add a `main.tf` with two resources: a `docker_image` for `redis:8-alpine` with `keep_locally = true`, and a `docker_container` named `hello-redis` that uses it.",
            "Run `terraform fmt`, `terraform init` and `terraform plan`. Before you read the summary line, predict it.",
            "Apply, then check that Redis answers with `docker exec hello-redis redis-cli ping`.",
            "Add `restart = \"unless-stopped\"` to the container and plan. Is it `~` or `-/+`? Apply it.",
            "Change the container's name and plan again. Find the line that forces replacement, then change the name back without applying.",
            "Run `ls -a` and `cat .terraform.lock.hcl`, then `git status`. Which new files does git offer to commit, and which does it ignore?",
            "Run `terraform destroy`. Check with `docker ps -a` that the container is gone and with `docker image ls redis` that the image stayed.",
            "Commit `versions.tf`, `main.tf` and `.terraform.lock.hcl`.",
        ],
        "hints": [
            "The container's `image` argument should be a reference to the image resource's `image_id`, like in the nginx example.",
            "Redis needs no published port today. `docker exec` runs `redis-cli` inside the container.",
            "If Terraform cannot connect to Docker but `docker ps` works, run `docker context inspect` to find your socket, then set `DOCKER_HOST` to it.",
        ],
        "done_when": "`docker exec hello-redis redis-cli ping` printed PONG, `git status` shows no state file, and after `terraform destroy` the container is gone from `docker ps -a`.",
    },
    "explain_back": {
        "prompt": "A teammate has never used Terraform. In 3 to 4 sentences, tell them what happens when you run `terraform plan` and then `terraform apply`. Mention the state file and what `-/+` means.",
        "answer": "Plan reads my .tf files, the state file and the real world, then prints the difference without changing anything. Apply makes that plan again, asks me to confirm, and calls the provider to make the changes. Then it updates the state file, so next time Terraform knows what already exists. A `-/+` means a setting cannot change on the existing object, so Terraform destroys it and creates a new one.",
    },
    "recap": [
        "IaC means describing infrastructure in files, so you get review, history and repeatable setups.",
        "Terraform is declarative and idempotent: you describe the result, and a second run changes nothing.",
        "A resource address such as `docker_container.web` is the type plus your own name.",
        "init downloads providers, plan previews, apply makes the changes, destroy cleans up.",
        "Plan symbols: `+` create, `~` update in place, `-/+` replace, `-` destroy. Look for `forces replacement`.",
        "Commit `.terraform.lock.hcl`; never commit `.terraform/` or `terraform.tfstate`.",
    ],
    "check": [
        mcq("You change only the `image` of a `docker_container` and run plan. The container shows `-/+`. What will apply do?",
            ["Edit the running container in place", "Stop because the file has an error", "Destroy the container and create a new one", "Pull the new image but keep the old container"],
            2, "`-/+` means replace: a running container cannot switch images, so Terraform removes it and creates a new one."),
        mcq("A teammate deletes the `tf-web` container by hand. You run `terraform plan` without changing any file. What will the plan most likely show?",
            ["A create, to bring the container back", "Nothing, because your files did not change", "An error saying the state is broken", "A destroy, to remove it from your files"],
            0, "Plan reads the real world, sees the container is missing, and proposes to create it again so reality matches the code."),
        mcq("You started a `db` container with `docker run` yesterday. Today you run `terraform destroy` in `~/code/tf-first`. What happens to `db`?",
            ["It is destroyed, because destroy removes all containers", "Terraform asks whether to destroy it too", "It is imported into the state first", "Nothing, because this folder's state does not track it"],
            3, "Destroy only removes what this folder's state tracks; Terraform never learned about `db`."),
    ],
    "interview": [
        {"q": "What is Infrastructure as Code, and why would a team use it?",
         "a": "Infrastructure as Code means describing infrastructure, such as networks, servers and permissions, in text files that a tool applies. The files live in git, so every change gets reviewed and leaves a history. You can rebuild the same setup in another region or account, which helps testing and disaster recovery. It also exposes drift: the code is the source of truth, and a plan shows any difference."},
        {"q": "What is the difference between Terraform and Ansible?",
         "a": "Terraform is declarative. It mainly creates infrastructure through cloud and platform APIs, and it tracks what it created in a state file. Ansible is mainly for configuration: it connects to existing machines over SSH and runs tasks such as installing packages, in order. Many teams use both. Terraform creates the machines, and Ansible or a container image decides what runs on them."},
        {"q": "What does `forces replacement` mean in a plan, and why does it matter?",
         "a": "It marks an attribute that the provider cannot change on an existing object, so Terraform must destroy the object and create a new one. The plan shows the resource as `-/+`. For a stateless container that is a short blip. For a database or a disk it can mean data loss or downtime, so you read those lines before approving and look for a safer change if needed."},
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Version constraints and the lock file decide which provider code runs on your machine. They deserve ten minutes, because a surprise upgrade can break a plan that worked yesterday.\n\n"
            "The `version` argument in `required_providers` is a constraint, and three forms cover most needs:\n"
            "- `= 4.6.0` allows exactly one version.\n"
            "- `~> 4.6` allows 4.6 and newer, but stays below 5.0. This is the usual choice.\n"
            "- `~> 4.6.0` allows 4.6.x patch releases only.\n\n"
            "`~>` is called the pessimistic constraint: only the rightmost number you wrote may grow. Major versions can remove or rename things, so you move to a new major version on purpose, after reading the provider's upgrade guide. The [version constraints page](https://developer.hashicorp.com/terraform/language/expressions/version-constraints) has the full syntax.\n\n"
            "`terraform init` picks the newest version that fits and records it in `.terraform.lock.hcl`, together with checksums of the provider files. From then on, init installs that exact version, even when a newer one exists. To move forward, run `terraform init -upgrade`, read the plan, and commit the new lock file. Gradle users can think of it as a dependency lock that is on by default.\n\n"
            "Mac users run into one edge case. Checksums are per platform: your Mac is `darwin_arm64`, while GitHub's runners are `linux_amd64`. A normal install from the public registry records checksums for every platform. When providers come from a local mirror or cache instead, init may record only your own platform, and init in CI then fails on the checksum. Terraform prints a warning when this happens. Fix it once with `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64`, which records both, and commit the result.\n\n"
            "The `terraform` block can also hold `required_version`, which sets the Terraform CLI versions allowed to run the code. The lab's `infra/local` asks for `>= 1.10`, and `infra/aws` asks for `>= 1.11` because the S3 lock file you meet on Day 29 needs it.\n\n"
            "OpenTofu reads the same blocks but downloads providers from its own registry. Read the OpenTofu migration guide before you switch one state between `terraform` and `tofu`, and keep a backup of the state while you try it."
        ),
    },
    "sources": [
        {"title": "Get started with Terraform and Docker (HashiCorp tutorial)", "url": HC + "tutorials/docker-get-started"},
        {"title": "terraform plan command reference", "url": HC + "cli/commands/plan"},
        {"title": "Dependency lock file", "url": HC + "language/files/dependency-lock"},
        {"title": "kreuzwerker/docker provider documentation", "url": "https://github.com/kreuzwerker/terraform-provider-docker/blob/master/docs/index.md"},
    ],
}
