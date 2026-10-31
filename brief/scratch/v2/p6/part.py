from common import *

INTRO = (
    "Up to now you made containers by typing commands. From here on you describe infrastructure in files, and Terraform makes the real world match them. "
    "Four days run on Docker on your laptop and take the language, state and modules slowly, with real plans to read. "
    "The fifth day takes the same skills to AWS and GitHub Actions, and that part is optional."
)

RECAP = [
    "IaC keeps infrastructure in reviewed, versioned files; Terraform is declarative, so a second apply changes nothing.",
    "The loop is init, plan, apply, destroy. Read every plan, and look for `forces replacement` before you type yes.",
    "HCL is typed: variables with validation, locals, outputs, for expressions and functions, all testable in `terraform console`.",
    "`for_each` keys copies by name; `count` keys them by position, so removing an item shifts and replaces later copies.",
    "State maps addresses to real objects and holds secrets in plain text; keep it in a locked remote backend, never in git.",
    "`moved`, `import` and `removed` blocks change state through reviewed plans; refresh-only mode deals with drift.",
    "Modules package a shape you call many times; long-lived environments get their own root folders, and `terraform test` checks modules.",
    "In CI: cheap checks first, plan on pull requests, apply on main after approval, OIDC instead of keys, and scanners pinned by digest or SHA.",
]

FLASHCARDS = [
    {"front": "What does `-/+` mean in a Terraform plan?", "back": "Replace: destroy the object, then create a new one."},
    {"front": "What does `terraform init` do?", "back": "Downloads providers and modules, sets up the backend, and writes the lock file."},
    {"front": "Which do you commit: `.terraform.lock.hcl`, `.terraform/` or `terraform.tfstate`?", "back": "Only the lock file. Never the `.terraform/` folder or the state."},
    {"front": "Why does OpenTofu exist?", "back": "HashiCorp moved Terraform to the BSL in 2023, so the community forked the last open source version."},
    {"front": "Where can a variable get its value, from weakest to strongest?", "back": "Default, `TF_VAR_` environment variable, `terraform.tfvars`, `*.auto.tfvars`, then `-var` and `-var-file`."},
    {"front": "How do you try out an expression quickly?", "back": "`terraform console`, or `echo 'EXPR' | terraform console` for one expression."},
    {"front": "What does `for_each` accept?", "back": "A map, or a set of strings. Wrap a list in `toset()`."},
    {"front": "Why prefer `for_each` over `count` for named things?", "back": "Copies are keyed by name, so removing one destroys only that copy. `count` copies shift and get replaced."},
    {"front": "Does `sensitive = true` keep a value out of the state?", "back": "No. It only hides the value in output. The state still holds it in plain text."},
    {"front": "How do you rename a resource without rebuilding it?", "back": "Add a `moved` block with `from` (old address) and `to` (new address)."},
    {"front": "Does `terraform state rm` delete the real object?", "back": "No. Terraform only forgets it; the object keeps running."},
    {"front": "What two arguments does an `import` block need?", "back": "`to`, the resource address, and `id`, the provider's ID for the object."},
    {"front": "What does `terraform apply -refresh-only` change?", "back": "Only the state. No real object changes, and the code still wins on the next normal apply."},
    {"front": "What does `use_lockfile = true` do in the S3 backend?", "back": "It writes a `.tflock` file next to the state, so only one run can change the state at a time."},
    {"front": "What is the address of resource `docker_container.app` inside `module \"dev\"`?", "back": "`module.dev.docker_container.app`."},
    {"front": "Why are CLI workspaces a poor fit for separating dev and prod?", "back": "They share one backend, so the environments cannot have separate credentials and access rules."},
    {"front": "How does a `terraform test` run avoid creating real resources?", "back": "With `command = plan`, or with a `mock_provider` block."},
    {"front": "What must a GitHub Actions job have to ask GitHub for an OIDC token?", "back": "The `id-token: write` permission."},
]

