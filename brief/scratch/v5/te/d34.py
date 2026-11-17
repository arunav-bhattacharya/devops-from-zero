from common import apply

S0 = """
Our lab has the same two houses. The lab app, hello-devops, is a tiny web app that answers every visit with a greeting and a count of visits so far. Our `infra/local` folder runs it with Redis, the small database that keeps the count, on port 8080. Now we want a second copy for testing, our show home.

Copying `infra/local` into a new folder works for a week. Then someone fixes a setting in one copy and forgets the other, just like the dripping tap. A module lets you write the shape once and use it twice, with different names and ports.

You have written modules since the first Terraform lesson without knowing the word. A **module** is a folder of `.tf` files. The folder where you run `terraform` is the root module. When it uses another folder through a `module` block, that folder becomes a child module. Shortened, the call looks like this: `module "dev" { source = "../modules/hello-stack"  name = "hello"  host_port = 8080 }`.

A child module works like a standard house plan that a builder uses on many plots:
- Its variables are the options each buyer picks, such as the plot and the door colour. Those without a default must be filled in.
- Its outputs are what the builder hands back, read as `module.dev.url`.
- Its resources are the real houses. Use the plan twice and you get two sets of real objects.

One thing differs from a paper plan. Once a house is built, later changes to the paper leave it alone. Change a module, and every stack that uses it changes on its next apply. Each call also lives on in the state: its resources get addresses with a module prefix, such as `module.dev.docker_container.app`, and they stay until you remove the call.

After you add or change a `module` block, run `terraform init` again. It records where each module lives, and it downloads modules from elsewhere into `.terraform/modules`. Local folders are used in place. If you forget init, plan stops with `Error: Module not installed` and tells you to run it. Writing the call is easy. Deciding what the module asks for takes more thought.
"""

S1 = """
A module's variables are the face it shows to everyone who uses it, so design them with care:
- Ask only for what really changes between calls. hello-stack takes a name prefix, a port, the app image and version, an optional greeting and the Redis image ID.
- Give a default only where one value suits almost everyone, like `greeting = ""`.
- Validate inside the module. `host_port` rejects ports below 1024 there, so every caller gets the check for free.
- Return what callers need, such as the URL and the container names, and nothing more.

A child module names its providers in `required_providers`, but it has no `provider` block. The root sets up each provider once, and every module call uses it. So the caller decides which Docker engine or AWS account the module works in. Terraform then picks one provider version that fits the root's rule and every module's rule at once.

That is why you write the module's version rule loosely, like `>= 4.6, < 5.0`, and let the root pin the exact version. A tight pin inside a module would clash with any root that wants another version.

Names need care when one module is called twice. Docker refuses two containers with the same name, and clouds refuse two storage buckets with the same name. The hello-stack module builds every name from `var.name`, so the dev stack gets `hello-web` and the test stack gets `hello-test-web`.

The usual layout is four files, `main.tf`, `variables.tf`, `outputs.tf` and `versions.tf`, plus a README (a short guide) when other teams use the module. HashiCorp's style guide keeps local modules in a `modules` folder. The lab puts this one in `infra/modules/hello-stack`, next to the `local` and `aws` roots, so any root can use it. Our module lives next door, but many modules come from much further away.
"""

S2 = """
The `source` argument says where a module lives:
- A local path that starts with `./` or `../`. Terraform uses the folder in place, and a change shows up on the next plan.
- The public registry, an online catalogue of shared modules, such as `terraform-aws-modules/vpc/aws`, with a separate `version` argument like `version = "~> 6.7"`.
- A git repository, such as `git::https://example.com/acme/tf-modules.git//vpc?ref=v1.2.0`, where `?ref=` pins a tag (a named version) or a commit.

Registry modules save real work. The [terraform-aws-modules VPC module](https://github.com/terraform-aws-modules/terraform-aws-vpc) builds a whole private network in AWS from a handful of arguments. A module runs with your permissions and creates real resources that cost money. Read one before you use it, the way you would read a contract before you sign it.

Pin every module that comes from elsewhere. HashiCorp's style guide says to pin modules to a specific major and minor version, because an unpinned module can change your infrastructure on the next `init`. To move to a newer version, change the rule, run `terraform init -upgrade`, and read the plan before you apply.

Picture a platform team (the team that builds shared tools for other teams) that keeps one `service` module in its own git repository. It releases the module with tags such as v2.3.0. Product teams use it from their `envs/dev` and `envs/prod` folders, with `?ref=` pinned. An upgrade goes to dev first, and prod gets the new tag a week later through a one-line pull request. Shared modules raise a fair question: how much should one module hold?
"""

