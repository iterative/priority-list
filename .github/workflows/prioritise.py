#!/usr/bin/env python3
import datetime
import json
import os
import pathlib
import re

P_LABEL_GRAVEYARD = float(os.environ.get("P_LABEL_GRAVEYARD", 4) or 4)
WEIGHT_REACTIONS = float(os.environ.get("WEIGHT_REACTIONS", 14.0) or 14.0)
WEIGHT_STALENESS = float(os.environ.get("WEIGHT_STALENESS", 1.0) or 1.0)
WEIGHT_AGE = float(os.environ.get("WEIGHT_AGE", 0.14285714285714285) or 0.14285714285714285)  # 1/7
WEIGHT_ACTIVITY = float(os.environ.get("WEIGHT_ACTIVITY", 7.0) or 7.0)

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
        WEIGHT_REACTIONS * sum(r["users"]["totalCount"] for r in issue["reactionGroups"])
        + WEIGHT_STALENESS * age_days(issue["updatedAt"])
        + WEIGHT_AGE * age_days(issue["createdAt"])
        + WEIGHT_ACTIVITY * len(issue["comments"])
    ) * (sum(label_priority(lab["name"]) for lab in issue["labels"]) or P_LABEL_GRAVEYARD)


def markdown_link(issue):
    url = issue["url"]
    pretty = url.split("/", 3)[-1].replace("/issues/", "#").replace("/pull/", "#")
    return f"[{pretty}]({url})"


if __name__ == "__main__":
    issues = sum((json.load(d.open()) for d in pathlib.Path(".").glob("*.*.json")), [])
    issues.sort(key=priority, reverse=True)
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
