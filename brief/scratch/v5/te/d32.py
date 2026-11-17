from common import apply

S0 = """
Last time, every value in our file was typed in by hand: the name `tf-web`, the port 8090. A typed-in value like that is called a literal. A spreadsheet shows the other way. You type numbers into some cells, and other cells hold formulas such as "price times quantity". Change a price, and every cell that depends on it updates.

Terraform files work the same way. An expression is any piece of HCL (Terraform's language) that produces a value. Here are four shapes it can take:
- A literal, such as `8080`.
- A reference to another value, such as `var.host_port`.
- A template, a piece of text with a value placed inside: `"http://localhost:${var.host_port}"`.
- A function call, such as `upper("hi")`. A function is a ready-made tool that takes values and gives one back; `upper` turns text into capital letters.

References are how one block reads another. You will meet each of these forms in this lesson:
- `var.NAME` reads an input variable.
- `local.NAME` reads a local value.
- `TYPE.NAME.ATTRIBUTE` reads a resource, as in `docker_container.redis.name`.
- `each.key`, `each.value` and `count.index` exist inside resources that use `for_each` or `count`.
- `path.module` is the folder the current `.tf` file lives in.

HCL looks like a programming language, but it behaves like that spreadsheet. Nothing runs from top to bottom, you never change a value once it is set, and there are no loops that do things as they go. Terraform reads every block and follows the references to build a graph, a map of which value depends on which. Then it works out each value once its inputs are known. That is why the order of blocks in a file does not matter.

The picture has one limit. In a spreadsheet, a changed formula only redraws a number. In Terraform, some "cells" are real containers, and a changed formula can replace one.

The fastest way to learn expressions is to try them. `terraform console` opens a prompt where you type an expression and see its value. Inside a folder, it also knows that folder's variables, locals and state. You can pipe in one expression too (send it in with the `|` sign): `echo 'upper("hi")' | terraform console`. Every example in this lesson was checked that way. Before we compute anything, though, we need to know what kinds of values exist.
"""

S1 = """
Picture a paper form at the post office. The box for your age takes digits, the box for your name takes letters, and a clerk sends the form back if you mix them up. Terraform is that clerk. Every value has a type, and Terraform checks types before it touches anything.

There are three families of types:
- Primitive types hold one value: `string` (text), `number` and `bool` (true or false).
- Collection types hold many values of one type. A `list(string)` keeps its order. A `set(string)` has no order and no duplicates. A `map(number)` pairs names with values, like a phone book.
- Structural types mix types. An `object({ name = string, port = number })` has named fields, and a `tuple([string, number])` is a fixed row of positions.

`null` means "no value". Setting an argument to `null` is the same as leaving it out.

Terraform also converts between primitive types for you. `"8080" + 1` gives `8081`, because the text "8080" really is a number. Put the number 8080 into a `map(string)` and it becomes the text `"8080"`. When a conversion is impossible, such as `"abc"` where a number belongs, you get an error at plan time, before anything changes. That is the clerk sending the form back while it is still on the counter.

You will need sets for `for_each` later in this lesson. `toset(["b", "a", "b"])` gives `["a", "b"]`: the duplicate is gone, and Terraform picked the order. With types in hand, we can let a folder accept settings from outside.
"""

S2 = """
Our running example is the lab app, hello-devops: a tiny web app that answers every visit with a greeting and a count of visits so far. Today the lab's `infra/local` folder runs it next to Redis, the small database that keeps the count. Last time the port was written into `main.tf`, so a teammate who wanted another port had to edit the file.

A `variable` block fixes that. It declares a setting the folder accepts, so the same files work with different values. Look at `host_port` in the lab's new `variables.tf` in the Files section. It has four parts:
- `description` explains the variable to the next person who reads it.
- `type` rejects wrong values early: `number` here.
- `default` makes the variable optional. Without one, Terraform asks you for a value.
- `validation` adds your own rule, with a `condition` and an `error_message`.

Let's try a bad value. A flag is an extra option you type after a command, and `-var` sets a variable for one run. Pass `-var host_port=80`, and the plan stops before anything runs, with `host_port must be between 1024 and 65535.` Validation is the cheapest place to catch a bad input.

`sensitive = true` hides a value in plan and apply output, which then shows `(sensitive value)`. It encrypts nothing. The value still lands in the state file in plain text, as Day 33 shows.

A value can come from several places. When two of them set the same variable, the later one in this list wins. Each step was checked in the console:
1. The `default` in the variable block.
2. An environment variable (a named setting your shell hands to programs), such as `TF_VAR_host_port=9001`.
3. A `terraform.tfvars` file, then `terraform.tfvars.json`, loaded automatically.
4. Any `*.auto.tfvars` files, in alphabetical order.
5. The `-var` and `-var-file` flags, in the order you type them.

The `-var` flag hides a trap: Terraform does not remember it. Apply with `-var host_port=8081` today, plan without it tomorrow, and the plan moves the app back to 8080.

**Terraform forgets `-var` after one run. Put values you always want in a `.tfvars` file.**

Variables bring values in. Next, we name values inside the folder and hand answers back out.
"""

