from common import *
from svg import D28

V_DD_MOD = ref("Complete Terraform course: modules and multiple environments (DevOps Directive)", V_DD, "watch")

SECTIONS = [
    {
        "h": "Every folder is a module",
        "body": (
            "You have written modules since Day 25 without the word. A **module** is a folder of `.tf` files. The folder where you run `terraform` is the root module. When it calls another folder with a `module` block, that folder becomes a child module. Shortened, a call looks like this: `module \"dev\" { source = \"../modules/hello-stack\"  name = \"hello\"  host_port = 8080 }`.\n\n"
            "Think of a child module as a Kotlin function:\n"
            "- Its variables are the parameters. Those without a default are required.\n"
            "- Its outputs are the return values, read as `module.dev.url`.\n"
            "- Its resources are the side effects. Call it twice and you get two sets of real objects.\n\n"
            "The comparison breaks in one place. A function call is gone when it returns, but a module call lives on in the state. Its resources get addresses with a module prefix, such as `module.dev.docker_container.app`, and they stay until you remove the call.\n\n"
            "After you add or change a `module` block, run `terraform init` again. It records where each module lives, and it downloads remote modules into `.terraform/modules`. Local folders are used in place. You can see what init found in `.terraform/modules/modules.json`, which lists each call and its folder. If you forget init, plan stops with `Error: Module not installed` and tells you to run it."
        ),
        "refs": [
            ref("Modules overview (Terraform docs)", HC + "language/modules", "docs"),
            V_DD_MOD,
        ],
    },
    {
        "h": "Designing a module's inputs and outputs",
        "body": (
            "A module's variables are its API, so design them like one:\n"
            "- Ask only for what really changes between calls. hello-stack takes a name prefix, a port, the app image and version, an optional greeting and the Redis image ID.\n"
            "- Give a default only where one value suits almost everyone, like `greeting = \"\"`.\n"
            "- Validate inside the module. `host_port` rejects ports below 1024 there, so every caller gets the check for free.\n"
            "- Return what callers need, such as the URL and the container names, and nothing more.\n\n"
            "A child module names its providers in `required_providers`, but it has no `provider` block. The root configures each provider once, and every module call uses it. Write the module's constraint loosely, like `>= 4.6, < 5.0`, and let the root pin the exact version.\n\n"
            "Names need care when one module is called twice. Docker refuses two containers with the same name, and clouds refuse two buckets with the same name. The hello-stack module builds every name from `var.name`, so the dev stack gets `hello-web` and the test stack gets `hello-test-web`.\n\n"
            "The usual layout is four files, `main.tf`, `variables.tf`, `outputs.tf` and `versions.tf`, plus a README when other teams use the module. HashiCorp's style guide keeps local modules in a `modules` folder. The lab puts it in `infra/modules/hello-stack`, next to the `local` and `aws` roots, so any root can call it."
        ),
        "refs": [
            ref("Standard module structure (Terraform docs)", HC + "language/modules/develop/structure", "docs"),
            ref("Terraform style guide", HC + "language/style", "docs"),
        ],
    },
    {
        "h": "Where modules come from, and pinning them",
        "body": (
            "The `source` argument says where a module lives:\n"
            "- A local path that starts with `./` or `../`. Terraform uses the folder in place, and a change shows up on the next plan.\n"
            "- The public registry, such as `terraform-aws-modules/vpc/aws`, with a separate `version` argument like `version = \"~> 6.7\"`.\n"
            "- A git repository, such as `git::https://example.com/acme/tf-modules.git//vpc?ref=v1.2.0`, where `?ref=` pins a tag or a commit.\n\n"
            "Registry modules save real work. The [terraform-aws-modules VPC module](https://github.com/terraform-aws-modules/terraform-aws-vpc) builds a whole network with subnets and gateways from a handful of arguments. Remember that a module runs with your permissions and creates real, billed resources. Read one before you use it, the way you would read a library before adding it to `build.gradle.kts`.\n\n"
            "Pin every remote module. HashiCorp's style guide says to pin modules to a specific major and minor version, because an unpinned module can change your infrastructure on the next `init`. To move to a newer version, change the constraint, run `terraform init -upgrade`, and read the plan before you apply."
        ),
        "refs": [
            ref("Module sources (Terraform docs)", HC + "language/modules/sources", "docs"),
            ref("terraform-aws-modules/terraform-aws-vpc", "https://github.com/terraform-aws-modules/terraform-aws-vpc", "read"),
        ],
    },
    {
        "h": "Small modules, composed in a thin root",
        "body": (
            "How big should a module be? Draw the line around something one team owns and changes as a unit, like \"one hello-devops stack\" or \"one service's database\". Avoid both extremes:\n"
            "- A module that wraps a single resource adds a layer to read and saves nothing.\n"
            "- One giant module for the whole company puts everything at risk on every change, and its plans take minutes.\n\n"
            "Composition means wiring small modules together in the root, instead of nesting them deeply. Data flows through arguments and outputs. In the lab, the root owns the Redis image and passes its ID into both stacks. The module does not create the image itself, because two stacks would then manage the same image twice.\n\n"
            "A good root module ends up short. It configures providers, calls modules, and connects outputs to inputs. HashiCorp's docs describe each environment the same way: a backend block plus a small number of module blocks, with arguments for the few things that differ. Free advice from many teams: if your root folder grows past a few hundred lines, look for a module hiding in it."
        ),
        "refs": [
            ref("Module composition (Terraform docs)", HC + "language/modules/develop/composition", "docs"),
            ref("Terraform best practices, a free book by Anton Babenko", "https://www.terraform-best-practices.com", "read"),
        ],
    },
    {
        "h": "Environments: workspaces, folders or tfvars files",
        "body": (
            "Dev, test and prod need the same shape with small differences. Teams handle that in three ways:\n"
            "1. One folder, several workspaces. `terraform workspace new qa` gives the same code a second, empty state, and `terraform.workspace` holds the current name.\n"
            "2. One folder, one `.tfvars` file per environment, used as `terraform plan -var-file=prod.tfvars`. Each environment still needs its own state, so you also switch backend settings per environment, which is easy to get wrong.\n"
            "3. One folder per environment, like `envs/dev` and `envs/prod`. Each is a short root that calls shared modules and has its own backend and state.\n\n"
            "HashiCorp's own docs lean towards the third. They say CLI workspaces share one backend, so they are not a suitable isolation mechanism when environments need separate credentials and access controls. Prod should not share a bucket, or a set of permissions, with someone's experiment.\n\n"
            "So most teams use a folder per long-lived environment, with differences kept in a few module arguments. Workspaces are still handy for short-lived copies, such as one stack per feature branch. They need care, though: the worked example shows a fresh workspace planning to create containers whose names and ports are already taken. If you use workspaces, build names from `terraform.workspace`, such as `name = \"site-${terraform.workspace}\"`, and look up ports in a map keyed by workspace. With the S3 backend, each extra workspace's state is stored under `env:/<workspace>/` in the same bucket, next to the default one."
        ),
        "refs": [
            ref("Workspaces (Terraform docs)", HC + "cli/workspaces", "docs"),
            ref("terraform workspace command reference", HC + "cli/commands/workspace", "docs"),
        ],
    },
    {
        "h": "Testing modules with terraform test",
        "body": (
            "A module is code, so it deserves tests. `terraform test` runs files that end in `.tftest.hcl`, usually from a `tests` folder inside the module. A test file holds one or more `run` blocks:\n"
            "- `command = plan` checks the plan only, like a unit test. Nothing is created.\n"
            "- `command = apply` is the default. It creates real resources, checks them, and destroys them when the file finishes, like an integration test.\n"
            "- An `assert` block holds a `condition` and an `error_message`.\n"
            "- A `variables` block sets inputs for the whole file or for one run.\n"
            "- `expect_failures` says a run must fail, such as `expect_failures = [var.host_port]` to prove that port 80 is rejected.\n\n"
            "A `mock_provider \"docker\" {}` block swaps the real provider for a fake one that invents values for computed attributes. Then even `command = apply` creates nothing, and the tests need no Docker and no cloud account. That makes them cheap enough to run on every pull request, which Day 29 does.\n\n"
            "The lab's test file has five runs: three check names and settings, one checks the `url` output, and one proves that port 80 is rejected. When a run fails, the output shows the actual and the expected value side by side, so you see the problem without guessing. Run the tests after every change to the module, the way you run unit tests after changing a class."
        ),
        "refs": [
            ref("Tests (Terraform docs)", HC + "language/tests", "docs"),
            ref("Mocks in Terraform tests", HC + "language/tests/mocking", "docs"),
            V_HC_TESTS,
        ],
    },
    {
        "h": "Before every push: fmt, validate and tflint",
        "body": (
            "Three cheap checks catch most problems before a plan:\n"
            "- `terraform fmt -recursive` rewrites every file in the standard style. In CI you run `terraform fmt -check -recursive`, which fails instead of rewriting.\n"
            "- `terraform validate` checks syntax, types and references, with no credentials and without touching anything.\n"
            "- tflint is a separate linter with more rules. Its built-in rules catch things like unused variables and providers with no version constraint. Plugins add provider rules, such as the AWS plugin spotting an instance type that does not exist, which `validate` cannot know.\n\n"
            "Install tflint with `brew install --cask terraform-linters/tap/tflint`, as its README says. Run `tflint --init` once to download the plugins named in `.tflint.hcl`, then run `tflint` in a folder, or `tflint --recursive` from the top.\n\n"
            "Run all three before you push. Day 29 puts them into the pipeline, in front of a security scanner and the AWS plan."
        ),
        "refs": [
            ref("TFLint", "https://github.com/terraform-linters/tflint", "docs"),
            ref("terraform fmt command reference", HC + "cli/commands/fmt", "docs"),
        ],
    },
]

