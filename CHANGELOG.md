# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.12] (unreleased)

### Added
- **Cycles management**: Added cycle creation, update, deletion, and archival operations
  - `linear cycles create` - Create new cycle with `--name`, `--team`, `--starts-at`, `--ends-at`, and `--description` flags
  - `linear cycles update <cycle-id>` - Update cycle name, dates, or description
  - `linear cycles delete <cycle-id>` - Delete cycle (with confirmation prompt, use `--yes` to skip)
  - `linear cycles archive <cycle-id>` - Archive cycle (with confirmation prompt, use `--yes` to skip)
  - Supports both detail and JSON output formats via `--format` flag
  - Team lookup by ID or key for cycle creation

## [0.0.11]

### Added
- **Comments management**: Added full CRUD operations for issue comments
  - `linear comments list <issue-id>` - List all comments on an issue
  - `linear comments create <issue-id>` - Add comment to issue (supports `--body` flag or opens `$EDITOR`)
  - `linear comments update <comment-id>` - Update comment body (supports `--body` flag or opens `$EDITOR`)
  - `linear comments delete <comment-id>` - Delete comment (with confirmation prompt, use `--yes` to skip)
  - Supports both table and JSON output formats via `--format` flag
  - Comments display author name, timestamp, and body (truncated in table view, full in detail view)
- **Pagination support**: Added cursor-based pagination for issue list and search commands
  - `--per-page` flag to control number of results per page (max 250, default 50)
  - `--page` flag to fetch a specific page number (starts at 1)
  - `--all` flag to automatically fetch all results across multiple pages
  - Pagination info displayed in table footer (e.g., "Showing 1-50 of 247 (more available, use --page to see more)")
  - Supports both grouped and ungrouped table views
  - Works with `linear issues list` and `linear issues search` commands
  - Note: `--limit` flag is deprecated in favor of `--per-page`
- **Verbose mode**: Added `--verbose` / `-v` global flag to display GraphQL queries, variables, and response times for debugging
  - GraphQL queries are syntax-highlighted using Rich
  - Variables displayed in formatted JSON
  - Response times measured in milliseconds
  - All verbose output sent to stderr to keep stdout clean for piping and automation
  - Works with all commands across issues, projects, teams, cycles, users, and labels
- **Issue deletion**: Added `linear issues delete <issue-id>` command to trash/delete issues
  - Shows issue details before deletion for confirmation
  - Supports `--yes` / `-y` flag to skip confirmation prompt
  - Accepts both issue identifiers (e.g., `ENG-123`) and UUIDs
- **Issue archiving**: Added `linear issues archive <issue-id>` command to archive issues
  - Shows issue details before archiving for confirmation
  - Supports `--yes` / `-y` flag to skip confirmation prompt
  - Accepts both issue identifiers (e.g., `ENG-123`) and UUIDs
- **Issue unarchiving**: Added `linear issues unarchive <issue-id>` command to unarchive issues
  - Shows issue details before unarchiving for confirmation
  - Supports `--yes` / `-y` flag to skip confirmation prompt
  - Accepts both issue identifiers (e.g., `ENG-123`) and UUIDs
- **State management**: Fixed and improved workflow state handling
  - Added `linear issues move-state <issue-id> <state>` command to change issue states by name
  - Fixed state lookup by name in `linear issues create` (now supports `--state "In Progress"`)
  - Fixed state lookup by name in `linear issues update` (now supports `--state "In Progress"`)
  - Shows available states when an invalid state name is provided
  - Confirmation prompt with before/after state comparison
- **Label management**: Added full CRUD operations for labels
  - `linear labels create` - Create new label with `--name`, `--description`, `--color`, and optional `--team`
  - `linear labels update <label-id>` - Update label name, description, or color
  - `linear labels delete <label-id>` - Permanently delete label (with confirmation prompt, use `--yes` to skip)
  - `linear labels archive <label-id>` - Archive label

### Changed
- **Version flag**: Changed version flag shorthand from `-v` to `-V` to avoid conflict with the new `--verbose` flag
  - `--version` (long form) remains unchanged
  - New shorthand: `linear -V` or `linear --version`
- **Release script**: GitHub releases now use CHANGELOG.md sections instead of auto-generated notes
  - Automatically extracts the relevant version section from CHANGELOG.md
  - Falls back to auto-generated notes if no changelog section is found

### Deprecated
- **`--limit` flag**: Deprecated in favor of `--per-page` for consistency with pagination terminology
  - Still works but shows a warning message
  - Will be removed in a future version

---

## Previous Releases

_Version history prior to 0.0.11 not tracked in changelog._