S3 = """
Some values are worked out inside the folder and used in several places. A builder might write "wall height: 2.4 metres" once at the top of the drawing, so every wall can point to it. Terraform calls such a named value a local. You write locals in a `locals` block and read them as `local.NAME`. You work a local out once, then read it by name as often as you like. The lab's `main.tf` now uses one called `app_env`, which gathers the app's settings in one place.

Use locals to remove repetition, or to give a hard expression a name. HashiCorp's style guide says to use them sparingly, because a reader has to jump around to find each one. If a value should change between runs, make it a variable instead.

Outputs go the other way: they are the folder's answers. Apply prints them at the end, and later you can read them again:
- `terraform output` prints all of them.
- `terraform output -raw url` prints one piece of text without quotes, handy in `curl $(terraform output -raw url)`.
- `terraform output -json` prints them as JSON (a common text format for data), for tools like `jq` that read it.

Day 34 needs outputs even more, because a module (a folder that another folder uses) can hand values back only through outputs. An output can be `sensitive` too, and then Terraform prints `<sensitive>` instead of the value. We have values coming in, named and going out. Now let's build new values from them.
"""

S4 = """
Most expressions you write are one of four kinds. The first is the template you have already seen, which places values into text: `"http://localhost:${var.host_port}"`. Terraform can also build longer text over several lines, and the Go deeper section shows how.

The second kind is a conditional, which picks one of two values. In plain words: "if the greeting is empty, use the app default, otherwise use the greeting." In HCL that reads `var.greeting == "" ? "app default" : var.greeting`. The part before `?` is the question, and `:` separates the two answers. Both answers must have the same type. The lab uses a conditional to add `GREETING` only when you set one.

The third kind is a for expression, which builds a new collection from an old one. It goes through each item and either changes it or skips it. With `var.names` set to alpha, bravo and charlie:
- `[for n in var.names : upper(n)]` gives each name in capitals.
- `[for n in var.names : n if n != "bravo"]` keeps every name except bravo.
- `{for n in var.names : n => length(n)}` pairs each name with its number of letters.

Square brackets build a list, and braces build a map. A splat is a shortcut for one common case. `local_file.by_count[*].filename` is the list of every copy's `filename`.

The fourth kind is the built-in functions: `merge`, `lookup`, `join`, `format`, `try` and many more. You cannot write your own functions. That keeps files predictable, and it is also why some expressions grow long. Expressions shape values, but none of them makes a second container. For that, we need copies.
"""

S5 = """
To make several copies of a resource, you use a meta-argument: an argument that Terraform itself reads, on any resource.
- `count` takes a number. `count = 3` makes three copies with the addresses `local_file.by_count[0]`, `[1]` and `[2]`, and `count.index` tells each copy its number.
- `for_each` takes a map or a set of strings, and each key becomes one copy, with an address like `docker_container.site["blue"]`. Inside the block, `each.key` is the key and `each.value` is the value. A plain list is rejected with `Invalid for_each argument`, so wrap it in `toset()`.

Slow down for this part, because it surprises nearly everyone once. Picture a builder making garden sheds for three families on a list: alpha, bravo and charlie. The builder numbers the sheds by their place on the list, so alpha gets shed 0. Then alpha cancels. Now bravo is first on the list, so shed 0 is repainted for bravo, shed 1 for charlie, and shed 2 is knocked down. One cancelled order, three sheds touched.

That is `count`. A copy's address is its identity, and with `count` the identity is a position. Remove the first name, and every later name moves up one place. Copy `[0]` now holds what `[1]` held, so its content changes and it is replaced. The same happens to `[1]`, and `[2]` is destroyed. With `for_each`, the identity is the name, like a name card on each shed. Only the removed copy goes. The worked example shows the real plan: `Plan: 2 to add, 0 to change, 4 to destroy.` Three of those four destroys come from `count`, for one removed name.

**A copy's address is its identity. Give named things names, not numbers.**

The docs give simple advice. Use `count` for nearly identical copies, or as an on-off switch such as `count = var.enabled ? 1 : 0`. Use `for_each` when each copy has its own name or settings. The style guide adds: use both sparingly. Picture a team whose product runs in several regions. The list of regions lives in one map, with a key per region, so adding a region adds one key and the plan shows only that region. Reviewers there send back any `count` over a list of names, because the next removal would replace everything after it.

One more limit applies to both. The plan lists every copy by its address, so Terraform must know the count or the keys before anything exists. They cannot come from an attribute that only exists after apply. `for_each` copies a whole resource. Sometimes you need copies of something smaller, inside one resource.
"""

