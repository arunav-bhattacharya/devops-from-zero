#!/usr/bin/env python3
"""Human-writing pass (v3, blog mode) for content/p6.json (Part 6, Terraform, d25 to d29).
Loads the current JSON, rewrites prose fields only, and writes it back.
Each edit is either a substring rewrite (old text must occur exactly once) or a full field replacement."""
import json
import pathlib

PATH = pathlib.Path("/home/user/devops-from-zero/content/p6.json")
D = json.loads(PATH.read_text())
LESSONS = {L["id"]: L for L in D["lessons"]}


def _node(lid, path):
    obj = D if lid is None else LESSONS[lid]
    for k in path[:-1]:
        obj = obj[k]
    return obj, path[-1]


def sub(lid, path, old, new):
    obj, k = _node(lid, path)
    cur = obj[k]
    n = cur.count(old)
    assert n == 1, f"{lid} {path}: expected 1 match, found {n}: {old[:60]!r}"
    obj[k] = cur.replace(old, new)


def put(lid, path, new):
    obj, k = _node(lid, path)
    assert isinstance(obj[k], str)
    obj[k] = new


# ---------------------------------------------------------------- part level
put(None, ("intro",),
    "Up to now you made containers by typing commands. In this part you describe infrastructure in files, "
    "and Terraform makes the real world match them. The first four days run on Docker on your laptop and cost nothing. "
    "They go slowly through the language, state and modules, with real plans to read. "
    "Day 29 takes the same skills to AWS and GitHub Actions, and you can skip it.")

put(None, ("recap", 0), "IaC keeps infrastructure in reviewed, versioned files. Terraform is declarative, so a second apply changes nothing.")
put(None, ("recap", 2), "HCL has types, variables with validation, locals, outputs, for expressions and functions. Try any expression in `terraform console`.")
put(None, ("recap", 4), "State maps addresses to real objects and holds secrets in plain text, so it lives in a locked remote backend and never in git.")
put(None, ("recap", 5), "`moved`, `import` and `removed` blocks change state through plans you review. Refresh-only mode shows drift and copies it into state.")
put(None, ("recap", 6), "A module packages a shape you call many times. Each long-lived environment gets its own root folder, and `terraform test` checks the modules.")

put(None, ("flashcards", 10, "back"), "No. Terraform forgets it, and the object keeps running.")

put(None, ("resources", 0, "why"), "The official reference. Every block, expression and function in this part has a page here.")
put(None, ("resources", 4, "why"), "A quick tour of the architecture and the basic commands. Watch it if Day 25 needs a second explanation.")
put(None, ("resources", 5, "why"),
    "About two and a half hours on AWS: variables, modules, environments, testing and CI. "
    "It is from 2022, so it still locks state with DynamoDB, which is now deprecated.")
put(None, ("resources", 6, "why"), "A longer AWS project for more cloud practice after Day 29. Destroy what you build as you go.")
put(None, ("resources", 8, "why"), "The standard Terraform book (paid). Chapter 5 goes deep on loops, conditionals and the ways they go wrong.")
put(None, ("resources", 10, "why"), "Read this before you move a real state between the two tools. Its first step is a backup of the state.")

put(None, ("quiz", 2, "why"),
    "With `use_lockfile = true`, the first run holds a lock file and the second is refused. "
    "`.terraform.lock.hcl` has nothing to do with it: that file pins provider versions.")
put(None, ("quiz", 4, "why"),
    "Without `moved` blocks, Terraform sees the old addresses vanish and new ones appear. "
    "With them, the plan shows three moves and 0 to destroy.")
put(None, ("quiz", 6, "why"),
    "You apply IAM changes from your laptop, with your own login. "
    "Keeping them out of CI means a pull request cannot give the pipeline more power.")

# ---------------------------------------------------------------- d25
sub("d25", ("sections", 0, "body"),
    "The files live in git next to your app, so infrastructure gets the same treatment as your Kotlin code:",
    "The files live in git next to your app, so a change to infrastructure goes through the same pull request flow as your Kotlin code:")
