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
from linear.utils.editor import IssueData, edit_issue_in_editor

app = typer.Typer(help="Manage Linear issues")


@app.command("list")
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
        issues = client.list_issues(
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
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("view")
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
        issues = client.search_issues(
            query=query,
            limit=limit,
            include_archived=include_archived,
            sort=order_by,
        )

        # Parse response

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
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("create")
def create_issue(
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
        console = Console()
        client = LinearClient()

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
            labels_list = client.list_labels(team=team_id, limit=250)
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
                projects_list = client.list_projects(team=team_id, limit=250)
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
        if state:
            # Get team states
            # Note: get_team() doesn't return workflow states, so we can't look up by name
            # The user must provide the state ID or leave it empty
            typer.echo(
                "Warning: State lookup by name not supported. Please provide state ID or leave empty.",
                err=True,
            )
            state_id = None

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
                            projects_list = client.list_projects(
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
                            labels_list = client.list_labels(team=team_id, limit=250)
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
