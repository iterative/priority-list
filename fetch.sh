#!/usr/bin/env bash
REPOS=("$@")

for repo in "${REPOS[@]}"; do
  fname="${repo//\//-}.json"
  # fname="$(basename $repo).json"
  CMD="list -R ${repo} -L 98765 --json comments,createdAt,labels,reactionGroups,updatedAt,url,assignees,title"
  echo >&2 "$repo -> {issue,pr}s.$fname"
  for TYP in issue pr; do
    if test ! -f ${TYP}s.$fname; then
      gh $TYP $CMD > ${TYP}s.$fname || (
        if test -n "$GITHUB_STEP_SUMMARY"; then
          echo "::error file=$0,line=12,title=could not load::token likely missing read access for https://github.com/$repo"
        else
          echo >&2 "Could not load $repo"
        fi
        rm -f ${TYP}s.$fname
      )
    fi
  done
done
