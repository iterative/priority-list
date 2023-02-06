#!/usr/bin/env bash
REPOS=("$@")

for repo in "${REPOS[@]}"; do
  fname="${repo//\//-}.json"
  # fname="$(basename $repo).json"
  echo >&2 "$repo -> {issues,prs}.$fname"
  if test ! -f issues.$fname; then
    gh api -H "Accept: application/vnd.github+json" --paginate /repos/${repo}/issues?state=open > issues.$fname && \
    gh api -H "Accept: application/vnd.github+json" --paginate /repos/${repo}/pulls?state=open > prs.$fname || (
      if test -n "$GITHUB_STEP_SUMMARY"; then
        echo "Could not load $repo" >> $GITHUB_STEP_SUMMARY
      else
        echo >&2 "Could not load $repo"
      fi
      rm -f {issues,prs}.$fname
    )
  fi
  # CMD="list -R ${repo} -L 98765 --json comments,createdAt,labels,reactionGroups,updatedAt,url,assignees,title"
  # gh issue $CMD > issues.$fname && gh pr list $CMD > prs.$fname || rm -f {issues,prs}.$fname
done
