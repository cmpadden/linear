<img width="1400" height="225" src="https://github.com/user-attachments/assets/ce620de7-718d-4205-b4a0-bb287dc910a4" />

# Linear CLI

A command-line interface for interacting with [Linear](https://linear.app).

## Getting started

```bash
$ alias linear="uvx --from linear-app linear"
$ linear login
$ linear auth status
```

### Authentication

`linear login` opens Linear in your browser and requests read/write access as
**you**, using OAuth with PKCE (no client secret). It temporarily listens on
`http://localhost:8765/oauth/callback`; port 8765 must be free and the browser
must be able to reach the machine running the CLI. If the browser does not open,
use the URL printed in the terminal. The default authorization timeout is 180
seconds; use `linear login --timeout 300` to allow more time.

Tokens are stored in the OS keychain (macOS Keychain, Windows Credential Locker,
Linux Secret Service/libsecret, or KWallet), never in a plaintext config file.
The CLI refreshes expiring access tokens automatically. One OAuth login is saved
at a time; a successful login replaces the previous one.

- `linear auth status` verifies the active login and displays its credential source.
- `linear auth status --format json` provides machine-readable status (exit 1 if unauthenticated).
- `linear logout` attempts remote revocation and deletes the saved local tokens.
  If remote revocation fails, revoke the application in Linear settings as well.

For CI, SSH sessions, or systems without a supported unlocked keychain, use a
[personal API key](https://linear.app/settings/api) instead:

```bash
$ export LINEAR_API_KEY="<linear-api-key>"
```

`LINEAR_API_KEY` overrides saved OAuth credentials. Unset it to use browser login.
Logging out does not unset or revoke personal API keys. Library callers can also
supply an explicit API key, which takes precedence over the environment variable.

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

**Common patterns:**
- Use `--help` on any command for details: `linear issues list --help`
- `linear issues list` shows your assigned issues by default; use `--no-assignee` for unassigned issues or `--all-assignees` to remove the assignee filter
- Most list commands support `--format json` for scripting
- Command aliases available: `linear i` = `linear issues`, `linear p` = `linear projects`, etc.
- Global options: `--verbose` (show GraphQL queries), `--version` (show CLI version)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

```bash
uv sync --dev --locked
make check
make test  # Offline regression and CLI smoke tests; no API key required
```
