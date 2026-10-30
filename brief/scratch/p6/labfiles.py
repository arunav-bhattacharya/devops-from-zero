import pathlib

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops")
HERE = pathlib.Path(__file__).resolve().parent


def lab(path):
    """Return a lab file exactly as it is on disk (no trailing newline)."""
    return (LAB / path).read_text().rstrip("\n")


def scratch(path):
    """Return a file from this scratch folder (files the lead will merge into the lab)."""
    return (HERE / path).read_text().rstrip("\n")
