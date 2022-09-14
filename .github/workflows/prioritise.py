#!/usr/bin/env python3
import datetime
import json
import os
import pathlib
import re
from bisect import bisect_right
from functools import reduce

WEIGHT_ACTIVITY = float(os.environ.get("WEIGHT_ACTIVITY", 14) or 14)
WEIGHT_REACTIONS = float(os.environ.get("WEIGHT_REACTIONS", 7) or 7)
WEIGHT_STALENESS = float(os.environ.get("WEIGHT_STALENESS", 1) or 1)
WEIGHT_AGE = float(os.environ.get("WEIGHT_AGE", 0.142857) or 0.142857)  # 1/7
MULTIPLIER_PR = float(os.environ.get("MULTIPLIER_PR", 7) or 7)
MULTIPLIER_LABELS = "example:-1 epic:0.142857 blocked:0.142857 invalid:0.142857"
MULTIPLIER_LABELS = os.environ.get("MULTIPLIER_LABELS", MULTIPLIER_LABELS) or MULTIPLIER_LABELS
MULTIPLIER_LABELS = dict(i.rsplit(":", 1) for i in MULTIPLIER_LABELS.split())
MULTIPLIER_LABELS = {k: float(v) for k, v in MULTIPLIER_LABELS.items()}
P_LABEL_GRAVEYARD = float(os.environ.get("P_LABEL_GRAVEYARD", 4) or 4)

NOW = datetime.datetime.now()


def age_days(t):
    return (NOW - datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")).days


def label_priority(label):
    if p := re.search(r"[pP](?:riority)[\s:-]*([0-9]+).*", label):
        return P_LABEL_GRAVEYARD - int(p.group(1))
    if re.search("bug|external-request", label, flags=re.I):
        return P_LABEL_GRAVEYARD - 1  # same as p1-important
    return P_LABEL_GRAVEYARD - 0  # default: p0-unlabelled


def priority(issue):
    return (
        (
            WEIGHT_REACTIONS * sum(r["users"]["totalCount"] for r in issue["reactionGroups"])
            + WEIGHT_STALENESS * age_days(issue["updatedAt"])
            + WEIGHT_AGE * age_days(issue["createdAt"])
            + WEIGHT_ACTIVITY * len(issue["comments"])
        )
        * (sum(label_priority(lab["name"]) for lab in issue["labels"]) or P_LABEL_GRAVEYARD)
        * reduce(
            lambda x, y: x * y,
            (MULTIPLIER_LABELS.get(lab["name"], 1) for lab in issue["labels"]),
            1,
        )
        * (MULTIPLIER_PR if issue["url"].rsplit("/", 2)[-2] == "pull" else 1)
    )


def markdown_link(issue):
    url = issue["url"]
    pretty = url.split("/", 3)[-1].replace("/issues/", "#").replace("/pull/", "#")
    return f"[{pretty}]({url})"


if __name__ == "__main__":
    issues = sum((json.load(d.open()) for d in pathlib.Path(".").glob("*.*.json")), [])
    issues.sort(key=priority, reverse=True)
    # drop excluded (more efficient version uses `bisect`)
    # while issues and priority(issues[-1]) < 0: issues.pop()
    issues = issues[: len(issues) - bisect_right(issues[::-1], 0, key=priority)]
    assert not issues or priority(issues[-1]) >= 0

    print("#|weight|link")
    print("-:|-:|:-")
    N = len(issues)
    print(
        "\n".join(
            f"{i}|{priority(issues[i]):.0f}|{markdown_link(issues[i])}" for i in range(min(10, N))
        )
    )
    if N > 15:
        print("...|...|...")
        print(
            "\n".join(
                f"{i}|{priority(issues[i]):.0f}|{markdown_link(issues[i])}"
                for i in range(N - 5, N)
            )
        )