sub("d25", ("sections", 0, "body"),
    "The short version: your infrastructure gets a pull request. This part of the course uses Terraform, the most widely used IaC tool. "
    "You practise on Docker on your laptop for four days, so nothing costs money. Day 29 is the optional trip to a real cloud.",
    "This part of the course uses Terraform, the most widely used IaC tool. For four days you practise on Docker on your laptop, "
    "so nothing costs money. Day 29 goes to a real cloud, and you can skip it.")

sub("d25", ("sections", 1, "body"),
    "Terraform is similar. You write the end state, and Terraform makes a plan of API calls to get there. "
    "Under the hood it still runs steps in order. You just do not write them.",
    "Terraform works the same way. You write the end state, and Terraform makes a plan of API calls to get there. "
    "It still runs steps in order. You just never write them down.")

sub("d25", ("sections", 2, "body"),
    "Terraform can configure servers too, but that is not where it shines.",
    "Terraform can set up software on servers too, but that is not its strength.")

sub("d25", ("sections", 4, "body"),
    "Plan is safe to run any time, so run it often. People sometimes worry that plan changes things. It does not. Apply is the only step that does.\n\n"
    "There is one gap to know about. Apply makes a new plan, and the world may have changed since your last plan. For a laptop that does not matter.",
    "Plan is safe to run any time, so run it often. People sometimes worry that plan changes things, but only apply does.\n\n"
    "Apply makes its own new plan, and the world may have changed since you last ran plan. On a laptop that gap does not matter.")
sub("d25", ("sections", 4, "body"),
    "`terraform destroy` deletes everything in this folder's state, not only what you added today.",
    "`terraform destroy` deletes everything in this folder's state, whenever it was added.")

sub("d25", ("sections", 5, "body"),
    "Three more things show up all the time. `(known after apply)` means the provider will only know the value once the object exists, "
    "like a container's ID. That is normal, not an error. `# (50 unchanged attributes hidden)` means Terraform left out the lines that do not change. "
    "The last line is the summary, such as `Plan: 1 to add, 0 to change, 1 to destroy.`",
    "You will also see these in almost every plan:\n"
    "- `(known after apply)`: the provider learns the value once the object exists, like a container's ID. That is normal.\n"
    "- `# (50 unchanged attributes hidden)`: Terraform left out the lines that do not change.\n"
    "- The summary on the last line, such as `Plan: 1 to add, 0 to change, 1 to destroy.`")
sub("d25", ("sections", 5, "body"),
    "So build one habit now. Before you type `yes`, read the summary line and search the plan for `forces replacement`.",
    "Build the habit now, while the containers are toys: before you type `yes`, read the summary line and search the plan for `forces replacement`.")

put("d25", ("analogy",),
    "Terraform works like a thermostat. You set the temperature you want, and it turns the heating on or off until the room matches. "
    "You never tell it \"heat for ten minutes\", and setting the same temperature twice does nothing. "
    "A thermostat checks the room all the time, while Terraform only looks when you run plan or apply. "
    "A change made by hand stays in place until your next run.")

sub("d25", ("worked", "steps", 1, "say"),
    "The real plan lists about 40 attributes for the container; these are the ones worth reading.",
    "The real plan lists about 40 attributes for the container, and these are the ones to read.")
sub("d25", ("worked", "steps", 3, "say"),
    "This is idempotence in action: a second `docker run` would have failed.",
    "That is idempotence. A second `docker run` would have failed, because the name was taken.")

put("d25", ("mistake",),
    "You type `yes` without reading the plan, because the edit was one word. That one word can turn into `-/+`, "
    "and replacing a database means losing its data. Read the summary line and search for `forces replacement` every time, "
    "most of all when you are sure the change is small.")

put("d25", ("real_world",),
    "Changes made by clicking leave no review and no record, so on a payments team nobody creates production infrastructure that way. "
    "Every change is a pull request with the Terraform plan attached, and a second engineer reads the plan before anyone applies it. "
    "People still open the console to look around, or during an incident. Whatever they change by hand shows up in the next plan.")

put("d25", ("check", 2, "why"), "Destroy only removes what this folder's state tracks, and Terraform never learned about `db`.")

sub("d25", ("deeper", "body"),
    "Gradle users can think of it as a dependency lock that is on by default.",
    "If you know Gradle's dependency locking, this is the same idea, switched on by default.")

