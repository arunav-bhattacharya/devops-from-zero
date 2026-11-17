import sys
sys.path.insert(0, ".")
from common import apply

S0 = """
Last part, Terraform built things: on Day 35 it created resources in AWS. Before that, on Day 14, a user data script installed hello-devops on one EC2 server, a server rented from Amazon. A user data script holds commands AWS runs once, when a server first starts. That works for one server. It gets hard with twenty, and harder a year later, when nobody remembers which ones got last month's fix.

That is the neighbour's house, twenty times over. Configuration management is the answer: you write down what each server should have, such as its packages (installed programs), files, users and services (programs that run in the background). A tool then makes every server match, every time you run it. Terraform is good at creating machines through a cloud's API. Ansible, today's tool, is good at what happens inside them after they start.

How much of this you need depends on how you run servers:
- Mutable infrastructure: servers live for months, and you change them in place. Ansible was built for this.
- Immutable infrastructure: you never change a running server. You build a new image, start new servers from it and delete the old ones. Docker images (Day 18) and Kubernetes (Part 10) work this way.

Most new apps ship as containers, so you may write little Ansible for your own app. It still has plenty of work:
- VMs (whole computers simulated in software) that will not move to containers, such as databases, build machines or old Java apps
- setting up fresh machines, including the ones a Kubernetes cluster runs on
- network devices such as switches and routers
- changes across a whole fleet, like a security patch on every server this afternoon

Picture that last one. OpenSSH, the program behind SSH logins, ships a security fix, and every VM a team runs needs it the same day. With Ansible, someone previews the patch on two servers, then runs it on the rest, and Ansible's summary lists any server that failed. How does one laptop reach all those servers? Through a door they already have.
"""

S1 = """
Ansible runs on one machine, the control node, which is your Mac. The servers it looks after are called managed nodes. Nothing of Ansible is installed on them, and no Ansible program waits there for orders. That is what agentless means: there is no agent, no helper program living on each server.

Older tools such as Puppet and Chef do install an agent on every server, and the agent fetches its settings from a central server. Without an agent, there is nothing to install or keep updated on the servers. A fresh Ubuntu server is ready for Ansible as soon as you can log in to it.

A managed node needs two things: an SSH login (a secure way to log in and run commands, from Day 7) and Python 3. For every task, Ansible does this on each server:
1. It opens an SSH connection, or reuses an open one.
2. It copies a small Python program, the module, into a temporary folder.
3. It runs the module with the server's python3. The module checks the server and fixes what differs.
4. It reads the JSON result the module prints, then deletes the temporary folder.

That result has a `changed` field, and it is where the green ok and the yellow changed in Ansible's output come from. Ansible works on five servers at a time by default, and the `-f` option raises that number.

Network switches are the exception to the Python rule. Their modules run on the control node and talk to the device over SSH or an API. Our servers are ordinary ones, so next we need Ansible on the Mac, and some servers to practise on.
"""

S2 = """
Ansible comes as two Python packages:
- `ansible-core` is the engine: the commands and the built-in modules, called `ansible.builtin`.
- `ansible` is ansible-core plus a large set of community collections (bundles of extra modules), such as `amazon.aws`. It is much bigger, and its current release still ships ansible-core 2.21.

Start with ansible-core, installed as a tool with its own Python. Pick one way:
- `uv tool install ansible-core`
- `pipx install ansible-core`
- `brew install ansible`, for the big package

ansible-core 2.22, the current version, needs Python 3.13 or newer on the control node. The `python3` that comes with macOS is older, so do not run plain `pip install` with it. uv downloads a suitable Python by itself. Check the current docs for the install command, then run `ansible --version`.

Now the houses to look after. The lab's `compose.yaml` starts three Ubuntu 24.04 containers: web1 and web2 for the app, and lb1 for nginx, a web server that will later share visitors between them. Each one runs sshd, the program that answers SSH logins, and has python3, like a fresh cloud server.

The script `./setup.sh` makes an SSH key for the lab in `.keys/`. It builds the image with only the public half of the key inside, starts the servers and waits until SSH answers. These servers run systemd, the program that starts and watches services, so `systemctl` works as it did on Day 6. They are not quite real servers, and the box below says how they differ. With three servers running, Ansible needs a list of them.
"""

