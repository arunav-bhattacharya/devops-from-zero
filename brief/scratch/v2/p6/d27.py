from common import *
from svg import D27

V_DD_STATE = ref("Complete Terraform course: state and remote backends (DevOps Directive)", V_DD, "watch")

SECTIONS = [
    {
        "h": "Three pictures of the world",
        "body": (
            "Terraform never looks at your cloud console or at `docker ps`. Every plan compares three pictures:\n"
            "- Your code: the `.tf` files, which describe the desired state.\n"
            "- The state: Terraform's memory of what it created, in `terraform.tfstate`.\n"
            "- The real world: what the provider reports when Terraform asks the API.\n\n"
            "Plan starts with a refresh. Terraform asks the provider about every object in the state and updates its memory. Then it compares that memory with your code and lists the differences. Apply makes the changes and writes the new memory.\n\n"
            "The state's main job is a mapping from addresses to real objects: `docker_container.web` is the container with ID `d8eb279c...`. Why not just ask Docker which containers exist? Because Docker cannot tell which ones this folder owns. A container called `state-web` might be yours, a teammate's, or one from another Terraform folder. State is the list of what this folder owns, with the ID of each.\n\n"
            "Once you see the three pictures, the rest of this lesson falls into place, because each tool fixes one link between them:\n"
            "- `moved` changes an address in the state when you rename code.\n"
            "- `import` adds a real object that the state does not know yet.\n"
            "- Refresh-only mode copies reality into the state after someone changed things by hand."
        ),
        "refs": [
            ref("State (Terraform docs)", HC + "language/state", "docs"),
            V_DD_STATE,
        ],
    },
    {
        "h": "What is inside terraform.tfstate",
        "body": (
            "State is a JSON file. Open it with `jq` and you find a few top-level keys:\n"
            "- `version` is the file format, 4 today.\n"
            "- `terraform_version` is the Terraform version that last wrote it.\n"
            "- `serial` counts how many times this state has been written.\n"
            "- `lineage` is an ID given when the state was first created, so two unrelated states never get mixed up.\n"
            "- `resources` holds every resource, with its type, name, provider and every attribute the provider reported.\n\n"
            "Every attribute means every attribute, secrets included. In a test, a variable marked `sensitive` went into a resource as `REDIS_PASSWORD=s3cret-123`. Plan and apply printed `(sensitive value)`, and `terraform output` printed `<sensitive>`. The state file held `\"REDIS_PASSWORD=s3cret-123\"` in plain text. Anyone who can read your state can read your secrets.\n\n"
            "So never edit state by hand, never commit it, and treat it like a password file. Read it through commands instead:\n"
            "- `terraform state list` prints every address.\n"
            "- `terraform state show ADDRESS` prints one resource's attributes.\n"
            "- `terraform show` prints everything in a readable form."
        ),
        "refs": [
            ref("terraform state list command reference", HC + "cli/commands/state/list", "docs"),
            ref("Manage sensitive data (Terraform docs)", HC + "language/manage-sensitive-data", "docs"),
        ],
    },
    {
        "h": "Changing state on purpose: mv and rm",
        "body": (
            "Two commands change state directly:\n"
            "- `terraform state mv OLD NEW` gives an object a new address, right away.\n"
            "- `terraform state rm ADDRESS` makes Terraform forget an object.\n\n"
            "The name `rm` misleads people, so be clear on it: `state rm` deletes nothing real. The container keeps running, and in a cloud the server keeps running and keeps costing money. Terraform just stops tracking it. The next plan then wants to create it again, because the code still asks for it. With Docker that apply fails with `Conflict. The container name \"/state-legacy\" is already in use`.\n\n"
            "Both commands act at once, with no plan and no review. That made them risky in teams, so Terraform added blocks that do the same jobs from inside your code:\n"
            "- `moved` replaces `state mv`.\n"
            "- `import` replaces the older `terraform import` command.\n"
            "- `removed` replaces `state rm`.\n\n"
            "A block shows up in a pull request, its effect shows up in the plan, and nothing happens until apply. Prefer the blocks, and keep the commands for emergencies."
        ),
        "refs": [
            ref("terraform state rm command reference", HC + "cli/commands/state/rm", "docs"),
            ref("removed block reference", HC + "language/block/removed", "docs"),
        ],
    },
    {
        "h": "Renaming safely with moved blocks",
        "body": (
            "Rename a resource label from `web` to `site`, and to Terraform you deleted one resource and wrote a new one. The plan says `docker_container.web will be destroyed (because docker_container.web is not in configuration)` and `docker_container.site will be created`. The real container would be rebuilt to change a name only you can see.\n\n"
            "A `moved` block fixes that:\n\n"
            "`moved { from = docker_container.web  to = docker_container.site }`\n\n"
            "Now the plan says `docker_container.web has moved to docker_container.site` and `Plan: 0 to add, 0 to change, 0 to destroy.` Apply, and the state uses the new address.\n\n"
            "You use the same block for bigger refactors, such as moving a resource into a module on Day 28. Terraform also follows chains of moves, so a later move from `site` to somewhere else still works for a teammate who is two versions behind.\n\n"
            "When can you delete a `moved` block? The docs call removing one a breaking change for shared modules, because anyone still on the old address would get a destroy and a create. In your own root folder it is safe once every copy of the state has been applied with the block. Keeping it costs nothing.\n\n"
            "To stop managing something without destroying it, use a `removed` block with `lifecycle { destroy = false }`. The plan then says the object `will no longer be managed by Terraform, but will not be destroyed`."
        ),
        "refs": [
            ref("moved block reference", HC + "language/block/moved", "docs"),
            ref("Refactoring modules (Terraform docs)", HC + "language/modules/develop/refactoring", "docs"),
        ],
    },
    {
        "h": "Adopting what already exists with import blocks",
        "body": (
            "Sometimes the real object comes first: a bucket made in the console last year, or a container someone started by hand. An `import` block adopts it, and it takes two arguments:\n"
            "- `to` is the address it should get, such as `docker_container.legacy`.\n"
            "- `id` is the provider's ID for it. For a Docker container that is the full ID from `docker inspect -f '{{.Id}}' NAME`. A name does not work: the plan fails with `Cannot import non-existent remote object`.\n\n"
            "You also write the matching `resource` block yourself. Then you plan, and here is the part that bites people. Import does not make your code match reality. If your block differs from the real object, the plan imports it and then replaces it, with `# Warning: this will destroy the imported resource`.\n\n"
            "That warning is common with Docker, because the provider cannot read every setting back from a running container. In the worked example, three differences forced a replacement: `env`, the image written as an ID instead of a name, and `ports`. You adjust the code until the plan imports and destroys nothing. Either copy what Docker reports, or tell Terraform to ignore what it cannot read with `lifecycle { ignore_changes = [env, ports] }`.\n\n"
            "`terraform plan -generate-config-out=generated.tf` can write a first draft of the resource block. Treat it as a draft: it lists every attribute, including defaults you do not need. Once the import is applied, the `import` block has nothing left to do, so delete it."
        ),
        "refs": [
            ref("Import resources overview (Terraform docs)", HC + "language/import", "docs"),
            ref("import block reference", HC + "language/block/import", "docs"),
            ref("Generate configuration for imported resources", HC + "language/import/generating-configuration", "docs"),
        ],
    },
    {
        "h": "Drift, and what refresh-only really does",
        "body": (
            "Drift is any difference between the real world and Terraform's state, usually from a change made by hand. Every plan begins with a refresh, so a normal plan notices drift and proposes to undo it. In the middle of an incident that can be a surprise.\n\n"
            "Refresh-only mode separates the two jobs:\n"
            "- `terraform plan -refresh-only` shows only the changes made outside Terraform, under `Note: Objects have changed outside of Terraform`. It proposes no actions.\n"
            "- `terraform apply -refresh-only` writes those changes into the state. It changes no real object.\n\n"
            "The second one is widely misunderstood: it does not make the manual change permanent. In a test, `docker update --restart=always` changed a container by hand. After `apply -refresh-only` the state said `always`, but the code still said `no`. The very next normal plan proposed `~ restart = \"always\" -> \"no\"`. The code wins in the end.\n\n"
            "So after drift, decide which side is right:\n"
            "- The code is right: run a normal apply, and Terraform undoes the manual change.\n"
            "- Reality is right: change the code to match, then apply.\n\n"
            "Use `apply -refresh-only` when you only need the state to stop being stale, for example after someone deleted an object that the code will recreate anyway."
        ),
        "refs": [
            ref("terraform plan: refresh-only mode", HC + "cli/commands/plan", "docs"),
            ref("Use refresh-only mode to sync Terraform state (tutorial)", HC + "tutorials/state/refresh", "docs"),
        ],
    },
    {
        "h": "Where state lives in a team",
        "body": (
            "By default, state is a local file. That breaks as soon as a second person or a pipeline runs Terraform. Two copies drift apart, nobody has the full truth, and nothing stops two applies at once.\n\n"
            "A **backend** decides where state is stored. A remote backend keeps one copy that everyone uses, and most of them also lock it, so only one run at a time can change the state. Start an apply in one terminal and a plan in another, and the second stops with `Error: Error acquiring the state lock`, naming the operation that holds it.\n\n"
            "These are the common choices:\n"
            "- S3 on AWS, with `use_lockfile = true`. While a run holds the lock, Terraform keeps a small `.tflock` file next to the state. Older guides lock with a DynamoDB table, which is now deprecated. The docs also strongly recommend bucket versioning, so you can roll back a bad write. Day 29 sets this up.\n"
            "- HCP Terraform, HashiCorp's hosted service. Its docs say the Free plan is limited to 500 managed resources.\n"
            "- Similar backends for Google Cloud Storage, Azure Storage, PostgreSQL and more.\n\n"
            "Terraform also has better ways to keep secrets out of state. Since Terraform 1.10 a variable can be `ephemeral`: usable during a run, but never written to plan or state files. Since 1.11, some resources accept write-only arguments, such as a database password, for the same reason. OpenTofu can encrypt the whole state file. The Go deeper section shows all three."
        ),
        "refs": [
            ref("Backend type: s3 (Terraform docs)", HC + "language/backend/s3", "docs"),
            ref("State locking (Terraform docs)", HC + "language/state/locking", "docs"),
        ],
    },
]

