"""Issues commands for Linear CLI."""

import json
import sys
import webbrowser
from typing import Optional

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.prompt import Prompt
from pydantic import ValidationError

from linear.api import LinearClient, LinearClientError
from linear.models import Issue
from linear.ai.claude import (
    extract_with_claude,
    should_use_claude_parsing,
)
from linear.formatters import (
    format_issue_detail,
    format_issue_json,
    format_json,
    format_table,
)
from linear.utils import VerboseLogger
from linear.utils.editor import IssueData, edit_issue_in_editor

app = typer.Typer(
    help="Manage Linear issues. Run 'linear issues list' to see your assigned issues."
)
relations_app = typer.Typer(help="Manage issue relations")


def _list_issues_impl(
    ctx: typer.Context,
    assignee: str | None = None,
    creator: str | None = None,
    project: str | None = None,
    status: str | None = None,
    team: str | None = None,
    priority: int | None = None,
    labels: list[str] | None = None,
    per_page: int = 50,
    page: int | None = None,
    all: bool = False,
    limit: int | None = None,
    include_archived: bool = False,
    format: str = "table",
    order_by: str = "updated",
    group_by: str | None = "cycle",
) -> None:
    """Core implementation for listing issues (shared between default and list commands)."""
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Handle deprecated --limit flag
        if limit is not None:
            console = Console()
            console.print(
                "[yellow]Warning: --limit is deprecated, use --per-page instead[/yellow]"
            )
            per_page = limit

        # Validate per_page
        if per_page > 250:
            console = Console()
            console.print("[red]Error: --per-page cannot exceed 250[/red]")
            sys.exit(1)

        # Resolve 'me' or 'self' to current user's email
        if assignee and assignee.lower() in ("me", "self"):
            viewer_response = client.get_viewer()
            viewer = viewer_response.get("viewer", {})
            assignee = viewer.get("email")

        # Resolve 'me' or 'self' for creator to current user's email
        if creator and creator.lower() in ("me", "self"):
            if assignee and assignee.lower() in ("me", "self"):
                # Reuse the viewer data if we already fetched it
                creator = assignee
            else:
                viewer_response = client.get_viewer()
                viewer = viewer_response.get("viewer", {})
                creator = viewer.get("email")

        # Calculate cursor for pagination
        after_cursor: str | None = None
        if page and page > 1:
            # For now, we need to iterate through pages to get the cursor
            # This is a limitation of cursor-based pagination
            # In a real implementation, we might want to cache cursors
            current_page = 1
            while current_page < page:
                _, page_info = client.list_issues(
                    assignee=assignee,
                    creator=creator,
                    project=project,
                    status=status,
                    team=team,
                    priority=priority,
                    labels=labels,
                    limit=per_page,
                    include_archived=include_archived,
                    sort=order_by,
                    after=after_cursor,
                    fetch_all=False,
                )
                cursor_value = page_info.get("endCursor")
                if not cursor_value or cursor_value == "":
                    console = Console()
                    console.print(
                        f"[yellow]Page {page} does not exist (only {current_page} page(s) available)[/yellow]"
                    )
                    sys.exit(1)
                after_cursor = str(cursor_value) if cursor_value else None
                current_page += 1

        # Fetch issues
        issues, pagination_info = client.list_issues(
            assignee=assignee,
            creator=creator,
            project=project,
            status=status,
            team=team,
            priority=priority,
            labels=labels,
            limit=per_page,
            include_archived=include_archived,
            sort=order_by,
            after=after_cursor,
            fetch_all=all,
        )

        # Enhance pagination info for display
        display_pagination_info: dict[str, str | bool | int] = dict(pagination_info)
        if not all:
            start_index = ((page or 1) - 1) * per_page + 1
            end_index = start_index + len(issues) - 1
            display_pagination_info["startIndex"] = start_index
            display_pagination_info["endIndex"] = end_index
            display_pagination_info["currentPage"] = page or 1
            display_pagination_info["perPage"] = per_page

        # Format output
        if format == "json":
            format_json(issues)
        else:  # table
            if group_by in ["cycle", "project", "team"]:
                from typing import cast, Literal
                from linear.formatters import format_table_grouped

                format_table_grouped(
                    issues,
                    cast(Literal["cycle", "project", "team"], group_by),
                    display_pagination_info,
                )
            else:
                format_table(issues, display_pagination_info)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("list")
def list_issues(
    ctx: typer.Context,
    assignee: Annotated[
        Optional[str],
        typer.Option(
            "--assignee",
            "-a",
            help="Filter by assignee email (use 'me' or 'self' for yourself)",
        ),
    ] = None,
    creator: Annotated[
        Optional[str],
        typer.Option(
            "--creator",
            "-c",
            help="Filter by issue creator email (use 'me' or 'self' for yourself)",
        ),
    ] = None,
    no_assignee: Annotated[
        bool,
        typer.Option(
            "--no-assignee", help="Show all issues (disable default 'my issues' filter)"
        ),
    ] = False,
    project: Annotated[
        Optional[str], typer.Option("--project", "-p", help="Filter by project name")
    ] = None,
    status: Annotated[
        Optional[str], typer.Option("--status", "-s", help="Filter by status")
    ] = None,
    team: Annotated[
        Optional[str],
        typer.Option("--team", "-t", help="Filter by team key (e.g., ENG, DESIGN)"),
    ] = None,
    priority: Annotated[
        Optional[int], typer.Option("--priority", help="Filter by priority (0-4)")
    ] = None,
    label: Annotated[
        Optional[list[str]],
        typer.Option("--label", "-l", help="Filter by label (repeatable)"),
    ] = None,
    per_page: Annotated[
        int, typer.Option("--per-page", help="Number of issues per page (max 250)")
    ] = 50,
    page: Annotated[
        Optional[int], typer.Option("--page", help="Page number to fetch (starts at 1)")
    ] = None,
    all: Annotated[
        bool, typer.Option("--all", help="Fetch all results automatically")
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", help="DEPRECATED: use --per-page instead"),
    ] = None,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived issues")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort by: created, updated, priority")
    ] = "updated",
    group_by: Annotated[
        Optional[str],
        typer.Option(
            "--group-by", help="Group by: cycle, project, team (default: cycle)"
        ),
    ] = "cycle",
) -> None:
    """List Linear issues.

    By default, shows issues assigned to you (like "My Issues" in Linear's web app).
    Use --no-assignee to see all issues, or provide explicit filters.

    Examples:

      # List your assigned issues (default)
      linear issues list

      # List all issues in workspace
      linear issues list --no-assignee

      # List issues you created (manager view: see delegated work)
      linear issues list --creator me

      # List your team's issues (disable default assignee filter)
      linear issues list --team ENG --no-assignee

      # List your assigned issues in a specific team
      linear issues list --team ENG

      # Filter by status
      linear issues list --status "in progress"

      # Explicitly filter by different assignee
      linear issues list --assignee user@example.com

      # Combine filters
      linear issues list --creator me --status "in progress"

      # Fetch all results
      linear issues list --all

      # Output as JSON
      linear issues list --format json

      # Filter by labels
      linear issues list --label bug --label urgent
    """
    # Apply default assignee filter unless explicitly disabled or overridden
    if assignee is None and not no_assignee:
        assignee = "me"

    _list_issues_impl(
        ctx=ctx,
        assignee=assignee,
        creator=creator,
        project=project,
        status=status,
        team=team,
        priority=priority,
        labels=label,
        per_page=per_page,
        page=page,
        all=all,
        limit=limit,
        include_archived=include_archived,
        format=format,
        order_by=order_by,
        group_by=group_by,
    )