S3 = """
A house sitter for a whole street needs the addresses, and Ansible needs the same. An inventory lists your servers and sorts them into groups. The lab's `inventory.ini` has three groups:
- `[web]` holds web1 and web2.
- `[lb]` holds lb1.
- `[lab:children]` is a group of groups: everything in web and lb.

A host line can carry host variables, settings for that host only. `web1 ansible_host=127.0.0.1 ansible_port=2201` names the host web1 and tells Ansible where its SSH really answers. Every inventory also has two groups you never write: `all`, with every host, and `ungrouped`, for hosts in no group.

The file `inventory.yml` is the same inventory in YAML, a text format that shows nesting by indenting lines. YAML is also easy for a program to write. The command `ansible-inventory --graph` prints the tree of groups, and both files give the same one.

Ansible reads its settings from the first config file it finds, in this order:
1. The file named in the `ANSIBLE_CONFIG` environment variable.
2. `ansible.cfg` in the current folder.
3. `~/.ansible.cfg` in your home folder.
4. `/etc/ansible/ansible.cfg`.

So run Ansible from the lab folder. Its `ansible.cfg` picks the inventory, logs in as `ubuntu` with the lab key and says where roles (Day 37) live. It also gives SSH a known_hosts file of the lab's own, the list of server fingerprints SSH has already seen. The option `StrictHostKeyChecking=accept-new` trusts a new server the first time and refuses a changed fingerprint later, the same rule as Day 7. The setting `interpreter_python = auto_silent` hides a warning about which Python Ansible found on each server. The list is ready. Let's send one instruction to every house on it.
"""

S4 = """
An ad-hoc command runs one module once, straight from the terminal. Its shape is `ansible PATTERN -m MODULE -a ARGUMENTS`. The pattern is a host or a group from the inventory, such as `all`, `web` or `web1`.

`ansible all -m ansible.builtin.ping` logs in to every server and runs the ping module. It answers `pong` when SSH and Python work. `ansible.builtin.ping` is the module's full name: the ping module from the builtin collection inside ansible-core. Day 37 explains the naming.

Without `-m`, Ansible uses the command module, which runs a program directly, with no shell. The shell is the program that reads what you type in a terminal, and it is what understands pipes, `>`, `;` and `&&`. So those do not work in the command module. `ansible web1 -a 'cat /etc/os-release | grep PRETTY'` failed with `cat: '|': No such file or directory`, because cat got the pipe as a file name. The shell module runs the same line through `/bin/sh`, and it printed the one line we wanted.

Add `-b` (become) to run as root, the all-powerful user, through sudo. `ansible web1 -a whoami` printed `ubuntu`, and with `-b` it printed `root`. Modules you will use all the time:
- `ansible.builtin.apt`, or the generic `package`, installs packages.
- `ansible.builtin.copy` puts a file on the server.
- `ansible.builtin.service` starts, stops, restarts and enables services.

Our first `apt` call taught us something. We asked for jq, a small tool that reads JSON. It installed on web1 but failed on web2 with `No package matching 'jq' is available`. Ubuntu's container image ships with no package list, and an earlier command of ours had refreshed that list on web1 only. Adding `update_cache=true` runs `apt-get update` first. That run also showed something quieter: on the second try, web1 had nothing to do.
"""

S5 = """
Back to the neighbour's plants. Watering them is a chore, and doing it twice drowns them. Damp soil is a result, and checking it twice is harmless. Ansible modules are written as results. `name=jq state=present` means "jq must be installed".

The apt module checks first. If jq is there, it does nothing and reports ok. If not, it installs jq and reports changed. So running a task twice is safe, and the second run tells you whether anything had drifted. This property is called idempotence, and it is the main thing Ansible gives you over a shell script.

**A chore repeated does harm, and a result checked twice does none. Write tasks as results.**

The command and shell modules cannot know what your command did, so they report changed every time. A task such as `shell: apt-get install -y nginx` turns Ansible back into a slow shell script. It reports changed on every run, a preview cannot see inside it, and any handler it notifies fires every time. Look for a real module first, with `ansible-doc -l | grep apt`, and keep `command` for jobs that no module covers. The command `ansible-doc -l` lists every module you have, and `ansible-doc ansible.builtin.apt` shows one module's options and examples.

Two flags show what a run would do before it does it:
- `--check` runs every task in a dry mode. Modules report what they would change, and change nothing.
- `--diff` prints the lines a task changes in a file, like `git diff`.

Together they work like Terraform's plan, with one difference. Ansible has no state file, so the preview comes from the real servers at that moment. Check mode is still a prediction. A task that depends on an earlier task's result can guess wrong, because the earlier task did not really run.

No state file also means no memory of past runs. A good house sitter would notice a broken window that no line on the list mentions. Ansible never does. Delete a resource block in Terraform and the next plan destroys the object, because the state remembers it. Delete the jq task from a playbook and jq stays installed. To remove something, you write a task that says so, such as `state=absent`. Single commands are handy, but a real checklist has many lines, and it belongs in a file.
"""