# ---------------------------------------------------------------- d26
sub("d26", ("sections", 1, "body"),
    "Sets matter later in this lesson. `toset([\"b\", \"a\", \"b\"])` gives `[\"a\", \"b\"]`: the duplicate is gone, and Terraform chose the order.",
    "You will need sets for `for_each` later in this lesson. `toset([\"b\", \"a\", \"b\"])` gives `[\"a\", \"b\"]`: the duplicate is gone, and Terraform picked the order.")

sub("d26", ("sections", 3, "body"),
    "Think of a `val` inside a Kotlin function: computed once, named, and read many times.",
    "A local works like a `val` inside a Kotlin function: you compute it once and read it by name as often as you like.")
sub("d26", ("sections", 3, "body"),
    "Outputs matter even more on Day 28. A module, a folder that another folder calls, can hand values back only through outputs.",
    "Day 28 needs outputs even more, because a module (a folder that another folder calls) can hand values back only through outputs.")

sub("d26", ("sections", 4, "body"),
    "Built-in functions finish the toolbox: `merge`,",
    "The fourth kind is the built-in functions: `merge`,")

sub("d26", ("sections", 5, "body"),
    "This trips most people up: the address is the copy's identity.",
    "Slow down for this part. A copy's address is its identity, and the two meta-arguments build addresses in different ways.")
sub("d26", ("sections", 5, "body"),
    "The docs give a rule of thumb.",
    "The docs give simple advice.")

put("d26", ("analogy",),
    "A Terraform configuration is like a spreadsheet. Variables are input cells, locals and outputs are formula cells, "
    "and a formula can refer to any other cell. Change one input and everything that depends on it is worked out again, "
    "and you never say in which order. In a spreadsheet, a changed formula only redraws a number. "
    "In Terraform some \"cells\" are real containers, and a changed formula can replace one.")

put("d26", ("mistake",),
    "`count` over a list of names, such as servers or sites, works until someone removes an item from the middle. "
    "Then every later copy is replaced. Use `for_each` over a set or map with stable keys from the start. "
    "If `count` code already exists, the Go deeper section shows how to switch without destroying anything.")

put("d26", ("real_world",),
    "A payments product that runs in several regions keeps the list of regions in one map variable, with a key per region. "
    "Adding a region adds one key, and the plan shows only that region's resources. "
    "Reviewers send back any pull request that uses `count` over a list of names, because the next removal would replace everything after it.")

put("d26", ("recap", 0), "Expressions compute values, and references like `var.x` and `docker_container.redis.name` also set the order.")
put("d26", ("recap", 4), "for expressions transform collections, while `count` and `for_each` make copies of a resource.")

put("d26", ("check", 1, "why"), "The string \"8081\" really is a number, so Terraform converts it. Only something like \"abc\" would fail.")

sub("d26", ("interview", 1, "a"),
    "Secrets do not go in those files; they come from a secret store or CI at run time.",
    "Secrets stay out of those files and come from a secret store or CI at run time.")

sub("d26", ("deeper", "body"),
    "Simply editing the block is not enough.",
    "Editing the block alone is not enough.")
sub("d26", ("deeper", "body"),
    "Finally, `for_each` also works on whole modules.",
    "`for_each` works on whole modules too.")

# ---------------------------------------------------------------- d27
put("d27", ("guess", "why"),
    "Terraform knows what it owns only through the state, so without it every resource looks new and apply tries to create them all. "
    "With Docker that fails on taken names, and in a cloud you can end up with duplicates.")

sub("d27", ("sections", 0, "body"),
    "Once you see the three pictures, the rest of this lesson falls into place, because each tool fixes one link between them:",
    "Each tool in the rest of this lesson fixes one link between the three pictures:")

sub("d27", ("sections", 1, "body"),
    "Every attribute means every attribute, secrets included.",
    "Those attributes include secrets.")
sub("d27", ("sections", 1, "body"),
    "So never edit state by hand, never commit it, and treat it like a password file. Read it through commands instead:",
    "Treat the file like a password file: never commit it, and never edit it by hand. Read it through commands instead:")