WORKED = {
    "title": "One module, two environment folders, and a workspace",
    "steps": [
        step("Copy the `modules` practice folder to `~/code/tf-modules`. It has one module and two roots, one per environment. The module runs one nginx site and takes a name, a port and a message.",
             """$ cd ~/code/tf-modules && find . -name '*.tf' | sort
./envs/dev/main.tf
./envs/prod/main.tf
./modules/site/main.tf"""),
        step("Each environment root is tiny: a provider and one module call. Only the arguments differ between `envs/dev` and `envs/prod`. This is the module call in `envs/dev/main.tf`.",
             """module "site" {
  source = "../../modules/site"

  name    = "site-dev"
  port    = 8201
  message = "Hello from dev"
}""", "hcl"),
        step("Init the dev root. It finds the module, then the provider. Apply and check the page. The addresses now carry the module prefix.",
             """$ cd envs/dev && terraform init
Initializing modules...
- site in ../../modules/site
- Installing kreuzwerker/docker v4.6.0...
Terraform has been successfully initialized!
$ terraform apply -auto-approve
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
Outputs:
url = "http://localhost:8201"
$ curl -s localhost:8201
<h1>Hello from dev</h1>
$ terraform state list
module.site.docker_container.site
module.site.docker_image.nginx"""),
        step("Do the same in `envs/prod`. Two folders, two state files, and no way for a prod apply to touch dev.",
             """$ cd ../prod && terraform init && terraform apply -auto-approve
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
Outputs:
url = "http://localhost:8202"
$ curl -s localhost:8202
<h1>Hello from prod</h1>
$ ls ../*/terraform.tfstate
../dev/terraform.tfstate
../prod/terraform.tfstate"""),
        step("Now compare a workspace. In `envs/dev`, create one called qa. Terraform switches to a new, empty state, so the plan wants to create everything again, with the same name `site-dev` and port 8201 that dev already uses. Applying would fail. Workspaces copy the code, not the differences. Switch back and delete it.",
             """$ cd ../dev && terraform workspace new qa
Created and switched to workspace "qa"!
$ terraform workspace list
  default
* qa
$ terraform plan
  # module.site.docker_container.site will be created
  # module.site.docker_image.nginx will be created
Plan: 2 to add, 0 to change, 0 to destroy.
$ terraform workspace select default && terraform workspace delete qa
Switched to workspace "default".
Deleted workspace "qa"!"""),
        step("Clean up both environments.",
             """$ terraform destroy -auto-approve
Destroy complete! Resources: 2 destroyed.
$ cd ../prod && terraform destroy -auto-approve
Destroy complete! Resources: 2 destroyed."""),
    ],
}

