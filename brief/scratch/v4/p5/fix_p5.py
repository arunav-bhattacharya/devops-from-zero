"""First-principles review of content/p5.json (Days 17 to 22, Docker).
Exact old/new replacements in prose fields only. Re-runnable: an edit whose new
text is already present is skipped. Run from the repo root:
    python3 brief/scratch/v4/p5/fix_p5.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p5.json"

# (lesson id, path inside the lesson, old, new)
EDITS = [
    # ---------------- d17: what a container really is ----------------
    ("d17", ("sections", 1, "body"),
     "You can watch them work. `docker run --rm alpine ps` lists a single process, `ps` itself, running as PID 1. "
     "The machine runs hundreds of processes, and the container sees none of them.",
     "You can watch them work with Alpine, a tiny Linux image. The command `docker run --rm alpine ps` lists a single process, "
     "`ps` itself, running as PID 1, the number a system gives its first process (Day 6). "
     "The machine runs hundreds of processes, and the container sees none of them. "
     "In the same way, `docker run --rm alpine ls /` lists Alpine's own folders. "
     "Those files come from the image, and none of the VM's files show up."),

    ("d17", ("sections", 1, "body"),
     "- cgroups (control groups) give it a budget: a cap on how much CPU and memory it may use.",
     "- cgroups (control groups) give it a budget: a cap on CPU and memory. Past the memory cap, the kernel kills it."),

    ("d17", ("sections", 3, "body"),
     "Leave the tag out and Docker uses `latest`, which is only a default label and does not promise the newest version.",
     "Leave the tag out and Docker uses `latest`, which is only a default label and does not promise the newest version.\n\n"
     "Put together, `docker run nginx` does five things, in this order:\n\n"
     "1. The `docker` command on your Mac sends the request to Docker Engine in the VM.\n"
     "2. The engine checks whether it already has the image, and pulls it if not.\n"
     "3. It puts a fresh writable layer on top of the image's files. That merged folder tree becomes the container's `/`.\n"
     "4. It asks the kernel for new namespaces and a cgroup.\n"
     "5. It starts the image's default command inside them, as PID 1. For nginx that is the nginx server, for Alpine the shell `/bin/sh`.\n\n"
     "The engine hands steps 3 to 5 to two helper programs, containerd and runc. Their names show up in error messages, "
     "as the next section shows."),

    ("d17", ("sections", 4, "body"),
     "- `-d` (detached) runs it in the background and prints the container ID.",
     "- `-d` (detached) runs it in the background and prints its ID, instead of tying your terminal to the app's output."),
    ("d17", ("sections", 4, "body"),
     "- `--rm` deletes the container when it stops, which suits one-off commands.",
     "- `--rm` deletes the container when it stops, so one-off runs do not pile up in `docker ps -a`."),
    ("d17", ("sections", 4, "body"),
     "`docker run -it --rm ubuntu:24.04 bash` gives you the Ubuntu practice box from Part 1.",
     "`docker run -it --rm ubuntu:24.04 bash` gives you the Ubuntu practice box from Part 1. "
     "The program you name must exist inside the image, because the container sees only the image's files. "
     "Alpine has no bash, so `docker run --rm alpine bash` fails. The error says `runc create failed` "
     "and ends with `executable file not found in $PATH`."),

    ("d17", ("sections", 5, "body"),
     "traffic to port 8080 on your Mac goes to port 80 in the container. ",
     "traffic to port 8080 on your Mac goes to port 80 in the container. "
     "Docker Desktop carries that traffic into the VM, and the engine forwards it to the container's own network address. "),
    ("d17", ("sections", 5, "body"),
     "- The app inside must listen on `0.0.0.0`, as you saw on Day 10. An app bound to `127.0.0.1` only hears its own container.",
     "- The app inside must listen on `0.0.0.0` (Day 10). Forwarded traffic arrives at the container's address, never at its `127.0.0.1`."),

    ("d17", ("sections", 6, "body"),
     "A container lives exactly as long as its main process, PID 1. When that process ends, the container exits, and its exit code tells you how.",
     "A container lives exactly as long as its main process, PID 1. That follows from what a container is: "
     "when PID 1 ends, the kernel also ends every other process in its namespace. "
     "So the container exits, and the exit code of PID 1 tells you how."),

    # ---------------- d18: why layers, and what a Dockerfile step is ----------------
    ("d18", ("sections", 0, "body"),
     "When you pull an image it looks like one thing. Inside, it is a small bundle of parts:",
     "An image holds a whole small Linux system: `python:3.14-slim` unpacks to about 135 MB of Debian and Python files. "
     "If that were one big archive, each change to your app would mean shipping all of it again. "
     "Ten Python images would also store Python ten times. "
     "So an image looks like one thing when you pull it, but inside it is a small bundle of parts:"),
    ("d18", ("sections", 0, "body"),
     "Dockerfile instructions that change files, such as `RUN` and `COPY`, each create a layer. "
     "Instructions that only change settings, such as `CMD`, `ENV` and `EXPOSE`, only edit the config. "
     "`docker history` lists those with a size of 0B.",
     "Images are built from a Dockerfile, a text file of build steps that Day 19 covers in full. "
     "Two kinds of steps matter today. Steps that change files each create a layer: `RUN` runs a shell command during the build, "
     "and `COPY` copies files in from your laptop. "
     "Steps that only change settings, such as `CMD` (the default command), `ENV` (a variable) and `EXPOSE` (a port note), only edit the config. "
     "In `docker history` they show a size of 0B."),
    ("d18", ("sections", 0, "body"),
     "If you know git, layers are like immutable snapshots of changes, and the manifest is like a commit that points at them.",
     "The manifest works much like a git commit from Day 8: it names its parts by their hashes, so it cannot point at the wrong ones. "
     "One difference: a layer holds only the changes its step made, while a git commit points at a full snapshot."),

    ("d18", ("sections", 2, "body"),
     "On Linux that is OverlayFS: it stacks the image layers under the container layer and shows you the merged view.",
     "On Linux that is OverlayFS: it stacks the image layers under the container layer and shows you the merged view. "
     "That merged view is the `/` that the container's process sees, as on Day 17."),

    ("d18", ("sections", 4, "body"),
     " A digest is the hash of the manifest, so it always means one exact image.",
     "\n\nAn image's digest is the hash of its manifest, and that one hash pins every byte. "
     "The manifest lists the config and each layer by digest. "
     "Change one byte in a layer, and that layer's digest changes, so the manifest changes, and so does its digest."),
    ("d18", ("sections", 4, "body"),
     "A tag works like a git branch name, and a digest like a commit SHA.",
     "A tag works like a git branch name from Day 8, a pointer that moves, and a digest like a commit SHA."),

    ("d18", ("sections", 5, "body"),
     "Fresh installs and Docker Desktop use the containerd image store, which can keep several platforms of one image on your machine.",
     "Fresh installs and Docker Desktop use the containerd image store. "
     "That means containerd, the helper program from Day 17, keeps the images, and it can hold several platforms of one image."),

    ("d18", ("sections", 6, "body"),
     "Every image you build starts from someone else's image, so pick bases you can trust.",
     "Every image you build starts from someone else's image, and everything in that base ships inside yours, "
     "old packages with known bugs included. So pick bases you can trust."),
    ("d18", ("sections", 6, "body"),
     "Docker says this approach cuts the attack surface by up to 95%.",
     "Docker says this approach cuts the attack surface, the code an attacker could try to use, by up to 95%."),

    # ---------------- d19: how a build runs, and why the cache works as it does ----------------
    ("d19", ("sections", 0, "body"),
     "The Dockerfile lives in git next to the app, and teammates review changes to it like any other code. "
     "That is the Day 1 idea of everything as code, applied to packaging.",
     "Each `RUN` step runs in a container of its own. The builder starts a temporary container from the layers built so far, "
     "runs the command in it, and saves the files that changed as the next layer. "
     "So `RUN pip install -r requirements.txt` sees only what earlier steps put in the image. "
     "If no `COPY` brought `requirements.txt` in first, pip cannot find it."),

    ("d19", ("sections", 1, "body"),
     "- `WORKDIR` sets the folder that later instructions work in, and creates it.",
     "- `WORKDIR` sets and creates the folder later steps work in, so `COPY app.py .` lands in `/app`, not `/`."),

    ("d19", ("sections", 2, "body"),
     "A `COPY` can only take files from inside it, so `COPY ../secrets.txt .` fails.",
     "The builder runs inside Docker's Linux VM, not on your Mac. "
     "The `docker` command gives it this one folder, and the builder loads files from it as it needs them. "
     "Nothing outside it exists for the build, so `COPY ../secrets.txt .` fails."),

    ("d19", ("sections", 3, "body"),
     "The second half is the one that surprises people. It works like a row of dominoes: tip one over and every one after it falls too.",
     "The second half has a reason: each layer holds the changes one step made on top of the exact layers below it. "
     "If a lower layer changes, Docker cannot know whether a later `RUN pip install` would give the same result without running it again."),

    ("d19", ("sections", 4, "body"),
     " PID 1 is also special in Linux: it gets no default signal handlers, which is why `sleep` ignored SIGTERM on Day 17.",
     "\n\nPID 1 is also special in Linux. The kernel drops any signal that PID 1 has no handler for, SIGKILL aside. "
     "`sleep` sets up no handler, which is why it ignored SIGTERM on Day 17. "
     "So exec form is only half the fix, and the app must also handle SIGTERM itself. Gunicorn does. "
     "A bare Python script does not: as PID 1 it waited out the full 10 seconds in our test, just like `sleep`."),

    ("d19", ("check", 2, "why"),
     "In shell form a shell is PID 1 and does not forward SIGTERM, so Docker waits 10 seconds and sends SIGKILL; exec form makes Python PID 1.",
     "A shell as PID 1 drops SIGTERM, so Docker sends SIGKILL after 10 seconds. "
     "Exec form makes Python PID 1, so a server that handles SIGTERM stops cleanly."),

    # ---------------- d20: how ownership, cables and names work ----------------
    ("d20", ("sections", 0, "body"),
     "So data you care about must live outside the container. Docker gives you three kinds of mounts, which attach storage at a folder inside the container. Pick by asking who owns the data:",
     "So data you care about must live outside the container. Docker gives you three kinds of mounts. "
     "A mount places other storage at one folder of the container's file tree, such as `/data`. Pick by asking who owns the data:"),

    ("d20", ("sections", 2, "body"),
     "File ownership works by user ID numbers, not names. On a Linux machine,",
     "File ownership works by user ID numbers, not names. The kernel stores each file's owner as a number, "
     "and the container shares the host's kernel. Names come from `/etc/passwd`, and the image has its own copy, "
     "so one name can mean different users on each side.\n\nOn a Linux machine,"),

    ("d20", ("sections", 3, "body"),
     "Docker connects containers through a bridge, a virtual network switch inside the Linux VM. ",
     "Docker connects containers through a bridge, a virtual network switch inside the Linux VM. "
     "Each container gets a virtual cable, called a veth pair: one end is `eth0` inside the container, and the other end plugs into the bridge. "),

    ("d20", ("sections", 4, "body"),
     "\n\nIn the worked example, `wget http://web`",
     "\n\nThe DNS server knows those names because Docker Engine handed out the addresses in the first place. "
     "Names it does not know, such as `github.com`, it passes on to the host's DNS servers.\n\n"
     "In the worked example, `wget http://web`"),

    # ---------------- d21: what Compose really does ----------------
    ("d21", ("sections", 0, "body"),
     "Run it again and Compose changes only what differs from the file. Teammates get the same setup by cloning the repo.",
     "Teammates get the same setup by cloning the repo.\n\n"
     "Compose is only a client. It turns the file into the same requests to Docker Engine that your `docker run` commands made. "
     "It also labels every container with its project, its service and a hash of that service's settings. "
     "Run `up` again and Compose compares those labels with the file. "
     "A service that matches keeps running, and one whose settings changed is recreated."),

    ("d21", ("sections", 3, "body"),
     "The override file in this lesson sets `unless-stopped`.",
     "Docker Engine applies the policy, not Compose. It notices when the main process ends and starts it again, "
     "with no compose command running. `docker run --restart unless-stopped` sets the same policy without Compose.\n\n"
     "The override file in this lesson sets `unless-stopped`."),

    # ---------------- d22: the why behind two rules ----------------
    ("d22", ("sections", 2, "body"),
     "Write the number in `USER`, not the name. Kubernetes can then check that an image runs as non-root without looking inside it.",
     "Write the number in `USER`, not the name. A name means nothing until someone reads the image's `/etc/passwd`, "
     "while `10001` is plainly not 0. So Kubernetes can check that an image runs as non-root without looking inside it."),

    ("d22", ("sections", 6, "body"),
     "hands the secret to that one `RUN` step, as an environment variable.",
     "hands the secret to the temporary container of that one `RUN` step (Day 19), as an environment variable."),
]


def get_parent(lesson, path):
    node = lesson
    for key in path[:-1]:
        node = node[key]
    return node, path[-1]


def main():
    data = json.loads(PATH.read_text())
    lessons = {l["id"]: l for l in data["lessons"]}
    applied = skipped = 0
    for lid, path, old, new in EDITS:
        parent, key = get_parent(lessons[lid], path)
        text = parent[key]
        if new in text:
            skipped += 1
        elif text.count(old) == 1:
            parent[key] = text.replace(old, new)
            applied += 1
        else:
            raise SystemExit(f"NOT FOUND in {lid} {path}: {old[:70]!r}")
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"applied {applied}, already present {skipped}, total {len(EDITS)}")


if __name__ == "__main__":
    main()
