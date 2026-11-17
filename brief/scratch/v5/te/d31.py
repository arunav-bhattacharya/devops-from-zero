from common import apply

S0 = """
Computers have the café's problem on a bigger scale. Many companies rent computers from a cloud, a company such as Amazon that rents out computers and storage over the internet. Each cloud has a web console, a website where you set things up by clicking.

In ten minutes you can click together a server and a database, with a network that joins them. (A server is a computer that runs programs for other computers. A database is a program that stores data safely.) It works. Six months later the team needs the same setup again, this time for testing. Which boxes did you tick? Nobody remembers, and nobody wrote it down.

Everything an app needs around it to run is called infrastructure: the computers, the networks, the storage. In the café, it is the room, the wiring and the fridge, not the coffee. Doing infrastructure by hand goes wrong in three ways:
- You cannot repeat it. There is no exact copy for testing, for another region (data centres in another part of the world), or for recovery after a disaster.
- Nobody reviews it. A change happens without a second pair of eyes, and no record says who did what.
- It drifts. During an incident (a moment when something is broken and people rush to fix it), someone changes a setting by hand. Slowly, reality moves away from what the team believes.

The cure is to write the setup down for a tool to follow. This is called **Infrastructure as Code** (IaC): you describe your infrastructure in text files, and a tool makes the real world match them. The files live in git, the tool from Part 2 that keeps every saved version of your files, right next to the app's code. So a change to infrastructure goes through the same steps as any change to code:
- `git log` shows every change, who made it and why.
- A pull request (a proposed change that a teammate reads before it is accepted) lets someone review the change before it reaches anything real.
- Undoing one saved change and applying again rolls the infrastructure back.
- The same files build a second, identical environment.

This part of the course uses Terraform, the most widely used IaC tool. For four lessons you practise with Docker on your own laptop, so nothing costs money. Day 35, "Terraform on a real cloud, and in CI", goes to a real cloud, and you can skip it. First, though, we need to see how a tool can follow a description instead of a list of steps.
"""

S1 = """
You can ask a helper to set up the café in two ways. You can hand over a list of steps, such as "carry in the chairs, then plug in the fridge". Or you can hand over a drawing of the finished room. The first way is called imperative: you list the steps. The second is declarative: you describe the result, and the helper works out the steps.

Now the computer version, with this lesson's running example. Docker is the tool that runs containers: sealed boxes that each run one program the same way on any computer. Our program is nginx, a popular program that answers web browsers with a page.

A container starts from an image, a packed copy of the program. We want ours on port 8090. A port is a numbered door that a program listens at.
- Imperative: "Pull (download) the nginx image, then start a container, then publish port 8090." A shell script, a file of typed commands that run one after another, works this way.
- Declarative: "There is one nginx container called tf-web on port 8090." The tool works out the steps.

Terraform is declarative. Your files describe the desired state: what should exist once Terraform is done. You feel the difference the second time you run it. Run a script that uses `docker run`, then run it again: the second run fails, because the name tf-web is already taken. Run Terraform twice and the second run prints `No changes`. A command that gives the same result however many times you run it is called idempotent.

How does Terraform know the container is already there? Picture an architect's drawing of a house, and a builder who compares the drawing with the house on every visit. The drawing is your Terraform files, the builder is Terraform, and the house is the real containers. The builder also keeps a notebook of everything built so far. That notebook is the state: a file called `terraform.tfstate` that records each object Terraform made and that object's real ID (the unique name Docker gave it).

Every run lines up three pictures:
1. Your files: the desired state.
2. The state: what Terraform made last time.
3. The real world: Terraform asks Docker about every ID in the state.

The plan is the difference between the desired state and what really exists, written as actions:
- In your files but not in the state: create it.
- In both, but with other settings: change it.
- In the state but gone from your files: delete it.

Apply carries out the plan and writes the result back into the state. On the second run, Docker reported the saved container with the right settings, so the plan was empty.

The builder picture has one limit. This builder only comes when called: Terraform looks only when you run plan or apply. A change made by hand stays in place until your next run.

Docker Compose, from Part 5, is declarative too, but it only knows Docker on one machine. Terraform talks to almost anything that has an API, a set of rules that lets one program ask another for things. That means Docker, AWS, Google Cloud, Azure, GitHub, Cloudflare and thousands more. Before we see how, a quick look at the other tools you will hear named beside it.
"""

