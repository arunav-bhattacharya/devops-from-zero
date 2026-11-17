from common import apply

S0 = """
Last time, the playbook had the port, the folder and the greeting typed in. A variable is a named value, such as `hello_devops_greeting`, that tasks use instead of a typed-in one. Change the value, and every task that reads it follows, without any edit to the tasks. Variables let one playbook serve many servers that differ a little.

You can set a variable in many places, just as the street had notes in many places. The rule for which value wins is called **variable precedence**. The docs list 22 levels. In practice you need seven, from weakest to strongest:
1. Role defaults, in `roles/NAME/defaults/main.yml`. A role is a packaged set of tasks, which we build later in this lesson.
2. `group_vars/all.yml`, for every host.
3. `group_vars/web.yml` or a `group_vars/web/` folder, for one group.
4. `host_vars/web2.yml`, for one host.
5. `vars:` in a play.
6. Role vars, in `roles/NAME/vars/main.yml`.
7. Extra vars on the command line, `-e name=value`, which always win.

Ansible loads the `group_vars` and `host_vars` folders that sit next to the inventory file or the playbook, and it matches file names to group and host names. The lab sets the greeting twice. The file `group_vars/web/vars.yml` says `Hello from Ansible`. The file `host_vars/web2.yml` gives web2 its own text, because web2 is the canary. A canary is the one server that gets a change first, so a problem shows up on one machine instead of all.

The command `ansible web -m ansible.builtin.debug -a var=hello_devops_greeting` asks each host what it sees. It printed exactly those two values. With `-e 'hello_devops_greeting="Hi from -e"'` added, both hosts printed `Hi from -e`.

The street explains the order. A role default is the printed checklist, only the author's suggestion, so it is weakest. Next come the notes on the inventory: the note for one side of the street, then the sticky note on one front door, so a host beats its group. Values written in the playbook beat the inventory, and the owner's phone call tonight (`-e`) beats everything.

Role vars break the pattern: they sit above group_vars and host_vars. A value in a role's `vars/` folder cannot be changed from the inventory at all, and Ansible gives no warning. So `defaults/` is for every setting a user may want to change, and `vars/` for the role's own fixed details. A real sitter would notice two notes that disagree and ask. Ansible never asks. It picks the winner by its list, silently, so a forgotten override can hide your change for weeks.

**When the same name sits in four files, nobody can predict the result. Set each variable in one place, plus its role default.**

Next, we put variables to work inside files.
"""

S1 = """
At the start of each play, the Gathering Facts step runs the setup module on every host. It collects facts, things Ansible learns about the server: its operating system and version, its memory and a lot more. Facts include its IP addresses, the numbers that identify it on a network. Running `ansible web1 -m ansible.builtin.setup -a 'filter=ansible_distribution*'` printed `Ubuntu`, `24.04` and `noble`. In a playbook you read them as `ansible_facts['distribution']`. A play that needs no facts can say `gather_facts: false` and save a few seconds per host.

Ansible also sets some magic variables itself:
- `inventory_hostname` is the host's name in the inventory, such as web1.
- `groups['web']` is the list of hosts in the web group.
- `hostvars['web1']` holds every variable of another host.

Templates are where variables and facts pay off. A template is a file with blanks that Ansible fills in for each host, like a form letter that prints a different name at the top of each copy. The template module reads a Jinja2 file on your Mac, fills it in for each host and copies the result to the server. Jinja2, the template language Ansible uses, has two kinds of markers:
- `{{ name }}` prints a value.
- `{% if %}` and `{% for %}` blocks add conditions and loops.

The role's `hello-devops.service.j2` is Day 36's systemd unit with variables for the user, the folder, the port and the number of workers. The load balancer's `nginx-lb.conf.j2` loops over `groups['web']`. It writes one `server` line per web host, with each host's `hello_devops_port` from `hostvars`. Add a third web server to the inventory, run the playbook, and nginx learns about it with no edit to the template.

The line `{{ ansible_managed }}` at the top prints `Ansible managed`, a warning to anyone who opens the file on the server. Templates render on the control node, so the servers do not need Jinja2. Templates shape files. Tasks need a little logic of their own too.
"""