S3 = """
How big should a module be? Draw the line around something one team owns and changes as a unit, like "one hello-devops stack" or "one service's database". Avoid both extremes:
- A module that wraps a single resource adds a layer to read and saves nothing.
- One giant module for the whole company puts everything at risk on every change, and its plans take minutes.

Composition means wiring small modules together in the root, instead of putting modules inside modules inside modules. Values flow through arguments and outputs. In the lab, the root owns the Redis image and passes its ID into both stacks. The module does not create the image itself, because two stacks would then manage the same image twice.

A good root module ends up short. It sets up providers, calls modules, and connects outputs to inputs. HashiCorp's docs describe each environment the same way: a backend block (where the state lives) plus a small number of module blocks, with arguments for the few things that differ. A rough rule: when a root folder grows past a few hundred lines, part of it probably belongs in a module.

**Keep modules focused and roots thin.** With a thin root in hand, the next question is how to give each environment one of its own.
"""

S4 = """
An environment is one full copy of a system for one purpose. Dev is for building, test is for trying, and prod (production) is the real one your users depend on. They need the same shape with small differences, and teams handle that in three ways:
1. One folder, several workspaces. `terraform workspace new qa` gives the same code a second, empty state, and `terraform.workspace` holds the current name.
2. One folder, one `.tfvars` file per environment, used as `terraform plan -var-file=prod.tfvars`. Each environment still needs its own state, since an address like `docker_container.app` points at one object only. So you also switch the backend settings per environment, which is easy to get wrong.
3. One folder per environment, like `envs/dev` and `envs/prod`. Each is a short root that calls shared modules and has its own backend and state.

HashiCorp's own docs lean towards the third. They say CLI workspaces share one backend, so they are not a suitable way to keep environments apart when each needs its own credentials (keys and passwords) and access rules. The show home's keys should not open the family's front door. Prod should not share a storage bucket, or a set of permissions, with someone's experiment.

That is why most teams use a folder per long-lived environment, with the differences kept in a few module arguments. Workspaces are still handy for short-lived copies, such as one stack per feature branch (a line of work in git that lives for a few days).

They need care, though. In the worked example, a fresh workspace plans to create containers whose names and ports are already taken. If you use workspaces, build names from `terraform.workspace`, such as `name = "site-${terraform.workspace}"`, and look up ports in a map keyed by workspace. Whatever the layout, a bug in a shared module now reaches every environment, so the module deserves tests.
"""

S5 = """
A bug in a shared module reaches every stack that uses it. So a module deserves tests like any other code. `terraform test` runs files that end in `.tftest.hcl`, usually kept in a `tests` folder inside the module. A test file holds one or more `run` blocks:
- `command = plan` checks the plan only. Nothing is created, so it is a quick check on paper.
- `command = apply` is the default. It creates real resources, checks them, and destroys them when the file finishes.
- An `assert` block holds a `condition` and an `error_message`.
- A `variables` block sets inputs for the whole file or for one run.
- `expect_failures` says a run must fail, such as `expect_failures = [var.host_port]` to prove that port 80 is rejected.

Real resources in every test would be slow, and in a cloud they cost money. A `mock_provider "docker" {}` block swaps the real provider for a stand-in. The stand-in answers every request itself and makes up values that are normally only known after apply, such as IDs. Then even `command = apply` creates nothing, and the tests need no Docker and no cloud account. That makes them cheap enough to run on every pull request, which Day 35 does.

The lab's test file has five runs. Three check names and settings, one checks the `url` output, and one proves that port 80 is rejected. When a run fails, the output shows the actual and the expected value side by side, so you see the problem without guessing. Run the tests after every change to the module. Tests catch wrong behaviour. A few even cheaper checks catch sloppy files before you get that far.
"""