sub("d27", ("sections", 4, "body"),
    "You also write the matching `resource` block yourself. Then you plan, and here is the part that bites people. "
    "Import does not make your code match reality.",
    "You also write the matching `resource` block yourself, then plan. Read that plan with care, "
    "because import does not make your code match reality.")

sub("d27", ("sections", 5, "body"),
    "The second one is widely misunderstood: it does not make the manual change permanent.",
    "People often expect the second one to make the manual change permanent. It does not.")
sub("d27", ("sections", 5, "body"),
    "The very next normal plan proposed `~ restart = \"always\" -> \"no\"`. The code wins in the end.\n\n"
    "So after drift, decide which side is right:",
    "The very next normal plan proposed `~ restart = \"always\" -> \"no\"`, because the code still wins.\n\n"
    "After drift, you decide which side is right:")

sub("d27", ("sections", 6, "body"),
    "Two copies drift apart, nobody has the full truth, and nothing stops two applies at once.",
    "Two copies drift apart, and nothing stops two applies from running at once.")

put("d27", ("analogy",),
    "State is like the ticket book in a theatre cloakroom. When you hand in a coat, the attendant writes your ticket number next to a hook. "
    "Lose the book and you have a room full of coats, with no way to tell which ones are yours. "
    "A cloakroom book only notes a hook. Terraform's state copies every detail of each object, secrets included, "
    "so you guard it far more closely.")

put("d27", ("mistake",),
    "You rename a resource, or move it into a module, and leave out the `moved` block. In git it looks like a harmless rename. "
    "To Terraform it is a destroy plus a create, and the real object is rebuilt, data and all. "
    "After every refactor, read the plan: you want \"has moved to\" and `0 to destroy`.")

put("d27", ("real_world",),
    "Drift usually starts with a hand fix during an incident. At PayLoop, a payments company made up for this course, "
    "a nightly job runs `terraform plan -refresh-only` and posts any drift to the team chat. "
    "Each environment's state lives in a versioned, locked S3 bucket, and only the pipeline's role may write to it. "
    "The follow-up to a hand change is a pull request that brings the code in line, never a quiet `apply -refresh-only`.")

put("d27", ("recap", 2), "`moved` renames without rebuilding, `import` adopts, and `removed` forgets. You see each of them in the plan.")
put("d27", ("recap", 4), "`apply -refresh-only` updates state only, and the next normal apply still enforces the code.")

put("d27", ("check", 0, "why"), "`sensitive` only hides the value in Terraform's output. The state still stores it as plain text.")
put("d27", ("check", 2, "why"),
    "`state rm` only made Terraform forget. The code still asks for the container, so apply tries to create it and Docker refuses the duplicate name.")

sub("d27", ("deeper", "body"),
    "And whatever is left, protect by protecting the state.",
    "Anything that still ends up in state, you protect by locking down the state itself.")

# ---------------------------------------------------------------- d28
put("d28", ("guess", "why"),
    "CLI workspaces share one backend, so the docs call them unsuitable for isolation. "
    "A separate root per environment that calls shared modules gets its own backend and permissions.")

put("d28", ("terms", 1, "plain"), "The folder where you run terraform. It calls child modules and owns the state.")

sub("d28", ("sections", 0, "body"),
    "You have written modules since Day 25 without the word.",
    "You have written modules since Day 25 without knowing the word.")
sub("d28", ("sections", 0, "body"),
    "Think of a child module as a Kotlin function:",
    "A child module works like a Kotlin function:")
sub("d28", ("sections", 0, "body"),
    "The comparison breaks in one place. A function call is gone when it returns, but a module call lives on in the state.",
    "The difference is what happens afterwards. A function call is gone once it returns, while a module call lives on in the state.")

sub("d28", ("sections", 2, "body"),
    "Remember that a module runs with your permissions and creates real, billed resources.",
    "A module runs with your permissions and creates real, billed resources.")

sub("d28", ("sections", 3, "body"),
    "Free advice from many teams: if your root folder grows past a few hundred lines, look for a module hiding in it.",
    "A rough rule: when a root folder grows past a few hundred lines, part of it probably belongs in a module.")