S2 = """
Four task keywords cover most of the logic you will write:
- `loop:` runs a task once per item. The role copies `app.py` and `requirements.txt` with one task that loops over `hello_devops_files`, and `item` holds the current entry.
- `when:` runs a task only if a condition is true. The apt task has `when: ansible_facts['os_family'] == "Debian"`, so the role would skip it on a Red Hat server (another family of Linux) instead of failing.
- `notify:` names a handler, as on Day 36. The copy, pip and template tasks all notify `Restart hello-devops`, and the app still restarts once.
- `tags:` labels tasks, so you can run part of a playbook.

The role tags its tasks `install` or `config`. Running `ansible-playbook site.yml --list-tags` lists them, and `--tags config` ran only the settings file, the unit, the service and the nginx config. That is useful when you change one template and do not want to wait for apt and pip. The flag `--skip-tags install` does the opposite.

Handlers have one trap. When a task fails, the play stops for that host, and handlers that were already notified do not run. Say the copy of `app.py` changed, and then the pip task failed. The restart never happens. On the next run the copy reports ok, so nothing notifies the handler again, and the old code keeps running with the new file on disk. The flag `--force-handlers` runs notified handlers even after a failure. The playbook is getting long now, so it is time to pack it up.
"""

S3 = """
Day 36's `hello-devops.yml` puts all of the app's tasks and its handler into one playbook. A second playbook that needs the same app would have to copy all of it. A role packages that job once, much like a Terraform module on Day 34, and any play can use it.

A role is a folder with a fixed layout, so Ansible knows where to look in it. `ansible-galaxy role init roles/hello_devops` makes the empty skeleton, and the lab's role uses these parts:
- `tasks/main.yml` and `handlers/main.yml`, the tasks and their handlers.
- `templates/`, the `.j2` files, which a template task in the role finds by name alone.
- `defaults/main.yml`, settings meant to be overridden.
- `vars/main.yml`, the role's own fixed values.
- `meta/main.yml`, a description and the supported platforms.

A play uses the role with `roles: [hello_devops]`, so `site.yml` is two short plays. Put the role's name in front of its variables, as in `hello_devops_port`. All variables of a host share one pool of names, so a plain `port` in two roles would clash. ansible-lint, a checker we meet shortly, enforces this rule.

Modules come in collections, packages named `namespace.collection`. ansible-core ships `ansible.builtin`, with about 70 modules such as copy, template and apt. Everything else comes from collections such as `amazon.aws`, `community.general` or `community.docker`. A fully qualified name (FQCN) such as `ansible.builtin.copy` says exactly which collection a module comes from. Short names like `copy` still work, but two collections can ship a module with the same short name, so the lab writes full names everywhere.

List the collections a project needs in `requirements.yml`, with version ranges, and install them with `ansible-galaxy collection install -r requirements.yml`. It is the same idea as the `requirements.txt` list of Python packages in hello-devops: your laptop and CI get the same code. The big `ansible` package from Homebrew already bundles amazon.aws and many more. Roles and collections that other people wrote come from Ansible Galaxy, a public site for sharing them. Read one before you run it as root on your servers. A packed role is easy to share, which makes the next question urgent: what about its secrets?
"""

S4 = """
A playbook often needs a secret, such as a database password or an API token (a long password that one program uses to call another). Written in plain text in group_vars, it lands in git, and git history keeps it even after you delete the line. That is the spare key's hiding place, photocopied for every sitter.

Ansible Vault encrypts the secret with AES256, a strong standard cipher, and a password, so the scrambled text can sit in git. You have two ways to use it:
- `ansible-vault encrypt FILE` (or `create`) encrypts a whole file, names and values.
- `ansible-vault encrypt_string --name NAME 'value'` encrypts one value and prints a YAML block to paste into a normal vars file.

The difference showed up in the lab. With a whole encrypted file in `group_vars/web/`, even `ansible web -m ping` failed with `Attempting to decrypt but no vault secrets found`. Ansible decrypts such files while it loads the inventory. A single encrypted value is decrypted only when a task uses it, so ping and Day 36's playbooks keep working without the password.

That is why the lab's `group_vars/web/vault.yml` holds one `encrypt_string` value. The plain `vars.yml` next to it says `hello_devops_api_token: "{{ vault_hello_devops_api_token }}"`. The `vault_` prefix tells readers the real value is encrypted, and grep (the search command) still finds the plain name.

You give Ansible the password with `--ask-vault-pass` or `--vault-password-file .vault_pass`. Keep that file out of git, as the lab's `.gitignore` does, with mode 600, so only you can read it. Teams keep the real password in a password manager or a CI secret. The lab's token is fake, and its practice password is `practice-only-password`.

ansible-core 2.22 added secret masking: values decrypted from Vault print as `$REDACTED$`, even in `debug` output and in `--diff`. The same `debug` command on ansible-core 2.21, the version inside today's `ansible` package, printed the token in plain text. So the role also sets `diff: false` on the task that writes the secret, which keeps it out of the output on any version. Secrets are safe in git now. Next, we make sure mistakes do not get that far.
"""