@app.command("view")
def view_issue(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
    web: Annotated[
        bool, typer.Option("--web", "-w", help="Open issue in web browser")
    ] = False,
) -> None:
    """Get details of a specific Linear issue.

    Examples:

      # View issue by identifier
      linear issues view ENG-123

      # Open issue in browser
      linear issues view ENG-123 --web

       # View issue as JSON
       linear issues view ENG-123 --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch issue
        issue = client.get_issue(issue_id)

        # Open in browser if requested
        if web:
            webbrowser.open(str(issue.url))
            console = Console()
            console.print(f"[green][/green] Opened {issue_id} in browser")

        # Format output (still show details even with --web)
        if format == "json":
            format_issue_json(issue)
        else:  # detail
            format_issue_detail(issue)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("search")
def search_issues(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Search query (searches issue titles)")],
    per_page: Annotated[
        int, typer.Option("--per-page", help="Number of issues per page (max 250)")
    ] = 50,
    all: Annotated[
        bool, typer.Option("--all", help="Fetch all results automatically")
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", help="DEPRECATED: use --per-page instead"),
    ] = None,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived issues")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort by: created, updated, priority")
    ] = "updated",
    group_by: Annotated[
        Optional[str],
        typer.Option("--group-by", help="Group by: cycle, project, team"),
    ] = None,
) -> None:
    """Search Linear issues by title.

    Examples:

      # Search for issues with "authentication" in title
      linear issues search authentication

      # Search with output as JSON
      linear issues search "bug fix" --format json

      # Fetch all matching results
      linear issues search refactor --all

      # Limit results per page
      linear issues search bug --per-page 10
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Handle deprecated --limit flag
        if limit is not None:
            console = Console()
            console.print(
                "[yellow]Warning: --limit is deprecated, use --per-page instead[/yellow]"
            )
            per_page = limit

        # Validate per_page
        if per_page > 250:
            console = Console()
            console.print("[red]Error: --per-page cannot exceed 250[/red]")
            sys.exit(1)

        # Search issues
        issues, pagination_info = client.search_issues(
            query=query,
            limit=per_page,
            include_archived=include_archived,
            sort=order_by,
            fetch_all=all,
        )

        # Format output
        if format == "json":
            format_json(issues)
        else:  # table
            display_pagination_info: dict[str, str | bool | int] = dict(pagination_info)
            if group_by in ["cycle", "project", "team"]:
                from typing import cast, Literal
                from linear.formatters import format_table_grouped

                format_table_grouped(
                    issues,
                    cast(Literal["cycle", "project", "team"], group_by),
                    display_pagination_info,
                )
            else:
                format_table(issues, display_pagination_info)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("create")