LESSON = {
    "id": "d28",
    "title": "Modules and environments",
    "minutes": 50,
    "goal": "By the end you can write a small module with inputs and outputs, call it more than once, choose a layout for environments, and test a module with terraform test.",
    "guess": mcq(
        "Your dev and prod environments need different credentials and access rules. Which setup does HashiCorp's documentation recommend?",
        ["Two CLI workspaces in one folder", "One folder with a tfvars file each", "A folder per environment calling shared modules", "Copying the whole folder and editing it"],
        2,
        "CLI workspaces share one backend, so the docs call them unsuitable for isolation; a separate root per environment that calls shared modules gets its own backend and permissions.",
    ),
    "terms": [
        {"term": "Module", "plain": "A folder of .tf files. Another folder can call it with a module block, like a function."},
        {"term": "Root module", "plain": "The folder where you run terraform; it calls child modules and owns the state."},
        {"term": "Child module", "plain": "A folder called from a module block, with variables as inputs and outputs as return values."},
        {"term": "Module source", "plain": "Where a module lives: a local path, a registry address or a git URL."},
        {"term": "Workspace", "plain": "A second, separate state for the same folder of code, chosen with terraform workspace."},
        {"term": "terraform test", "plain": "Terraform's test runner. It runs run blocks from .tftest.hcl files and checks assert conditions."},
        {"term": "Mock provider", "plain": "A fake provider in tests that invents computed values, so tests create nothing real."},
    ],
    "sections": SECTIONS,
    "analogy": "A module is like an architect's house plan. The same plan builds many houses on different plots, and each owner picks a few options, such as the paint colour and the size of the garage. The comparison breaks in one place: changing the plan does not touch houses already built, but changing a module changes every stack that uses it on the next apply.",
    "diagram": D28,
    "diagram_caption": "infra/local calls the hello-stack module twice. Same code, different names and ports, two separate stacks.",
    "worked": WORKED,
    "code": [
        code("hcl", "infra/modules/hello-stack/versions.tf", lab("infra/modules/hello-stack/versions.tf"), "cd infra/modules/hello-stack && terraform init"),
        code("hcl", "infra/modules/hello-stack/variables.tf", lab("infra/modules/hello-stack/variables.tf"), "terraform validate"),
        code("hcl", "infra/modules/hello-stack/main.tf", lab("infra/modules/hello-stack/main.tf"), "terraform validate"),
        code("hcl", "infra/modules/hello-stack/outputs.tf", lab("infra/modules/hello-stack/outputs.tf"), "terraform validate"),
        code("hcl", "infra/modules/hello-stack/tests/hello_stack.tftest.hcl", lab("infra/modules/hello-stack/tests/hello_stack.tftest.hcl"), "terraform init && terraform test"),
        code("hcl", "infra/local/main.tf (Day 28 version: two stacks)", lab("infra/local/main.tf"), "terraform init && terraform plan"),
        code("hcl", "infra/local/variables.tf (Day 28 version)", lab("infra/local/variables.tf"), "terraform validate"),
        code("hcl", "infra/local/moved.tf", lab("infra/local/moved.tf"), "terraform plan"),
        code("hcl", "infra/local/outputs.tf (Day 28 version)", lab("infra/local/outputs.tf"), "terraform apply && terraform output"),
        code("hcl", "~/code/tf-modules/modules/site/main.tf (labs/terraform-practice/modules)", practice("modules/modules/site/main.tf"), "cd envs/dev && terraform init"),
        code("hcl", "~/code/tf-modules/envs/dev/main.tf (envs/prod differs only in name, port and message)", practice("modules/envs/dev/main.tf"), "terraform init && terraform apply"),
    ],
    "commands": [
        cmd("terraform init", "Also installs modules: run it after adding or changing any module block."),
        cmd("terraform init -upgrade", "Move modules and providers to the newest versions your constraints allow."),
        cmd("terraform -chdir=envs/dev plan", "Run a command in another folder without cd."),
        cmd("terraform state list", "List addresses, including module ones like module.dev.docker_container.app."),
        cmd("terraform test", "Run every .tftest.hcl file in this folder and its tests folder."),
        cmd("terraform test -verbose", "Also print the plan or state of each run block."),
        cmd("terraform fmt -recursive", "Format this folder and every subfolder, modules included."),
        cmd("terraform validate", "Check syntax, types and references, offline."),
        cmd("terraform workspace new qa", "Create a workspace with its own empty state and switch to it."),
        cmd("terraform workspace list", "List workspaces; a star marks the current one."),
        cmd("terraform workspace select default", "Switch back to the default workspace."),
        cmd("terraform workspace delete qa", "Delete a workspace whose state is empty."),
        cmd("tflint --init", "Download the tflint plugins named in .tflint.hcl."),
        cmd("tflint --recursive", "Lint every folder below this one."),
    ],
    "mistake": "Copying a whole folder for each environment and editing the copies by hand. Within weeks dev and prod differ in ways nobody chose, and every fix has to be made twice. Put the shared shape in a module, and keep each environment folder down to a backend and a few module arguments.",
    "real_world": "At PayLoop (made up), the platform team keeps a `service` module in its own git repo and releases it with tags such as v2.3.0. Its `terraform test` suite runs on every pull request. Each product team has `envs/dev` and `envs/prod` folders that call the module with `?ref=` pinned. An upgrade goes to dev first, and prod gets the new tag a week later through a one-line pull request.",
    "task": {
        "title": "Turn infra/local into a module used twice",
        "steps": [
            "Create `infra/modules/hello-stack/` with a `versions.tf` that only lists the docker provider. Add a `variables.tf` for the name prefix, host port (with validation), app image, app version, greeting and Redis image ID.",
            "Move the network, the Redis container, the `app_env` local and the app container from `infra/local/main.tf` into the module's `main.tf`. Build every name from `var.name`. Add an `outputs.tf` with the URL, the container names and the network.",
            "In `infra/local`, keep the `docker_image` and the provider. Add `module \"dev\"` with name `hello` and port 8080, passing `docker_image.redis.image_id` as the Redis image. Update `variables.tf` and `outputs.tf` to match.",
            "Run `terraform init`, then `terraform plan`. Count the destroys, and do not apply.",
            "Add `moved.tf` with one `moved` block per resource that moved into `module.dev`. Plan until you see three \"has moved to\" lines and 0 to destroy, then apply. Your visit count should carry on from before.",
            "Add `module \"test\"` with name `hello-test`, port 8082 and its own greeting. Apply, then `curl` both ports.",
            "Copy the test file from the Files section into the module's `tests` folder. From the module folder, run `terraform init` and `terraform test`.",
            "Break a test on purpose: change the app container's name to `${var.name}-app` and run `terraform test` again. Read the diff, then change it back.",
            "From `infra`, run `terraform fmt -recursive`, then `terraform validate` in `local`. Commit everything except `.terraform` folders and state.",
        ],
        "hints": [
            "The moves are `docker_network.app`, `docker_container.redis` and `docker_container.app`, each to the same name under `module.dev.`",
            "Run `terraform test` from `infra/modules/hello-stack`, not from `infra/local`.",
            "If plan says `Module not installed`, you added a module block since your last `terraform init`.",
        ],
        "done_when": "`curl localhost:8080` and `curl localhost:8082` both answer (the second with your test greeting), the plan after adding moved.tf showed 0 to destroy, and `terraform test` printed `Success! 5 passed, 0 failed.`",
    },
    "explain_back": {
        "prompt": "In 3 to 4 sentences, explain to a teammate how one module can create both a dev and a test stack without them colliding. Mention inputs, outputs and resource addresses.",
        "answer": "The module is one folder of code with variables as its inputs and outputs as its return values. The root calls it twice, as `module.dev` and `module.test`, with different inputs such as the name prefix and the port. Every name inside is built from the name input, so Docker gets `hello-web` and `hello-test-web`, and each call's resources get their own addresses in the state. Changing the module's code changes both stacks on the next apply, which is the point.",
    },
    "recap": [
        "Every folder is a module; the root calls child modules with `module` blocks and `source`.",
        "Variables are a module's API, outputs its return values, and resources get addresses like `module.dev.docker_container.app`.",
        "Run `terraform init` after adding a module; pin every remote module's version.",
        "Keep modules focused and roots thin: providers, module calls and wiring.",
        "Prefer a folder per long-lived environment over CLI workspaces when credentials differ.",
        "`terraform test` runs `.tftest.hcl` files; `mock_provider` makes tests free and fast.",
    ],
    "check": [
        mcq("Inside the module called `test`, there is `resource \"docker_container\" \"app\"`. What is that container's address in the state?",
            ["docker_container.app", "module.test.docker_container.app", "hello-stack.docker_container.app", "test.app"],
            1, "Resources inside a module call get the `module.<call name>.` prefix in front of their normal address."),
        mcq("You add a new `module` block and run `terraform plan` straight away. What happens?",
            ["Plan works, because local modules need nothing", "Plan downloads the module by itself", "Plan creates the module's folder for you", "Plan stops and asks you to run terraform init"],
            3, "Plan fails with `Module not installed` until `terraform init` records the new module."),
        mcq("A test file has a `run` block with no `command` and no mock provider. What happens when you run `terraform test`?",
            ["It creates real resources, checks them, then destroys them", "It only plans, because tests never apply", "It fails, because command is required", "It applies and leaves the resources running"],
            0, "The default command is apply, so Terraform creates real infrastructure for the test and destroys it when the file finishes."),
    ],
    "interview": [
        {"q": "What is a Terraform module, and when do you write one?",
         "a": "A module is a folder of Terraform code with input variables and outputs, called from another configuration with a `module` block. I write one when the same shape of infrastructure appears more than once, such as a service stack per environment, or when a team wants a reviewed, versioned building block. I keep modules focused on one unit of ownership, not one resource. I pin remote modules to a version and test shared ones with `terraform test`."},
        {"q": "How do you manage dev, staging and prod with Terraform?",
         "a": "I put the shared shape into modules and give each long-lived environment its own small root folder with its own backend, state and credentials. The differences live in a few module arguments or a small tfvars file per folder. HashiCorp's docs say CLI workspaces share a backend and are not a suitable isolation mechanism for environments with different access controls. Changes roll through dev first, then prod, often by bumping a module version."},
        {"q": "How do you test Terraform code?",
         "a": "First the cheap checks: `terraform fmt -check`, `terraform validate` and tflint, plus a security scanner such as trivy. Then `terraform test` with `.tftest.hcl` files: plan-mode runs for logic and naming, `expect_failures` for validation rules, and mock providers so the tests need no cloud account. For important modules I add an apply-mode test against a real sandbox account, which creates and destroys real resources. And every pull request still gets a human reading the real plan."},
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Once other teams use your module, it becomes a product with users, and changes need the care you give a library.\n\n"
            "Version it with git tags and semantic versioning. A new optional input is a minor version, like v1.3.0. A renamed input, a removed output, or anything that replaces resources is a major version, like v2.0.0. Callers pin with `?ref=v1.3.0` in a git source, or with `version = \"~> 1.3\"` for a registry module. HashiCorp's style guide names registry module repos `terraform-<PROVIDER>-<NAME>`, such as `terraform-aws-vpc`.\n\n"
            "Refactors inside a module need `moved` blocks too, and they belong in the module itself. Say version 2 renames `docker_container.app` to `docker_container.web`. A `moved` block inside the module turns that into a move for every caller, on their next apply. The refactoring docs strongly recommend keeping old `moved` blocks in shared modules, because removing one breaks anyone still upgrading from an older version.\n\n"
            "Test where your users will feel it:\n"
            "- Plan-mode tests with a mock provider for naming, validation and wiring. They are fast and need no credentials.\n"
            "- An apply-mode test against a sandbox account for anything subtle, such as IAM policies. It costs a little time and money, so many teams run it nightly instead of on every push.\n"
            "- An `examples` folder with a small root that calls the module. It doubles as documentation and as an extra check that the module really works from the outside.\n\n"
            "Two bigger tools exist once a company has many environments. HCP Terraform has Stacks, which describe repeated deployments of the same components with `component` and `deployment` blocks, each deployment with its own state. Some teams use a wrapper tool to generate many small roots from one template. Neither is needed for this course. Folders, modules and pinned versions carry you a long way, and they work the same in Terraform and OpenTofu."
        ),
    },
    "sources": [
        {"title": "Modules overview", "url": HC + "language/modules"},
        {"title": "Workspaces", "url": HC + "cli/workspaces"},
        {"title": "Tests", "url": HC + "language/tests"},
        {"title": "Terraform style guide", "url": HC + "language/style"},
    ],
}