S5 = """
Three checks catch most mistakes before a server sees them:
1. `ansible-playbook --syntax-check site.yml` reads the playbook and stops at YAML or structure errors. It contacts no servers.
2. `ansible-lint` checks style and known traps: short module names, `shell` where a module exists, tasks with no name, risky file permissions. The lab's `.ansible-lint` picks the strictest profile, `production`.
3. A real run against throwaway servers, done twice, where the second run must show `changed=0`.

Molecule automates the third check. It is a test tool for roles, playbooks and collections, kept by the Ansible project. A Molecule scenario creates test servers (often containers), applies your role, applies it again to prove that the second run changes nothing, runs your checks and deletes everything. Its current setup uses ordinary Ansible playbooks and inventory to create and destroy the test servers. The lab skips Molecule, because the compose servers already play that part by hand.

The lab's `.github/workflows/ansible.yml` runs the first two checks on every pull request. It installs ansible-core, ansible-lint and the collections, and it needs no servers and no secrets. Running playbooks from CI against real servers is the next step. That job needs an SSH key as a secret, a network path to the servers and the vault password.

Picture a team that still runs many VMs. It keeps one Ansible repo, with an inventory folder per environment and the same roles for staging and production. Every change goes through a pull request where CI runs ansible-lint and a syntax check, and a reviewer reads the `--check --diff` output for one staging host. The real run happens from a shared tool or a CI job with the SSH key as a secret, never from one person's laptop. So far our servers are three containers on a laptop. Real ones live in a cloud and come and go.
"""

S6 = """
A list of addresses goes out of date on a cloud, where servers start and stop all day. A dynamic inventory asks the cloud instead. The `amazon.aws.aws_ec2` inventory plugin reads a YAML file whose name must end in `aws_ec2.yml`. The lab's `aws/hello.aws_ec2.yml` asks one Region for running instances (EC2 servers) with the tag `Project=hello-devops`.

That is the tag Day 35's `default_tags` puts on everything Terraform creates, so an `aws_instance` you add there shows up by itself. Tag a Day 14 instance the same way and it appears too. The file also:
- names each host after its `Name` tag, or its instance ID,
- turns tags into groups, so `Role=web` becomes the group `role_web`,
- sets `ansible_host` to the public IP and `ansible_user` to `ubuntu`.

It needs the amazon.aws collection, boto3 (the Python library for AWS, from Day 16) next to Ansible (`uv tool install ansible-core --with boto3`) and the AWS login from Day 13. Then `ansible-inventory -i aws/hello.aws_ec2.yml --graph` lists the servers, and two `-i` options combine it with `inventory.ini`. Go deeper runs the plugin against an AWS emulator, a program that pretends to be AWS, so you can try it with no account.

Day 14 recommends instances with no open SSH port. Ansible can reach those through SSM Session Manager, AWS's way to reach a server without SSH, with the `amazon.aws.aws_ssm` connection plugin. It also needs an S3 bucket for file transfers.

Ansible is one of several ways to get software onto a server:
- cloud-init user data (Day 14) runs once, at first boot. It is enough for a server you never change.
- Ansible changes long-lived servers again and again, and undoes drift.
- Packer bakes an image with everything installed, often by running Ansible inside the build, so new servers start ready.
- Kubernetes replaces containers instead of changing them.

For a fleet of long-lived VMs, I would pick Ansible. For anything that can be a container, the image is the configuration, and Ansible's part shrinks to preparing the machines underneath. That is where the course goes next: a world where nobody repairs a running container, because something replaces it.
"""

