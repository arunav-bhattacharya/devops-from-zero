from common import apply

S0 = """
Back to the cloakroom for a moment. The coats are the real objects, and they are easy to see. The book is what tells you which coat belongs to which ticket. Terraform has the same three things, and every plan compares the three pictures you met in the first Terraform lesson:
- Your code: the `.tf` files, which describe the desired state.
- The state: Terraform's book of what it created, in `terraform.tfstate`.
- The real world: what the provider (the plugin that talks to Docker or a cloud) reports when Terraform asks.

Terraform never browses a cloud's website or runs `docker ps` to see what is out there. Plan starts with a refresh instead: Terraform asks the provider about every object in the state and updates its book. Then it compares the book with your code and lists the differences. Apply makes the changes and writes the new book.

The state's main job is to link addresses to real objects: `docker_container.web` is the container with ID `d8eb279c...`. You might ask, "Why not just ask Docker which containers exist?" Because Docker cannot tell which ones this folder owns. A container called `state-web` might be yours, a teammate's, or one from another Terraform folder. Only the book says which coats are ours.

The cloakroom picture stops short in one place. A cloakroom book notes a ticket and a hook. Terraform's state copies every detail of each object, secrets included, so you guard it far more closely.

Each tool later in this lesson fixes one link between the three pictures:
- `moved` changes an address in the state when you rename something in your code.
- `import` adds a real object that the state does not know yet.
- Refresh-only mode copies reality into the state after someone changed things by hand.

First, though, let's open the book and read it.
"""

S1 = """
State is a JSON file, JSON being a common text format for nested data. `jq`, a small tool that reads JSON, picks out its parts. At the top you find a few keys:
- `version` is the file format, 4 today.
- `terraform_version` is the Terraform version that last wrote it.
- `serial` counts how many times this state has been written.
- `lineage` is an ID given when the state was first created, so two unrelated states never get mixed up.
- `resources` holds every resource, with its type, name, provider and every attribute the provider reported.

Those attributes include secrets. In a test, a variable marked `sensitive` went into a resource as `REDIS_PASSWORD=s3cret-123`. Plan and apply printed `(sensitive value)`, and `terraform output` printed `<sensitive>`. So far, so reassuring. The state file, though, held `"REDIS_PASSWORD=s3cret-123"` in plain text. Anyone who can read your state can read your secrets.

Treat the file like a password file: never commit it to git, and never edit it by hand. One wrong ID in a hand edit points an address at someone else's object, and the next apply can change or delete it. Read the state through commands instead:
- `terraform state list` prints every address.
- `terraform state show ADDRESS` prints one resource's attributes.
- `terraform show` prints everything in a readable form.

Reading is safe. Writing in the book is another matter, and Terraform has two commands for it.
"""

S2 = """
Two commands change the state directly:
- `terraform state mv OLD NEW` gives an object a new address, right away.
- `terraform state rm ADDRESS` makes Terraform forget an object.

The name `rm` (short for remove) misleads people, so be clear on it: `state rm` deletes nothing real. The container keeps running. In a cloud, the server keeps running and keeps costing money. Terraform only crosses the line out of its book.

The next plan then wants to create the object again, because the code still asks for it. With Docker that apply fails with `Conflict. The container name "/state-legacy" is already in use`. That is the cloakroom again: a coat on a hook with no line in the book, and a new coat arriving for the same hook.

Both commands act at once, with no plan and no review, and that made them risky in teams. So Terraform added blocks that do the same jobs from inside your code:
- `moved` replaces `state mv`.
- `import` replaces the older `terraform import` command.
- `removed` replaces `state rm`.

A block shows up in a pull request, its effect shows up in the plan, and nothing happens until apply. Prefer the blocks, and keep the commands for emergencies. The first block to meet is the one you will use most.
"""

