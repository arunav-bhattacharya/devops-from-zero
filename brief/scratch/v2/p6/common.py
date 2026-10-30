"""Shared helpers for the Part 6 (Terraform) build.

Code blocks are read from tested files on disk, so the JSON always matches
what was applied and destroyed while writing the lessons.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # /home/user/devops-from-zero
LABS = ROOT / "labs"
HELLO = LABS / "hello-devops"
PRACTICE = LABS / "terraform-practice"
FILES = HERE / "files"


def read(path):
    return pathlib.Path(path).read_text()


def lab(rel):
    """A file from labs/hello-devops."""
    return read(HELLO / rel)


def practice(rel):
    """A file from labs/terraform-practice."""
    return read(PRACTICE / rel)


def day(d, rel):
    """A day-specific version of a lab file (the lab holds only the final one)."""
    return read(FILES / d / rel)


def code(lang, title, src, run):
    return {"lang": lang, "title": title, "src": src, "run": run}


def step(say, code_=None, lang="console"):
    s = {"say": say}
    if code_:
        s["code"] = code_.strip("\n")
        s["lang"] = lang
    return s


def mcq(q, options, answer, why, **extra):
    d = {"q": q, "options": options, "answer": answer, "why": why}
    d.update(extra)
    return d


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


def cmd(c, what):
    return {"cmd": c, "what": what}


# Links used in more than one lesson. Every developer.hashicorp.com path was
# confirmed by finding its source file in hashicorp/web-unified-docs
# (content/terraform/v1.17.x/docs/...), because the site itself is blocked here.
HC = "https://developer.hashicorp.com/terraform/"
V_INTRO_HC = ref("Introduction to Terraform, with Armon Dadgar (HashiCorp)", "https://www.youtube.com/watch?v=ZFLWA1kQ3ls", "watch")
V_NANA = ref("Terraform explained in 15 mins (TechWorld with Nana)", "https://www.youtube.com/watch?v=l5k1ai_GBDE", "watch")
V_DD = "https://www.youtube.com/watch?v=7xngnjfIlK4"
V_FCC_AWS = ref("Terraform course: automate your AWS cloud infrastructure (freeCodeCamp)", "https://www.youtube.com/watch?v=SLB_c_ayRMo", "watch")
V_HC_TESTS = ref("Snapshot demo: automating tests for Terraform (HashiCorp)", "https://www.youtube.com/watch?v=oLRtFy6mYSg", "watch")