new = {
    "goal": "By the end you can turn a playbook into a role with defaults and templates, decide where each variable belongs, keep a secret in Vault, check the code in CI, and let Ansible find EC2 servers by tag.",
    "opening": """The house sitter's checklist works on every house in the street, and now the owners start asking for small changes. The houses on the left want the heating at 19 degrees. The corner house is trying a new kind of plant food first, before anyone else. Each owner writes a note, and soon there are notes in the checklist, on the fridges and on one front door.

Then someone adds a helpful line to the checklist: "spare key under the blue pot". The checklist gets photocopied for every new sitter, and the key's hiding place goes with it. Writing exceptions and secrets straight onto the list is the quick thing to do, which is why it happens.

Last time, our first playbook set up three servers, with every value typed in. In this lesson, we'll learn where each note belongs and which one wins. Then we'll fill in files per server, pack the checklist into a role, lock a secret away, and find servers in AWS. Before we start, make a guess, and keep it in mind.""",
    "guess": (
        "A role's defaults/main.yml sets `hello_devops_greeting: Hello`. group_vars/web.yml sets it to `Hi`, and host_vars/web2.yml sets it to `Hey`. What does web2 get?",
        "Role defaults have the lowest precedence of all, so the inventory can override them. Host variables beat group variables, because a value for one host is more specific than a value for its whole group.",
    ),
    "terms": [
        "The rule that decides which value wins when one variable is set in several places.",
        "Something Ansible learns about a server at the start of a play, such as its operating system or IP address.",
        "A text file with {{ variables }} and {% loops %} that Ansible fills in for each host.",
        "A folder with a fixed layout (tasks, handlers, templates, defaults) that packages one job for reuse.",
        "A package of modules, plugins and roles, such as amazon.aws, installed with ansible-galaxy.",
        "A fully qualified collection name: namespace.collection.module, such as ansible.builtin.copy.",
        "Encryption built into Ansible, so secrets can sit in git as unreadable text.",
        "An inventory plugin that asks a cloud, such as AWS, which servers exist right now.",
    ],
    "sections": [
        ("Notes in many places: where variables live and which one wins", S0),
        ("Facts and templates: one file, filled in per host", S1),
        ("Loops, conditions, handlers and tags", S2),
        ("Packing it up: roles and collections", S3),
        ("Ansible Vault: secrets you can commit", S4),
        ("Lint, test and run it from CI", S5),
        ("Real servers: find them in AWS, and know when not to use Ansible", S6),
    ],
    "aside": {
        "title": "What are AWX and Ansible Automation Platform?",
        "body": "Teams that run Ansible a lot often move it off laptops and into AWX or Red Hat Ansible Automation Platform. Both add a web page, an API, schedules, access control and a log of every run. AWX is the open source project that the Red Hat product is built from. Its releases have been paused since July 2024, during a large rewrite.",
        "after": 5,
    },
    "diagram_caption": "Higher wins: web2 gets its host_vars greeting unless -e overrides it, and role vars beat the whole inventory.",
    "worked": [
        "Let Ansible make the role's skeleton. Then move Day 36's tasks into `tasks/main.yml`, the restart into `handlers/main.yml`, and the unit file into `templates/` as a `.j2` file with variables. Delete `files/`, `tests/` and the README, which this role does not need.",
        "Lint before the first run. The first version of the role used short names like `hello_port`, and ansible-lint stopped with ten findings of one rule (one is shown). After renaming all ten to start with `hello_devops_`, the strictest profile passed. You will also see two deprecation warnings about the oneline and tree callbacks. They come from ansible-lint 26.11 running on ansible-core 2.22, not from your code.",
        "Write the practice vault password into `.vault_pass` and run `site.yml` over the servers from Day 36, with `--diff`. The template replaces Day 36's fixed unit file, so the diff shows the new lines. The handler restarts the app once per host, and lb1 gets its load balancer config. The output is trimmed to web1's unit and the recap.",
        "Each web server answers with its own greeting, because web2 has a host_vars file. Through the load balancer, requests take turns between web1 and web2. The visit counter jumps around because each of gunicorn's two workers counts in its own memory: there is no Redis here.",
        "Before you trust a change, ask Ansible which value each host sees. `debug` prints a variable after all the precedence rules. Extra vars from `-e` beat everything, for this one command only.",
        "Preview a version bump on one server. The unit's diff is one line. The settings file reports changed with no diff, because the role sets `diff: false` on that task. The pip task also says changed, although a real run reports ok: with a requirements file, the pip module cannot tell in check mode. Output trimmed.",
        "Last, the secret. ansible-core 2.22 masks values that came from Vault, so `debug` cannot leak the token. On the server the token is in plain text in `/etc/hello-devops.env`, with mode 0640, so only root and the app's `hello` group can read it.",
    ],
    "task": {
        "steps": [
            "Start the servers if needed, write the practice password into `.vault_pass`, and run `ansible-playbook site.yml --vault-password-file .vault_pass` once.",
            "Create a role `roles/lb` with `ansible-galaxy role init`, and delete the folders you will not use.",
            "Move the three tasks and the handler of the lb play into the role, and move `nginx-lb.conf.j2` into the role's `templates/`. Make the listen port a default called `lb_listen_port` and use it in the template.",
            "Change the lb play in `site.yml` to `roles: [lb]` and run with `--check --diff`. Nothing should change on lb1.",
            "Release version 1.1.0 to the canary first: set `hello_devops_version` in `host_vars/web2.yml`, run with `--limit web2`, and curl `localhost:8180` a few times.",
            "Make a vault password of your own. Encrypt a new fake token with `encrypt_string` and replace the value in `group_vars/web/vault.yml`. From now on, run with `--ask-vault-pass`.",
            "Run `ansible-lint` and fix what it finds.",
            "Move the version to `group_vars/all.yml` for everyone, remove it from host_vars, and run `site.yml` twice.",
        ],
        "hints": [
            "Inside a role, `ansible.builtin.template` with `src: nginx-lb.conf.j2` looks in the role's own templates/ folder first.",
            "ansible-lint wants a role's variables to start with the role's name, so `lb_` is right for a role called lb.",
            "`ansible-vault encrypt_string --ask-vault-pass --name vault_hello_devops_api_token 'my-fake-token'` prints a block you can paste into the file as it is.",
        ],
        "done_when": "You are done when ansible-lint passes, a second run of site.yml shows `changed=0` on all three servers, and `curl localhost:8180` shows version 1.1.0 from both web1 and web2.",
    },
    "explain_back": (
        "Explain in 3 to 4 sentences how the lab's role gives web2 a different greeting from web1, and why the role keeps the greeting in defaults. Mention precedence and templates.",
        "The role's defaults/main.yml sets a greeting with the lowest precedence of all. The file group_vars/web/vars.yml overrides it for both web servers, and host_vars/web2.yml overrides it again for web2 only, because host variables beat group variables. The template module then fills the greeting into the settings file on each host, so one template gives each server its own file. If the greeting were in the role's vars/ folder, it would beat group_vars and host_vars, and nobody could change it from the inventory.",
    ),
    "recap": [
        "Put settings in role defaults, shared values in group_vars, exceptions in host_vars, and one-off overrides in -e.",
        "Facts and magic variables such as groups and hostvars feed templates, which are filled in on the control node.",
        "loop, when, notify and tags cover most task logic, and a failed play can lose a pending restart.",
        "A role has a fixed layout and puts its name in front of its variables. Collections come from requirements.yml.",
        "Encrypt single values with encrypt_string, keep the vault password out of git, and expect $REDACTED$ in 2.22 output.",
        "Lint in CI and find cloud servers by tag. Ansible changes servers in place, which matters less once apps run in containers.",
    ],
    "closing": """We started with notes on fridges and a spare key's hiding place on a photocopied list. Now each note has its place and a clear order of who wins, one template fills in every server's files, and the secret sits in git as unreadable text.

In the lab, pick any variable and run `ansible web -m ansible.builtin.debug -a var=NAME`. If the answer surprises you, search for that name across `group_vars`, `host_vars` and the role, and see how many notes it has.

Next, we'll leave servers we repair and meet a system that replaces things instead. What if a manager kept every table staffed, no matter who called in sick?""",
    "check": [
        ("A role's `vars/main.yml` sets `app_port: 9000`. A teammate puts `app_port: 8000` in host_vars/app1.yml and runs the playbook. Which port does app1 get?",
         "Role vars sit above all inventory variables in the precedence list. Move the value to defaults/ so the inventory can change it."),
        ("`group_vars/db/vault.yml` is one whole file encrypted with ansible-vault. A teammate without the password runs `ansible db -m ansible.builtin.ping`. What happens?",
         "A fully encrypted vars file is decrypted when the inventory loads. Values made with encrypt_string are decrypted only when a task uses them."),
        ("With the lab's `hello.aws_ec2.yml`, you start a new instance tagged `Project=hello-devops` and `Role=db`. Where does it appear in `ansible-inventory --graph`?",
         "The plugin puts every matching instance in aws_ec2, and keyed_groups turns its Role tag into a role_ group."),
    ],
    "interview": [
        ("How does Ansible decide which value a variable gets?",
         "Ansible has a fixed precedence order with 22 levels. The ones that matter most, from weak to strong, are role defaults, group_vars/all, group_vars for a group, host_vars, play vars and role vars. Extra vars from -e always win. More specific inventory beats less specific, so a host beats its group. I keep each variable in one place plus its role default, and when in doubt I check with the debug module or `ansible-inventory --host`."),
        ("How do you keep secrets in an Ansible repository?",
         "I encrypt them with Ansible Vault, usually value by value with encrypt_string, in a vault_-prefixed variable that a plain vars file refers to. The vault password stays outside git: in a password manager, a CI secret or a mode-600 file listed in .gitignore. Tasks that write secrets get `diff: false` or `no_log`, and ansible-core 2.22 also masks decrypted values in its output. When there are many secrets, or they change often, teams read them at run time from a secrets manager with a lookup plugin instead."),
        ("When would you choose Ansible, and when Packer, cloud-init or Kubernetes?",
         "cloud-init runs once at first boot, which suits simple servers that never change. Ansible fits long-lived servers that need repeated changes and drift fixes, and it also manages network devices. Packer bakes the same changes into an image, so new servers start ready and nothing changes in place, which pairs well with autoscaling (adding and removing servers as load changes). For apps in containers, Kubernetes replaces containers instead of changing them, and Ansible's job shrinks to preparing the machines underneath."),
    ],
    "deeper": """
The aws_ec2 plugin only reads from AWS, so you can try it against an emulator. The moto library imitates AWS in Python, and its server mode answers on a local port. Everything below is free and stays on your Mac.

1. Give Ansible boto3 and the collection: `uv tool install ansible-core --with boto3`, then `ansible-galaxy collection install -r requirements.yml`.
2. In a second terminal, start the emulator: `uvx --from 'moto[server]' moto_server -p 5055`.
3. Back in the lab folder, use fake credentials so nothing can reach a real account: `export AWS_ACCESS_KEY_ID=testing AWS_SECRET_ACCESS_KEY=testing AWS_URL=http://127.0.0.1:5055`. The plugin reads `AWS_URL` as the address to send its requests to.
4. Create two instances with the course tag and one without, using `aws ec2 run-instances` from Day 13 with `--endpoint-url http://127.0.0.1:5055 --region us-east-1`. moto accepts any image ID, such as `ami-12345678`. Tag them with `--tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=hello-web-1},{Key=Project,Value=hello-devops},{Key=Role,Value=web}]'`.
5. Run `ansible-inventory -i aws/hello.aws_ec2.yml --graph`.

When we did this, the graph showed `hello-web-1` and `hello-web-2` in two groups, `aws_ec2` and `role_web`. The third instance, tagged `Project=billing`, was missing, because the filter dropped it. Running `ansible-inventory -i aws/hello.aws_ec2.yml --host hello-web-1` printed what AWS knows about the host, including `ec2_tags`, `instance_type`, `private_ip_address` and the `ansible_host` that `compose` set from the public IP.

Two details matter before you use this for real. First, the plugin's old `tags` host variable is being replaced by `ec2_tags`, and `use_deprecated_tags: false` in the lab's file switches the old one off now. Second, a dynamic inventory works with group_vars like any other. A file `group_vars/role_web.yml` next to your playbooks applies to every instance tagged `Role=web`, whatever its name. With `--playbook-dir .`, `ansible-inventory --host` showed a test variable from such a file on hello-web-1.

Two `-i` options merge inventories: `ansible-inventory -i inventory.ini -i aws/hello.aws_ec2.yml --graph` printed the lab's three containers and the cloud hosts in one tree. Stop moto with Ctrl+C when you are done. Nothing was created in AWS.
""",
    "drop": ["analogy", "mistake", "real_world"],
}

apply(9, "d37", new)
