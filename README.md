# QE Tools Backlog Status

[![Backlog Status](https://img.shields.io/github/actions/workflow/status/os-autoinst/qa-tools-backlog-assistant/backlog_checker.yml?label=backlog)](https://os-autoinst.github.io/qa-tools-backlog-assistant/)

This is the dashboard for [QE Tools](https://progress.opensuse.org/projects/qa/wiki/Tools).

Implemented using [openSUSE/backlogger](https://github.com/openSUSE/backlogger).

See https://os-autoinst.github.io/qa-tools-backlog-assistant/

## Local preview

To check changes to `queries.yaml` before pushing, render the dashboard in a
podman container and open it at http://localhost:8000:

```sh
export REDMINE_API_KEY=...
tools/preview
```

See `tools/preview --help` for options.
