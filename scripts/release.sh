#!/usr/bin/env bash
set -e

BUMP_TYPE=$1

if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "Usage: $0 {patch|minor|major}"
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working directory has uncommitted changes"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: Must be on main branch (currently on: $CURRENT_BRANCH)"
    exit 1
fi

echo "Current version:"
uv version
echo ""
echo "Proposed $BUMP_TYPE bump:"
uv version --bump $BUMP_TYPE --dry-run
echo ""
read -p "Proceed with $BUMP_TYPE bump? (y/N): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

uv version --bump $BUMP_TYPE

NEW_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

git add pyproject.toml uv.lock
git commit -m "Bump $NEW_VERSION"
git tag "v$NEW_VERSION"

git push origin main
git push origin "v$NEW_VERSION"

echo ""
echo "Version bumped to $NEW_VERSION"
echo ""
echo "Extracting changelog section..."

# Extract the changelog section for this version
CHANGELOG_SECTION=$(awk -v version="$NEW_VERSION" '
    /^## \[/ {
        if (found) exit
        if ($0 ~ "\\[" version "\\]") {
            found = 1
            next
        }
    }
    found && /^## \[/ { exit }
    found { print }
' CHANGELOG.md)

if [ -z "$CHANGELOG_SECTION" ]; then
    echo "⚠️  Warning: No changelog section found for version $NEW_VERSION"
    echo "Creating release with auto-generated notes..."
    gh release create "v$NEW_VERSION" --generate-notes
else
    echo "Creating GitHub release with changelog..."
    gh release create "v$NEW_VERSION" --notes "$CHANGELOG_SECTION"
fi

echo ""
echo "Release v$NEW_VERSION created!"
echo ""
echo "GitHub Actions will now:"
echo "  1. Validate version matches tag"
echo "  2. Run quality checks"
echo "  3. Build distributions"
echo "  4. Publish to PyPI"
echo ""
echo "Monitor: https://github.com/cmpadden/linear/actions"
echo "Verify:  https://pypi.org/project/linear-app/$NEW_VERSION/"
