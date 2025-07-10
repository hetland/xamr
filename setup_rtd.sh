#!/bin/bash
# Script to help set up Read the Docs for xamr project

echo "Setting up Read the Docs for xamr..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: This is not a git repository. Please initialize git first."
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# If we're on master, create main branch
if [ "$CURRENT_BRANCH" = "master" ]; then
    echo "You're on the 'master' branch. Read the Docs works better with 'main'."
    echo "Creating and switching to 'main' branch..."
    git checkout -b main
    git push origin main
    git push origin --delete master
fi

# Commit any changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Committing changes..."
    git add .
    git commit -m "Update documentation configuration for Read the Docs"
fi

echo ""
echo "Setup complete! To use with Read the Docs:"
echo "1. Push your code to GitHub/GitLab"
echo "2. Go to https://readthedocs.org/"
echo "3. Import your project"
echo "4. Make sure the default branch is set to 'main'"
echo "5. The documentation will build automatically"
echo ""
echo "Configuration files created:"
echo "  - .readthedocs.yaml (Read the Docs config)"
echo "  - docs/requirements-rtd.txt (lightweight requirements)"
echo "  - .github/workflows/docs.yml (GitHub Actions)"
