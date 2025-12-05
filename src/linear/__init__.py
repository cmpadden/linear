"""Linear - Command line interface for Linear."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("linear-app")
except PackageNotFoundError:
    # Package is not installed, fallback for development
    __version__ = "dev"

# Re-export commonly used items
from linear.api import LinearClient, LinearClientError
from linear.models import Issue, Project, Team, Cycle, User, Label

__all__ = [
    "__version__",
    "LinearClient",
    "LinearClientError",
    "Issue",
    "Project",
    "Team",
    "Cycle",
    "User",
    "Label",
]