S2 = """
You will hear other names next to Terraform's. The closest is OpenTofu, a free copy of Terraform that part of the community started in 2023, after Terraform's license changed. The box below tells that story. You type `tofu` instead of `terraform`, and `tofu plan` behaves like `terraform plan`. The language is the same, and everything in this part works with both. A few newer features exist in only one of them. If your team already uses one, stay with it.

Three more tools come up often:
- CloudFormation: the IaC service of AWS (Amazon Web Services, Amazon's cloud). You write it as YAML or JSON, two text formats for neatly nested settings. It works only for AWS.
- Pulumi: IaC written in normal programming languages such as TypeScript, Python, Go, C# or Java.
- Ansible: connects to servers that already exist and sets them up (packages, files, services). Days 36 and 37 teach it.

Teams often combine them, the way a house needs both a builder and a decorator. Terraform creates the network, the machines and the Kubernetes cluster (a group of computers that run containers together, Part 10). A container image or Ansible decides what runs inside. Terraform can set up software on servers too, but that is not its strength. Now let's open a Terraform file and see what it is made of.
"""

S3 = """
Terraform files end in `.tf` and use HCL, the HashiCorp Configuration Language. Terraform reads every `.tf` file in a folder as one configuration, so file names are only for humans. A file is made of blocks:
- A block has a type, labels and curly braces: `resource "docker_container" "web" { }`.
- An argument sets a value inside a block: `name = "tf-web"`.
- A reference reads a value from another block: `docker_image.nginx.image_id`.

Terraform itself knows nothing about Docker or AWS. A provider is a plugin (a separate program that adds a skill to a bigger one) that turns your blocks into requests for one platform. The `init` command downloads each provider. During plan and apply, Terraform starts the provider and asks it to read, create, change or delete objects.

The `terraform` block lists the providers you need, each with a source (where to download it) and a version, like a shopping list that names brand and size. This lesson uses `kreuzwerker/docker`. It talks to the same Docker engine (the background program that runs containers) as the `docker` command.

The `provider "docker" {}` block then sets the provider up, and empty braces mean the defaults. An environment variable is a named setting that your shell hands to every program it starts. If the variable `DOCKER_HOST` is set, the provider uses its address. Otherwise it uses `/var/run/docker.sock` from Day 2, the special file through which programs talk to the Docker engine.

A resource block has two labels. The first is the resource type, such as `docker_container`, and it always starts with the provider's name. The second is your own name for it, such as `web`. Together they make the address `docker_container.web`. The address must be unique in the folder, and Terraform uses it everywhere: in plans, in commands, and in the state, which stores the real container ID under it.

References also set the order. The container refers to the image, so Terraform pulls the image first. You never write "do this first". Resources with no reference between them are created in parallel. Next come the few commands that turn this file into something real.
"""

S4 = """
You use the same few commands every day, in this order:
1. `terraform init` downloads the providers into the `.terraform` folder and writes `.terraform.lock.hcl`. Names that start with a dot are hidden from a plain `ls`. Run init once per folder, and again after you add a provider or module. A module is a folder of Terraform files that other files reuse, and Day 34 teaches it.
2. `terraform fmt` tidies the layout of your files, and `terraform validate` checks for typos and broken references. Neither touches anything real.
3. `terraform plan` asks the provider about every object in the state (the `Refreshing state...` lines), compares the answers with your files, and prints the difference. It changes nothing.
4. `terraform apply` makes a fresh plan, shows it, waits for you to type `yes`, makes the changes and updates the state.
5. `terraform destroy` removes everything this folder manages, after the same `yes`.

Plan is safe to run any time, because only apply changes things. Run it often, the way the builder checks the drawing before picking up a hammer.

Apply makes its own new plan, and the world may have changed since you last ran plan. On a laptop that gap does not matter. In a pipeline (a series of steps a server runs for you on every change, like the GitHub Actions workflows from Part 6) it does. There you save the plan with `terraform plan -out=tfplan` and later run `terraform apply tfplan`. Terraform then does exactly what you reviewed, or stops if the state moved on. Day 35 uses this.

`terraform destroy` deletes everything in this folder's state, whenever it was added. It never touches things the folder does not manage, such as a container you started by hand. With the commands in place, the next skill is the one that keeps you safe: reading what plan prints.
"""

