# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.12] (unreleased)

### Added
- **Comprehensive CLI documentation**: Added auto-generated documentation in DOCUMENTATION.md
  - Complete command reference with all available commands, options, and examples
  - Generated from Typer app structure using built-in `typer utils docs` command
  - Documentation generation script available at `scripts/generate_documentation.sh`
  - Includes all command groups: issues, projects, teams, cycles, users, labels, roadmaps, comments, attachments
  - Shows command aliases (e.g., `i` for `issues`, `p` for `projects`)
  - All examples from command docstrings preserved in generated documentation
  - Accessible via `make docs` command for easy regeneration
- **Roadmaps management**: Added full support for managing Linear roadmaps
  - `linear roadmaps list` - List roadmaps with table and JSON output formats
  - `linear roadmaps view <roadmap-id>` - View roadmap details by ID or slug
  - `linear roadmaps create` - Create new roadmap with `--name`, `--description`, and `--owner-id` flags (supports `--editor` for description editing)
  - `linear roadmaps update <roadmap-id>` - Update roadmap name, description, or owner (supports `--editor` for description editing)
  - Supports pagination via `--per-page`, `--page`, and `--all` flags
  - Supports both table/detail and JSON output formats via `--format` flag
  - Roadmap alias: `linear r` for quick access
- **Attachments management**: Added full support for managing issue attachments
  - `linear attachments list <issue-id>` - List all attachments for an issue with title, URL, and creation date
  - `linear attachments upload <issue-id> <file-path>` - Upload file attachment to an issue (supports `--title` flag for custom title, defaults to filename)
  - `linear attachments delete <attachment-id>` - Delete attachment (with confirmation prompt, use `--yes` to skip)
  - Supports both table and JSON output formats via `--format` flag
  - Automatically handles file upload to Linear's storage and creates attachment record
  - Resolves issue identifiers (e.g., ENG-123) to UUIDs for all operations
- **Issue relations management**: Added full support for managing relationships between issues
  - `linear issues relations list <issue-id>` - List all relations for an issue with type, related issue details, status, and team
  - `linear issues relations add <issue-id> <related-issue-id>` - Create relation between two issues with `--type` flag (blocks, blocked, related, duplicate)
  - `linear issues relations remove <issue-id> <relation-id>` - Remove relation from issue (with confirmation prompt, use `--yes` to skip)
  - Supports both table and JSON output formats via `--format` flag
  - Relations table shows relation type, related issue identifier, title, status, and team
  - Automatically resolves issue identifiers (e.g., ENG-123) to UUIDs for all operations
- **Extended pagination support**: Added cursor-based pagination to projects, teams, and users list commands
  - `linear projects list` - Full pagination support with `--per-page`, `--page`, and `--all` flags
  - `linear teams list` - Full pagination support with `--per-page`, `--page`, and `--all` flags
  - `linear users list` - Full pagination support with `--per-page`, `--page`, and `--all` flags
  - Pagination info displayed in table footer showing current range and availability of more results
  - Examples: `linear users list --page 2 --per-page 10`, `linear projects list --all`
  - Note: Cycles and labels pagination API updated, command layer updates in progress
- **Teams admin operations**: Added team creation, update, deletion, and archival operations
  - `linear teams create` - Create new team with `--name`, `--key`, `--description`, and `--private` flags
  - `linear teams update <team-id>` - Update team name, key, description, or privacy settings
  - `linear teams delete <team-id>` - Delete team (with confirmation prompt, use `--yes` to skip)
  - `linear teams archive <team-id>` - Archive team (with confirmation prompt, use `--yes` to skip)
  - Supports both detail and JSON output formats via `--format` flag
  - Team lookup by ID or key for all operations
- **Cycles management**: Added cycle creation, update, deletion, and archival operations
  - `linear cycles create` - Create new cycle with `--name`, `--team`, `--starts-at`, `--ends-at`, and `--description` flags
  - `linear cycles update <cycle-id>` - Update cycle name, dates, or description
  - `linear cycles delete <cycle-id>` - Delete cycle (with confirmation prompt, use `--yes` to skip)
  - `linear cycles archive <cycle-id>` - Archive cycle (with confirmation prompt, use `--yes` to skip)
  - Supports both detail and JSON output formats via `--format` flag
  - Team lookup by ID or key for cycle creation

### Changed
- **Simplified README**: Removed detailed command reference from README.md, replaced with link to comprehensive DOCUMENTATION.md
  - README now focuses on getting started and quick reference
  - All detailed command documentation moved to auto-generated DOCUMENTATION.md
  - Avoids duplication and keeps documentation in sync with code
- **Enhanced issue search**: `linear issues search` now searches both title and description fields (previously title only) using OR logic for more comprehensive results (2025-12-19)
- **Enforce absolute imports**: Enabled TID252 rule to ban all relative imports in favor of absolute imports (e.g., `from linear.models import Issue`)

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