S6 = """
Three cheap checks catch most problems before a plan:
- `terraform fmt -recursive` rewrites every file in the standard style. In CI you run `terraform fmt -check -recursive`, which fails instead of rewriting.
- `terraform validate` checks the language, the types and the references, with no credentials and without touching anything.
- tflint is a separate linter, a tool that reads code and points out likely mistakes. Its built-in rules catch things like unused variables and providers with no version rule. Plugins add rules for one platform. The AWS plugin, for example, spots a server size that does not exist, which `validate` cannot know.

Install tflint with `brew install --cask terraform-linters/tap/tflint`, as its README says. Homebrew, the `brew` command, installs programs on a Mac. Run `tflint --init` once to download the plugins named in `.tflint.hcl`, then run `tflint` in a folder, or `tflint --recursive` from the top.

Run all three before you push. So far, though, everything has run on your laptop, against Docker. Day 35 puts these checks into a pipeline, in front of a security scanner and a plan against a real cloud.
"""

new = {
    "goal": "By the end you can write a small module with inputs and outputs, use it more than once, choose a layout for environments, and test a module with terraform test.",
    "opening": """Picture a builder putting up the same small house twice. One is a show home that visitors can poke around in. The other is where a family will really live. The architect copies the drawing for the second plot, and for a while all is well.

Then a tap in the show home drips. The architect fixes the show home's drawing and forgets the family's copy. A month later the family's tap drips too, and nobody can say why the two houses differ. Copying felt safe because both drawings started out the same. Copies only stay the same if every change is made twice, and people forget.

Last time, we opened Terraform's state and saw that each folder keeps one book. In this lesson, we'll write the shape of our lab once, as a module, and use it for two separate stacks. We'll give each environment its own folder and state, and test the module without creating anything. Before we start, make a guess, and keep it in mind.""",
    "guess": (
        "Your dev and prod environments need different credentials (keys and passwords) and different access rules. Which setup does HashiCorp's documentation recommend?",
        "CLI workspaces share one backend, the place the state is kept, so the docs call them unsuitable for keeping environments apart. A separate root folder per environment that calls shared modules gets its own backend and permissions.",
    ),
    "terms": [
        "A folder of .tf files that another folder can use through a module block, filling in its inputs.",
        "The folder where you run terraform. It calls child modules and owns the state.",
        "A folder used through a module block, with variables as its inputs and outputs as its answers.",
        "Where a module lives: a local path, an address in the public registry or a git URL.",
        "A second, separate state for the same folder of code, chosen with terraform workspace.",
        "Terraform's built-in test tool. It runs the run blocks in .tftest.hcl files and checks their assert conditions.",
        "A stand-in provider used in tests that makes up values such as IDs, so the tests create nothing real.",
    ],
    "sections": [
        ("One plan, many houses: every folder is a module", S0),
        ("What a module asks for and what it hands back", S1),
        ("Modules from elsewhere, and pinning them", S2),
        ("Small modules, wired together in a thin root", S3),
        ("Keeping environments apart: workspaces, folders or tfvars files", S4),
        ("Testing a module without building anything", S5),
        ("Cheap checks before every push", S6),
    ],
    "diagram_caption": "infra/local uses the hello-stack module twice, with different names and ports, so you get two separate stacks.",
    "worked": [
        "Copy the `modules` practice folder to `~/code/tf-modules`. It has one module and two roots, one per environment. The module runs one nginx site (a small web server) and takes a name, a port and a message.",
        "Each environment root is tiny: a provider and one module call. Only the arguments differ between `envs/dev` and `envs/prod`. This is the module call in `envs/dev/main.tf`.",
        "Init the dev root. It finds the module, then the provider. Apply and check the page. The addresses now carry the module prefix.",
        "Do the same in `envs/prod`. Each folder now has its own state file, so an apply in prod has no way to touch dev.",
        "Now compare a workspace. In `envs/dev`, create one called qa. Terraform switches to a new, empty state, so the plan wants to create everything again, with the same name `site-dev` and port 8201 that dev already uses. Applying would fail, because the code never uses the workspace name. Switch back and delete it.",
        "Clean up both environments.",
    ],
    "task": {
        "steps": [
            "Create `infra/modules/hello-stack/` with a `versions.tf` that only lists the docker provider. Add a `variables.tf` for the name prefix, the host port (with validation), the app image, the app version, the greeting and the Redis image ID.",
            "Move the network, the Redis container, the `app_env` local and the app container from `infra/local/main.tf` into the module's `main.tf`. Build every name from `var.name`. Add an `outputs.tf` with the URL, the container names and the network.",
            "In `infra/local`, keep the `docker_image` and the provider. Add `module \"dev\"` with name `hello` and port 8080, passing `docker_image.redis.image_id` as the Redis image. Update `variables.tf` and `outputs.tf` to match.",
            "Run `terraform init`, then `terraform plan`. Count the destroys, and do not apply.",
            "Add `moved.tf` with one `moved` block per resource that moved into `module.dev`. Plan until you see three \"has moved to\" lines and 0 to destroy, then apply. Your visit count should carry on from before.",
            "Add `module \"test\"` with name `hello-test`, port 8082 and its own greeting. Apply, then `curl` both ports.",
            "Copy the test file from the Files section into the module's `tests` folder. From the module folder, run `terraform init` and `terraform test`.",
            "Break a test on purpose: change the app container's name to `${var.name}-app` and run `terraform test` again. Read the difference it prints, then change the name back.",
            "From `infra`, run `terraform fmt -recursive`, then `terraform validate` in `local`. Commit everything except `.terraform` folders and state.",
        ],
        "hints": [
            "The moves are `docker_network.app`, `docker_container.redis` and `docker_container.app`, each to the same name under `module.dev.`",
            "Run `terraform test` from `infra/modules/hello-stack`, not from `infra/local`.",
            "If plan says `Module not installed`, you added a module block since your last `terraform init`.",
        ],
        "done_when": "`curl localhost:8080` and `curl localhost:8082` both answer (the second with your test greeting), the plan after adding moved.tf showed 0 to destroy, and `terraform test` printed `Success! 5 passed, 0 failed.`",
    },
    "explain_back": (
        "In 3 to 4 sentences, explain to a friend how one module can create both a dev and a test stack without them colliding. Mention inputs, outputs and resource addresses.",
        "The module is one folder of code, with variables as its inputs and outputs as its answers. The root uses it twice, as `module.dev` and `module.test`, with different inputs such as the name prefix and the port. Every name inside is built from the name input, so Docker gets `hello-web` and `hello-test-web`, and each call's resources get their own addresses in the state. One change to the module's code reaches both stacks on the next apply, so a fix is made once.",
    ),
    "recap": [
        "Every folder is a module. The root uses child modules through `module` blocks and `source`.",
        "Variables are a module's inputs, outputs its answers, and resources get addresses like `module.dev.docker_container.app`.",
        "Run `terraform init` after adding a module, and pin the version of every module from elsewhere.",
        "Keep modules focused and roots thin: providers, module calls and wiring.",
        "Prefer a folder per long-lived environment over CLI workspaces when credentials differ.",
        "`terraform test` with `mock_provider` is free and fast, but all of this still runs on your laptop, not on a real cloud.",
    ],
    "closing": """We began with a show home and a family home whose drawings slowly drifted apart. Now both stacks come from one module, so a fix lands in both. Each environment keeps its own folder and its own book.

In the lab, run `terraform state list` in `infra/local` and look for the `module.dev.` and `module.test.` prefixes. If you ever see the same resource under two roots, two books are claiming one house.

Next, we'll take these skills off the laptop. What changes when Terraform builds real things in a real cloud, and runs from a pipeline instead of your terminal?""",
    "check": [
        ("Inside the module called `test`, there is `resource \"docker_container\" \"app\"`. What is that container's address in the state?",
         "Resources inside a module call get the `module.<call name>.` prefix in front of their normal address."),
        ("You add a new `module` block and run `terraform plan` straight away. What happens?",
         "Plan fails with `Module not installed` until `terraform init` records the new module."),
        ("A test file has a `run` block with no `command` and no mock provider. What happens when you run `terraform test`?",
         "The default command is apply, so Terraform creates real infrastructure for the test and destroys it when the file finishes."),
    ],
    "interview": [
        ("What is a Terraform module, and when do you write one?",
         "A module is a folder of Terraform code with input variables and outputs, used from another configuration through a `module` block. I write one when the same shape of infrastructure appears more than once, such as one service stack per environment, or when a team wants a reviewed, versioned building block. I keep modules focused on one thing a team owns, not on one resource. I pin modules from elsewhere to a version, and test shared ones with `terraform test`."),
        ("How do you manage dev, staging and prod with Terraform?",
         "I put the shared shape into modules and give each long-lived environment its own small root folder, with its own backend, state and credentials. The differences live in a few module arguments, or a small tfvars file per folder. HashiCorp's docs say CLI workspaces share a backend and are not a suitable way to separate environments with different access rules. Changes roll through dev first, then prod, often by raising a module version."),
        ("How do you test Terraform code?",
         "First the cheap checks: `terraform fmt -check`, `terraform validate` and tflint, plus a security scanner such as trivy. Then `terraform test` with `.tftest.hcl` files: plan-mode runs for logic and naming, `expect_failures` for validation rules, and mock providers so the tests need no cloud account. For important modules I add an apply-mode test against a real practice account, which creates and destroys real resources. And every pull request still gets a person reading the real plan."),
    ],
    "deeper": """
Once other teams use your module, it becomes a product with users, and changes need the care you would give any shared library of code.

Version it with git tags and semantic versioning, a common way to number releases as MAJOR.MINOR.PATCH. A new optional input is a minor version, like v1.3.0. A renamed input, a removed output, or anything that replaces resources is a major version, like v2.0.0. Callers pin with `?ref=v1.3.0` in a git source, or with `version = "~> 1.3"` for a registry module. HashiCorp's style guide names registry module repositories `terraform-<PROVIDER>-<NAME>`, such as `terraform-aws-vpc`.

Clean-ups inside a module need `moved` blocks too, and they belong in the module itself. Say version 2 renames `docker_container.app` to `docker_container.web`. A `moved` block inside the module turns that into a move for every caller, on their next apply. The refactoring docs strongly recommend keeping old `moved` blocks in shared modules, because removing one breaks anyone still upgrading from an older version.

Test where your users will feel it:
- Plan-mode tests with a mock provider for naming, validation and wiring. They are fast and need no credentials.
- An apply-mode test against a practice account for anything subtle, such as IAM policies (AWS's permission rules). It costs a little time and money, so many teams run it nightly instead of on every push.
- An `examples` folder with a small root that uses the module. It is documentation, and also a check that the module works when someone uses it from outside.

Workspaces have one more detail. With the S3 backend, each extra workspace's state is stored under `env:/<workspace>/` in the same bucket, next to the default one. That is the sharing the docs warn about: one bucket, one set of permissions.

Two bigger tools exist once a company has many environments. HCP Terraform has Stacks, which describe repeated deployments of the same components with `component` and `deployment` blocks, each deployment with its own state. Some teams use a wrapper tool to generate many small roots from one template. You need neither for this course. It sticks to folders, modules and pinned versions, which work the same in Terraform and OpenTofu.
""",
    "drop": ["analogy", "mistake", "real_world"],
}

apply(8, "d34", new)