S5 = """
A plan lists every resource it would touch, each with a symbol in front:
- `+` create a new resource.
- `~` update in place: the same object stays, and a setting changes.
- `-/+` replace: destroy the old object, then create a new one.
- `-` destroy.

You will also see these in almost every plan:
- `(known after apply)`: the provider learns the value once the object exists, like a container's ID. That is normal.
- `# (50 unchanged attributes hidden)`: Terraform left out the attributes (single settings of a resource) that do not change.
- The summary on the last line, such as `Plan: 1 to add, 0 to change, 1 to destroy.`

In the worked example below, changing the restart policy (what Docker does when the container stops) gives `~`. Docker can change it on a running container, so the container keeps its ID.

Replacement is where people get hurt. Some settings cannot change on a running object. Docker cannot move a running container to a new host port (the port on your laptop), or give it new environment variables. So changing the port from 8090 to 8091 becomes `-/+`, and the line that caused it ends with `# forces replacement`. One small edit, and the container comes back with a new ID.

For an nginx container, replacement means a second of downtime. For a database it can mean an empty database. It is easy to type `yes` without reading when the edit was one word. Build the habit now, while the containers are toys: read the summary line and search the plan for `forces replacement`. If the numbers surprise you, stop and find out why.

**A one-word edit can replace a whole object. Read the plan before you type yes.**

Apply also leaves a few files in your folder, each with its own rule.
"""

S6 = """
After your first apply, the folder holds three new things. Each has a different rule for git, and to commit a file means to save it into git's history:
- `.terraform/` holds the downloaded providers. It is a cache, a store of copies that `init` can always rebuild. Never commit it.
- `.terraform.lock.hcl` records the exact provider version and its checksums. A checksum is a short fingerprint made from a file's contents, so any change to the file changes it. Commit the lock file, so your laptop, your teammates and CI (the server that builds and tests every change) all run the same provider code.
- `terraform.tfstate` is the state, the builder's notebook. Never commit it.

Inside, the state pairs each address, such as `docker_container.web`, with the real container ID and every setting Docker reported. State can also hold passwords in plain text, which is the main reason it stays out of git. Day 33, "State: Terraform's memory", is all about it.

Two names sound alike, so keep them apart. The lock file fixes the provider versions. A state lock, which you meet on Day 33, stops two people from changing the same state at once.

The lab's `.gitignore`, the file that lists names git should ignore, already blocks `.terraform/` and `*.tfstate`. GitHub keeps a [ready-made Terraform .gitignore](https://github.com/github/gitignore/blob/main/Terraform.gitignore) if you start a new repo (a folder that git tracks).

Our file still has a weakness, though. Every value, such as the port 8090, is typed straight into the block, so three containers would mean three copied blocks. The next lesson fixes that.
"""