def create_issue(
    ctx: typer.Context,
    prompt: Annotated[
        Optional[str],
        typer.Argument(help="Natural language prompt describing the issue"),
    ] = None,
    title: Annotated[
        Optional[str], typer.Option("--title", help="Issue title (skips AI parsing)")
    ] = None,
    team: Annotated[
        Optional[str], typer.Option("--team", "-t", help="Team ID or key")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="Issue description")
    ] = None,
    assignee: Annotated[
        Optional[str],
        typer.Option("--assignee", "-a", help="Assignee email (defaults to you)"),
    ] = None,
    priority: Annotated[
        Optional[int],
        typer.Option(
            "--priority",
            "-p",
            help="Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low",
        ),
    ] = None,
    project: Annotated[
        Optional[str], typer.Option("--project", help="Project ID or name")
    ] = None,
    labels: Annotated[
        Optional[list[str]],
        typer.Option("--label", "-l", help="Label name (repeatable)"),
    ] = None,
    state: Annotated[
        Optional[str], typer.Option("--state", "-s", help="Workflow state name")
    ] = None,
    estimate: Annotated[
        Optional[int], typer.Option("--estimate", "-e", help="Story points estimate")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Create a new Linear issue.

    \b
    # Natural language with AI parsing (requires claude CLI)
    linear issues create "High priority bug to fix login for john@example.com in ENG team"
    \b
    # Structured mode with explicit --title (skips AI)
    linear issues create --title "Fix login bug" --team ENG
    \b
    # Structured mode with all options
    linear issues create --title "Add dark mode" --team ENG --description "Support dark theme" --priority 2 --label feature --label ui
    \b
    # Defaults: assignee=current user, team=auto-selected if only 1, priority=none
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        if should_use_claude_parsing(
            prompt,
            title,
            team,
            description,
            assignee,
            priority,
            project,
            labels,
            state,
            estimate,
        ):
            # Type narrowing: should_use_claude_parsing ensures prompt is not None
            assert prompt is not None
            with console.status("[dim]Parsing with Claude...[/dim]", spinner="dots"):
                extracted = extract_with_claude(prompt)

            # Override parameters with extracted values
            title = extracted.get("title", prompt)
            description = description or extracted.get("description")
            team = team or extracted.get("team")

            # Handle "me" as special assignee indicator
            extracted_assignee = extracted.get("assignee")
            if extracted_assignee and extracted_assignee.lower() != "me":
                assignee = assignee or extracted_assignee

            priority = priority if priority is not None else extracted.get("priority")
            project = project or extracted.get("project")
            labels = labels or extracted.get("labels")
            state = state or extracted.get("state")
            estimate = estimate if estimate is not None else extracted.get("estimate")

        viewer_response = client.get_viewer()
        viewer = viewer_response.get("viewer", {})
        viewer_id = viewer.get("id")
        viewer_email = viewer.get("email")
        viewer_teams = viewer.get("teams", {}).get("nodes", [])

        # Title is required
        if not title:
            console.print("[red]Error: --title is required[/red]")
            console.print(
                '[dim]Use: linear issues create "Your issue description"[/dim]'
            )
            console.print('[dim]Or:  linear issues create --title "Your title"[/dim]')
            raise typer.Exit(1)

        # Description defaults to None if not provided (no prompt)

        # Handle assignee: default to viewer if not provided
        assignee_id = None
        assignee_email = None
        if assignee:
            # Look up user by email
            try:
                user = client.get_user(assignee)
                assignee_id = user.id
                assignee_email = assignee
            except LinearClientError:
                console.print(f"[red]Error: User '{assignee}' not found[/red]")
                raise typer.Exit(1)
        else:
            # Default to viewer (current user)
            assignee_id = viewer_id
            assignee_email = viewer_email

        # Handle team: auto-select if 1 team, error if multiple
        team_id: str | None = None
        team_name: str | None = None
        if not team:
            # Use viewer's teams
            teams_data = viewer_teams

            if len(teams_data) == 0:
                console.print("[red]Error: No teams available[/red]")
                raise typer.Exit(1)
            elif len(teams_data) == 1:
                # Only one team, use it automatically
                team_id = teams_data[0]["id"]
                team_key = teams_data[0]["key"]
                team_name = f"{team_key} - {teams_data[0]['name']}"
                console.print(f"[dim]Using team: {team_key}[/dim]")
            else:
                # Multiple teams - error, require --team flag
                console.print(
                    "[red]Error: --team required (you belong to multiple teams)[/red]"
                )
                console.print("\n[bold]Available teams:[/bold]")
                for t in teams_data:
                    console.print(f"  {t['key']} - {t['name']}")
                console.print(
                    f"\n[dim]Use: linear issues create --team {teams_data[0]['key']} ...[/dim]"
                )
                raise typer.Exit(1)
        else:
            # Resolve team key/name to ID
            try:
                team_obj = client.get_team(team)
                team_id = team_obj.id
                team_name = f"{team_obj.key} - {team_obj.name}"
            except LinearClientError:
                console.print(f"[red]Error: Team '{team}' not found[/red]")
                raise typer.Exit(1)

        # Priority defaults to 0 (None) if not provided
        if priority is None:
            priority = 0

        label_ids = None
        if labels:
            labels_list, _ = client.list_labels(team=team_id, limit=250)
            label_map = {label.name.lower(): label.id for label in labels_list}

            label_ids = []
            for label_name in labels:
                label_id = label_map.get(label_name.lower())
                if not label_id:
                    typer.echo(
                        f"Warning: Label '{label_name}' not found, skipping", err=True
                    )
                else:
                    label_ids.append(label_id)

            if not label_ids:
                label_ids = None

        # Resolve project name to ID
        project_id = None
        if project:
            # Check if it's already a UUID
            if "-" in project and len(project) == 36:
                project_id = project
            else:
                # Look up by name
                projects_list, _ = client.list_projects(team=team_id, limit=250)
                for p in projects_list:
                    if p.name.lower() == project.lower():
                        project_id = p.id
                        break

                if not project_id:
                    typer.echo(
                        f"Warning: Project '{project}' not found, skipping", err=True
                    )

        # Resolve state name to ID
        state_id = None
        if state and team_id:
            # Look up state by name
            try:
                states_list = client.get_team_states(team_id)
                for s in states_list:
                    if s["name"].lower() == state.lower():
                        state_id = s["id"]
                        break

                if not state_id:
                    console.print(
                        f"[yellow]Warning: State '{state}' not found in team {team_name.split(' - ')[0] if team_name else team_id}, skipping[/yellow]"
                    )
            except LinearClientError as e:
                console.print(
                    f"[yellow]Warning: Failed to list states: {e}, skipping[/yellow]"
                )

        # Show summary and ask for confirmation (with edit loop)
        while True:
            console.print("\n[bold]Issue details:[/bold]")
            console.print(f"  [bold]Title:[/bold] {title}")

            # Always show description (even if empty)
            if description:
                # Truncate long descriptions
                desc_preview = (
                    description[:50] + "..." if len(description) > 50 else description
                )
                console.print(f"  [bold]Description:[/bold] {desc_preview}")
            else:
                console.print("  [bold]Description:[/bold] [dim](none)[/dim]")

            console.print(f"  [bold]Assignee:[/bold] {assignee_email}")
            console.print(f"  [bold]Team:[/bold] {team_name}")

            # Always show priority
            if priority is not None:
                priority_labels = {
                    1: "Urgent",
                    2: "High",
                    3: "Medium",
                    4: "Low",
                }
                console.print(
                    f"  [bold]Priority:[/bold] {priority_labels.get(priority, 'None')}"
                )
            else:
                console.print("  [bold]Priority:[/bold] [dim](none)[/dim]")
            if labels:
                console.print(f"  [bold]Labels:[/bold] {', '.join(labels)}")
            if project:
                console.print(f"  [bold]Project:[/bold] {project}")
            if state:
                console.print(f"  [bold]State:[/bold] {state}")
            if estimate:
                console.print(f"  [bold]Estimate:[/bold] {estimate} points")

            # Ask for confirmation with edit option
            response = Prompt.ask(
                "\nCreate issue?",
                choices=["y", "yes", "n", "no", "e", "edit"],
                default="y",
                show_choices=True,
                case_sensitive=False,
            )
            choice = response[0].lower()

            if choice == "n":
                console.print("[yellow]Issue creation cancelled.[/yellow]")
                sys.exit(0)
            elif choice == "y":
                break  # Proceed to create issue
            elif choice == "e":
                # Edit in $EDITOR
                try:
                    # Prepare IssueData with current values
                    issue_data = IssueData(
                        title=title,
                        description=description,
                        priority=priority if priority is not None else 0,
                        estimate=estimate,
                        team=team
                        if team
                        else (team_name.split(" - ")[0] if team_name else None),
                        assignee=assignee_email,
                        project=project,
                        labels=labels,
                        state=state,
                    )

                    # Open editor and get edited data
                    edited_data = edit_issue_in_editor(issue_data)

                    # Update basic fields
                    title = edited_data.title
                    description = edited_data.description
                    priority = edited_data.priority
                    estimate = edited_data.estimate

                    # Update metadata fields and re-resolve IDs if changed
                    if edited_data.team and edited_data.team != (
                        team
                        if team
                        else (team_name.split(" - ")[0] if team_name else None)
                    ):
                        team = edited_data.team
                        # Re-resolve team ID
                        try:
                            team_obj = client.get_team(team)
                            team_id = team_obj.id
                            team_name = f"{team_obj.key} - {team_obj.name}"
                        except LinearClientError:
                            console.print(f"[red]Error: Team '{team}' not found[/red]")
                            console.print(
                                "[yellow]Keeping original team. Please try again or cancel.[/yellow]"
                            )

                    if edited_data.assignee and edited_data.assignee != assignee_email:
                        assignee = edited_data.assignee
                        # Re-resolve assignee ID
                        try:
                            user = client.get_user(assignee)
                            assignee_id = user.id
                            assignee_email = assignee
                        except LinearClientError:
                            console.print(
                                f"[red]Error: User '{assignee}' not found[/red]"
                            )
                            console.print(
                                "[yellow]Keeping original assignee. Please try again or cancel.[/yellow]"
                            )

                    if edited_data.project != project:
                        project = edited_data.project
                        # Re-resolve project ID
                        if project:
                            project_id = None
                            projects_list, _ = client.list_projects(
                                team=team_id, limit=250
                            )
                            for p in projects_list:
                                if p.name.lower() == project.lower():
                                    project_id = p.id
                                    break
                            if not project_id:
                                console.print(
                                    f"[red]Error: Project '{project}' not found[/red]"
                                )
                                console.print(
                                    "[yellow]Keeping original project. Please try again or cancel.[/yellow]"
                                )
                        else:
                            project_id = None

                    if edited_data.labels != labels:
                        labels = edited_data.labels
                        # Re-resolve label IDs
                        if labels:
                            label_ids = []
                            labels_list, _ = client.list_labels(team=team_id, limit=250)
                            label_map = {
                                label.name.lower(): label.id for label in labels_list
                            }
                            label_ids = []
                            for label_name in labels:
                                label_id = label_map.get(label_name.lower())
                                if not label_id:
                                    console.print(
                                        f"[yellow]Warning: Label '{label_name}' not found, skipping[/yellow]"
                                    )
                                else:
                                    label_ids.append(label_id)
                            if not label_ids:
                                label_ids = None
                        else:
                            label_ids = None

                    if edited_data.state != state:
                        state = edited_data.state
                        # Note: State resolution by name not currently supported
                        # User must provide state ID or use API default
                        state_id = None

                    console.print("[green]Changes saved. Review updated issue:[/green]")
                    # Loop continues, will show updated summary

                except ValueError as e:
                    console.print(f"[red]Validation error: {e}[/red]")
                    console.print("[yellow]Please try again or cancel.[/yellow]")
                    # Loop continues, user can edit again or cancel
                except FileNotFoundError as e:
                    console.print(f"[red]Editor error: {e}[/red]")
                    sys.exit(1)  # Fatal error
                except Exception as e:
                    console.print(f"[red]Unexpected error: {e}[/red]")
                    console.print("[yellow]Continuing with original values.[/yellow]")
                    # Loop continues with original values

        # Ensure team_id is set (should always be set at this point)
        if not team_id:
            console.print("[red]Error: Team ID not set[/red]")
            raise typer.Exit(1)

        # Create the issue
        issue = client.create_issue(
            title=title,
            team_id=team_id,
            description=description,
            assignee_id=assignee_id,
            priority=priority,
            label_ids=label_ids,
            project_id=project_id,
            state_id=state_id,
            estimate=estimate,
        )

        # Format output
        if format == "json":
            typer.echo(json.dumps(issue.model_dump(by_alias=True), indent=2))
        else:
            # Detail format - success message with key info
            console.print("\n[green][/green] Issue created successfully!")
            console.print(f"[bold]Identifier:[/bold] {issue.identifier}")
            console.print(f"[bold]Title:[/bold] {issue.title}")
            console.print(f"[bold]URL:[/bold] {issue.url}")

            if issue.assignee:
                console.print(f"[bold]Assignee:[/bold] {issue.assignee.name}")

            console.print(f"[bold]Priority:[/bold] {issue.priority_label}")
            console.print(f"[bold]State:[/bold] {issue.state.name}")

            if issue.labels:
                label_names = ", ".join([label.name for label in issue.labels])
                console.print(f"[bold]Labels:[/bold] {label_names}")

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


# Helper functions for issue updates


def _issue_to_issue_data(issue: Issue) -> IssueData:
    """Convert Issue model to IssueData for editing.

    Args:
        issue: Issue object from API

    Returns:
        IssueData with current values pre-populated
    """
    return IssueData(
        title=issue.title,
        description=issue.description,
        priority=issue.priority,
        estimate=issue.estimate,
        team=issue.team.key,
        assignee=issue.assignee.email if issue.assignee else None,
        project=issue.project.name if issue.project else None,
        labels=[label.name for label in issue.labels] if issue.labels else None,
        state=issue.state.name,
    )


def _detect_changes(original: IssueData, edited: IssueData) -> dict:
    """Compare two IssueData objects and return dict of changes.

    Args:
        original: Original issue data
        edited: Edited issue data

    Returns:
        Dict of field names to new values (only changed fields)
    """
    changes = {}

    if edited.title != original.title:
        changes["title"] = edited.title

    if edited.description != original.description:
        changes["description"] = edited.description

    if edited.priority != original.priority:
        changes["priority"] = edited.priority

    if edited.estimate != original.estimate:
        changes["estimate"] = edited.estimate

    if edited.team != original.team:
        changes["team"] = edited.team

    if edited.assignee != original.assignee:
        changes["assignee"] = edited.assignee

    if edited.project != original.project:
        changes["project"] = edited.project

    # Labels comparison (handle None vs empty list)
    original_labels = set(original.labels or [])
    edited_labels = set(edited.labels or [])
    if original_labels != edited_labels:
        changes["labels"] = edited.labels

    if edited.state != original.state:
        changes["state"] = edited.state

    return changes


def _display_issue_comparison(
    original: Issue,
    updates: dict,
    display_values: dict,
    console: Console,
) -> None:
    """Display side-by-side comparison of changes.

    Args:
        original: Original issue
        updates: Dict of field names to new values (API format with IDs)
        display_values: Dict of field names to human-readable values
        console: Rich console
    """
    console.print("\n[bold]Changes to apply:[/bold]\n")

    # Priority labels mapping
    priority_labels = {
        0: "None",
        1: "Urgent",
        2: "High",
        3: "Medium",
        4: "Low",
    }

    has_changes = False

    # Title
    if "title" in updates:
        has_changes = True
        console.print("  [bold]Title:[/bold]")
        console.print(f"    [dim]Current:[/dim] {original.title}")
        console.print(f"    [green]New:[/green]     {updates['title']}")
        console.print()

    # Description
    if "description" in updates:
        has_changes = True
        console.print("  [bold]Description:[/bold]")

        old_desc = original.description or "[dim](none)[/dim]"
        if original.description and len(original.description) > 50:
            old_desc = original.description[:50] + "..."

        new_desc = updates["description"] or "[dim](none)[/dim]"
        if updates["description"] and len(updates["description"]) > 50:
            new_desc = updates["description"][:50] + "..."

        console.print(f"    [dim]Current:[/dim] {old_desc}")
        console.print(f"    [green]New:[/green]     {new_desc}")
        console.print()

    # Assignee
    if "assignee_id" in updates:
        has_changes = True
        console.print("  [bold]Assignee:[/bold]")
        old_assignee = (
            original.assignee.email if original.assignee else "[dim](unassigned)[/dim]"
        )
        new_assignee = display_values.get("assignee", "[dim](unassigned)[/dim]")
        console.print(f"    [dim]Current:[/dim] {old_assignee}")
        console.print(f"    [green]New:[/green]     {new_assignee}")
        console.print()

    # Priority
    if "priority" in updates:
        has_changes = True
        console.print("  [bold]Priority:[/bold]")
        console.print(f"    [dim]Current:[/dim] {priority_labels[original.priority]}")
        console.print(
            f"    [green]New:[/green]     {priority_labels[updates['priority']]}"
        )
        console.print()

    # Estimate
    if "estimate" in updates:
        has_changes = True
        console.print("  [bold]Estimate:[/bold]")
        old_est = (
            f"{original.estimate} points" if original.estimate else "[dim](none)[/dim]"
        )
        new_est = (
            f"{updates['estimate']} points"
            if updates["estimate"]
            else "[dim](none)[/dim]"
        )
        console.print(f"    [dim]Current:[/dim] {old_est}")
        console.print(f"    [green]New:[/green]     {new_est}")
        console.print()

    # Project
    if "project_id" in updates:
        has_changes = True
        console.print("  [bold]Project:[/bold]")
        old_proj = original.project.name if original.project else "[dim](none)[/dim]"
        new_proj = display_values.get("project", "[dim](none)[/dim]")
        console.print(f"    [dim]Current:[/dim] {old_proj}")
        console.print(f"    [green]New:[/green]     {new_proj}")
        console.print()

    # Labels
    if "label_ids" in updates:
        has_changes = True
        console.print("  [bold]Labels:[/bold]")
        old_labels = (
            ", ".join([label.name for label in original.labels])
            if original.labels
            else "[dim](none)[/dim]"
        )
        new_labels = display_values.get("labels", "[dim](none)[/dim]")
        console.print(f"    [dim]Current:[/dim] {old_labels}")
        console.print(f"    [green]New:[/green]     {new_labels}")
        console.print()

    # State
    if "state_id" in updates:
        has_changes = True
        console.print("  [bold]State:[/bold]")
        console.print(f"    [dim]Current:[/dim] {original.state.name}")
        new_state = display_values.get("state", "[dim](unknown)[/dim]")
        console.print(f"    [green]New:[/green]     {new_state}")
        console.print()

    if not has_changes:
        console.print("  [dim]No changes to apply[/dim]\n")
    else:
        console.print("[dim]All other fields will remain unchanged[/dim]\n")


def _resolve_update_ids(
    changes: dict,
    original_issue: Issue,
    client: LinearClient,
    console: Console,
) -> tuple[dict, dict]:
    """Centralized ID resolution for updates.

    Args:
        changes: Dict of field names to new values (human-readable)
        original_issue: Original issue object
        client: Linear API client
        console: Rich console

    Returns:
        Tuple of (api_input_dict, display_values_dict)
        - api_input_dict: Fields with resolved IDs for API call
        - display_values_dict: Human-readable values for display

    Raises:
        typer.Exit: If resolution fails
    """
    api_input = {}
    display_values = {}

    # Team changes - not supported in v1
    if "team" in changes:
        console.print("[red]Error: Changing issue team is not supported via CLI[/red]")
        console.print(
            "[dim]Please use the Linear web app to move issues between teams[/dim]"
        )
        raise typer.Exit(1)

    # Title - direct copy
    if "title" in changes:
        api_input["title"] = changes["title"]

    # Description - direct copy
    if "description" in changes:
        api_input["description"] = changes["description"]

    # Priority - direct copy
    if "priority" in changes:
        api_input["priority"] = changes["priority"]

    # Estimate - direct copy
    if "estimate" in changes:
        api_input["estimate"] = changes["estimate"]

    # Assignee resolution
    if "assignee" in changes:
        assignee = changes["assignee"]
        if assignee is None or (
            isinstance(assignee, str) and assignee.lower() == "null"
        ):
            # Explicitly unassign
            api_input["assignee_id"] = None
            display_values["assignee"] = "[dim](unassigned)[/dim]"
        elif assignee.lower() in ("me", "self"):
            # Assign to current user
            try:
                viewer_response = client.get_viewer()
                api_input["assignee_id"] = viewer_response["viewer"]["id"]
                display_values["assignee"] = viewer_response["viewer"]["email"]
            except LinearClientError as e:
                console.print(f"[red]Error: Failed to get current user: {e}[/red]")
                raise typer.Exit(1)
        else:
            # Look up user by email
            try:
                user = client.get_user(assignee)
                api_input["assignee_id"] = user.id
                display_values["assignee"] = user.email
            except LinearClientError:
                console.print(f"[red]Error: User '{assignee}' not found[/red]")
                raise typer.Exit(1)

    # Project resolution
    if "project" in changes:
        project = changes["project"]
        if project is None or (isinstance(project, str) and project.lower() == "null"):
            # Explicitly remove project
            api_input["project_id"] = None
            display_values["project"] = "[dim](none)[/dim]"
        else:
            # Look up project by name in the issue's team
            try:
                projects_list, _ = client.list_projects(
                    team=original_issue.team.id, limit=250
                )
                project_found = False
                for p in projects_list:
                    if p.name.lower() == project.lower():
                        api_input["project_id"] = p.id
                        display_values["project"] = p.name
                        project_found = True
                        break
                if not project_found:
                    console.print(
                        f"[red]Error: Project '{project}' not found in team {original_issue.team.key}[/red]"
                    )
                    raise typer.Exit(1)
            except LinearClientError as e:
                console.print(f"[red]Error: Failed to list projects: {e}[/red]")
                raise typer.Exit(1)

    # Labels resolution
    if "labels" in changes:
        labels = changes["labels"]
        if labels is None or (isinstance(labels, list) and len(labels) == 0):
            # Clear all labels
            api_input["label_ids"] = []
            display_values["labels"] = "[dim](none)[/dim]"
        else:
            # Look up labels by name in the issue's team
            try:
                labels_list, _ = client.list_labels(
                    team=original_issue.team.id, limit=250
                )
                label_map = {label.name.lower(): label for label in labels_list}

                resolved_label_ids = []
                resolved_label_names = []
                for label_name in labels:
                    label = label_map.get(label_name.lower())
                    if not label:
                        console.print(
                            f"[yellow]Warning: Label '{label_name}' not found in team {original_issue.team.key}, skipping[/yellow]"
                        )
                    else:
                        resolved_label_ids.append(label.id)
                        resolved_label_names.append(label.name)

                api_input["label_ids"] = (
                    resolved_label_ids if resolved_label_ids else []
                )
                display_values["labels"] = (
                    ", ".join(resolved_label_names)
                    if resolved_label_names
                    else "[dim](none)[/dim]"
                )
            except LinearClientError as e:
                console.print(f"[red]Error: Failed to list labels: {e}[/red]")
                raise typer.Exit(1)

    # State resolution
    if "state" in changes:
        state = changes["state"]
        if state is None or (isinstance(state, str) and state.lower() == "null"):
            # Cannot unset state (every issue must have a state)
            console.print(
                "[yellow]Warning: Cannot remove state from issue, skipping[/yellow]"
            )
        else:
            # Look up state by name in the issue's team
            try:
                team_id = original_issue.team.id
                if not team_id:
                    console.print("[red]Error: Issue team ID not found[/red]")
                    raise typer.Exit(1)

                states_list = client.get_team_states(team_id)
                state_found = False
                for s in states_list:
                    if s["name"].lower() == state.lower():
                        api_input["state_id"] = s["id"]
                        display_values["state"] = s["name"]
                        state_found = True
                        break
                if not state_found:
                    console.print(
                        f"[red]Error: State '{state}' not found in team {original_issue.team.key}[/red]"
                    )
                    raise typer.Exit(1)
            except LinearClientError as e:
                console.print(f"[red]Error: Failed to list states: {e}[/red]")
                raise typer.Exit(1)

    return api_input, display_values


def _update_with_flags(
    issue_id: str,
    title: str | None,
    description: str | None,
    assignee: str | None,
    priority: int | None,
    project: str | None,
    labels: list[str] | None,
    state: str | None,
    estimate: int | None,
    client: LinearClient,
    console: Console,
) -> Issue:
    """CLI flag mode workflow for updating issues.

    Args:
        issue_id: Issue identifier or UUID
        title: New title
        description: New description
        assignee: New assignee (email, "me", or "null")
        priority: New priority (0-4)
        project: New project (name or "null")
        labels: New labels list (replaces all)
        state: New state name
        estimate: New estimate (-1 to clear)
        client: Linear API client
        console: Rich console

    Returns:
        Updated Issue object

    Raises:
        typer.Exit: If update fails
    """
    # Fetch existing issue
    try:
        original = client.get_issue(issue_id)
    except LinearClientError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(
            f"[dim]Make sure '{issue_id}' is a valid issue identifier or ID[/dim]"
        )
        raise typer.Exit(1)

    # Build changes dict from provided flags
    changes = {}

    if title is not None:
        changes["title"] = title
    if description is not None:
        changes["description"] = description
    if assignee is not None:
        changes["assignee"] = assignee
    if priority is not None:
        changes["priority"] = priority
    if project is not None:
        changes["project"] = project
    if labels is not None:
        changes["labels"] = labels
    if state is not None:
        changes["state"] = state
    if estimate is not None:
        # Special handling: -1 means clear estimate
        changes["estimate"] = None if estimate == -1 else estimate

    # Resolve IDs
    api_input, display_values = _resolve_update_ids(changes, original, client, console)

    # Display comparison
    _display_issue_comparison(original, api_input, display_values, console)

    # Prompt for confirmation
    response = Prompt.ask(
        "Apply these changes?",
        choices=["y", "yes", "n", "no"],
        default="y",
        show_choices=True,
        case_sensitive=False,
    )

    if response[0].lower() == "n":
        console.print("[yellow]Update cancelled.[/yellow]")
        raise typer.Exit()

    # Apply update
    try:
        updated_issue = client.update_issue(issue_id=original.id, **api_input)
        console.print("\n[green]Issue updated successfully[/green]")
        return updated_issue
    except LinearClientError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _update_with_editor(
    issue_id: str,
    client: LinearClient,
    console: Console,
) -> Issue:
    """Interactive editor mode workflow for updating issues.

    Args:
        issue_id: Issue identifier or UUID
        client: Linear API client
        console: Rich console

    Returns:
        Updated Issue object

    Raises:
        typer.Exit: If update fails or is cancelled
    """
    # Fetch existing issue
    try:
        original = client.get_issue(issue_id)
    except LinearClientError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(
            f"[dim]Make sure '{issue_id}' is a valid issue identifier or ID[/dim]"
        )
        raise typer.Exit(1)

    # Convert to IssueData
    original_data = _issue_to_issue_data(original)

    # Open editor
    try:
        edited_data = edit_issue_in_editor(original_data)
    except ValueError as e:
        console.print(f"[red]Validation error: {e}[/red]")
        raise typer.Exit(1)
    except FileNotFoundError as e:
        console.print(f"[red]Editor error: {e}[/red]")
        raise typer.Exit(1)

    # Detect changes
    changes = _detect_changes(original_data, edited_data)

    if not changes:
        console.print("[yellow]No changes detected. Update cancelled.[/yellow]")
        raise typer.Exit()

    # Confirmation loop with re-edit support
    while True:
        # Resolve IDs
        api_input, display_values = _resolve_update_ids(
            changes, original, client, console
        )

        # Display comparison
        _display_issue_comparison(original, api_input, display_values, console)

        # Prompt for confirmation
        response = Prompt.ask(
            "Apply these changes?",
            choices=["y", "yes", "n", "no", "e", "edit"],
            default="y",
            show_choices=True,
            case_sensitive=False,
        )

        if response[0].lower() == "n":
            console.print("[yellow]Update cancelled.[/yellow]")
            raise typer.Exit()
        elif response[0].lower() == "y":
            break  # Proceed to apply changes
        elif response[0].lower() == "e":
            # Re-open editor with current edited values
            try:
                edited_data = edit_issue_in_editor(edited_data)
                changes = _detect_changes(original_data, edited_data)

                if not changes:
                    console.print(
                        "[yellow]No changes detected. Update cancelled.[/yellow]"
                    )
                    raise typer.Exit()
                # Loop continues
            except ValueError as e:
                console.print(f"[red]Validation error: {e}[/red]")
                raise typer.Exit(1)
            except FileNotFoundError as e:
                console.print(f"[red]Editor error: {e}[/red]")
                raise typer.Exit(1)

    # Apply update
    try:
        updated_issue = client.update_issue(issue_id=original.id, **api_input)
        console.print("\n[green]Issue updated successfully[/green]")
        return updated_issue
    except LinearClientError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("update")
def update_issue(
    ctx: typer.Context,
    issue_id: Annotated[
        str,
        typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')"),
    ],
    title: Annotated[
        Optional[str],
        typer.Option("--title", help="New issue title"),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option("--description", "-d", help="New issue description"),
    ] = None,
    assignee: Annotated[
        Optional[str],
        typer.Option(
            "--assignee",
            "-a",
            help="Assignee email (use 'me' for yourself, 'null' to unassign)",
        ),
    ] = None,
    priority: Annotated[
        Optional[int],
        typer.Option(
            "--priority",
            "-p",
            help="Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low",
        ),
    ] = None,
    project: Annotated[
        Optional[str],
        typer.Option("--project", help="Project ID or name (use 'null' to remove)"),
    ] = None,
    labels: Annotated[
        Optional[list[str]],
        typer.Option(
            "--label", "-l", help="Label name (repeatable, replaces all labels)"
        ),
    ] = None,
    state: Annotated[
        Optional[str],
        typer.Option("--state", "-s", help="Workflow state name"),
    ] = None,
    estimate: Annotated[
        Optional[int],
        typer.Option(
            "--estimate", "-e", help="Story points estimate (use -1 to clear)"
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: detail, json"),
    ] = "detail",
) -> None:
    """Update an existing Linear issue.

    Supports two modes:

    \b
    1. CLI flags (update specific fields):
       linear issues update ENG-123 --title "New title" --priority 2

    \b
    2. Interactive editor (edit all fields in $EDITOR):
       linear issues update ENG-123

    \b
    The command will show a before/after comparison and ask for confirmation
    before applying changes. Only specified fields are updated; all other
    fields remain unchanged.

    \b
    Examples:
      # Update title and priority
      linear issues update ENG-123 --title "Fix login bug" --priority 1

      # Reassign to yourself
      linear issues update ENG-123 --assignee me

      # Unassign issue
      linear issues update ENG-123 --assignee null

      # Clear estimate
      linear issues update ENG-123 --estimate -1

      # Update multiple labels (replaces all)
      linear issues update ENG-123 --label bug --label urgent

      # Open in editor for interactive editing
      linear issues update ENG-123

       # Output as JSON
       linear issues update ENG-123 --title "New title" --format json
    """
    # Extract verbose flag from context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    verbose_logger = VerboseLogger(enabled=verbose)

    # Initialize
    client = LinearClient(verbose_logger=verbose_logger)
    console = Console()

    # Validation
    if priority is not None and (priority < 0 or priority > 4):
        console.print("[red]Error: Priority must be between 0 and 4[/red]")
        console.print("[dim]0=None, 1=Urgent, 2=High, 3=Medium, 4=Low[/dim]")
        raise typer.Exit(1)

    if estimate is not None and estimate < -1:
        console.print("[red]Error: Estimate must be >= 0 (or -1 to clear)[/red]")
        raise typer.Exit(1)

    # Mode detection
    has_any_flags = any(
        [
            title is not None,
            description is not None,
            assignee is not None,
            priority is not None,
            project is not None,
            labels is not None,
            state is not None,
            estimate is not None,
        ]
    )

    try:
        if has_any_flags:
            # CLI flag mode
            updated_issue = _update_with_flags(
                issue_id,
                title,
                description,
                assignee,
                priority,
                project,
                labels,
                state,
                estimate,
                client,
                console,
            )
        else:
            # Interactive editor mode
            updated_issue = _update_with_editor(issue_id, client, console)

        # Display result for JSON format only
        if format == "json":
            console.print(format_issue_json(updated_issue))

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_issue(
    ctx: typer.Context,
    issue_id: Annotated[
        str,
        typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')"),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Delete (trash) a Linear issue.

    Examples:

      # Delete an issue with confirmation
      linear issues delete ENG-123

      # Delete without confirmation prompt
      linear issues delete ENG-123 --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch the issue first to get details and resolve identifier to UUID
        try:
            issue = client.get_issue(issue_id)
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(
                f"[dim]Make sure '{issue_id}' is a valid issue identifier or ID[/dim]"
            )
            raise typer.Exit(1)

        # Show issue details
        console.print("\n[bold]Issue to delete:[/bold]")
        console.print(f"  [bold]Identifier:[/bold] {issue.identifier}")
        console.print(f"  [bold]Title:[/bold] {issue.title}")
        console.print(f"  [bold]Team:[/bold] {issue.team.key}")
        console.print(f"  [bold]State:[/bold] {issue.state.name}")

        if issue.assignee:
            console.print(f"  [bold]Assignee:[/bold] {issue.assignee.email}")

        # Confirmation (unless --yes flag is used)
        if not yes:
            response = Prompt.ask(
                "\n[yellow]Are you sure you want to delete this issue?[/yellow]",
                choices=["y", "yes", "n", "no"],
                default="n",
                show_choices=True,
                case_sensitive=False,
            )

            if response[0].lower() == "n":
                console.print("[yellow]Deletion cancelled.[/yellow]")
                sys.exit(0)

        # Delete the issue
        try:
            client.delete_issue(issue_id=issue.id)
            console.print(
                f"\n[green]Issue {issue.identifier} deleted successfully[/green]"
            )
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("archive")
def archive_issue(
    ctx: typer.Context,
    issue_id: Annotated[
        str,
        typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')"),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Archive a Linear issue.

    Examples:

      # Archive an issue with confirmation
      linear issues archive ENG-123

      # Archive without confirmation prompt
      linear issues archive ENG-123 --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch the issue first to get details and resolve identifier to UUID
        try:
            issue = client.get_issue(issue_id)
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(
                f"[dim]Make sure '{issue_id}' is a valid issue identifier or ID[/dim]"
            )
            raise typer.Exit(1)

        # Show issue details
        console.print("\n[bold]Issue to archive:[/bold]")
        console.print(f"  [bold]Identifier:[/bold] {issue.identifier}")
        console.print(f"  [bold]Title:[/bold] {issue.title}")
        console.print(f"  [bold]Team:[/bold] {issue.team.key}")
        console.print(f"  [bold]State:[/bold] {issue.state.name}")

        if issue.assignee:
            console.print(f"  [bold]Assignee:[/bold] {issue.assignee.email}")

        # Confirmation (unless --yes flag is used)
        if not yes:
            response = Prompt.ask(
                "\n[yellow]Are you sure you want to archive this issue?[/yellow]",
                choices=["y", "yes", "n", "no"],
                default="n",
                show_choices=True,
                case_sensitive=False,
            )

            if response[0].lower() == "n":
                console.print("[yellow]Archive cancelled.[/yellow]")
                sys.exit(0)

        # Archive the issue
        try:
            client.archive_issue(issue_id=issue.id)
            console.print(
                f"\n[green]Issue {issue.identifier} archived successfully[/green]"
            )
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("unarchive")
def unarchive_issue(
    ctx: typer.Context,
    issue_id: Annotated[
        str,
        typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')"),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Unarchive a Linear issue.

    Examples:

      # Unarchive an issue with confirmation
      linear issues unarchive ENG-123

      # Unarchive without confirmation prompt
      linear issues unarchive ENG-123 --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch the issue first to get details and resolve identifier to UUID
        try:
            issue = client.get_issue(issue_id)
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(
                f"[dim]Make sure '{issue_id}' is a valid issue identifier or ID[/dim]"
            )
            raise typer.Exit(1)

        # Show issue details
        console.print("\n[bold]Issue to unarchive:[/bold]")
        console.print(f"  [bold]Identifier:[/bold] {issue.identifier}")
        console.print(f"  [bold]Title:[/bold] {issue.title}")
        console.print(f"  [bold]Team:[/bold] {issue.team.key}")
        console.print(f"  [bold]State:[/bold] {issue.state.name}")

        if issue.assignee:
            console.print(f"  [bold]Assignee:[/bold] {issue.assignee.email}")

        # Confirmation (unless --yes flag is used)
        if not yes:
            response = Prompt.ask(
                "\n[yellow]Are you sure you want to unarchive this issue?[/yellow]",
                choices=["y", "yes", "n", "no"],
                default="n",
                show_choices=True,
                case_sensitive=False,
            )

            if response[0].lower() == "n":
                console.print("[yellow]Unarchive cancelled.[/yellow]")
                sys.exit(0)

        # Unarchive the issue
        try:
            client.unarchive_issue(issue_id=issue.id)
            console.print(
                f"\n[green]Issue {issue.identifier} unarchived successfully[/green]"
            )
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("move-state")
def move_state(
    ctx: typer.Context,
    issue_id: Annotated[
        str,
        typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')"),
    ],
    state: Annotated[
        str,
        typer.Argument(help="State name (e.g., 'In Progress', 'Done')"),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Move an issue to a different workflow state.

    Examples:

      # Move issue to "In Progress" state
      linear issues move-state ENG-123 "In Progress"

      # Move issue to "Done" state without confirmation
      linear issues move-state ENG-123 Done --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch the issue first to get details and resolve identifier to UUID
        try:
            issue = client.get_issue(issue_id)
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(
                f"[dim]Make sure '{issue_id}' is a valid issue identifier or ID[/dim]"
            )
            raise typer.Exit(1)

        # Look up state by name in the issue's team
        try:
            team_id = issue.team.id
            if not team_id:
                console.print("[red]Error: Issue team ID not found[/red]")
                raise typer.Exit(1)

            states_list = client.get_team_states(team_id)
            state_id = None
            state_name = None
            for s in states_list:
                if s["name"].lower() == state.lower():
                    state_id = s["id"]
                    state_name = s["name"]
                    break

            if not state_id:
                console.print(
                    f"[red]Error: State '{state}' not found in team {issue.team.key}[/red]"
                )
                console.print("\n[bold]Available states:[/bold]")
                for s in states_list:
                    console.print(f"  {s['name']}")
                raise typer.Exit(1)
        except LinearClientError as e:
            console.print(f"[red]Error: Failed to list states: {e}[/red]")
            raise typer.Exit(1)

        # Show issue details and state change
        console.print("\n[bold]Issue:[/bold]")
        console.print(f"  [bold]Identifier:[/bold] {issue.identifier}")
        console.print(f"  [bold]Title:[/bold] {issue.title}")
        console.print(f"  [bold]Team:[/bold] {issue.team.key}")
        console.print("\n[bold]State change:[/bold]")
        console.print(f"  [dim]Current:[/dim] {issue.state.name}")
        console.print(f"  [green]New:[/green]     {state_name}")

        # Confirmation (unless --yes flag is used)
        if not yes:
            response = Prompt.ask(
                "\n[yellow]Apply this state change?[/yellow]",
                choices=["y", "yes", "n", "no"],
                default="y",
                show_choices=True,
                case_sensitive=False,
            )

            if response[0].lower() == "n":
                console.print("[yellow]State change cancelled.[/yellow]")
                sys.exit(0)

        # Update the issue state
        try:
            client.update_issue(issue_id=issue.id, state_id=state_id)
            console.print(
                f"\n[green]Issue {issue.identifier} moved to '{state_name}' successfully[/green]"
            )
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@relations_app.command("list")
def list_relations(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List all relations for an issue.

    Examples:

      # List relations for an issue
      linear issues relations list ENG-123

      # Output as JSON
      linear issues relations list ENG-123 --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch issue to resolve identifier to UUID
        issue = client.get_issue(issue_id)

        # Fetch relations
        relations = client.list_issue_relations(issue.id)

        # Format output
        if format == "json":
            from linear.formatters import format_relations_json

            format_relations_json(relations)
        else:  # table
            from linear.formatters import format_relations_table

            format_relations_table(relations, source_issue_id=issue.id)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@relations_app.command("add")
def add_relation(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Source issue ID or identifier (e.g., 'ENG-123')")
    ],
    related_issue_id: Annotated[
        str, typer.Argument(help="Related issue ID or identifier (e.g., 'ENG-456')")
    ],
    type: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Relation type: blocks, blocked, related, duplicate",
        ),
    ] = "related",
) -> None:
    """Add a relation between two issues.

    Examples:

      # Add a 'related' relation
      linear issues relations add ENG-123 ENG-456

      # Add a 'blocks' relation
      linear issues relations add ENG-123 ENG-456 --type blocks

      # Add a 'blocked' relation
      linear issues relations add ENG-123 ENG-456 --type blocked

      # Add a 'duplicate' relation
      linear issues relations add ENG-123 ENG-456 --type duplicate
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client and console
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Validate relation type
        valid_types = ["blocks", "blocked", "related", "duplicate"]
        if type not in valid_types:
            console.print(
                f"[red]Error: Invalid relation type '{type}'. Must be one of: {', '.join(valid_types)}[/red]"
            )
            sys.exit(1)

        # Fetch issues to resolve identifiers to UUIDs
        issue = client.get_issue(issue_id)
        related_issue = client.get_issue(related_issue_id)

        # Show summary
        console.print("\n[bold]Creating relation:[/bold]")
        console.print(f"  [bold]From:[/bold] {issue.identifier} - {issue.title}")
        console.print(
            f"  [bold]To:[/bold] {related_issue.identifier} - {related_issue.title}"
        )
        console.print(f"  [bold]Type:[/bold] {type}")

        # Create relation
        relation = client.create_issue_relation(issue.id, related_issue.id, type)

        console.print(
            f"\n[green]Relation created successfully (ID: {relation.id})[/green]"
        )

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@relations_app.command("remove")
def remove_relation(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    relation_id: Annotated[
        str, typer.Argument(help="Relation ID to remove (use 'list' to see IDs)")
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Remove a relation from an issue.

    Use 'linear issues relations list <issue-id>' to find relation IDs.

    Examples:

      # Remove a relation
      linear issues relations remove ENG-123 <relation-id>

      # Remove without confirmation
      linear issues relations remove ENG-123 <relation-id> --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client and console
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch issue to validate it exists
        issue = client.get_issue(issue_id)

        # Fetch relations to validate relation_id exists and belongs to this issue
        relations = client.list_issue_relations(issue.id)

        # Find the relation
        target_relation = None
        for relation in relations:
            if relation.id == relation_id:
                target_relation = relation
                break

        if not target_relation:
            console.print(
                f"[red]Error: Relation '{relation_id}' not found for issue {issue.identifier}[/red]"
            )
            console.print(
                f"[dim]Use: linear issues relations list {issue.identifier}[/dim]"
            )
            sys.exit(1)

        # Type assertion: target_relation is guaranteed to be non-None after the check above
        assert target_relation is not None

        # Determine which issue to show
        if target_relation.issue.id == issue.id:
            related = target_relation.related_issue
        else:
            related = target_relation.issue

        # Show summary
        console.print("\n[bold]Removing relation:[/bold]")
        console.print(f"  [bold]Issue:[/bold] {issue.identifier} - {issue.title}")
        console.print(f"  [bold]Related:[/bold] {related.identifier} - {related.title}")
        console.print(f"  [bold]Type:[/bold] {target_relation.type}")

        # Confirmation (unless --yes flag is used)
        if not yes:
            response = Prompt.ask(
                "\n[yellow]Are you sure you want to remove this relation?[/yellow]",
                choices=["y", "yes", "n", "no"],
                default="n",
                show_choices=True,
                case_sensitive=False,
            )

            if response[0].lower() == "n":
                console.print("[yellow]Removal cancelled.[/yellow]")
                sys.exit(0)

        # Remove relation
        client.delete_issue_relation(relation_id)

        console.print("\n[green]Relation removed successfully[/green]")

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


# Register relations subcommand
app.add_typer(relations_app, name="relations")
