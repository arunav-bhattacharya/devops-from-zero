from common import *
from svg import D26

V_DD_LANG = ref("Complete Terraform course: variables, outputs and language features (DevOps Directive)", V_DD, "watch")

SECTIONS = [
    {
        "h": "HCL is configuration with expressions",
        "body": (
            "On Day 25 every value was a literal: a fixed string or number. Real configurations compute values. An expression is any piece of HCL that produces a value: a literal like `8080`, a reference like `var.host_port`, a template like `\"http://localhost:${var.host_port}\"`, or a function call like `upper(\"hi\")`.\n\n"
            "References are how one block reads another. You will use these forms all the time:\n"
            "- `var.NAME` reads an input variable.\n"
            "- `local.NAME` reads a local value.\n"
            "- `TYPE.NAME.ATTRIBUTE` reads a resource, as in `docker_container.redis.name`.\n"
            "- `each.key`, `each.value` and `count.index` exist inside resources that use `for_each` or `count`.\n"
            "- `path.module` is the folder the current `.tf` file lives in.\n\n"
            "HCL looks like a programming language, but it behaves more like a spreadsheet. Nothing runs top to bottom, you never reassign a variable, and there are no loops with side effects. Terraform reads every block, follows the references to build a graph, and works out each value once its inputs are known. That is why the order of blocks in a file does not matter.\n\n"
            "The fastest way to learn expressions is to try them. `terraform console` opens a prompt, like `jshell` or the Kotlin REPL, where you type an expression and see its value. Inside a folder it also knows that folder's variables, locals and state. You can pipe in one expression too: `echo 'upper(\"hi\")' | terraform console`. Every example in this lesson was checked that way."
        ),
        "refs": [
            ref("terraform console command reference", HC + "cli/commands/console", "docs"),
            ref("Expressions overview (Terraform docs)", HC + "language/expressions", "docs"),
        ],
    },
    {
        "h": "Types: from strings to objects",
        "body": (
            "Every value has a type, and Terraform checks types before it touches anything. There are three families:\n"
            "- Primitive types hold one value: `string`, `number` and `bool`.\n"
            "- Collection types hold many values of one type. `list(string)` is ordered, `set(string)` has no order and no duplicates, and `map(number)` has string keys.\n"
            "- Structural types mix types. `object({ name = string, port = number })` has named fields, and `tuple([string, number])` is a fixed row of positions.\n\n"
            "`null` means \"no value\". Setting an argument to `null` is the same as leaving it out.\n\n"
            "Two things surprise newcomers. First, a literal in square brackets is a tuple, not a list, and a literal in braces is an object, not a map. Ask the console for `type([\"b\", \"a\"])` and it says `tuple([string, string])`. Terraform converts it to a list or a map when a variable's type asks for one, so you rarely notice.\n\n"
            "Second, Terraform converts between primitives for you. `\"8080\" + 1` gives `8081`. Put the number 8080 into a `map(string)` and it becomes the string `\"8080\"`. When a conversion is impossible, such as `\"abc\"` where a number belongs, you get an error at plan time, before anything changes.\n\n"
            "Sets matter later in this lesson. `toset([\"b\", \"a\", \"b\"])` gives `[\"a\", \"b\"]`: the duplicate is gone, and Terraform chose the order."
        ),
        "refs": [
            ref("Types and values (Terraform docs)", HC + "language/expressions/types", "docs"),
            V_DD_LANG,
        ],
    },
    {
        "h": "Input variables: defaults, validation and sensitive",
        "body": (
            "A `variable` block declares a setting the folder accepts. Look at `host_port` in the lab's new `variables.tf` in the Files section. It has four parts:\n"
            "- `description` explains the variable to the next person.\n"
            "- `type` rejects wrong values early: `number` here.\n"
            "- `default` makes the variable optional. Without one, Terraform asks you for a value.\n"
            "- `validation` adds your own rule, with a `condition` and an `error_message`.\n\n"
            "Pass `-var host_port=80` and the plan stops before anything runs, with `host_port must be between 1024 and 65535.` Validation is the cheapest place to catch a bad input.\n\n"
            "`sensitive = true` hides a value in plan and apply output, which then shows `(sensitive value)`. It encrypts nothing. The value still lands in the state file in plain text, as Day 27 shows.\n\n"
            "A value can come from several places. When two of them set the same variable, the later one in this list wins. Each step was checked in the console:\n"
            "1. The `default` in the variable block.\n"
            "2. An environment variable, such as `TF_VAR_host_port=9001`.\n"
            "3. A `terraform.tfvars` file, then `terraform.tfvars.json`, loaded automatically.\n"
            "4. Any `*.auto.tfvars` files, in alphabetical order.\n"
            "5. The `-var` and `-var-file` flags, in the order you type them.\n\n"
            "The `-var` flag has a trap: Terraform does not remember it. Apply with `-var host_port=8081` today, plan without it tomorrow, and the plan moves the app back to 8080. Put values you always want in a `.tfvars` file."
        ),
        "refs": [
            ref("Input variables (Terraform docs)", HC + "language/values/variables", "docs"),
            ref("Terraform style guide", HC + "language/style", "docs"),
        ],
    },
    {
        "h": "Locals and outputs",
        "body": (
            "Locals are named expressions inside one folder. You write them in a `locals` block and read them as `local.NAME`. Think of a `val` inside a Kotlin function: computed once, named, and read many times. The lab's `main.tf` now uses one called `app_env` to build the app's settings in one place.\n\n"
            "Use locals to remove repetition or to give a hard expression a name. HashiCorp's style guide says to use them sparingly, because a reader has to jump around to find each one. If a value should change between runs, make it a variable instead.\n\n"
            "Outputs are the folder's return values. Apply prints them at the end, and later you read them again:\n"
            "- `terraform output` prints all of them.\n"
            "- `terraform output -raw url` prints one string without quotes, handy in `curl $(terraform output -raw url)`.\n"
            "- `terraform output -json` prints them for tools like `jq`.\n\n"
            "Outputs matter even more on Day 28. A module, a folder that another folder calls, can hand values back only through outputs. An output can be `sensitive` too, and then the CLI prints `<sensitive>` instead of the value."
        ),
        "refs": [
            ref("Local values (Terraform docs)", HC + "language/values/locals", "docs"),
            ref("Output values (Terraform docs)", HC + "language/values/outputs", "docs"),
        ],
    },
    {
        "h": "Strings, conditionals and for expressions",
        "body": (
            "Most expressions you write are one of four kinds.\n\n"
            "String templates put values into text: `\"http://localhost:${var.host_port}\"`. Inside a string, `%{ if }` and `%{ for }` directives add logic, so `\"%{ for n in [\"a\", \"b\"] }<li>${n}</li>%{ endfor }\"` gives `<li>a</li><li>b</li>`. For text over several lines, a heredoc starts with `<<-EOT` and ends with `EOT`.\n\n"
            "A conditional picks one of two values: `var.greeting == \"\" ? \"app default\" : var.greeting`. Both results must have the same type. The lab uses one to add `GREETING` only when you set it.\n\n"
            "A for expression builds a new collection from an old one. If you know Kotlin's `map`, `filter` and `associateWith`, you already know it:\n"
            "- `[for n in var.names : upper(n)]` is like `names.map { it.uppercase() }`.\n"
            "- `[for n in var.names : n if n != \"bravo\"]` is like `names.filter { it != \"bravo\" }`.\n"
            "- `{for n in var.names : n => length(n)}` is like `names.associateWith { it.length }`.\n\n"
            "Square brackets build a list and braces build a map. A splat is a shortcut for one common case: `local_file.by_count[*].filename` is the list of every copy's `filename`.\n\n"
            "Built-in functions finish the toolbox: `merge`, `lookup`, `join`, `format`, `cidrsubnet`, `try` and many more. You cannot write your own functions. That keeps configurations predictable, and it is also why some expressions grow long."
        ),
        "refs": [
            ref("for expressions (Terraform docs)", HC + "language/expressions/for", "docs"),
            ref("Strings and templates (Terraform docs)", HC + "language/expressions/strings", "docs"),
            ref("Built-in functions (Terraform docs)", HC + "language/functions", "docs"),
        ],
    },
    {
        "h": "Copies with count and for_each, and the trap between them",
        "body": (
            "Expressions transform values. To make several copies of a resource you need a meta-argument, an argument that Terraform itself reads on any resource.\n\n"
            "`count` takes a number. `count = 3` makes three copies with the addresses `local_file.by_count[0]`, `[1]` and `[2]`, and `count.index` tells each copy its number.\n\n"
            "`for_each` takes a map or a set of strings, and each key becomes one copy, with an address like `docker_container.site[\"blue\"]`. Inside the block, `each.key` is the key and `each.value` is the value. A plain list is rejected with `Invalid for_each argument`, so wrap it in `toset()`.\n\n"
            "This trips most people up: the address is the copy's identity. With `count`, the identity is a position. Remove the first name from a list of three, and every later name moves up one place. Copy `[0]` now holds what `[1]` held, so its content changes and it is replaced. The same happens to `[1]`, and `[2]` is destroyed. With `for_each`, the identity is the name, so only the removed copy goes. The worked example shows the real plan.\n\n"
            "The docs give a rule of thumb. Use `count` for nearly identical copies, or as an on-off switch such as `count = var.enabled ? 1 : 0`. Use `for_each` when each copy has its own name or settings. The style guide adds: use both sparingly.\n\n"
            "One more limit applies to both. Terraform must know the count or the keys at plan time, so they cannot come from an attribute that only exists after apply."
        ),
        "refs": [
            ref("The count meta-argument (Terraform docs)", HC + "language/meta-arguments/count", "docs"),
            ref("The for_each meta-argument (Terraform docs)", HC + "language/meta-arguments/for_each", "docs"),
            ref("Terraform tips and tricks: loops, if-statements and gotchas (Gruntwork)", "https://www.gruntwork.io/blog/terraform-tips-tricks-loops-if-statements-and-gotchas", "read"),
        ],
    },
    {
        "h": "Dynamic blocks: a loop inside one resource",
        "body": (
            "`for_each` copies a whole resource. Sometimes you want copies of a block inside one resource instead, such as several `ports` blocks on one container. A `dynamic` block does that:\n\n"
            "`dynamic \"ports\" { for_each = var.port_map  content { internal = tonumber(ports.key)  external = ports.value } }`\n\n"
            "With `port_map = { \"80\" = 8091, \"8080\" = 8092 }`, the plan shows two `ports` blocks, and Docker publishes both ports on one container. Inside `content`, the loop variable is named after the block, so you write `ports.key` and `ports.value`.\n\n"
            "Use dynamic blocks rarely. The docs warn that overuse makes configuration hard to read, and they suggest writing nested blocks out by hand wherever you can. Two `ports` blocks typed out are easier to review than a loop that builds them."
        ),
        "refs": [
            ref("Dynamic blocks (Terraform docs)", HC + "language/expressions/dynamic-blocks", "docs"),
        ],
    },
]