S6 = """
One container can publish several ports, and each one is a `ports` block inside the container. To make those blocks from a map, you use a `dynamic` block, a loop inside one resource:

`dynamic "ports" { for_each = var.port_map  content { internal = tonumber(ports.key)  external = ports.value } }`

With `port_map = { "80" = 8091, "8080" = 8092 }`, the plan shows two `ports` blocks, and Docker publishes both ports on one container. Inside `content`, the loop variable is named after the block, so you write `ports.key` and `ports.value`.

Use dynamic blocks rarely. The docs warn that overuse makes files hard to read, and they suggest writing nested blocks out by hand wherever you can. Two `ports` blocks typed out are easier to review than a loop that builds them.

Our file has grown up today: it takes settings, names values, hands back answers and makes copies by name. One thing kept coming up, though. Twice we said the state holds values in plain text, even sensitive ones. The next lesson opens that file.
"""

new = {
    "goal": "By the end you can write Terraform with typed variables, locals, outputs and expressions, try any expression in terraform console, and choose between count and for_each.",
    "opening": """Your friend's café did well, and now she wants three of them, in three parts of town. You have the drawing for the first one. So you copy it three times and change the street address on each copy by hand. On the third copy you forget, and the builder turns up at the wrong street.

The drawing was fine. The copying was the problem, and it is easy to fall into, because copying feels like the quickest way to get three of something. Each copy is one more place for a small mistake to hide.

Last time, we wrote one nginx container into a Terraform file, and every value in it, such as port 8090, was typed straight in. In this lesson, we'll teach the file to take settings from outside, to work values out from other values, and to make many copies from one block. We'll also meet a quiet trap in how those copies are counted. Before we start, make a guess, and keep it in mind.""",
    "guess": (
        "You made three containers with `count` from the list [\"alpha\", \"bravo\", \"charlie\"]. Then you delete \"alpha\" from the list. What does the next plan do?",
        "With `count`, each copy is known by its place in the list. Every name after alpha moves up one place, so copies [0] and [1] get new content and are replaced, and [2] is destroyed.",
    ),
    "terms": [
        "Any piece of HCL that produces a value, such as \"web-${var.name}\" or var.port + 1.",
        "A named setting with a type that a Terraform folder accepts from outside, read as var.NAME.",
        "A named value worked out inside one folder, read as local.NAME, so you write it only once.",
        "A value a folder hands back after apply, shown by terraform output.",
        "An expression that builds a new list or map from an existing one, by changing or skipping each item.",
        "A setting Terraform itself reads that makes a number of copies of a resource, known as [0], [1] and so on.",
        "A setting Terraform itself reads that makes one copy of a resource per key in a map or set, known as [\"key\"].",
    ],
    "sections": [
        ("Values that are worked out, not typed in", S0),
        ("Every value has a type", S1),
        ("Settings from outside: input variables", S2),
        ("Names inside, answers out: locals and outputs", S3),
        ("Building new values: text, choices and for expressions", S4),
        ("Many copies, and the trap of numbered copies", S5),
        ("A loop inside one resource: dynamic blocks", S6),
    ],
    "aside": {
        "title": "Why does the console say tuple when I wrote a list?",
        "body": "Values written straight into the file have their own types. A literal in square brackets is a tuple, not a list, and a literal in braces is an object, not a map. Ask the console for `type([\"b\", \"a\"])` and it says `tuple([string, string])`. Terraform converts it to a list or a map when a variable's type asks for one, so you rarely notice. It only matters when you read the console's answers closely.",
        "after": 1,
    },
    "diagram_caption": "Remove one name from the list: count copies shift and get replaced, for_each copies keep their names.",
    "worked": [
        "Apply the Day 32 `infra/local` files, then open the console in that folder. It knows the variables, the locals and the state, so you can see the real values behind `main.tf`. The for expression turns the `app_env` map into the `KEY=value` list Docker wants.",
        "Now poke at types. A literal list is a tuple until something converts it. A set drops the duplicate and picks its own order. Text that looks like a number is converted for you.",
        "Try a for expression with a filter, a map built from a map, and a function. Press Ctrl+D or type `exit` to leave the console.",
        "Copy the `loops` practice folder from the Files section. It makes one small file per name twice, once with `count` and once with `for_each`. Apply it and list the addresses: numbers for `count`, names for `for_each`. It uses the `local` provider, which makes files on your laptop, so no Docker is needed.",
        "Plan with alpha removed from the list, and read it slowly. `count` replaces two copies and destroys a third, because every name moved up one place. `for_each` destroys only alpha. Here is the real output, trimmed:",
        "Out of that plan, 3 of the 4 destroys come from `count`, for one removed name. Files are cheap to replace. Containers with data, or servers in a cloud, are not. Clean up.",
    ],
    "task": {
        "steps": [
            "Make a folder `~/code/tf-sites` and copy the `terraform` and `provider` blocks from your Day 31 `main.tf`.",
            "Declare a variable `sites` of type `map(number)` with three entries: blue on 8101, green on 8102 and red on 8103.",
            "Add a `docker_image` for `nginx:1.30-alpine` with `keep_locally = true`.",
            "Add ONE `docker_container` resource with `for_each = var.sites`. Name each container after its key, such as `site-blue`, and publish container port 80 on the entry's port.",
            "Add an output `urls` that uses a for expression to pair each site name with `http://localhost:PORT`.",
            "Run init and plan. Predict the summary line first, then apply and `curl` each URL.",
            "Remove red from the map and plan. Check that exactly one container is destroyed, then apply.",
            "Add a `validation` block to `sites` that rejects any port below 1024. Prove it works with `-var='sites={blue=80}'`.",
            "Optional: add an `upload` block that writes `<h1>Hello from KEY</h1>` to `/usr/share/nginx/html/index.html`, so each site shows its own name.",
            "Run `terraform destroy`.",
        ],
        "hints": [
            "Inside the container block, `each.key` is the site name and `each.value` is its port.",
            "A condition over every value can use `alltrue([for port in values(var.sites) : port >= 1024])`.",
            "The lab's `labs/terraform-practice/nginx-map/main.tf` is one possible answer. Look only after you have tried.",
        ],
        "done_when": "`curl -s localhost:8102` answers, `terraform state list` shows `docker_container.site[\"green\"]`, and removing one site planned exactly 1 to destroy.",
    },
    "explain_back": (
        "In 3 to 4 sentences, explain to a friend why removing the first item from a list used with `count` replaces other resources, and how `for_each` avoids it. Mention resource addresses.",
        "Terraform tracks every copy by its address. With `count`, the address is a position such as `[0]`, so removing the first item moves every later item up one place. Terraform then sees copies whose settings changed, replaces them, and destroys the last one. With `for_each`, the address is a key such as `[\"bravo\"]`, so removing one key destroys only that one copy.",
    ),
    "recap": [
        "Expressions work values out, and references like `var.x` and `docker_container.redis.name` also set the order.",
        "Types catch mistakes at plan time: primitives, collections (list, set, map) and structural types (object, tuple).",
        "Variables take values from defaults, `TF_VAR_`, tfvars files and `-var`. Later sources win, and `-var` is not remembered.",
        "Locals name values inside a folder, and outputs are the folder's answers.",
        "for expressions reshape collections, while `count` and `for_each` make copies of a resource.",
        "Prefer `for_each` with stable keys: `count` copies are known by position and shift. Neither can use a value that exists only after apply.",
    ],
    "closing": """We began with three copies of a café drawing and one forgotten address. Now there is one drawing and a list of names, and Terraform makes a copy for each name. Remove one name, and only that copy goes.

In your `tf-sites` folder, run `terraform state list` and look at the brackets. Names in quotes mean `for_each`, and bare numbers mean `count`. Wherever you see numbers next to things that have names, ask what happens if the first one leaves.

Next, we'll open the state file itself. What exactly does Terraform's notebook hold, and what happens when two people write in it at once?""",
    "check": [
        ("You export `TF_VAR_host_port=9001`, and `terraform.tfvars` contains `host_port = 9002`. You run `terraform plan` with no flags. Which value does Terraform use?",
         "A `terraform.tfvars` file beats a `TF_VAR_` environment variable, and both beat the default."),
        ("A variable has type `map(number)`. A friend passes `{ web = \"8081\" }`, with the port in quotes. What happens at plan time?",
         "The text \"8081\" really is a number, so Terraform converts it. Only something like \"abc\" would fail."),
        ("You write `for_each = var.names`, where `names` is a `list(string)`. Plan fails with \"Invalid for_each argument\". What is the usual fix?",
         "`for_each` needs a map or a set of strings, and `toset()` turns the list into a set."),
    ],
    "interview": [
        ("When do you use count and when for_each?",
         "Both create several copies of a resource. The `count` argument numbers the copies, so it fits identical copies or an on-off switch like `count = var.enabled ? 1 : 0`. The `for_each` argument names each copy by a map key or set value, so it fits copies with their own names or settings. I default to `for_each` for anything named, because removing an item from a `count` list shifts the later copies, and Terraform replaces them."),
        ("How do you give one Terraform configuration different values per environment?",
         "I declare input variables with types and validation, and keep each environment's values in files such as `dev.tfvars` and `prod.tfvars`, passed with `-var-file`. Secrets such as passwords stay out of those files and come from a secret store or the CI system at run time. Each environment also needs its own state, so I usually give each one its own top-level folder that uses shared modules. I avoid `-var` for anything permanent, because Terraform does not remember it."),
        ("What is the difference between a variable, a local and an output?",
         "A variable is an input that the caller or the command line can set. A local is a named value inside the folder that nobody outside can set, used to avoid repeating a long expression. An output is a value the folder hands back, printed after apply and readable by a parent module or a script. A recipe card is a fair picture: the ingredients you hand in, the notes you make while cooking, and the dish you hand back."),
    ],
    "deeper": """
Say you already have resources built with `count`, and you want to move to `for_each` before the position trap bites. Editing the block alone is not enough. Terraform sees `[0]`, `[1]` and `[2]` vanish and `["alpha"]`, `["bravo"]` and `["charlie"]` appear, so it plans to destroy three and create three. The real plan says `local_file.greeting[0] will be destroyed (because resource does not use count)` and ends with `Plan: 3 to add, 0 to change, 3 to destroy.`

The fix is a `moved` block per copy. It tells Terraform that an object changed its address and nothing else:

`moved { from = local_file.greeting[0]  to = local_file.greeting["alpha"] }`

Add one for `[1]` to `"bravo"` and one for `[2]` to `"charlie"`. The plan now shows `local_file.greeting[0] has moved to local_file.greeting["alpha"]`, three times, and `Plan: 0 to add, 0 to change, 0 to destroy.` Apply, and the state uses the new addresses. Day 33 covers `moved` properly. You will use it for renames and for moving code into modules.

Two details make this safe:
- You must write one block per copy. A `moved` block cannot loop, because Terraform has to know every move before it plans.
- The old position and the new key must point at the same real object. Check the plan: each line should say "has moved to", and nothing should say "must be replaced".

The "known at plan time" rule from the copies section also explains a common error. Imagine you want one container per network, and the network IDs only exist after apply. If you write `for_each = toset(docker_network.all[*].id)`, plan fails, because Terraform cannot know the keys yet. Build keys from values in your own code instead, such as the network names in a variable, and look up the IDs inside the block. Keys from your own code are known at plan time. IDs are not.

`for_each` works on whole modules too. `module "site" { for_each = var.sites ... }` makes one copy of a module per key, with addresses like `module.site["blue"]`. Day 34 builds a module and uses it more than once.

Templates can do more than place one value into text. Inside a string, `%{ if }` and `%{ for }` directives add logic, so `"%{ for n in ["a", "b"] }<li>${n}</li>%{ endfor }"` gives `<li>a</li><li>b</li>`. For text over several lines, a heredoc starts with `<<-EOT` and ends with `EOT`. The dash lets you indent the text along with your code, and Terraform removes that shared indent.
""",
    "drop": ["analogy", "mistake", "real_world"],
}

apply(8, "d32", new)