RESOURCES = [
    {"title": "Terraform language documentation", "url": HC + "language", "kind": "docs", "why": "The official reference for every block, expression and function used in this part."},
    {"title": "Get started with Terraform and Docker (HashiCorp tutorials)", "url": HC + "tutorials/docker-get-started", "kind": "docs", "why": "HashiCorp's own short hands-on track with the same Docker provider you used here."},
    {"title": "Terraform style guide", "url": HC + "language/style", "kind": "docs", "why": "HashiCorp's rules for layout, naming, version pinning and what never to commit."},
    {"title": "Introduction to Terraform, with Armon Dadgar (HashiCorp)", "url": "https://www.youtube.com/watch?v=ZFLWA1kQ3ls", "kind": "watch", "why": "A short whiteboard talk by HashiCorp's co-founder on what Terraform is for."},
    {"title": "Terraform explained in 15 mins (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=l5k1ai_GBDE", "kind": "watch", "why": "A clear overview of the architecture and the basic commands, good for a second explanation of Day 25."},
    {"title": "Complete Terraform course: from beginner to pro (DevOps Directive)", "url": "https://www.youtube.com/watch?v=7xngnjfIlK4", "kind": "watch", "why": "About two and a half hours on AWS covering variables, modules, environments, testing and CI; it is from 2022, so it locks state with DynamoDB, which is now deprecated."},
    {"title": "Terraform course: automate your AWS cloud infrastructure (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=SLB_c_ayRMo", "kind": "watch", "why": "A longer AWS project if you want more cloud practice after Day 29; destroy as you go."},
    {"title": "Snapshot demo: automating tests for Terraform (HashiCorp)", "url": "https://www.youtube.com/watch?v=oLRtFy6mYSg", "kind": "watch", "why": "A HashiCorp engineer walks through testing strategies and the native test framework from Day 28."},
    {"title": "Terraform: Up & Running, 3rd edition, chapter 5 (Yevgeniy Brikman)", "url": "https://www.oreilly.com/library/view/terraform-up-and/9781098116736/ch05.html", "kind": "read", "why": "The standard Terraform book; this chapter covers loops, conditionals and their gotchas in depth (paid)."},
    {"title": "Terraform best practices (Anton Babenko)", "url": "https://www.terraform-best-practices.com", "kind": "read", "why": "A free book on structuring code, modules and environments from the maintainer of the terraform-aws-modules project."},
    {"title": "Migrating from Terraform to OpenTofu (guide source)", "url": "https://github.com/opentofu/opentofu/blob/main/website/docs/intro/migration/migration-guide.mdx", "kind": "docs", "why": "Read this before switching a real state between the two tools; it starts with backing up state."},
]

QUIZ = [
    mcq("A plan line ends with `# forces replacement`. What will apply do to that resource?",
        ["Edit it in place", "Destroy it and create a new one", "Skip it until next time", "Import it into the state"],
        1, "Terraform cannot change that attribute on the existing object, so it destroys the object and creates a new one."),
    mcq("Which statement about Terraform state is true?",
        ["It is a cache you can delete safely", "Terraform encrypts it on your laptop", "You should commit it so teammates share it", "It can contain secrets in plain text"],
        3, "State stores every attribute, passwords and tokens included, so protect it and keep it in a proper backend."),
    mcq("Two pipeline runs try to apply against the same S3-backed state at the same moment. What stops them from corrupting it?",
        ["The lock file from `use_lockfile = true`", "The `-refresh-only` flag", "Bucket versioning on its own", "The `.terraform.lock.hcl` file"],
        0, "With `use_lockfile = true`, the first run holds a lock file and the second is refused; `.terraform.lock.hcl` only pins provider versions."),
    mcq("What does `[for s in [\"a\", \"b\", \"c\"] : upper(s) if s != \"b\"]` evaluate to?",
        ["[\"A\", \"B\", \"C\"]", "[\"a\", \"c\"]", "[\"A\", \"C\"]", "{\"a\" = \"A\", \"c\" = \"C\"}"],
        2, "The `if` drops \"b\", `upper` changes the rest, and square brackets build a list."),
    mcq("You move three resources into `module.dev`, and the plan says 3 to add and 3 to destroy. What is missing?",
        ["A `terraform init -upgrade`", "An import block for each resource", "`moved` blocks from the old to the new addresses", "A `removed` block for each resource"],
        2, "Without `moved` blocks Terraform sees old addresses vanish and new ones appear; with them the plan shows moves and 0 to destroy."),
    mcq("Which `terraform test` setup checks a module without creating any real resources?",
        ["`command = plan` runs, or a mock provider", "`command = apply` runs with the real provider", "A run block that only calls validate", "A workspace named test"],
        0, "Plan-mode runs create nothing, and a mock provider makes even apply-mode runs fake."),
    mcq("In the lab, the CI role may not change IAM. So how do changes to the role itself get applied?",
        ["By the plan job on pull requests", "By the apply job after approval", "By a nightly drift job", "From your laptop, with your own login"],
        3, "Keeping IAM changes out of CI means a pull request cannot give the pipeline more power."),
    mcq("You applied with `-var host_port=9000` yesterday. Today you run `terraform plan` with no flags and no tfvars file. What do you see?",
        ["No changes, because Terraform remembers 9000", "A plan that moves the app back to the default port", "An error that asks you for host_port", "A plan to destroy everything"],
        1, "Terraform does not remember `-var` values, so today's plan uses the default and proposes to change the port back."),
    mcq("In `infra/local`, the app reaches Redis at the host name `hello-redis`. Which Docker feature makes that work?",
        ["Port mapping with `-p`", "A bind mount", "DNS on a user-defined network", "The HEALTHCHECK instruction"],
        2, "Containers on the same user-defined network find each other by container name through Docker's built-in DNS.", **{"from": "Part 3"}),
    mcq("A job uses `environment: production`, and that environment has a required reviewer. What happens when the job is triggered?",
        ["It runs, then asks for a review afterwards", "It fails, because environments need secrets", "It runs only on pull requests", "It waits until a reviewer approves it"],
        3, "Required reviewers are a protection rule: the job pauses before it starts until someone approves.", **{"from": "Part 4"}),
]