WORKED = {
    "title": "Console experiments, then the count trap",
    "steps": [
        step("Apply the Day 26 `infra/local` files, then open the console in that folder. It knows the variables, the locals and the state, so you can inspect the real values behind `main.tf`. The for expression turns the `app_env` map into Docker's `KEY=value` list.",
             """$ terraform console
> var.host_port
8080
> local.app_env
{
  "APP_VERSION" = "1.0.0"
  "REDIS_HOST" = "hello-redis"
}
> [for key, value in local.app_env : "${key}=${value}"]
[
  "APP_VERSION=1.0.0",
  "REDIS_HOST=hello-redis",
]
> docker_container.web.ports[0].external
8080"""),
        step("Now poke at types. A literal list is a tuple until something converts it. A set drops the duplicate and picks its own order. A string that looks like a number is converted for you.",
             """> type(["b", "a"])
tuple([
    string,
    string,
])
> type(tolist(["b", "a"]))
list(string)
> toset(["b", "a", "b"])
toset([
  "a",
  "b",
])
> "8080" + 1
8081"""),
        step("Try a for expression with a filter, a map built from a map, and a function. Press Ctrl+D or type `exit` to leave the console.",
             """> [for n in ["alpha", "bravo", "charlie"] : upper(n) if n != "bravo"]
[
  "ALPHA",
  "CHARLIE",
]
> { for name, port in { blue = 8101, green = 8102 } : name => "http://localhost:${port}" }
{
  "blue" = "http://localhost:8101"
  "green" = "http://localhost:8102"
}
> merge({ a = 1 }, { b = 2 }, { a = 3 })
{
  "a" = 3
  "b" = 2
}"""),
        step("Copy the `loops` practice folder from the Files section. It makes one file per name twice, once with `count` and once with `for_each`. Apply it and list the addresses: numbers for `count`, names for `for_each`. It uses the `local` provider, so no Docker is needed.",
             """$ cd ~/code/tf-loops && terraform init && terraform apply -auto-approve
Apply complete! Resources: 6 added, 0 changed, 0 destroyed.
$ terraform state list
local_file.by_count[0]
local_file.by_count[1]
local_file.by_count[2]
local_file.by_each["alpha"]
local_file.by_each["bravo"]
local_file.by_each["charlie"]"""),
        step("Plan with alpha removed from the list. Read it slowly. `count` replaces two copies and destroys a third, because every name moved up one position. `for_each` destroys only alpha. Trimmed real output:",
             """$ terraform plan -var='names=["bravo","charlie"]'
  # local_file.by_count[0] must be replaced
      ~ content              = <<-EOT # forces replacement
          - hello alpha
          + hello bravo
  # local_file.by_count[1] must be replaced
          - hello bravo
          + hello charlie
  # local_file.by_count[2] will be destroyed
  # (because index [2] is out of range for count)
  # local_file.by_each["alpha"] will be destroyed
  # (because key ["alpha"] is not in for_each map)
Plan: 2 to add, 0 to change, 4 to destroy."""),
        step("Out of that plan, 3 of the 4 destroys come from `count`, for one removed name. Files are cheap to replace. Containers with data, or cloud servers, are not. Clean up.",
             """$ terraform destroy -auto-approve
Destroy complete! Resources: 6 destroyed."""),
    ],
}