S6 = """
A playbook is that checklist written down: a YAML file with a list of plays. A play names its hosts and lists its tasks, and each task calls one module with arguments, like an ad-hoc command saved in a file. The lab's `first-playbook.yml` has two plays:
1. "Basics on every server" installs tree and htop and writes `/etc/motd` (the message shown at login) on the whole lab group.
2. "Web server on the load balancer" installs nginx on lb1, gives it a site config and a page, and starts it.

Ansible runs the first task on every host of the play, then the second task, and so on from top to bottom. Setting `become: true` on a play makes every task use sudo. Each play starts with Gathering Facts, where Ansible collects details about each server. Day 37 puts them to use.

A handler waits until something notifies it, like a note on the checklist saying "if you changed the boiler setting, restart the boiler at the end". The site config task has `notify: Reload nginx`. When that task reports changed, the handler runs once, at the end of the play. When the file was already right, nginx is left alone. Ten tasks can notify the same handler, and it still runs once.

The run ends with PLAY RECAP, one line per host:
- `ok` counts every task that succeeded, changed or not.
- `changed` counts the tasks that changed something.
- `unreachable` means SSH failed, and `failed` means a task failed.

A failed task stops the play for that host only. Its notified handlers do not run, which is how a restart gets lost. The hands-on brings Day 6 back: `ansible.builtin.systemd_service` with `enabled: true` does what `systemctl enable` did.

Our first checklist works, and it is safe to run twice. It also has every value typed straight in, and every server gets the same files. The next lesson makes it fit each server, and keeps its secrets safe.
"""

