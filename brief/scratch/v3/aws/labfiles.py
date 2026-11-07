"""Read lab files so the lesson's code blocks always match labs/aws exactly."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAB = ROOT / "labs" / "aws"


def lab(rel: str) -> str:
    return (LAB / rel).read_text()