WORKED = {
    "title": "Inspect, rename, import and drift in one practice folder",
    "steps": [
        step("Copy the `state` practice folder to `~/code/tf-state`, but start from the old version: name the container resource `web`, and leave out the `moved` block and `legacy.tf`. Apply, then look at the state from both sides.",
             """$ terraform init && terraform apply -auto-approve
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
$ terraform state list
docker_container.web
docker_image.nginx
$ jq '{version, terraform_version, serial, lineage}' terraform.tfstate
{
  "version": 4,
  "terraform_version": "1.17.1",
  "serial": 3,
  "lineage": "3a40a665-d793-e5ce-8aff-bb87d6b66138"
}"""),
        step("Rename the resource label from `web` to `site` and plan. You changed a word in a file, and Terraform wants to destroy a container and build a new one. Do not apply this.",
             """$ terraform plan
  # docker_container.site will be created
  # docker_container.web will be destroyed
  # (because docker_container.web is not in configuration)
Plan: 1 to add, 0 to change, 1 to destroy."""),
        step("Add the `moved` block from the Files section and plan again. Same container, same ID, new address. Apply it.",
             """$ terraform plan
  # docker_container.web has moved to docker_container.site
    resource "docker_container" "site" {
        id                                          = "d8eb279cfd6edf874baa636071c889575b0e02b0bc75f075ec3e84e81e713f80"
        name                                        = "state-web"
        # (51 unchanged attributes hidden)
    }

Plan: 0 to add, 0 to change, 0 to destroy.
$ terraform apply -auto-approve
Apply complete! Resources: 0 added, 0 changed, 0 destroyed."""),
        step("Now someone starts a container by hand: `docker run -d --name state-legacy -p 8112:80 nginx:1.30-alpine`. Get its full ID with `docker inspect -f '{{.Id}}' state-legacy`. Write a first `legacy.tf` with an import block and a resource block copied from the site container.",
             """import {
  to = docker_container.legacy
  id = "b8491ec38963d1eb4fb9e31f335b8f2c0b8a28cc1966593613c0ced9d2453dfa"
}

resource "docker_container" "legacy" {
  name  = "state-legacy"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8112
  }
}""", "hcl"),
        step("Plan, and read the warning. Terraform would import the container and then destroy it, because three attributes differ from what Docker reports. This is why you never apply an import plan without reading it.",
             """$ terraform plan
  # docker_container.legacy must be replaced
  # (imported from "b8491ec38963d1eb4fb9e31f335b8f2c0b8a28cc1966593613c0ced9d2453dfa")
  # Warning: this will destroy the imported resource
      + env                                         = (known after apply) # forces replacement
      ~ image                                       = "nginx:1.30-alpine" -> "sha256:0e52bd054126cdc040b1276c0af347aeb02a41b9cfe305d6094767ac30e97949" # forces replacement
      + ports { # forces replacement
Plan: 1 to import, 1 to add, 0 to change, 1 to destroy."""),
        step("Fix the block as in the final `legacy.tf`: use `docker_image.nginx.name`, and add `lifecycle { ignore_changes = [env, ports] }`. Now the plan imports and only fills in provider defaults. Apply, then check that the container kept its ID. Delete the import block afterwards. The output is trimmed.",
             """$ terraform plan
  # docker_container.legacy will be updated in-place
  # (imported from "b8491ec38963d1eb4fb9e31f335b8f2c0b8a28cc1966593613c0ced9d2453dfa")
  ~ resource "docker_container" "legacy" {
      + attach                                      = false
      + must_run                                    = true
      + start                                       = true
Plan: 1 to import, 0 to add, 1 to change, 0 to destroy.
$ terraform apply -auto-approve
Apply complete! Resources: 1 imported, 0 added, 1 changed, 0 destroyed.
$ docker inspect -f '{{.Id}}' state-legacy
b8491ec38963d1eb4fb9e31f335b8f2c0b8a28cc1966593613c0ced9d2453dfa"""),
        step("Last, cause drift by hand. Refresh-only shows the change and proposes nothing. A normal plan wants to put the code's value back. Then clean up.",
             """$ docker update --restart=always state-web
state-web
$ terraform plan -refresh-only
  # docker_container.site has changed
      ~ restart                                     = "no" -> "always"
This is a refresh-only plan, so Terraform will not take any actions to undo
these.
$ terraform plan
  # docker_container.site will be updated in-place
      ~ restart                                     = "always" -> "no"
Plan: 0 to add, 1 to change, 0 to destroy.
$ terraform destroy -auto-approve
Destroy complete! Resources: 3 destroyed."""),
    ],
}