S3 = """
Say you rename a resource label from `web` to `site`, because the new name reads better. In git it looks like a harmless rename. To Terraform you deleted one resource and wrote a new one. The plan says `docker_container.web will be destroyed (because docker_container.web is not in configuration)` and `docker_container.site will be created`. The real container would be rebuilt, data and all, to change a name only you can see.

A `moved` block fixes that:

`moved { from = docker_container.web  to = docker_container.site }`

Now the plan says `docker_container.web has moved to docker_container.site` and `Plan: 0 to add, 0 to change, 0 to destroy.` Apply, and the state uses the new address.

**A rename in code is a destroy to Terraform. Add a `moved` block, and check for "has moved to".**

You use the same block for bigger clean-ups, such as moving a resource into a module (a reusable folder of Terraform files) in the next lesson. Terraform also follows chains of moves. A later move from `site` to somewhere else still works for a teammate whose copy is two versions behind.

When can you delete a `moved` block? The docs call removing one a breaking change for shared modules: anyone still on the old address would get a destroy and a create. In your own top-level folder it is safe once every copy of the state has been applied with the block. Keeping it costs nothing.

To stop managing something without destroying it, use a `removed` block with `lifecycle { destroy = false }`. The plan then says the object `will no longer be managed by Terraform, but will not be destroyed`. Renaming and forgetting are covered. The opposite case is a coat that arrives with no ticket at all.
"""

S4 = """
Sometimes the real object comes first. Someone made a storage bucket (a place in a cloud that holds files) by clicking last year, or started a container by hand. An `import` block adopts it, and it takes two arguments:
- `to` is the address it should get, such as `docker_container.legacy`.
- `id` is the provider's ID for it. For a Docker container that is the full ID from `docker inspect -f '{{.Id}}' NAME`. A name does not work: the plan fails with `Cannot import non-existent remote object`.

You also write the matching `resource` block yourself, then plan. Read that plan with care, because import does not make your code match reality. If your block differs from the real object, the plan imports it and then replaces it, with `# Warning: this will destroy the imported resource`.

That warning is common with Docker, because the provider cannot read every setting back from a running container. In the worked example, three differences forced a replacement: `env` (the environment variables), the image written as an ID instead of a name, and `ports`. You adjust the code until the plan imports and destroys nothing. Either copy what Docker reports, or tell Terraform to ignore what it cannot read with `lifecycle { ignore_changes = [env, ports] }`.

`terraform plan -generate-config-out=generated.tf` can write a first draft of the resource block. Treat it as a draft: it lists every attribute, including defaults you do not need. Once the import is applied, the `import` block has nothing left to do, so delete it. Import handles objects Terraform never knew. Drift is the harder case: objects it knows, changed behind its back.
"""

S5 = """
Picture an incident late at night. Something is broken, and someone fixes it fast by changing a container by hand. The fix works, everyone goes to bed, and the code still says the old thing. That gap is drift: any difference between the real world and Terraform's state, usually from a change made by hand.

Every plan begins with a refresh, so a normal plan notices drift and proposes to undo it. In the middle of an incident, that can be an unpleasant surprise. Refresh-only mode separates the two jobs:
- `terraform plan -refresh-only` shows only the changes made outside Terraform, under `Note: Objects have changed outside of Terraform`. It proposes no actions.
- `terraform apply -refresh-only` writes those changes into the state. It changes no real object.

People often expect the second one to make the hand change permanent. It does not. In a test, `docker update --restart=always` changed a container by hand. After `apply -refresh-only` the state said `always`, but the code still said `no`. The very next normal plan proposed `~ restart = "always" -> "no"`.

**Refresh-only updates the book, not the code. The code still wins.**

After drift, you decide which side is right:
- The code is right: run a normal apply, and Terraform undoes the hand change.
- Reality is right: change the code to match, then apply.

Use `apply -refresh-only` when you only need the state to stop being out of date, for example after someone deleted an object that the code will recreate anyway. Picture a payments team that takes drift seriously. A nightly job runs `terraform plan -refresh-only` and posts any drift to the team chat. The follow-up to a hand change is a pull request that brings the code in line, never a quiet `apply -refresh-only`. A team like that also needs one shared book, which is our last question.
"""