new = {
    "goal": "By the end you can say what Ansible does that Terraform does not, list servers in an inventory, run ad-hoc commands and a first playbook against three practice servers, and explain why a second run changes nothing.",
    "opening": """Your neighbour goes away for a week and asks you to look after her house. She leaves a list of chores: water the plants, turn the heating on, lock the back door. On day one you do every chore. On day two you water the plants again, as the list says. By Friday the pots are swimming.

The list was the trouble, not you. It said what to do, when it should have said how the house should be: soil damp, room at 20 degrees, door locked. A list of chores is easy to write, because that is how we think about work. A list of results is the one you can follow twice without harm.

Last time, Terraform built storage and servers in a real cloud. It built the house, but something still has to set up what runs inside it. In this lesson, we'll meet Ansible, list our servers, send one command to many of them, and write a first checklist that is safe to run twice. Before we start, make a guess, and keep it in mind.""",
    "guess": (
        "A playbook installs nginx and writes its config file. It succeeds. You run the same playbook again a minute later. What does Ansible do?",
        "Each module looks at the server first and acts only when something differs, so the second run reports ok everywhere. Ansible keeps no state file like Terraform's. It checks the real server every time.",
    ),
    "terms": [
        "Keeping the programs, files and services on many servers the way you wrote them down as code.",
        "The machine you run Ansible from. In this course, your Mac.",
        "A server that Ansible looks after. It needs an SSH login and Python, but no Ansible.",
        "A file that lists your servers, sorts them into groups and says how to reach them.",
        "A small program Ansible sends to a server to do one job, such as installing a package.",
        "Safe to repeat: running it again when nothing needs to change changes nothing.",
        "A YAML file of plays. Each play runs a list of tasks on a group of servers.",
        "A task that runs only when another task reports a change, usually a restart or a reload.",
    ],
    "sections": [
        ("Terraform built the server. Something still has to set it up", S0),
        ("No helper on the server: everything happens over SSH", S1),
        ("Install Ansible, and start three practice servers", S2),
        ("The inventory: which servers exist", S3),
        ("Ad-hoc commands: one module on many servers", S4),
        ("Results, not chores: ok, changed and a preview", S5),
        ("A first playbook: plays, tasks, handlers and the recap", S6),
    ],
    "aside": {
        "title": "How are the practice servers different from real ones?",
        "body": "They are containers that run systemd as PID 1, the first program a machine starts. A plain container has no systemd, and systemd inside Docker needs extra rights: `privileged: true`, the host's cgroup tree and some tmpfs mounts. Those rights are fine on your laptop and wrong anywhere else. All three share the kernel (the core of the operating system) of Docker's VM, so `uptime` shows that VM's uptime. There is no real boot or disk setup, and the network is IPv4 only. They all live on 127.0.0.1 and differ by SSH port: 2201, 2202 and 2203.",
        "after": 2,
    },
    "diagram_caption": "For each task, Ansible logs in over SSH, runs a small Python module on the server and reads back ok or changed.",
    "worked": [
        "Start the practice servers from the lab folder, then check that Ansible can reach one. The first `setup.sh` takes a minute or two while Docker builds the image. `pong` means SSH, the key and Python all work.",
        "Run the first playbook. Every task that installs or writes something reports changed, and the handler runs because the site config changed. The output is trimmed to the second play and the recap, and the rows of stars after each banner are cut.",
        "Run it again without changing anything. Every task now reports ok, and the handler stays quiet because nothing notified it. lb1 shows ok=8 instead of 9 for the same reason. This run took about 10 seconds and changed nothing, which is what you want from a tool you may run every day.",
        "In `first-playbook.yml`, add a line `<p>Deployed by Ansible.</p>` under the h1 line of the page task. Preview it with `--check --diff`. Ansible shows the line it would add and counts the task as changed, but `curl` proves the page on lb1 is still the old one.",
        "Run it for real. Then change a server by hand, the way a quick fix often happens: add a line to `/etc/motd` on web2 over SSH. The next run with `--diff --limit web2` puts the file back and shows exactly what it removed. A difference between the code and the server is called drift, and a regular Ansible run finds it and undoes it.",
        "Last, make the handler fire. In `files/nginx-site.conf`, add a comment and `add_header X-Served-By $hostname;` under `server_tokens off;`, then run against lb only. The config task changes, so the handler reloads nginx at the end of the play, and the new header appears. Undo both edits afterwards, or keep them: the next run makes the servers match whatever the files say.",
    ],
    "task": {
        "steps": [
            "Keep the lab folder next to your hello-devops repo (`~/code/ansible-lab` and `~/code/hello-devops`). The hello-devops app is the course's tiny web app that answers every visit with a greeting and a count of visits. Start the servers with `./setup.sh` and check them with `ansible all -m ansible.builtin.ping`.",
            "Create `my-hello.yml` with one play for the `web` group and `become: true`.",
            "Add tasks that install `python3-venv` and `python3-packaging` with apt, create a system user `hello` with no login shell, and create `/opt/hello-devops`.",
            "Copy `app.py` and `requirements.txt` from your hello-devops repo into `/opt/hello-devops`.",
            "Install the requirements into `/opt/hello-devops/venv` with the `ansible.builtin.pip` module. A venv is a private folder of Python packages for one app.",
            "Write a systemd unit (Day 6) that runs gunicorn on `0.0.0.0:8000` as the `hello` user, keep it in `files/`, and copy it to `/etc/systemd/system/hello-devops.service`.",
            "Start and enable the service with `ansible.builtin.systemd_service`. Add a handler that restarts it, and notify it from the tasks that copy code or the unit.",
            "Run the playbook, then `curl -s localhost:8101` and `curl -s localhost:8102`. Run it a second time and read the recap.",
            "Add `Environment=\"GREETING=Hi from systemd\"` to the unit (the quotes keep the spaces), run again, and check that only that task and the handler changed. Then run `docker restart ansible-web1` and curl web1 again.",
            "Compare your playbook with the lab's `hello-devops.yml`, one possible answer.",
        ],
        "hints": [
            "If the pip task fails with `No module named 'packaging'`, the pip module needs the python3-packaging package on the server, not on your Mac.",
            "`src:` in a copy task can be a path on your Mac, such as `\"{{ playbook_dir }}/../hello-devops/app.py\"`.",
            "After a unit file changes, systemd must reload its files. `daemon_reload: true` on the systemd_service task and on the handler does that.",
        ],
        "done_when": "You are done when both curls return hello-devops JSON, a second run shows `changed=0` for web1 and web2, and web1 answers again after `docker restart ansible-web1`.",
    },
    "explain_back": (
        "Explain in 3 to 4 sentences what happens when you run a playbook against three servers. Mention SSH, modules, idempotence and handlers.",
        "Ansible reads the inventory, logs in to each server over SSH and runs the tasks in order. For each task it copies a small Python module to the server, runs it with python3 and reads back a JSON result. The module checks the server first and changes only what differs, so a second run reports ok and changes nothing. A handler, such as a reload, runs once at the end of the play, and only if a task that notified it reported a change.",
    ),
    "recap": [
        "Terraform creates servers, and Ansible sets up what runs inside them, as often as you like.",
        "Ansible is agentless: a managed node needs only an SSH login and Python 3.",
        "The inventory lists hosts in groups, and ansible.cfg in the current folder sets the defaults.",
        "Modules describe a result and report ok or changed. command and shell always say changed.",
        "--check --diff previews a run against the real servers, because there is no state file. Nothing is removed unless a task says so.",
        "Handlers run once at the end of a play, and only after a change.",
    ],
    "closing": """We started with a neighbour's list of chores and plants drowning by Friday. Ansible's modules are a list of results instead: each one looks at the server first, so the second run of our playbook changed nothing at all.

In your own playbook, look for every `shell:` and `command:` task. Each one is a chore, not a result, and it will say changed on every run until you replace it with a module or teach it when to say ok.

Next, we'll make the checklist fit each house. How can one playbook give every server its own settings, and keep a password in git without anyone reading it?""",
    "check": [
        ("A nightly playbook has the task `ansible.builtin.shell: echo 'vm.swappiness=10' >> /etc/sysctl.conf`. What does the file look like after a week?",
         "The shell module runs its command every time and cannot know it already ran. `ansible.builtin.lineinfile` with `line:` would add the line once."),
        ("The inventory has `[db]` with db1 and db2, `[web]` with web1, and `[prod:children]` listing web and db. Which hosts does `ansible prod -m ansible.builtin.ping` reach?",
         "A :children group contains every host of each of its child groups."),
        ("Three tasks in one play have `notify: Restart app`. On this run two of them report changed and one reports ok. What happens?",
         "A notified handler runs once, at the end of the play, however many tasks notified it."),
    ],
    "interview": [
        ("What does agentless mean for Ansible, and what does a server need before Ansible can manage it?",
         "Ansible runs on a control node and leaves nothing running on the servers it manages. For each task it connects over SSH, copies a small Python module to a temporary folder, runs it and deletes it. So a Linux server needs an SSH login, usually with sudo rights, and Python 3. Network devices are the exception: their modules run on the control node and talk to the device over SSH or an API. You have nothing to install or upgrade on the servers, but the control node must be able to reach every one of them."),
        ("What is idempotence, and how do you keep a playbook idempotent?",
         "An idempotent task gives the same result however often it runs, so a second run with nothing to do changes nothing. Ansible modules do this by checking the current state first and acting only on a difference. I keep playbooks idempotent by using modules that describe a state, such as apt with state=present, copy or template. Where I must use command or shell, I add `creates:` or `changed_when:` so the task can report ok. The test is simple: run the playbook twice and expect changed=0 the second time."),
        ("When would you use the command or shell module?",
         "Only when no module does the job, for example a vendor's own command-line tool or a one-off migration command of your own app. The command module runs the program directly with no shell, which is safer, but pipes and redirects do not work. The shell module runs the line through /bin/sh, so pipes work, but you have to quote carefully. Both always report changed, so I add `changed_when` or `creates` to keep the recap honest and stop handlers from firing on every run."),
    ],
    "deeper": """
Run `ansible web1 -m ansible.builtin.ping -vvv` and read the lines that start with `SSH: EXEC`. Verbose mode shows every command Ansible sends. With pipelining switched off (`ANSIBLE_PIPELINING=False`), one ping took seven SSH or SFTP calls (SFTP copies files over SSH):
1. Ask the server for the home folder of `ubuntu`.
2. Make a private temporary folder under `~/.ansible/tmp`.
3. Look for a Python, trying python3.15, python3.14 and so on down the list.
4. Copy the module over SFTP as `AnsiballZ_ping.py`.
5. Make it executable.
6. Run it with `/usr/bin/python3.12`.
7. Delete the temporary folder.

With the lab's `pipelining = True`, the same ping took two calls. Ansible found Python, then sent the module through the open connection's standard input, so nothing was written to disk. The `ControlPersist=60s` option in `ansible.cfg` keeps one SSH connection open for a minute, so the next tasks skip the login. Pipelining needs sudo to work without a terminal, which is the default on Ubuntu.

Three settings change how a run behaves on many servers:
- `forks`, or `-f 20` on the command line, sets how many hosts Ansible works on at once. The default is 5.
- `serial: 2` in a play finishes the whole play on two hosts before it starts the next two. That is how you roll a change through a fleet without touching every server at the same moment.
- `ansible.builtin.raw` sends a plain command over SSH with no Python. Teams use it to install Python on a bare machine, then switch to real modules.

Ansible pushes from a control node. `ansible-pull` turns that around: each server clones a git repo and runs a playbook on itself, often from a timer. It suits machines your control node cannot reach, such as laptops on home networks.
""",
    "drop": ["analogy", "mistake", "real_world"],
}

apply(9, "d36", new)
