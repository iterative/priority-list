#!/usr/bin/env bash
REPOS=("$@")

for repo in "${REPOS[@]}"; do
  fname="${repo//\//-}.json"
  # fname="$(basename $repo).json"
  echo >&2 "$repo -> {issues,prs}.$fname"
  [ ! -f issues.$fname ] && \
  gh issue list -R ${repo} -L 98765 --json comments,createdAt,labels,reactionGroups,updatedAt,url > issues.$fname && \
  gh pr list -R ${repo} -L 98765 --json comments,createdAt,labels,reactionGroups,updatedAt,url > prs.$fname
done
