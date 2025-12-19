<img width="1400" height="225" src="https://github.com/user-attachments/assets/ce620de7-718d-4205-b4a0-bb287dc910a4" />

# Linear CLI

A command-line interface for interacting with [Linear](https://linear.app).

## Getting started

```bash
$ export LINEAR_API_KEY="<linear-api-key>"  # https://linear.app/settings/api

$ alias linear="uvx --from linear-app linear"
```

## Documentation

For complete CLI command reference with all available commands, options, and examples, see [DOCUMENTATION.md](./DOCUMENTATION.md).

**Quick reference:**
- `linear issues` - Manage issues (list, create, view, update, search, delete, archive, etc.)
- `linear projects` - Manage projects (list, view, create, update)
- `linear teams` - Manage teams (list, view)
- `linear cycles` - Manage cycles (list, view)
- `linear users` - Manage users (list, view)
- `linear labels` - Manage labels (list)
- `linear roadmaps` - Manage roadmaps (list, view, create, update)
- `linear comments` - Manage issue comments (list, create, update, delete)
- `linear attachments` - Manage issue attachments (list, upload, delete)

**Common patterns:**
- Use `--help` on any command for details: `linear issues list --help`
- Most list commands support `--format json` for scripting
- Command aliases available: `linear i` = `linear issues`, `linear p` = `linear projects`, etc.
- Global options: `--verbose` (show GraphQL queries), `--version` (show CLI version)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
