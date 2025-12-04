"""Linear CLI - Command line interface for Linear."""

import json
import sys
import webbrowser
from typing import Optional

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

from linear import __version__
from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_cycle_detail,
    format_cycle_json,
    format_cycles_json,
    format_cycles_table,
    format_issue_detail,
    format_issue_json,
    format_json,
    format_labels_json,
    format_labels_table,
    format_project_detail,
    format_project_json,
    format_projects_json,
    format_projects_table,
    format_table,
    format_team_detail,
    format_team_json,
    format_teams_json,
    format_teams_table,
    format_user_detail,
    format_user_json,
    format_users_json,
    format_users_table,
)
from linear.models import (
    parse_cycles_response,
    parse_issues_response,
    parse_labels_response,
    parse_projects_response,
    parse_teams_response,
    parse_users_response,
)


def version_callback(value: bool) -> None:
    """Callback for --version flag."""
    if value:
        typer.echo(f"Linear CLI version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    help="Linear CLI - Interact with Linear from your terminal", no_args_is_help=True
)


@app.callback()
def main_callback(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """Linear CLI - Interact with Linear from your terminal."""
    pass


issues_app = typer.Typer(help="Manage Linear issues")
projects_app = typer.Typer(help="Manage Linear projects")
teams_app = typer.Typer(help="Manage Linear teams")
cycles_app = typer.Typer(help="Manage Linear cycles", no_args_is_help=True)
users_app = typer.Typer(help="Manage Linear users", no_args_is_help=True)
labels_app = typer.Typer(help="Manage Linear labels", no_args_is_help=True)
app.add_typer(issues_app, name="issues")
app.add_typer(issues_app, name="i", hidden=True)
app.add_typer(projects_app, name="projects")
app.add_typer(projects_app, name="p", hidden=True)
app.add_typer(teams_app, name="teams")
app.add_typer(teams_app, name="t", hidden=True)
app.add_typer(cycles_app, name="cycles")
app.add_typer(cycles_app, name="c", hidden=True)
app.add_typer(users_app, name="users")
app.add_typer(users_app, name="u", hidden=True)
app.add_typer(labels_app, name="labels")
app.add_typer(labels_app, name="l", hidden=True)


@issues_app.command("list")
def list_issues(
    assignee: Annotated[
        Optional[str],
        typer.Option(
            "--assignee",
            "-a",
            help="Filter by assignee email (use 'me' or 'self' for yourself)",
        ),
    ] = None,
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
    limit: Annotated[
        int, typer.Option("--limit", help="Number of issues to display")
    ] = 50,
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
    """List Linear issues with optional filters.

    Examples:

      # List all issues
      linear issues list

      # List your own issues
      linear issues list --assignee me

      # Filter by assignee
      linear issues list --assignee user@example.com

      # Filter by multiple criteria
      linear issues list --status "in progress" --priority 1 --limit 10

      # Output as JSON
      linear issues list --format json

      # Filter by labels
      linear issues list --label bug --label urgent
    """
    try:
        # Initialize client
        client = LinearClient()

        # Resolve 'me' or 'self' to current user's email
        if assignee and assignee.lower() in ("me", "self"):
            viewer_response = client.get_viewer()
            viewer = viewer_response.get("viewer", {})
            assignee = viewer.get("email")

        # Fetch issues
        response = client.list_issues(
            assignee=assignee,
            project=project,
            status=status,
            team=team,
            priority=priority,
            labels=label,
            limit=limit,
            include_archived=include_archived,
            sort=order_by,
        )

        # Parse response
        issues = parse_issues_response(response)

        # Format output
        if format == "json":
            format_json(issues)
        else:  # table
            if group_by in ["cycle", "project", "team"]:
                from typing import cast, Literal
                from linear.formatters import format_table_grouped

                format_table_grouped(
                    issues, cast(Literal["cycle", "project", "team"], group_by)
                )
            else:
                format_table(issues)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@issues_app.command("view")
def view_issue(
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
        # Initialize client
        client = LinearClient()

        # Fetch issue
        response = client.get_issue(issue_id)

        # Open in browser if requested
        if web:
            issue_url = response.get("issue", {}).get("url")
            if issue_url:
                webbrowser.open(issue_url)
                console = Console()
                console.print(f"[green]✓[/green] Opened {issue_id} in browser")
            else:
                typer.echo("Error: Issue URL not found", err=True)
                sys.exit(1)

        # Format output (still show details even with --web)
        if format == "json":
            format_issue_json(response)
        else:  # detail
            format_issue_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@issues_app.command("search")
def search_issues(
    query: Annotated[str, typer.Argument(help="Search query (searches issue titles)")],
    limit: Annotated[
        int, typer.Option("--limit", help="Number of issues to display")
    ] = 50,
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

      # Limit results
      linear issues search refactor --limit 10
    """
    try:
        # Initialize client
        client = LinearClient()

        # Search issues
        response = client.search_issues(
            query=query,
            limit=limit,
            include_archived=include_archived,
            sort=order_by,
        )

        # Parse response
        issues = parse_issues_response(response)

        # Format output
        if format == "json":
            format_json(issues)
        else:  # table
            if group_by in ["cycle", "project", "team"]:
                from typing import cast, Literal
                from linear.formatters import format_table_grouped

                format_table_grouped(
                    issues, cast(Literal["cycle", "project", "team"], group_by)
                )
            else:
                format_table(issues)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@issues_app.command("create")
def create_issue(
    title: Annotated[Optional[str], typer.Argument(help="Issue title")] = None,
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

    Examples:

      # Interactive mode (prompts for required fields)
      linear issues create

      # Non-interactive with required fields
      linear issues create "Fix login bug" --team ENG

      # With all options
      linear issues create "Add dark mode" --team ENG --description "Support dark theme" \\
        --priority 2 --label feature --label ui
    """
    try:
        console = Console()
        client = LinearClient()

        viewer_response = client.get_viewer()
        viewer = viewer_response.get("viewer", {})
        viewer_id = viewer.get("id")
        viewer_email = viewer.get("email")
        viewer_teams = viewer.get("teams", {}).get("nodes", [])

        if not title:
            title = Prompt.ask("Issue title")

        if not description:
            description_input = Prompt.ask("Description")
            description = description_input if description_input else None

        assignee_id = None
        assignee_email = None
        if assignee:
            # Look up user by email
            user_response = client.get_user(assignee)
            user_data = user_response.get("user")
            if user_data:
                assignee_id = user_data["id"]
                assignee_email = assignee
            else:
                typer.echo(f"Error: User '{assignee}' not found", err=True)
                sys.exit(1)
        else:
            # Prompt for assignee with current user as default
            assignee_email = Prompt.ask(
                "Assignee email", default=viewer_email if viewer_email else ""
            )

            # If user just pressed enter or entered the same email, use viewer
            if assignee_email == viewer_email or not assignee_email:
                assignee_id = viewer_id
                assignee_email = viewer_email
            else:
                # Look up the specified user
                user_response = client.get_user(assignee_email)
                user_data = user_response.get("user")
                if user_data:
                    assignee_id = user_data["id"]
                else:
                    typer.echo(f"Error: User '{assignee_email}' not found", err=True)
                    sys.exit(1)

        team_id = None
        team_name = None
        if not team:
            # Use viewer's teams only
            teams_data = viewer_teams

            if not teams_data:
                typer.echo("Error: You are not a member of any teams", err=True)
                sys.exit(1)
            elif len(teams_data) == 1:
                # Only one team, use it automatically
                team_id = teams_data[0]["id"]
                team_key = teams_data[0]["key"]
                team_name = f"{team_key} - {teams_data[0]['name']}"
                console.print(f"Using team: [cyan]{team_key}[/cyan]")
            else:
                # Multiple teams, prompt user
                console.print("\n[bold]Your teams:[/bold]")
                for i, t in enumerate(teams_data, 1):
                    console.print(f"  {i}. [cyan]{t['key']}[/cyan] - {t['name']}")

                team_choice = IntPrompt.ask(
                    "Select team number",
                    default=1,
                )

                if team_choice < 1 or team_choice > len(teams_data):
                    typer.echo("Error: Invalid team selection", err=True)
                    sys.exit(1)

                selected_team = teams_data[team_choice - 1]
                team_id = selected_team["id"]
                team_name = f"{selected_team['key']} - {selected_team['name']}"
        else:
            # Resolve team key/name to ID
            team_response = client.get_team(team)
            team_data = team_response.get("team")
            if team_data:
                team_id = team_data["id"]
                team_name = f"{team_data['key']} - {team_data['name']}"
            else:
                typer.echo(f"Error: Team '{team}' not found", err=True)
                sys.exit(1)

        if not priority:
            console.print("\n[bold]Priority:[/bold]")
            console.print(" 1. Urgent")
            console.print(" 2. High")
            console.print(" 3. Medium")
            console.print(" 4. Low")

            priority_input = Prompt.ask("Priority")

            try:
                priority = int(priority_input)
                if priority < 1 or priority > 4:
                    typer.echo("Error: Priority must be between 1 and 4", err=True)
                    sys.exit(1)
            except ValueError:
                priority = None

        label_ids = None
        if labels:
            labels_response = client.list_labels(team=team_id, limit=250)
            labels_data = labels_response.get("issueLabels", {}).get("nodes", [])
            label_map = {label["name"].lower(): label["id"] for label in labels_data}

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
                projects_response = client.list_projects(team=team_id, limit=250)
                projects_data = projects_response.get("projects", {}).get("nodes", [])
                for p in projects_data:
                    if p["name"].lower() == project.lower():
                        project_id = p["id"]
                        break

                if not project_id:
                    typer.echo(
                        f"Warning: Project '{project}' not found, skipping", err=True
                    )

        # Resolve state name to ID
        state_id = None
        if state:
            # Get team states
            team_response = client.get_team(team_id)
            states_data = (
                team_response.get("team", {}).get("states", {}).get("nodes", [])
            )
            for s in states_data:
                if s["name"].lower() == state.lower():
                    state_id = s["id"]
                    break

            if not state_id:
                typer.echo(f"Warning: State '{state}' not found, skipping", err=True)

        # Show summary and ask for confirmation
        console.print("\n[bold]Issue Summary:[/bold]")
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

        # Ask for confirmation
        if not Confirm.ask("\nCreate this issue?", default=True):
            console.print("[yellow]Issue creation cancelled.[/yellow]")
            sys.exit(0)

        # Create the issue
        response = client.create_issue(
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
        issue_data = response.get("issueCreate", {}).get("issue", {})

        if format == "json":
            typer.echo(json.dumps(issue_data, indent=2))
        else:
            # Detail format - success message with key info
            console.print("\n[green]✓[/green] Issue created successfully!")
            console.print(f"[bold]Identifier:[/bold] {issue_data.get('identifier')}")
            console.print(f"[bold]Title:[/bold] {issue_data.get('title')}")
            console.print(f"[bold]URL:[/bold] {issue_data.get('url')}")

            assignee_data = issue_data.get("assignee")
            if assignee_data:
                console.print(f"[bold]Assignee:[/bold] {assignee_data.get('name')}")

            console.print(f"[bold]Priority:[/bold] {issue_data.get('priorityLabel')}")
            console.print(
                f"[bold]State:[/bold] {issue_data.get('state', {}).get('name')}"
            )

            labels_data = issue_data.get("labels", {}).get("nodes", [])
            if labels_data:
                label_names = ", ".join([label["name"] for label in labels_data])
                console.print(f"[bold]Labels:[/bold] {label_names}")

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@projects_app.command("list")
def list_projects(
    state: Annotated[
        Optional[str],
        typer.Option(
            "--state",
            "-s",
            help="Filter by state (planned, started, paused, completed, canceled)",
        ),
    ] = None,
    team: Annotated[
        Optional[str],
        typer.Option("--team", "-t", help="Filter by team key (e.g., ENG, DESIGN)"),
    ] = None,
    limit: Annotated[
        int, typer.Option("--limit", help="Number of projects to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived projects")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort by: created, updated")
    ] = "updated",
) -> None:
    """List Linear projects with optional filters.

    Examples:

      # List all projects
      linear projects list

      # Filter by state
      linear projects list --state started

      # Filter by team
      linear projects list --team engineering

      # Output as JSON
      linear projects list --format json

      # Limit results
      linear projects list --limit 10
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch projects
        response = client.list_projects(
            state=state,
            team=team,
            limit=limit,
            include_archived=include_archived,
            sort=order_by,
        )

        # Parse response
        projects = parse_projects_response(response)

        # Format output
        if format == "json":
            format_projects_json(projects)
        else:  # table
            format_projects_table(projects)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@projects_app.command("view")
def view_project(
    project_id: Annotated[str, typer.Argument(help="Project ID or slug")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear project.

    Examples:

      # View project by ID
      linear projects view abc123-def456

      # View project as JSON
      linear projects view my-project --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch project
        response = client.get_project(project_id)

        # Format output
        if format == "json":
            format_project_json(response)
        else:  # detail
            format_project_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@teams_app.command("list")
def list_teams(
    limit: Annotated[
        int, typer.Option("--limit", help="Number of teams to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived teams")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List Linear teams.

    Examples:

      # List all teams
      linear teams list

      # Include archived teams
      linear teams list --include-archived

      # Output as JSON
      linear teams list --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch teams
        response = client.list_teams(
            limit=limit,
            include_archived=include_archived,
        )

        # Parse response
        teams = parse_teams_response(response)

        # Format output
        if format == "json":
            format_teams_json(teams)
        else:  # table
            format_teams_table(teams)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@teams_app.command("view")
def view_team(
    team_id: Annotated[str, typer.Argument(help="Team ID or key (e.g., 'ENG')")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear team.

    Examples:

      # View team by key
      linear teams view ENG

      # View team as JSON
      linear teams view ENG --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch team
        response = client.get_team(team_id)

        # Format output
        if format == "json":
            format_team_json(response)
        else:  # detail
            format_team_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cycles_app.command("list")
def list_cycles(
    team: Annotated[
        Optional[str], typer.Option("--team", "-t", help="Filter by team name or key")
    ] = None,
    active: Annotated[
        bool, typer.Option("--active", "-a", help="Show only active cycles")
    ] = False,
    future: Annotated[
        bool, typer.Option("--future", help="Show only future cycles")
    ] = False,
    past: Annotated[bool, typer.Option("--past", help="Show only past cycles")] = False,
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Number of cycles to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived cycles")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List Linear cycles with optional filters.

    Examples:

      # List all cycles
      linear cycles list

      # Filter by team
      linear cycles list --team ENG

      # Show only active cycles
      linear cycles list --active

      # Show future cycles for a specific team
      linear cycles list --team design --future

      # Output as JSON
      linear cycles list --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch cycles
        response = client.list_cycles(
            team=team,
            active=active,
            future=future,
            past=past,
            limit=limit,
            include_archived=include_archived,
        )

        # Parse cycles
        cycles = parse_cycles_response(response)

        # Format output
        if format == "json":
            format_cycles_json(cycles)
        else:  # table
            format_cycles_table(cycles)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cycles_app.command("view")
def view_cycle(
    cycle_id: Annotated[str, typer.Argument(help="Cycle ID")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear cycle.

    Examples:

      # View cycle by ID
      linear cycles view abc123-def456

      # View cycle as JSON
      linear cycles view abc123 --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch cycle
        response = client.get_cycle(cycle_id)

        # Format output
        if format == "json":
            format_cycle_json(response)
        else:  # detail
            format_cycle_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@users_app.command("list")
def list_users(
    active_only: Annotated[
        bool, typer.Option("--active-only", help="Show only active users")
    ] = True,
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Number of users to display")
    ] = 50,
    include_disabled: Annotated[
        bool, typer.Option("--include-disabled", help="Include disabled users")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List Linear users in the workspace.

    Examples:

      # List all active users
      linear users list

      # List all users including inactive
      linear users list --no-active-only

      # List with limit
      linear users list --limit 20

      # Output as JSON
      linear users list --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch users
        response = client.list_users(
            active_only=active_only,
            limit=limit,
            include_disabled=include_disabled,
        )

        # Parse users
        users = parse_users_response(response)

        # Format output
        if format == "json":
            format_users_json(users)
        else:  # table
            format_users_table(users)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@users_app.command("view")
def view_user(
    user_id: Annotated[str, typer.Argument(help="User ID or email")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear user.

    Examples:

      # View user by ID
      linear users view abc123-def456

      # View user by email
      linear users view user@example.com

      # View user as JSON
      linear users view abc123 --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch user
        response = client.get_user(user_id)

        # Format output
        if format == "json":
            format_user_json(response)
        else:  # detail
            format_user_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@labels_app.command("list")
def list_labels(
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Maximum number of labels to return")
    ] = 50,
    team: Annotated[
        Optional[str],
        typer.Option(
            "--team", "-t", help="Filter by team ID or key (e.g., 'ENG', 'DESIGN')"
        ),
    ] = None,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived labels")
    ] = False,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: table (default) or json"),
    ] = "table",
) -> None:
    """List issue labels.

    Examples:
        linear labels list
        linear labels list --team ENG
        linear labels list --limit 20 --format json
        linear labels list --include-archived
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch labels
        response = client.list_labels(
            limit=limit,
            team=team,
            include_archived=include_archived,
        )

        # Parse response
        labels = parse_labels_response(response)

        # Format output
        if format == "json":
            format_labels_json(labels)
        else:  # table
            format_labels_table(labels)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
