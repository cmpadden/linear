<img width="1400" height="225" src="https://github.com/user-attachments/assets/ce620de7-718d-4205-b4a0-bb287dc910a4" />

# Linear CLI

A command-line interface for interacting with [Linear](https://linear.app).

## Getting started

```bash
# Define `uvx` alias
$ alias linear="uvx --from linear-app linear"

# Login
$ linear login

# Start listing issues
$ linear issues list
```

### Authentication

`linear login` opens Linear in your browser and requests read/write access as **you**, using OAuth with PKCE (no client secret). 

- `linear auth status` verifies the active login and displays its credential source.
- `linear auth status --format json` provides machine-readable status (exit 1 if unauthenticated).
- `linear logout` attempts remote revocation and deletes the saved local tokens.

For CI, SSH sessions, or systems without a supported unlocked keychain, use a [personal API key](https://linear.app/settings/api) instead:

```bash
$ export LINEAR_API_KEY="<linear-api-key>"
```

## Documentation

For complete CLI command reference with all available commands, options, and examples, see [DOCUMENTATION.md](./DOCUMENTATION.md).

**Quick reference:**
- `linear login` / `linear logout` - Sign in through your browser or remove the saved login
- `linear auth status` - Verify authentication and show the active identity
- `linear issues` - Manage issues (list, create, view, update, search, delete, archive, etc.)
- `linear projects` - Manage projects (list, view, create, update)
- `linear teams` - Manage teams (list, view)
- `linear cycles` - Manage cycles (list, view)
- `linear users` - Manage users (list, view)
- `linear labels` - Manage labels (list)
- `linear roadmaps` - Manage roadmaps (list, view, create, update)
- `linear comments` - Manage issue comments (list, create, update, delete)
- `linear attachments` - Manage issue attachments (list, upload, delete)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
