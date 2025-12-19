# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.11] (unreleased)

### Added
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

### Changed
- **Version flag**: Changed version flag shorthand from `-v` to `-V` to avoid conflict with the new `--verbose` flag
  - `--version` (long form) remains unchanged
  - New shorthand: `linear -V` or `linear --version`

---

## Previous Releases

_Version history prior to 0.0.11 not tracked in changelog._
