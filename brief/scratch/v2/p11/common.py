"""Shared helpers for the Part 11 build."""
import pathlib

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops")
V_KIBANA = "9.5.5"


def lab(rel):
    """Return a lab file's text exactly as it is on disk (so lesson and lab never drift)."""
    return (LAB / rel).read_text().rstrip("\n")


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}
