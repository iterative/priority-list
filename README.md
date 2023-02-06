# Priority List

[![Priority List](https://img.shields.io/github/actions/workflow/status/iterative/priority-list/weekly.yml?label=action&logo=GitHub)](https://github.com/iterative/priority-list/actions/workflows/weekly.yml)

Make a dent in GitHub issue & PR backlogs across repositories.

Aimed at teams managing multiple projects and sick of [the time cost of refinement/triage](https://xkcd.com/1445).

![screenshot](https://imgs.xkcd.com/comics/efficiency.png "TODO: replace with GHA job summary + Slack screenshots")

See [`action.yml`](./action.yml) for a full list of configuration options.

## Example use

```yaml
name: Priority List
on: { schedule: [{ cron: '0 1 * * 1' }] }  # 01:00 (AM, UTC) Mondays
jobs:
  priority-list:
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
        slack_webhook: ${{ secrets.SLACK_WEBHOOK || '' }}  # optional; requires `people.json`
```

## Notes

The main calculation is done by the `priority` function in [`prioritise.py`](./prioritise.py). In summary:

- we assume you use `pN-label`s (e.g. `p0-critical`, `p1-important`, `p2-nice-to-have`) on issues/PRs
  + labels match the [Python regex](https://docs.python.org/3/library/re.html#regular-expression-syntax) `[pP](?:riority)[\s:-]*([0-9]+).*`
- `bug` and `external-request` labels are treated the same as `p1`
- issues/PRs lacking a `pN-label` are treated as `p0`
  + this bumps unnoticed/unlabelled items to the top of the list, thus encouraging you to at least assign a `pN-label` to (potentially) lower the priority
- if an issue/PR has multiple labels, their associated priorities will be summed
- use `multiplier_labels` to exclude (e.g. `wip:-1` will skip anything labelled `wip`) or scale (e.g. `upstream:0.01`) the overall priority of an issue/PR
- labels not matching the above rules are ignored

Results are posted in a [job summary](https://docs.github.com/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary). To post to your team's slack channel too:

- provide a `slack_webhook`
- create a file named `people.json` in the working directory (see e.g. https://status.cml.dev/people.json) to map GitHub usernames to Slack member IDs