LESSON = {
    "id": "d26",
    "title": "The Terraform language: variables, types and loops",
    "minutes": 50,
    "goal": "By the end you can write Terraform with typed variables, locals, outputs and expressions, try any expression in terraform console, and choose between count and for_each.",
    "guess": mcq(
        "You made three containers with `count` from the list [\"alpha\", \"bravo\", \"charlie\"]. You delete \"alpha\" from the list. What does the next plan do?",
        ["Destroys only the alpha container", "Nothing until you apply twice", "Replaces two copies and destroys a third", "Renames the alpha container to bravo"],
        2,
        "With `count`, each copy is known by its position. Every name after alpha moves up one place, so copies [0] and [1] get new content and are replaced, and [2] is destroyed.",
    ),
    "terms": [
        {"term": "Expression", "plain": "Any piece of HCL that produces a value, such as \"web-${var.name}\" or var.port + 1."},
        {"term": "Input variable", "plain": "A named, typed setting a Terraform folder accepts, read as var.NAME."},
        {"term": "Local value", "plain": "A named expression inside one folder, read as local.NAME, used to avoid repeating yourself."},
        {"term": "Output", "plain": "A value a folder hands back after apply, shown by terraform output."},
        {"term": "for expression", "plain": "An expression that builds a new list or map from an existing one, like map and filter in Kotlin."},
        {"term": "count", "plain": "A meta-argument that makes a number of copies of a resource, known as [0], [1] and so on."},
        {"term": "for_each", "plain": "A meta-argument that makes one copy of a resource per key in a map or set, known as [\"key\"]."},
    ],
    "sections": SECTIONS,
    "analogy": "A Terraform configuration is like a spreadsheet. Variables are input cells, locals and outputs are formula cells, and a formula can refer to any other cell. Change one input and everything that depends on it is worked out again, and you never say in which order. The comparison breaks because some of Terraform's \"cells\" are real containers: a changed formula can replace one.",
    "diagram": D26,
    "diagram_caption": "Remove one name from the list: count copies shift and get replaced, for_each copies keep their names.",
    "worked": WORKED,
    "code": [
        code("hcl", "infra/local/variables.tf (Day 26 version)", day("d26", "infra/local/variables.tf"), "terraform validate"),
        code("hcl", "infra/local/main.tf (Day 26 version: network, Redis and the app)", day("d26", "infra/local/main.tf"), "docker build -t hello-devops:1.0.0 ~/code/hello-devops && terraform apply"),
        code("hcl", "infra/local/outputs.tf (Day 26 version)", day("d26", "infra/local/outputs.tf"), "terraform output -raw url"),
        code("hcl", "~/code/tf-loops/main.tf (labs/terraform-practice/loops)", practice("loops/main.tf"), "terraform init && terraform apply"),
        code("hcl", "~/code/tf-sites/main.tf (labs/terraform-practice/nginx-map; read it after the hands-on)", practice("nginx-map/main.tf"), "terraform init && terraform apply"),
    ],
    "commands": [
        cmd("terraform console", "Open a prompt to try expressions against this folder's variables, locals and state."),
        cmd("echo 'upper(\"hi\")' | terraform console", "Evaluate one expression and exit, handy in scripts."),
        cmd("terraform plan -var host_port=8081", "Set one variable for this run only. Terraform does not remember it."),
        cmd("TF_VAR_host_port=8081 terraform plan", "Set a variable through the environment, weaker than any tfvars file."),
        cmd("terraform plan -var-file=dev.tfvars", "Load variable values from a file you name."),
        cmd("terraform output", "Print every output of this folder."),
        cmd("terraform output -raw url", "Print one output without quotes, for use in other commands."),
        cmd("terraform output -json", "Print all outputs as JSON, for jq and other tools."),
        cmd("terraform state list", "List resource addresses, including [0] and [\"key\"] copies."),
        cmd("terraform plan -var='names=[\"bravo\",\"charlie\"]'", "Pass a list on the command line; the single quotes protect it from the shell."),
        cmd("terraform fmt -check", "Fail if any file is not formatted, without changing files."),
        cmd("terraform validate", "Check types, references and syntax without touching anything."),
    ],
    "mistake": "Using `count` over a list of names, such as servers or sites. It works until someone removes an item from the middle, and then every later copy is replaced. Use `for_each` over a set or map with stable keys from the start. If `count` code already exists, the Go deeper section shows how to switch without destroying anything.",
    "real_world": "At PayLoop (still made up), the list of payment regions lives in one map variable, with a key per region. Adding a region adds one key, and the plan shows only that region's resources. Reviewers send back any pull request that uses `count` over a list of names, because the next removal would replace everything after it.",
    "task": {
        "title": "Three nginx sites from one map with for_each",
        "steps": [
            "Make a folder `~/code/tf-sites` and copy the `terraform` and `provider` blocks from your Day 25 `main.tf`.",
            "Declare a variable `sites` of type `map(number)` with three entries: blue on 8101, green on 8102 and red on 8103.",
            "Add a `docker_image` for `nginx:1.30-alpine` with `keep_locally = true`.",
            "Add ONE `docker_container` resource with `for_each = var.sites`. Name each container after its key, such as `site-blue`, and publish container port 80 on the entry's port.",
            "Add an output `urls` that uses a for expression to map each site name to `http://localhost:PORT`.",
            "Run init and plan. Predict the summary line first, then apply and `curl` each URL.",
            "Remove red from the map and plan. Check that exactly one container is destroyed, then apply.",
            "Add a `validation` block to `sites` that rejects any port below 1024. Prove it works with `-var='sites={blue=80}'`.",
            "Optional: add an `upload` block that writes `<h1>Hello from KEY</h1>` to `/usr/share/nginx/html/index.html`, so each site names itself.",
            "Run `terraform destroy`.",
        ],
        "hints": [
            "Inside the container block, `each.key` is the site name and `each.value` is its port.",
            "A condition over every value can use `alltrue([for port in values(var.sites) : port >= 1024])`.",
            "The lab's `labs/terraform-practice/nginx-map/main.tf` is one possible answer. Look only after you tried.",
        ],
        "done_when": "`curl -s localhost:8102` answers, `terraform state list` shows `docker_container.site[\"green\"]`, and removing one site planned exactly 1 to destroy.",
    },
    "explain_back": {
        "prompt": "In 3 to 4 sentences, explain to a teammate why removing the first item from a list used with `count` replaces other resources, and how `for_each` avoids it. Mention resource addresses.",
        "answer": "Terraform tracks every copy by its address. With `count`, the address is a position such as `[0]`, so removing the first item shifts every later item down one position. Terraform then sees copies whose settings changed, replaces them, and destroys the last one. With `for_each`, the address is a key such as `[\"bravo\"]`, so removing one key only destroys that one copy.",
    },
    "recap": [
        "Expressions compute values; references like `var.x` and `docker_container.redis.name` also set the order.",
        "Types catch mistakes at plan time: primitives, collections (list, set, map) and structural types (object, tuple).",
        "Variables take values from defaults, `TF_VAR_`, tfvars files and `-var`; later sources win, and `-var` is not remembered.",
        "Locals name expressions, and outputs are a folder's return values.",
        "for expressions transform collections; `count` and `for_each` create copies.",
        "Prefer `for_each` with stable keys, because `count` copies are known by position and shift.",
    ],
    "check": [
        mcq("You export `TF_VAR_host_port=9001`, and `terraform.tfvars` contains `host_port = 9002`. You run `terraform plan` with no flags. Which value does Terraform use?",
            ["9001, because environment variables win", "9002, because the tfvars file wins", "8080, because the default always wins", "None: Terraform asks you to choose"],
            1, "A `terraform.tfvars` file beats a `TF_VAR_` environment variable, and both beat the default."),
        mcq("A variable has type `map(number)`. A teammate passes `{ web = \"8081\" }`, with the port in quotes. What happens at plan time?",
            ["Plan fails, because a string is not a number", "Terraform skips that entry", "The value becomes null", "Terraform converts it to the number 8081"],
            3, "Terraform converts between primitive types when the string really is a number; only something like \"abc\" would fail."),
        mcq("You write `for_each = var.names`, where `names` is a `list(string)`. Plan fails with \"Invalid for_each argument\". What is the usual fix?",
            ["Use `for_each = toset(var.names)`", "Use `count = var.names` instead", "Add `depends_on = [var.names]`", "Mark the variable as sensitive"],
            0, "`for_each` needs a map or a set of strings, and `toset()` turns the list into a set."),
    ],
    "interview": [
        {"q": "When do you use count and when for_each?",
         "a": "Both create several copies of a resource. The `count` argument numbers the copies, so it fits identical copies or an on-off switch like `count = var.enabled ? 1 : 0`. The `for_each` argument keys each copy by a map key or set value, so it fits copies with their own names or settings. I default to `for_each` for anything named, because removing an item from a `count` list shifts the later copies and Terraform replaces them."},
        {"q": "How do you give one Terraform configuration different values per environment?",
         "a": "I declare typed input variables with validation, and keep the per-environment values in files such as `dev.tfvars` and `prod.tfvars`, passed with `-var-file`. Secrets do not go in those files; they come from a secret store or CI at run time. Each environment also needs its own state, so I usually give each one its own root folder that calls shared modules. I avoid `-var` for anything permanent, because Terraform does not remember it."},
        {"q": "What is the difference between a variable, a local and an output?",
         "a": "A variable is an input that the caller or the command line can set. A local is a named expression inside the folder that nobody outside can set, used to avoid repeating a long expression. An output is a value the folder hands back, printed after apply and readable by a parent module or a script. In function terms: parameters, local vals and return values."},
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Say you already have resources built with `count`, and you want to move to `for_each` before the index trap bites. Simply editing the block is not enough. Terraform sees `[0]`, `[1]` and `[2]` vanish and `[\"alpha\"]`, `[\"bravo\"]` and `[\"charlie\"]` appear, so it plans to destroy three and create three. The real plan says `local_file.greeting[0] will be destroyed (because resource does not use count)` and ends with `Plan: 3 to add, 0 to change, 3 to destroy.`\n\n"
            "The fix is a `moved` block per copy. It tells Terraform that an object changed address and nothing else:\n\n"
            "`moved { from = local_file.greeting[0]  to = local_file.greeting[\"alpha\"] }`\n\n"
            "Add one for `[1]` to `\"bravo\"` and one for `[2]` to `\"charlie\"`. The plan now shows `local_file.greeting[0] has moved to local_file.greeting[\"alpha\"]`, three times, and `Plan: 0 to add, 0 to change, 0 to destroy.` Apply, and the state uses the new addresses. Day 27 covers `moved` properly. You will use it for renames and for moving code into modules.\n\n"
            "Two details make this safe:\n"
            "- You must write one block per copy. A `moved` block cannot loop, because Terraform has to know every move before it plans.\n"
            "- The old index and the new key must point at the same real object. Check the plan: each line should say \"has moved to\", and nothing should say \"must be replaced\".\n\n"
            "The \"known at plan time\" rule from the count section also explains a common error. Imagine you want one container per network, and the network IDs only exist after apply. If you write `for_each = toset(docker_network.all[*].id)`, plan fails, because Terraform cannot know the keys yet. Build keys from values in your own code instead, such as the network names in a variable, and look up the IDs inside the block. Keys from your own code are known at plan time. IDs are not.\n\n"
            "Finally, `for_each` also works on whole modules. `module \"site\" { for_each = var.sites ... }` makes one copy of a module per key, with addresses like `module.site[\"blue\"]`. Day 28 builds a module and calls it more than once."
        ),
    },
    "sources": [
        {"title": "for expressions", "url": HC + "language/expressions/for"},
        {"title": "The count meta-argument", "url": HC + "language/meta-arguments/count"},
        {"title": "The for_each meta-argument", "url": HC + "language/meta-arguments/for_each"},
        {"title": "Input variables", "url": HC + "language/values/variables"},
    ],
}
