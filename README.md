# Priority List

[![Priority List](https://img.shields.io/github/actions/workflow/status/iterative/priority-list/weekly.yml?label=workflow&logo=GitHub)](https://github.com/iterative/priority-list/actions/workflows/weekly.yml)

Make a dent in GitHub issue & PR backlogs across repositories.

Aimed at teams managing multiple projects.

Click the badge above to see it in action, and see [`action.yml`](./action.yml) for a full list of configuration options.

## Example use

```yaml
name: Priority List
on: { schedule: [{ cron: '0 1 * * 1' }] }  # 01:00 (AM, UTC) Mondays
jobs:
  list:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with: { python-version: '3.x' }
    - uses: iterative/priority-list@v1
      with:
        repos: >-
          myorg/somerepo
          myorg/otherrepo
        github-token: ${{ secrets.GH_TOKEN }} # must have read access to `repos`
        weight_activity: 14   # weight for number of comments
        weight_reactions: 7   # weight for reactions to original issue
        weight_staleness: 1   # weight for days of inactivity
        weight_age: 0.142857  # weight for days open
        multiplier_pr: 7      # weight multiplier for PRs (compared to issues)
        # weight multiplier for labels (negative to exclude)
        multiplier_labels: >-
          example:-1
          epic:0.142857
          blocked:0.142857
          invalid:0.142857
        p_label_graveyard: 4  # largest pN-label (lowest priority)
        slack_webhook: ${{ secrets.SLACK_WEBHOOK || '' }}  # optional, requires `people.json`
```