LESSON = {
    "id": "d27",
    "title": "State: Terraform's memory",
    "minutes": 50,
    "goal": "By the end you can explain what Terraform's state holds, inspect it safely, rename and adopt resources with moved and import blocks, handle drift, and say where state should live in a team.",
    "guess": mcq(
        "You delete `terraform.tfstate` by mistake, while the containers it described keep running. What does the next `terraform apply` try to do?",
        ["Nothing: it finds them through Docker", "Create everything again, as if new", "Rebuild the state file from Docker", "Destroy the running containers first"],
        1,
        "Terraform only knows what it owns through the state. Without it every resource looks new, so apply tries to create them all; with Docker that fails on taken names, and in a cloud you can end up with duplicates.",
    ),
    "terms": [
        {"term": "State", "plain": "Terraform's record of the objects a folder manages: each address, its real ID and its attributes."},
        {"term": "Address", "plain": "The name Terraform uses for one resource, such as docker_container.web or module.dev.docker_network.app."},
        {"term": "Refresh", "plain": "The first step of every plan: Terraform asks the provider about each object in state and updates its memory."},
        {"term": "Drift", "plain": "A difference between the real world and Terraform's state, usually from a change made by hand."},
        {"term": "moved block", "plain": "A block that tells Terraform an object only changed address, so it is kept instead of rebuilt."},
        {"term": "import block", "plain": "A block that adopts an object that already exists into Terraform's state, through a normal plan and apply."},
        {"term": "Backend", "plain": "The place Terraform stores state, such as a local file, an S3 bucket or HCP Terraform."},
        {"term": "State lock", "plain": "A guard that lets only one Terraform run change a state at a time."},
    ],
    "sections": SECTIONS,
    "analogy": "State is like the ticket book in a theatre cloakroom. When you hand in a coat, the attendant writes your ticket number next to a hook. Without the book there is a room full of coats and no way to know which ones are yours, and a new attendant would hang a second copy of everything. The comparison has a limit: the book only notes the hook, while Terraform's state copies every detail of each object, secrets included.",
    "diagram": D27,
    "diagram_caption": "Plan compares three pictures: your code, the state file and the real world. moved, import and refresh-only each fix one link.",
    "worked": WORKED,
    "code": [
        code("hcl", "~/code/tf-state/main.tf (labs/terraform-practice/state, after the rename)", practice("state/main.tf"), "terraform init && terraform plan"),
        code("hcl", "~/code/tf-state/legacy.tf (after the import)", practice("state/legacy.tf"), "terraform plan"),
        code("hcl", "infra/local/main.tf (Day 27 version: web renamed to app)", day("d27", "infra/local/main.tf"), "terraform plan"),
        code("hcl", "infra/local/outputs.tf (Day 27 version)", day("d27", "infra/local/outputs.tf"), "terraform apply && terraform output"),
    ],
    "commands": [
        cmd("terraform state list", "List every address this folder's state tracks."),
        cmd("terraform state show docker_container.redis", "Show every attribute the state holds for one resource."),
        cmd("terraform show", "Print the whole state in a readable form."),
        cmd("jq '{version, serial, lineage}' terraform.tfstate", "Peek at the state file's header fields. Read only, never edit."),
        cmd("terraform state mv OLD NEW", "Change an address in state right away, with no plan. Prefer a moved block."),
        cmd("terraform state rm ADDRESS", "Make Terraform forget an object. The real object keeps running."),
        cmd("terraform plan -refresh-only", "Show only changes made outside Terraform. Proposes no actions."),
        cmd("terraform apply -refresh-only", "Write the real values into state without changing any real object."),
        cmd("docker inspect -f '{{.Id}}' NAME", "Print a container's full ID, which an import block needs."),
        cmd("terraform plan -generate-config-out=generated.tf", "With an import block, write a first draft of the resource block."),
        cmd("terraform plan -lock-timeout=60s", "Wait up to a minute for another run's state lock instead of failing at once."),
        cmd("terraform force-unlock LOCK_ID", "Remove a stuck lock, only after you are sure no run holds it."),
        cmd("terraform init -migrate-state", "After changing the backend block, copy the existing state to the new place."),
    ],
    "mistake": "Renaming a resource, or moving it into a module, without a `moved` block. In git it looks like a harmless rename. To Terraform it is a destroy plus a create, and the real object is rebuilt, data and all. After every refactor, read the plan: you want \"has moved to\" and `0 to destroy`.",
    "real_world": "At PayLoop (made up), each environment's state lives in a versioned S3 bucket with locking, and only the pipeline's role may write to it. A nightly job runs `terraform plan -refresh-only` and posts any drift to the team chat. When someone changes production by hand during an incident, the follow-up is a pull request that brings the code in line, never a quiet `apply -refresh-only`.",
    "task": {
        "title": "State surgery on infra/local: rename, drift, import, retire",
        "steps": [
            "Bring `infra/local` up to date with the Day 26 files, build the image if needed (`docker build -t hello-devops:1.0.0 .` in the repo root), and apply. `curl localhost:8080` a few times.",
            "Explore the state: run `terraform state list`, `terraform state show docker_container.redis` and `jq .serial terraform.tfstate`.",
            "Rename `docker_container.web` to `docker_container.app`, and fix the reference in `outputs.tf`. Plan once without a `moved` block and read the destroy. Then add the block from the Files section and plan until it says \"has moved to\". Apply.",
            "Cause drift: `docker rm -f hello-redis`. Check that `curl -s -o /dev/null -w '%{http_code}' localhost:8080/readyz` prints 503.",
            "Run `terraform plan -refresh-only`, then a normal `terraform apply`. Is `/readyz` back to 200? What happened to the `visits` count, and why?",
            "A teammate starts a Redis by hand: `docker run -d --name hello-redis-tmp redis:8-alpine`. Create `imported.tf` with an import block (the ID from `docker inspect`) and a `docker_container.redis_tmp` resource.",
            "Plan. If it says \"must be replaced\", change your resource block until the plan says \"will be updated in-place\" or \"will be imported\" with 0 to destroy. Then apply.",
            "Retire it the Terraform way: delete `imported.tf`, plan (expect 1 to destroy) and apply. Check that `docker ps` no longer lists hello-redis-tmp.",
            "Finish with `terraform plan`. Commit `main.tf` and `outputs.tf`.",
        ],
        "hints": [
            "Docker reports the image by the name you typed in `docker run`, so `image = docker_image.redis.name` matches and `image_id` does not.",
            "The Docker provider cannot read `env` back from a running container. `lifecycle { ignore_changes = [env] }` stops that one difference from forcing a replacement.",
            "Terraform recreated the Redis container, not the data inside it. The lab's Redis has no volume.",
        ],
        "done_when": "`terraform state list` shows `docker_container.app` and no `web`, `terraform plan` says No changes, and `docker ps` shows no hello-redis-tmp.",
    },
    "explain_back": {
        "prompt": "A teammate wants to commit `terraform.tfstate` so everyone can share it. In 3 to 4 sentences, explain what state contains, why it matters, and where it should live instead.",
        "answer": "The state file is Terraform's record of what this folder manages: it links each address in our code to a real object ID and stores every attribute. Plan depends on it to decide what to create, change or destroy, so a lost or stale copy causes real damage. It can hold secrets in plain text, even values marked sensitive, which rules out git, and git cannot lock it either. It belongs in a remote backend such as a versioned S3 bucket with `use_lockfile = true`, so there is one copy and only one run changes it at a time.",
    },
    "recap": [
        "Plan compares three pictures: your code, the state and the real world, refreshed from the provider.",
        "State maps addresses to real IDs and holds every attribute, secrets included, in plain text.",
        "`moved` renames without rebuilding, `import` adopts, and `removed` forgets; all of them show up in the plan.",
        "Read every import plan: \"must be replaced\" means your code does not match the real object yet.",
        "`apply -refresh-only` updates state only; the next normal apply still enforces the code.",
        "Teams keep state in a locked remote backend, such as S3 with `use_lockfile = true`, and never in git.",
    ],
    "check": [
        mcq("You mark a variable `db_password` as `sensitive = true` and pass it to a resource. Where can someone still read the real value?",
            ["Nowhere: Terraform encrypts it", "Only in the plan output", "Only inside the provider", "In the state file, in plain text"],
            3, "`sensitive` only hides the value in Terraform's output; the state still stores it as plain text."),
        mcq("Someone runs `docker update --restart=always` on a container that your code declares with `restart = \"no\"`. You run `terraform apply -refresh-only`, then `terraform plan`. What does the plan show?",
            ["No changes, because the state now matches", "An update that sets restart back to no", "A replacement of the whole container", "An error saying the state is stale"],
            1, "Refresh-only copied the drift into state, but the code still says `no`, so the next normal plan changes it back."),
        mcq("You run `terraform state rm docker_container.redis` and then `terraform apply`. The container is still running. What happens?",
            ["Apply tries to create it and fails on the name", "Terraform finds the container and adopts it", "Terraform deletes the running container", "Nothing, because the code did not change"],
            0, "`state rm` only made Terraform forget; the code still asks for the container, so apply tries to create it and Docker refuses the duplicate name."),
    ],
    "interview": [
        {"q": "How do you manage Terraform state in a team?",
         "a": "I keep it in a remote backend, such as a versioned and encrypted S3 bucket with `use_lockfile = true`, or HCP Terraform. Locking means only one run changes a state at a time. I limit who can read and write it, because it holds secrets, and usually only the pipeline may write. I split large setups into several states, one per environment or component, so a mistake has a smaller blast radius. Changes to addresses go through `moved`, `import` and `removed` blocks in pull requests, not hand edits."},
        {"q": "What is drift, and how do you handle it?",
         "a": "Drift is a difference between the real infrastructure and Terraform's state, usually from a manual change or another tool. A normal plan shows it and proposes to undo it, and `plan -refresh-only` shows only the outside changes. Then I decide which side is right: apply to restore the code, or change the code to match reality. `apply -refresh-only` only updates the state, so the code still wins on the next apply. A scheduled refresh-only plan in CI catches drift early."},
        {"q": "How do you bring existing infrastructure under Terraform?",
         "a": "I write an `import` block with the target address and the provider's ID, plus a resource block that describes the object. `plan -generate-config-out` can draft that block. Then I plan and iterate until the plan says the object will be imported with nothing destroyed, because a mismatch shows up as \"must be replaced\". After apply I delete the import block. For many resources, newer Terraform versions can also discover them in bulk with `terraform query`."},
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "State holds every attribute, so it holds every secret that passes through a resource. Terraform gives you several tools, and they do different jobs.\n\n"
            "1. `sensitive = true` on a variable or output hides the value in plan, apply and output, and that is all. The value is still in the state in plain text. It is still worth using, because it keeps secrets out of CI logs.\n"
            "2. `ephemeral = true` on a variable (Terraform 1.10 and later) makes the value exist only during the run. It is never written to plan or state files, and Terraform enforces that. In a test, an ephemeral variable passed into an ordinary argument failed the plan with `Ephemeral values are not valid for \"input\", because it is not a write-only attribute and must be persisted to state.`\n"
            "3. Write-only arguments (Terraform 1.11 and later) are arguments a provider sends to the API but never stores. The docs' example gives an AWS database its password through `password_wo`, generated by an `ephemeral \"random_password\"` block. Terraform never stores the value, so it cannot tell when it changed. You bump a number in a second argument, `password_wo_version`, to send a new password.\n"
            "4. An `ephemeral` resource block, like `ephemeral \"random_password\"`, produces a value that only lives during the run, so the secret never touches state.\n\n"
            "Not every provider supports write-only arguments yet, so check the provider's docs for each secret you handle.\n\n"
            "Then protect the state itself, because it will still hold IDs, addresses and whatever else a provider returns:\n"
            "- Keep it in a remote backend that encrypts at rest, such as S3 with server-side encryption.\n"
            "- Limit who can read it. Reading state is close to reading production.\n"
            "- On OpenTofu, turn on state encryption. An `encryption` block inside `terraform` encrypts state and plan files with a key from a passphrase or a key service such as AWS KMS.\n\n"
            "One last state topic: locks that get stuck. If a run crashes, or someone closes a laptop in the middle of an apply, the lock can stay behind. Every later run stops with `Error acquiring the state lock` and prints the lock's ID. First make sure no run is really in progress. Then `terraform force-unlock LOCK_ID` removes it. Never force-unlock a lock that someone is actively holding, because two applies writing one state is exactly how states get corrupted."
        ),
    },
    "sources": [
        {"title": "State", "url": HC + "language/state"},
        {"title": "moved block reference", "url": HC + "language/block/moved"},
        {"title": "Import resources overview", "url": HC + "language/import"},
        {"title": "Backend type: s3", "url": HC + "language/backend/s3"},
    ],
}