S6 = """
By default, the state is a file on your laptop. That breaks as soon as a second person, or a pipeline (a server that runs your steps on every change), runs Terraform. Two copies of the book drift apart, and nothing stops two applies from running at once.

A backend decides where the state is stored. A remote backend keeps one copy that everyone uses, somewhere on the network. Most remote backends also lock the state, so only one run at a time can change it. Start an apply in one terminal and a plan in another, and the second stops with `Error: Error acquiring the state lock`, naming the operation that holds it.

These are the common choices:
- S3, Amazon's file storage service, with `use_lockfile = true`. While a run holds the lock, Terraform keeps a small `.tflock` file next to the state. Older guides lock with a DynamoDB table (an Amazon database), which is now deprecated, meaning it still works but is on its way out.
- The docs also strongly recommend turning on versioning for the S3 bucket, so you can roll back a bad write. Day 35 sets this up.
- HCP Terraform, HashiCorp's hosted service. Its docs say the Free plan is limited to 500 managed resources.
- Similar backends exist for Google Cloud Storage, Azure Storage, PostgreSQL (a popular database) and more.

Terraform also has newer ways to keep secrets out of the state. Since Terraform 1.10, a variable can be `ephemeral`: usable during a run, but never written to plan or state files. Since 1.11, some resources accept write-only arguments, such as a database password, for the same reason. OpenTofu can encrypt the whole state file. The Go deeper section shows all three.

One limit remains. Each folder still has one state and one set of settings, so a test copy and a real copy of the same setup mean copying folders. The next lesson shows how to share the code and keep the books apart.
"""