sub("d28", ("sections", 4, "body"),
    "So most teams use a folder per long-lived environment, with differences kept in a few module arguments.",
    "That is why most teams use a folder per long-lived environment, with differences kept in a few module arguments.")

put("d28", ("analogy",),
    "A module is like an architect's house plan. The same plan builds many houses on different plots, and each owner picks a few options, "
    "such as the paint colour and the size of the garage. Once a house is built, later changes to the plan leave it alone. "
    "A module is different: change it, and every stack that uses it changes on its next apply.")

put("d28", ("diagram_caption",),
    "infra/local calls the hello-stack module twice, with different names and ports, so you get two separate stacks.")

sub("d28", ("worked", "steps", 3, "say"),
    "Two folders, two state files, and no way for a prod apply to touch dev.",
    "Each folder now has its own state file, and a prod apply has no way to touch dev.")
sub("d28", ("worked", "steps", 4, "say"),
    "Applying would fail. Workspaces copy the code, not the differences. Switch back and delete it.",
    "Applying would fail, because the code does not use the workspace name anywhere. Switch back and delete it.")

put("d28", ("mistake",),
    "Each environment starts as a copy of a whole folder, and people edit the copies by hand. "
    "Within weeks dev and prod differ in ways nobody chose, and every fix has to be made twice. "
    "Put the shared shape in a module, and keep each environment folder down to a backend and a few module arguments.")

put("d28", ("real_world",),
    "Once several product teams need the same service setup, copying folders stops working. "
    "A platform team keeps one `service` module in its own git repo, releases it with tags such as v2.3.0 "
    "and runs its `terraform test` suite on every pull request. "
    "Product teams call it from their `envs/dev` and `envs/prod` folders with `?ref=` pinned. "
    "An upgrade goes to dev first, and prod gets the new tag a week later through a one-line pull request.")

sub("d28", ("explain_back", "answer"),
    "Changing the module's code changes both stacks on the next apply, which is the point.",
    "One change to the module's code reaches both stacks on the next apply, so a fix is made once.")

put("d28", ("recap", 0), "Every folder is a module. The root calls child modules with `module` blocks and `source`.")
put("d28", ("recap", 5), "`terraform test` runs `.tftest.hcl` files, and `mock_provider` makes those tests free and fast.")

sub("d28", ("deeper", "body"),
    "It doubles as documentation and as an extra check that the module really works from the outside.",
    "It is documentation, and also a check that the module works when someone calls it from outside.")
sub("d28", ("deeper", "body"),
    "Neither is needed for this course. Folders, modules and pinned versions carry you a long way, and they work the same in Terraform and OpenTofu.",
    "You need neither for this course. It sticks to folders, modules and pinned versions, which work the same in Terraform and OpenTofu.")

# ---------------------------------------------------------------- d29
sub("d29", ("sections", 0, "body"),
    "Also, do not create an AWS Organization on a learning account:",
    "Do not create an AWS Organization on a learning account either:")

sub("d29", ("sections", 4, "body"),
    "A few more settings are worth spotting:",
    "Look for these settings in the file as well:")

put("d29", ("analogy",),
    "OIDC works like a hotel key card. At the front desk (GitHub) you prove who you are, and you get a card that opens one room "
    "(the IAM role) and stops working at checkout. Nobody carries a master key that works forever. "
    "A real hotel checks your passport in person, though, and AWS never sees you at all. "
    "It only trusts GitHub's signature, so the trust policy must name exactly which repo may get a card.")

put("d29", ("real_world",),
    "Where auditors check every production change, engineers get read-only access to production. "
    "Infrastructure changes go through a pull request with the plan posted for review. "
    "Only the pipeline's role can apply, and only after a second person approves. "
    "When the team accepts a scanner finding, the reason goes next to it, so auditors can see each decision.")

put("d29", ("task", "hints", 2),
    "If `terraform destroy` fails on the bucket, check that `force_destroy = true` is still in `main.tf`. Versioned buckets keep old file versions.")

put("d29", ("recap", 5),
    "Scanners such as trivy, tflint and checkov give advice, and you decide what to fix. Pin the scanner itself by digest or SHA.")

PATH.write_text(json.dumps(D, ensure_ascii=False, indent=1) + "\n")
print("wrote", PATH)
