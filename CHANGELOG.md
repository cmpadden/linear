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

### Changed
- **Version flag**: Changed version flag shorthand from `-v` to `-V` to avoid conflict with the new `--verbose` flag
  - `--version` (long form) remains unchanged
  - New shorthand: `linear -V` or `linear --version`

---

## Previous Releases

_Version history prior to 0.0.11 not tracked in changelog._
