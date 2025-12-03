"""Linear - Command line interface for Linear."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("linear-app")
except PackageNotFoundError:
    # Package is not installed, fallback for development
    __version__ = "dev"

__all__ = ["__version__"]
