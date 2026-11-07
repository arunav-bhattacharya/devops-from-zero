"""First-principles review edits for Days 31 to 37 (content/p8.json and content/p9.json).
Each edit is (part file, lesson id, field path, old text, new text). The old text must occur
exactly once in that field. Run from the repo root: python3 brief/scratch/v4/p8p9/edits.py
Re-running on already edited files is safe: an edit whose new text is already there is skipped."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]

E = []


def edit(part, lid, path, old, new):
    E.append((part, lid, path, old, new))


# ---------------------------------------------------------------- d31
edit(8, "d31", ("guess", "why"),
     "Terraform compares your files with what already exists. When they match",
     "Terraform remembers what it created, checks that those things still exist, and compares them with your files. When they match")

edit(8, "d31", ("sections", 1, "h"),
     "Declarative: describe the result, not the steps",
     "Declarative: desired state, memory and the plan")

edit(8, "d31", ("sections", 1, "body"),
     """Terraform is declarative, and you feel the difference the second time you run it. Run a `docker run` script twice and the second run fails, because the name is taken. Run Terraform twice and the second run prints `No changes`. The file only says what should exist, and it already does. A command that gives the same result however many times you run it is called idempotent.

As a backend engineer you already know this idea from SQL. You write `SELECT ... WHERE status = 'PAID'`, and the database decides whether to use an index or scan the table. Terraform works the same way. You write the end state, and Terraform makes a plan of API calls to get there. It still runs steps in order. You just never write them down.

You met the same idea on Day 21. `compose.yaml` describes services, and `docker compose up` makes them exist. Compose only knows Docker on one machine. Terraform talks""",
     """Terraform is declarative. Your files describe the desired state: what should exist once Terraform is done. You feel the difference the second time you run it. Run a `docker run` script twice and the second run fails, because the name is taken. Run Terraform twice and the second run prints `No changes`. A command that gives the same result however many times you run it is called idempotent.

How does Terraform know the container is already there? It keeps a memory. After every apply it writes a file called the state, `terraform.tfstate`, which records each object it made and that object's real ID. Every run then lines up three pictures:
1. Your files: the desired state.
2. The state: what Terraform made last time.
3. The real world: Terraform asks Docker about every ID in the state.

The plan is the difference between the desired state and what really exists, written as actions:
- In your files but not in the state: create it.
- In both, but with other settings: change it.
- In the state but gone from your files: delete it.

Apply carries out the plan and writes the result back into the state. On the second run, Docker reported the saved container with the right settings, so the plan was empty.

