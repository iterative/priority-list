#!/usr/bin/env bash
REPOS=("$@")

for repo in "${REPOS[@]}"; do
  fname="${repo//\//-}.json"
  # fname="$(basename $repo).json"
  echo >&2 "$repo -> issues.$fname"
  if test ! -f issues.$fname; then
    # also contains PRs
    gh api -H "Accept: application/vnd.github+json" --paginate /repos/${repo}/issues?state=open > issues.$fname || (
      if test -n "$GITHUB_STEP_SUMMARY"; then
        echo "::error file=$0,line=10,title=could not load::token likely missing read access for https://github.com/$repo"
      else
        echo >&2 "Could not load $repo"
      fi
      rm -f issues.$fname
    )
  fi
  # GraphQL (doesn't work with fine-grained tokens, vis. https://github.com/iterative/priority-list/issues/1)
  # CMD="list -R ${repo} -L 98765 --json comments,createdAt,labels,reactionGroups,updatedAt,url,assignees,title"
  # gh issue $CMD > issues.$fname && gh pr list $CMD > prs.$fname || rm -f {issues,prs}.$fname
done