new = {
    "goal": "By the end you can explain what Terraform's state holds, look inside it safely, rename and adopt resources with moved and import blocks, handle drift, and say where state should live in a team.",
    "opening": """You are helping at a friend's wedding, looking after the coats. Each coat goes on a hook, and you write the ticket number next to the hook in a small book. Halfway through the evening, the book falls into a bowl of punch. The coats are all still there, safe on their hooks. Then the first guest hands you ticket 41, and you have no idea which coat is hers.

It is easy to think the coats are what matter, because you can see and touch them. The book feels like a detail, right up to the moment it is gone.

Last time, Terraform made many containers from one block and kept track of each copy by its address. That tracking lives in one file, the state. In this lesson, we'll open it and read it safely. We'll rename things without rebuilding them, adopt a container someone started by hand, and decide where the book lives in a team. Before we start, make a guess, and keep it in mind.""",
    "guess": (
        "You delete `terraform.tfstate` by mistake, while the containers it described keep running. What does the next `terraform apply` try to do?",
        "Terraform knows what it owns only through the state. Without it, every resource looks new, so apply tries to create them all. With Docker that fails on names that are already taken, and in a cloud you can end up with two of everything.",
    ),
    "terms": [
        "Terraform's record of the objects a folder manages: each address, its real ID and its settings.",
        "The name Terraform uses for one resource, such as docker_container.web or module.dev.docker_network.app.",
        "The first step of every plan: Terraform asks the provider about each object in the state and updates its record.",
        "A difference between the real world and Terraform's state, usually from a change made by hand.",
        "A block that tells Terraform an object only changed its address, so it is kept instead of rebuilt.",
        "A block that adopts an object that already exists into Terraform's state, through a normal plan and apply.",
        "The place Terraform stores the state, such as a local file, a bucket in Amazon's S3, or HCP Terraform.",
        "A guard that lets only one Terraform run change a state at a time.",
    ],
    "sections": [
        ("Why Terraform keeps its own book", S0),
        ("Opening the book: what terraform.tfstate holds", S1),
        ("Writing in the book by hand: state mv and rm", S2),
        ("Renaming without rebuilding: moved blocks", S3),
        ("Adopting a container started by hand: import blocks", S4),
        ("Changes behind Terraform's back: drift and refresh-only", S5),
        ("Where the book lives when a team shares it", S6),
    ],
    "aside": {
        "title": "What if the state file is already gone?",
        "body": "Then you have coats with no book. Terraform will try to create everything again, which fails on taken names with Docker and can make duplicates in a cloud. The way back is the import block from this section: write one per object, with its real ID, and plan until nothing is replaced. With a remote backend that keeps old versions, you can often restore the last good copy instead. That is one more reason Day 35 turns versioning on.",
        "after": 4,
    },
    "diagram_caption": "Plan compares three pictures: your code, the state file and the real world. moved, import and refresh-only each fix one link.",
    "worked": [
        "Copy the `state` practice folder to `~/code/tf-state`, but start from the old version: name the container resource `web`, and leave out the `moved` block and `legacy.tf`. Apply, then look at the state from both sides.",
        "Rename the resource label from `web` to `site` and plan. You changed one word in a file, and Terraform wants to destroy a container and build a new one. Do not apply this.",
        "Add the `moved` block from the Files section and plan again. Same container, same ID, new address. Apply it.",
        "Now someone starts a container by hand: `docker run -d --name state-legacy -p 8112:80 nginx:1.30-alpine`. Get its full ID with `docker inspect -f '{{.Id}}' state-legacy`. Write a first `legacy.tf` with an import block, and a resource block copied from the site container.",
        "Plan, and read the warning. Terraform would import the container and then destroy it, because three attributes differ from what Docker reports. This is why you never apply an import plan without reading it.",
        "Fix the block as in the final `legacy.tf`: use `docker_image.nginx.name`, and add `lifecycle { ignore_changes = [env, ports] }`. Now the plan imports and only fills in the provider's defaults. Apply, then check that the container kept its ID. Delete the import block afterwards. The output is trimmed.",
        "Last, cause drift by hand. Refresh-only shows the change and proposes nothing. A normal plan wants to put the code's value back. Then clean up.",
    ],
    "task": {
        "steps": [
            "Bring `infra/local` up to date with the Day 32 files, build the image if needed (`docker build -t hello-devops:1.0.0 .` in the repo root), and apply. Then `curl localhost:8080` a few times, and watch the visit count grow.",
            "Explore the state: run `terraform state list`, `terraform state show docker_container.redis` and `jq .serial terraform.tfstate`.",
            "Rename `docker_container.web` to `docker_container.app`, and fix the reference in `outputs.tf`. Plan once without a `moved` block and read the destroy. Then add the block from the Files section and plan until it says \"has moved to\". Apply.",
            "Cause drift: `docker rm -f hello-redis`. The app's `/readyz` page answers 503 when Redis is missing. Check that `curl -s -o /dev/null -w '%{http_code}' localhost:8080/readyz` prints 503.",
            "Run `terraform plan -refresh-only`, then a normal `terraform apply`. Is `/readyz` back to 200? What happened to the `visits` count, and why?",
            "A teammate starts a Redis by hand: `docker run -d --name hello-redis-tmp redis:8-alpine`. Create `imported.tf` with an import block (the ID comes from `docker inspect`) and a `docker_container.redis_tmp` resource.",
            "Plan. If it says \"must be replaced\", change your resource block until the plan says \"will be updated in-place\" or \"will be imported\" with 0 to destroy. Then apply.",
            "Retire it the Terraform way: delete `imported.tf`, plan (expect 1 to destroy) and apply. Check that `docker ps` no longer lists hello-redis-tmp.",
            "Finish with `terraform plan`. Commit `main.tf` and `outputs.tf`.",
        ],
        "hints": [
            "Docker reports the image by the name you typed in `docker run`, so `image = docker_image.redis.name` matches and `image_id` does not.",
            "The Docker provider cannot read `env` back from a running container. `lifecycle { ignore_changes = [env] }` stops that one difference from forcing a replacement.",
            "Terraform recreated the Redis container, not the data inside it. The lab's Redis has no volume (no storage that outlives the container).",
        ],
        "done_when": "`terraform state list` shows `docker_container.app` and no `web`, `terraform plan` says No changes, and `docker ps` shows no hello-redis-tmp.",
    },
    "explain_back": (
        "A teammate wants to commit `terraform.tfstate` so everyone can share it. In 3 to 4 sentences, explain what the state contains, why it matters, and where it should live instead.",
        "The state file is Terraform's record of what this folder manages: it links each address in our code to a real object ID and stores every setting. Plan depends on it to decide what to create, change or destroy, so a lost or stale copy causes real damage. It can hold secrets in plain text, even values marked sensitive, which rules out git, and git cannot lock it either. It belongs in a remote backend such as a versioned S3 bucket with `use_lockfile = true`, so there is one copy and only one run changes it at a time.",
    ),
    "recap": [
        "Plan compares three pictures: your code, the state and the real world, refreshed from the provider.",
        "The state links addresses to real IDs and holds every setting, secrets included, in plain text.",
        "`moved` renames without rebuilding, `import` adopts, and `removed` forgets. You see each of them in the plan.",
        "Read every import plan: \"must be replaced\" means your code does not match the real object yet.",
        "`apply -refresh-only` updates the state only, and the next normal apply still enforces the code.",
        "Teams keep state in a locked remote backend, never in git. One folder still means one state, so test and real copies need more than this.",
    ],
    "closing": """We started with a cloakroom book in a bowl of punch, and coats nobody could match to tickets. Terraform's state is that book. Today you read it, renamed a container without rebuilding it, adopted one started by hand, and watched the code win after a change made behind its back.

In the lab, run `jq .serial terraform.tfstate` before and after your next apply. The number goes up each time Terraform writes the book.

Next, we'll split the code from the settings. How can a test copy and a real copy share one set of files, yet keep separate books?""",
    "check": [
        ("You mark a variable `db_password` as `sensitive = true` and pass it to a resource. Where can someone still read the real value?",
         "`sensitive` only hides the value in Terraform's output. The state still stores it as plain text."),
        ("Someone runs `docker update --restart=always` on a container that your code declares with `restart = \"no\"`. You run `terraform apply -refresh-only`, then `terraform plan`. What does the plan show?",
         "Refresh-only copied the drift into the state, but the code still says `no`, so the next normal plan changes it back."),
        ("You run `terraform state rm docker_container.redis` and then `terraform apply`. The container is still running. What happens?",
         "`state rm` only made Terraform forget. The code still asks for the container, so apply tries to create it, and Docker refuses the duplicate name."),
    ],
    "interview": [
        ("How do you manage Terraform state in a team?",
         "I keep it in a remote backend, such as a versioned and encrypted S3 bucket with `use_lockfile = true`, or HCP Terraform. Locking means only one run changes a state at a time. I limit who can read and write it, because it holds secrets, and usually only the pipeline may write. I split large setups into several states, one per environment or part of the system, so a mistake reaches less. Changes to addresses go through `moved`, `import` and `removed` blocks in pull requests, not hand edits."),
        ("What is drift, and how do you handle it?",
         "Drift is a difference between the real infrastructure and Terraform's state, usually from a change made by hand or by another tool. A normal plan shows it and proposes to undo it, and `plan -refresh-only` shows only the outside changes. Then I decide which side is right. Either I apply to restore the code, or I change the code to match reality. `apply -refresh-only` only updates the state, so the code still wins on the next apply. A scheduled refresh-only plan in CI catches drift early."),
        ("How do you bring existing infrastructure under Terraform?",
         "I write an `import` block with the target address and the provider's ID, plus a resource block that describes the object. `plan -generate-config-out` can draft that block. Then I plan and adjust until the plan says the object will be imported with nothing destroyed, because a mismatch shows up as \"must be replaced\". After apply I delete the import block. For many resources, newer Terraform versions can also find them in bulk with `terraform query`."),
    ],
    "deeper": """
The state holds every attribute, so it holds every secret that passes through a resource. Terraform gives you several tools for this, and they do different jobs.

1. `sensitive = true` on a variable or output hides the value in plan, apply and output, and that is all. The value is still in the state in plain text. It is still worth using, because it keeps secrets out of CI logs (the text a pipeline prints as it runs).
2. `ephemeral = true` on a variable (Terraform 1.10 and later) makes the value exist only during the run. It is never written to plan or state files, and Terraform enforces that. In a test, an ephemeral variable passed into an ordinary argument failed the plan with `Ephemeral values are not valid for "input", because it is not a write-only attribute and must be persisted to state.`
3. Write-only arguments (Terraform 1.11 and later) are arguments a provider sends to the platform but never stores. The docs' example gives an AWS database its password through `password_wo`, made by an `ephemeral "random_password"` block. Terraform never stores the value, so it cannot tell when it changed. You raise a number in a second argument, `password_wo_version`, to send a new password.
4. An `ephemeral` resource block, like `ephemeral "random_password"`, produces a value that only lives during the run, so the secret never touches the state.

Not every provider supports write-only arguments yet, so check the provider's docs for each secret you handle.

Then protect the state itself, because it will still hold IDs, addresses and whatever else a provider returns:
- Keep it in a remote backend that encrypts it on disk, such as S3 with server-side encryption.
- Limit who can read it. Reading the state is close to reading production, the real system your users depend on.
- On OpenTofu, turn on state encryption. An `encryption` block inside `terraform` encrypts state and plan files with a key from a passphrase or a key service such as AWS KMS.

Which tool should you reach for first? Keep secrets out of `.tf` files and committed `.tfvars` files, always. Mark anything secret as `sensitive`. Where your Terraform and provider versions allow it, pass secrets as ephemeral values into write-only arguments, so they never reach the state. Anything that still ends up in the state, you protect by locking down the state itself.
""",
    "drop": ["analogy", "mistake", "real_world"],
}

apply(8, "d33", new)