You know the idea from SQL. You write `SELECT ... WHERE status = 'PAID'`, and the database works out whether to use an index. Terraform still makes its API calls in a sensible order, but it works out that order itself. Compose on Day 21 is declarative too, but it only knows Docker on one machine. Terraform talks""")

edit(8, "d31", ("sections", 2, "body"),
     "Terraform was open source under the MPL licence until August 2023.",
     "Terraform was open source under the Mozilla Public License (MPL) until August 2023.")
edit(8, "d31", ("sections", 2, "body"),
     "It lives at the Linux Foundation and joined the CNCF in 2025.",
     "It lives at the Linux Foundation and joined the CNCF (Cloud Native Computing Foundation, the home of Kubernetes) in 2025.")
edit(8, "d31", ("sections", 2, "body"),
     "- Ansible: connects to servers that already exist and sets them up (packages, files, services).",
     "- Ansible: connects to servers that already exist and sets them up (packages, files, services). Days 36 and 37 teach it.")

edit(8, "d31", ("sections", 3, "body"),
     "A **provider** is a plugin that translates your blocks into API calls for one platform. The `terraform` block",
     "A **provider** is a plugin that translates your blocks into API calls for one platform. Terraform itself knows nothing about Docker or AWS. The `init` command downloads each provider as a separate program, and during plan and apply Terraform starts it and asks it to read, create, change or delete objects. The `terraform` block")
edit(8, "d31", ("sections", 3, "body"),
     "The `provider \"docker\" {}` block then configures it. Empty braces mean \"use the defaults\".",
     "The `provider \"docker\" {}` block then configures it. Empty braces mean the defaults: the address in `DOCKER_HOST` if it is set, otherwise `/var/run/docker.sock` from Day 2.")
edit(8, "d31", ("sections", 3, "body"),
     "The address must be unique in the folder, and Terraform uses it everywhere: in plans, in state and in commands.",
     "The address must be unique in the folder, and Terraform uses it everywhere: in plans, in commands, and in the state, which stores the real container ID under it.")

edit(8, "d31", ("sections", 4, "body"),
     "3. `terraform plan` compares your files, the state and the real world. It prints what it would do and changes nothing.",
     "3. `terraform plan` asks the provider about every object in the state (the `Refreshing state...` lines), compares the answers with your files, and prints the difference. It changes nothing.")

edit(8, "d31", ("sections", 6, "body"),
     "State is how Terraform links the address `docker_container.web` to one real container ID. Without it, Terraform could not tell \"create a container\" from \"this container already exists\". State can also hold",
     "Inside, the state pairs each address, such as `docker_container.web`, with the real container ID and every setting Docker reported. State can also hold")

edit(8, "d31", ("worked", "steps", 3, "say"),
     "Run plan again without touching the file. Terraform refreshes what it knows from Docker, compares, and finds nothing to do. That is idempotence.",
     "Run plan again without touching the file. The `Refreshing state` lines are Terraform asking Docker about each ID in its state. Both objects still exist with the settings your file asks for, so there is nothing to do.")

edit(8, "d31", ("check", 1, "why"),
     "Plan reads the real world, sees the container is missing, and proposes to create it again so reality matches the code.",
     "The refresh asks Docker about the container ID in the state, Docker reports it gone, so the plan proposes to create it again.")

# ---------------------------------------------------------------- d32
edit(8, "d32", ("sections", 2, "body"),
     "A `variable` block declares a setting the folder accepts. Look at",
     "Every value on Day 31 was written into `main.tf`, so a teammate who wanted another port had to edit the file. A `variable` block declares a setting the folder accepts instead, so the same files work with different values. Look at")

edit(8, "d32", ("sections", 4, "body"),
     "For text over several lines, a heredoc starts with `<<-EOT` and ends with `EOT`.",
     "For text over several lines, a heredoc starts with `<<-EOT` and ends with `EOT`. The dash lets you indent the text along with your code, and Terraform removes that shared indent.")

edit(8, "d32", ("sections", 5, "body"),
     "One more limit applies to both. Terraform must know the count or the keys at plan time, so they cannot come from an attribute that only exists after apply.",
     "One more limit applies to both. The plan lists every copy by its address, so Terraform must know the count or the keys before anything exists. They cannot come from an attribute that only exists after apply.")

# ---------------------------------------------------------------- d33
edit(8, "d33", ("sections", 0, "body"),
     "Every plan compares three pictures:",
     "Every plan compares the three pictures from Day 31:")

edit(8, "d33", ("sections", 1, "body"),
     "Treat the file like a password file: never commit it, and never edit it by hand. Read it",
     "Treat the file like a password file: never commit it, and never edit it by hand. One wrong ID in a hand edit points an address at someone else's object, and the next apply can change or delete it. Read it")

edit(8, "d33", ("sections", 6, "body"),
     "- HCP Terraform, HashiCorp's hosted service.",
     "- HCP Terraform, HashiCorp's hosted service (HCP is the HashiCorp Cloud Platform).")

# ---------------------------------------------------------------- d34
edit(8, "d34", ("sections", 0, "body"),
     "You have written modules since Day 31 without knowing the word. A **module** is a folder of `.tf` files.",
     "Say you want a second hello-devops stack for testing, next to the one on port 8080. Copying `infra/local` into a new folder works for a week. Then someone fixes a setting in one copy and forgets the other. A module lets you write the shape once and call it twice, with different names and ports.\n\nYou have written modules since Day 31 without knowing the word. A **module** is a folder of `.tf` files.")
edit(8, "d34", ("sections", 0, "body"),
     "Local folders are used in place. You can see what init found in `.terraform/modules/modules.json`, which lists each call and its folder. If you forget init,",
     "Local folders are used in place. If you forget init,")

edit(8, "d34", ("sections", 1, "body"),
     "The root configures each provider once, and every module call uses it. Write the module's constraint loosely, like `>= 4.6, < 5.0`, and let the root pin the exact version.",
     "The root configures each provider once, and every module call uses it, so the caller decides which Docker host or AWS account the module works in. Terraform then picks one provider version that fits the root's constraint and every module's at once. So write the module's constraint loosely, like `>= 4.6, < 5.0`, and let the root pin the exact version. A tight pin inside a module would clash with any root that wants another version.")

edit(8, "d34", ("sections", 2, "body"),
     "- The public registry, such as `terraform-aws-modules/vpc/aws`, with",
     "- The public registry, such as `terraform-aws-modules/vpc/aws` (namespace, name, provider), with")

edit(8, "d34", ("sections", 4, "body"),
     "Each environment still needs its own state, so you also switch backend settings per environment, which is easy to get wrong.",
     "Each environment still needs its own state, since an address like `docker_container.app` points at one object only. So you also switch backend settings per environment, which is easy to get wrong.")

edit(8, "d34", ("sections", 5, "body"),
     "A module is code, so it deserves tests. `terraform test`",
     "A bug in a shared module reaches every stack that calls it. So a module deserves tests like any other code. `terraform test`")
edit(8, "d34", ("sections", 5, "body"),
     "A `mock_provider \"docker\" {}` block swaps the real provider for a fake one that invents values for computed attributes. Then",
     "A `mock_provider \"docker\" {}` block swaps the real provider for a fake one. The fake answers every request itself and invents values for computed attributes, the ones a plan shows as `(known after apply)`, such as IDs. Then")

# ---------------------------------------------------------------- d35
edit(8, "d35", ("sections", 2, "body"),
     "In the AWS provider, a bucket's settings are separate resources that sit next to `aws_s3_bucket`:",
     "In the AWS provider, a bucket's settings are separate resources that sit next to `aws_s3_bucket`. Each one maps to its own call in the S3 API, so changing one setting leaves the others alone:")

edit(8, "d35", ("sections", 3, "body"),
     "On Day 27 you met OIDC: a workflow gets a short-lived token from GitHub instead of storing cloud keys. The lab's `github-oidc.tf` builds the AWS side:\n1. An OIDC identity provider for `token.actions.githubusercontent.com` with the audience `sts.amazonaws.com`.",
     "An AWS access key saved as a GitHub secret works until someone deletes it, so a leaked key stays useful for months. On Day 27 you met the fix, OIDC (OpenID Connect): a workflow gets a short-lived token from GitHub instead. GitHub signs the token, and it holds claims, named fields such as the repo and branch the job runs for. The lab's `github-oidc.tf` builds the AWS side:\n1. An OIDC identity provider for `token.actions.githubusercontent.com`, so AWS can check GitHub's signature. Its audience, `sts.amazonaws.com`, is the `aud` claim a token must carry.")

# ---------------------------------------------------------------- d36
edit(9, "d36", ("sections", 0, "body"),
     "A tool then makes every server match, and keeps doing it.",
     "A tool then makes every server match, every time you run it.")

edit(9, "d36", ("sections", 1, "body"),
     "Older tools such as Puppet and Chef install an agent on every server, and the agent pulls its config from a central server.",
     "Older tools such as Puppet and Chef install an agent on every server, and the agent pulls its config from a central server. Without an agent there is nothing to install or keep updated on the servers. A fresh Ubuntu server is ready for Ansible as soon as you can log in to it.")

edit(9, "d36", ("sections", 5, "body"),
     "A task that depends on an earlier task's result can guess wrong, because the earlier task did not really run.",
     "A task that depends on an earlier task's result can guess wrong, because the earlier task did not really run.\n\nNo state file also means no memory of past runs. Delete a resource block in Terraform and the next plan destroys the object, because the state remembers it. Delete the jq task from a playbook and jq stays installed. To remove something, you write a task that says so, such as `state=absent`.")

# ---------------------------------------------------------------- d37
edit(9, "d37", ("sections", 0, "body"),
     "Look at where role vars sit: above group_vars and host_vars.",
     "The order has a pattern. A role default is only the author's suggestion, so it is weakest. The inventory files come next, where a host beats its group. Values written in the playbook beat the inventory, and what you type for one run beats everything.\n\nRole vars break the pattern: they sit above group_vars and host_vars.")

edit(9, "d37", ("sections", 3, "body"),
     "A role is a folder with a fixed layout, so Ansible knows where to look in it.",
     "Day 36's `hello-devops.yml` puts all of the app's tasks and its handler into one playbook. A second playbook that needs the same app would have to copy all of it. A role packages that job once, much like a Terraform module on Day 34, and any play can use it. A role is a folder with a fixed layout, so Ansible knows where to look in it.")

edit(9, "d37", ("sections", 4, "body"),
     "A playbook often needs a secret, such as a database password or an API token. Ansible Vault encrypts it with AES256 and a password,",
     "A playbook often needs a secret, such as a database password or an API token. Written in plain text in group_vars, it lands in git, and git history keeps it even after you delete the line. Ansible Vault encrypts it with AES256 (the Advanced Encryption Standard, with a 256-bit key) and a password,")

edit(9, "d37", ("sections", 5, "body"),
     "It is a test framework for roles, playbooks and collections, maintained by the Ansible project and released about once a month.",
     "It is a test framework for roles, playbooks and collections, maintained by the Ansible project.")

edit(9, "d37", ("sections", 6, "body"),
     "It needs the amazon.aws collection, boto3 next to Ansible",
     "It needs the amazon.aws collection, boto3 (Day 16) next to Ansible")


def get(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def put(obj, path, value):
    for p in path[:-1]:
        obj = obj[p]
    obj[path[-1]] = value


def main():
    data = {n: json.loads((ROOT / f"content/p{n}.json").read_text()) for n in (8, 9)}
    lessons = {(n, L["id"]): L for n, d in data.items() for L in d["lessons"]}
    done = skipped = 0
    for part, lid, path, old, new in E:
        L = lessons[(part, lid)]
        text = get(L, path)
        if new in text:
            skipped += 1
            continue
        n = text.count(old)
        if n != 1:
            sys.exit(f"{lid} {path}: old text found {n} times: {old[:60]!r}")
        put(L, path, text.replace(old, new))
        done += 1
    for n, d in data.items():
        (ROOT / f"content/p{n}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(f"{done} edits applied, {skipped} already applied")


if __name__ == "__main__":
    main()