new = {
    "goal": "By the end you can explain why teams write their infrastructure as code, read a Terraform plan, and create, change and destroy a container with Terraform on your laptop.",
    "opening": """Picture a friend who opens a small café. On the first morning you help her set up. You plug in the coffee machine, set the fridge to four degrees and line up twelve chairs. It all works, and nobody writes any of it down. Why would you? You were both right there.

A year later she opens a second café and asks you to make it exactly the same. You stand in the empty room and can't remember half of what you did. The trap is easy to fall into: doing things by hand feels fast the first time, and the cost arrives later.

Last time, we made a program build fast on a build server and packed it into a container, a sealed box that runs anywhere. To start containers, we typed commands, which leave the same gap as the café: nothing remembers them. In this lesson, we'll write a setup down in a file and let a tool called Terraform build it, check it and tear it down. Before we start, make a guess, and keep it in mind.""",
    "guess": (
        "You run `terraform apply` and it succeeds. Then you run `terraform apply` again, without changing any file. What happens the second time?",
        "Terraform remembers what it created, checks that those things still exist, and compares them with your files. When they match there is nothing to do, so running it again is safe.",
    ),
    "terms": [
        "Describing the computers, networks and storage an app needs in text files, which a tool then turns into real things.",
        "You describe the end result you want, and the tool works out the steps to get there.",
        "Gives the same result however many times you run it, so a second run changes nothing.",
        "A plugin program that lets Terraform talk to one platform, such as Docker or AWS.",
        "One thing Terraform creates and looks after, such as a container, a network or a place to store files.",
        "Terraform's notebook of every object it created and that object's real ID, kept in the file terraform.tfstate.",
        "Terraform's preview of what it would create, change or destroy. Making a plan changes nothing.",
        "The file .terraform.lock.hcl, which records the exact provider versions a folder uses, with a fingerprint of each.",
    ],
    "sections": [
        ("A setup that lives only in someone's memory", S0),
        ("A drawing instead of a list of steps", S1),
        ("Terraform's close cousins", S2),
        ("What a Terraform file is made of", S3),
        ("Four commands: init, plan, apply, destroy", S4),
        ("Reading a plan before you say yes", S5),
        ("What init and apply leave in your folder", S6),
    ],
    "diagram_caption": "Plan compares your files with the state and the real world. Apply makes the changes through a provider and updates the state.",
    "worked": [
        "Make a practice folder outside your hello-devops repo, and save the `main.tf` from the Files section in it. Then run init. Init reads the `terraform` block and downloads the Docker provider. The output here is trimmed.",
        "Now preview. Nothing exists yet, so both resources get a `+`. The real plan lists about 40 attributes for the container, and these are the ones worth reading. The ID and the image are `(known after apply)`, because Docker only knows them once they exist.",
        "Apply. Terraform shows the plan again and waits for `yes`. The image comes first, because the container refers to it. Then `curl`, a command that fetches a web page, checks that nginx answers.",
        "Run plan again without touching the file. The `Refreshing state` lines are Terraform asking Docker about each ID in its state. Both objects still exist with the settings your file asks for, so there is nothing to do. A second `docker run` would have failed here, because the name was taken.",
        "Change `restart = \"no\"` to `\"unless-stopped\"` and plan. Docker can change a restart policy on a running container, so you get `~`, and the container keeps its ID. Apply it.",
        "Now change `external = 8090` to `8091`. Docker cannot move a running container to a new port, so Terraform must replace it. Find `forces replacement` in the plan, then notice the new container ID after apply.",
        "Clean up. Destroy removes both resources from Terraform's care. The container is gone. The image stays on your laptop because of `keep_locally = true`.",
    ],
    "task": {
        "steps": [
            "Open your hello-devops repo, the course's lab app: a tiny web app that answers every visit with a greeting and a count of visits so far. Create the folder `infra/local` and add `versions.tf` from the Files section.",
            "The app can keep its count in Redis, a small and fast database. Add a `main.tf` with two resources: a `docker_image` for `redis:8-alpine` with `keep_locally = true`, and a `docker_container` named `hello-redis` that uses it.",
            "Run `terraform fmt`, `terraform init` and `terraform plan`. Before you read the summary line, predict it.",
            "Apply, then check that Redis answers with `docker exec hello-redis redis-cli ping`.",
            "Add `restart = \"unless-stopped\"` to the container and plan. Is it `~` or `-/+`? Apply it.",
            "Change the container's name and plan again. Find the line that forces replacement, then change the name back without applying.",
            "Run `ls -a` and `cat .terraform.lock.hcl`, then `git status`. Which new files does git offer to commit, and which does it ignore?",
            "Run `terraform destroy`. Check with `docker ps -a` that the container is gone, and with `docker image ls redis` that the image stayed.",
            "Commit `versions.tf`, `main.tf` and `.terraform.lock.hcl`.",
        ],
        "hints": [
            "The container's `image` argument should be a reference to the image resource's `image_id`, as in the nginx example.",
            "Redis needs no published port today. `docker exec` runs `redis-cli` inside the container for you.",
            "If Terraform cannot connect to Docker but `docker ps` works, run `docker context inspect` to find your socket, then set `DOCKER_HOST` to it.",
        ],
        "done_when": "`docker exec hello-redis redis-cli ping` printed PONG, `git status` shows no state file, and after `terraform destroy` the container is gone from `docker ps -a`.",
    },
    "explain_back": (
        "A friend has never used Terraform. In 3 to 4 sentences, tell them what happens when you run `terraform plan` and then `terraform apply`. Mention the state file and what `-/+` means.",
        "Plan reads my .tf files, the state file and the real world, then prints the difference without changing anything. Apply makes that plan again, asks me to confirm, and asks the provider to make the changes. Then it updates the state file, so next time Terraform knows what already exists. A `-/+` means a setting cannot change on the existing object, so Terraform destroys it and creates a new one.",
    ),
    "recap": [
        "Infrastructure as Code means describing infrastructure in files, so you get review, history and setups you can repeat.",
        "Terraform is declarative and idempotent: you describe the result, and a second run changes nothing.",
        "A resource address such as `docker_container.web` is the type plus your own name.",
        "init downloads providers, plan previews, apply makes the changes, destroy cleans up.",
        "Plan symbols: `+` create, `~` update in place, `-/+` replace, `-` destroy. Look for `forces replacement` every time.",
        "Commit `.terraform.lock.hcl`, never `.terraform/` or `terraform.tfstate`. Today's file has every value typed in, so copies mean copied blocks.",
    ],
    "closing": """We started in an empty café, trying to remember a setup nobody wrote down. Now the setup is a file. Terraform built the nginx container from it and did nothing on the second run. It changed one setting in place, and replaced the container when the port moved.

In the lab, run `terraform state list` in `infra/local` and match each address it prints to a block in `main.tf`. That is the builder's notebook, read line by line.

Next, we'll teach the file to take settings from outside, and to make many containers from one block. How do you describe three similar things without writing them out three times?""",
    "check": [
        ("You change only the `image` of a `docker_container` and run plan. The container shows `-/+`. What will apply do?",
         "`-/+` means replace: a running container cannot switch images, so Terraform removes it and creates a new one."),
        ("A teammate deletes the `tf-web` container by hand. You run `terraform plan` without changing any file. What will the plan most likely show?",
         "The refresh asks Docker about the container ID in the state. Docker reports it gone, so the plan proposes to create it again."),
        ("Yesterday you started a `db` container with `docker run`. Today you run `terraform destroy` in `~/code/tf-first`. What happens to `db`?",
         "Destroy only removes what this folder's state tracks, and Terraform never learned about `db`."),
    ],
    "interview": [
        ("What is Infrastructure as Code, and why would a team use it?",
         "Infrastructure as Code means describing infrastructure, such as networks, servers and permissions, in text files that a tool applies. The files live in git, so every change gets reviewed and leaves a history. You can rebuild the same setup in another region or account, which helps testing and recovery after a disaster. It also exposes drift: the code is the source of truth, and a plan shows any difference."),
        ("What is the difference between Terraform and Ansible?",
         "Terraform is declarative. It mainly creates infrastructure by calling the APIs of clouds and other platforms, and it tracks what it created in a state file. Ansible is mainly for configuration. It connects to machines that already exist over SSH (a secure way to log in to another computer), then runs tasks in order, such as installing packages. Many teams use both. Terraform creates the machines, and Ansible or a container image decides what runs on them."),
        ("What does `forces replacement` mean in a plan, and why does it matter?",
         "It marks an attribute that the provider cannot change on an existing object, so Terraform must destroy the object and create a new one. The plan shows the resource as `-/+`. For a container that keeps no data, that is a short blip. For a database or a disk it can mean lost data or downtime, so you read those lines before approving, and look for a safer change if needed."),
    ],
    "deeper": """
Version constraints and the lock file decide which provider code runs on your machine. They deserve ten minutes, because a surprise upgrade can break a plan that worked yesterday.

The `version` argument in `required_providers` is a constraint: a rule about which versions are allowed. Three forms cover most needs:
- `= 4.6.0` allows exactly one version.
- `~> 4.6` allows 4.6 and newer, but stays below 5.0. This is the usual choice.
- `~> 4.6.0` allows 4.6.x patch releases only.

`~>` is called the pessimistic constraint: only the rightmost number you wrote may grow. A version number has three parts, and the first one is the major version. Major versions can remove or rename things, so you move to a new one on purpose, after reading the provider's upgrade guide. The [version constraints page](https://developer.hashicorp.com/terraform/language/expressions/version-constraints) has the full syntax.

`terraform init` picks the newest version that fits and records it in `.terraform.lock.hcl`, together with checksums of the provider files. From then on, init installs that exact version, even when a newer one exists. To move forward, run `terraform init -upgrade`, read the plan, and commit the new lock file. Many build tools have a lock like this as an option. Terraform has it switched on by default.

Mac users run into one edge case. Checksums differ per platform: your Mac is `darwin_arm64`, while GitHub's runners (the machines that run your CI jobs) are `linux_amd64`. A normal install from the public registry records checksums for every platform. When providers come from a local mirror or cache instead, init may record only your own platform. Then init in CI fails on the checksum. Terraform prints a warning when this happens. Fix it once with `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64`, which records both, and commit the result.

The `terraform` block can also hold `required_version`, which sets the versions of the Terraform program itself that may run the code. The lab's `infra/local` asks for `>= 1.10`, and `infra/aws` asks for `>= 1.11`, because the S3 lock file you meet on Day 35 needs it.

OpenTofu reads the same blocks but downloads providers from its own registry. Read the OpenTofu migration guide before you switch one state between `terraform` and `tofu`, and keep a backup of the state while you try it.
""",
    "aside": {
        "title": "Who owns Terraform, and why does OpenTofu exist?",
        "body": "A company called HashiCorp makes Terraform, and IBM bought HashiCorp in February 2025. Until August 2023, Terraform was open source under the Mozilla Public License (MPL), which let anyone read, change and share the code. Then [HashiCorp moved it to the Business Source License](https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license) (BSL). You may still use Terraform for free at work, but you may not sell a product that competes with HashiCorp's own. Part of the community disliked the change and forked the last open source version: they took a copy and carried it on as its own project. That fork is OpenTofu, which lives at the Linux Foundation and joined the CNCF (Cloud Native Computing Foundation, the home of Kubernetes) in 2025.",
        "after": 2,
    },
    "drop": ["analogy", "mistake", "real_world"],
}

apply(8, "d31", new)
