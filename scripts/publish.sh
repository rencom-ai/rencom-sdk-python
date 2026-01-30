#!/bin/bash
# Publishing helper script for Rencom SDK
# Usage: ./scripts/publish.sh [testpypi|pypi]

set -e  # Exit on error

TARGET="${1:-testpypi}"  # Default to testpypi for safety
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🚀 Rencom SDK Publishing Script"
echo "================================"
echo "Target: $TARGET"
echo ""

# Step 1: Run tests
echo "📝 Step 1: Running tests..."
if ! uv run pytest tests/unit/ -q; then
    echo "❌ Tests failed! Fix tests before publishing."
    exit 1
fi
echo "✅ Tests passed"
echo ""

# Step 2: Type check
echo "🔍 Step 2: Type checking..."
if ! uv run mypy rencom/ --ignore-missing-imports; then
    echo "⚠️  Type check failed, but continuing..."
fi
echo ""

# Step 3: Lint
echo "🧹 Step 3: Linting..."
if ! uv run ruff check .; then
    echo "⚠️  Linting issues found, but continuing..."
fi
echo ""

# Step 4: Clean old builds
echo "🧹 Step 4: Cleaning old builds..."
rm -rf dist/ build/ *.egg-info
echo "✅ Cleaned"
echo ""

# Step 5: Build package
echo "📦 Step 5: Building package..."
if ! uv build; then
    echo "❌ Build failed!"
    exit 1
fi
echo "✅ Built successfully"
echo ""

# Step 6: Check package
echo "🔍 Step 6: Checking package..."
if ! uv run twine check dist/*; then
    echo "❌ Package check failed!"
    exit 1
fi
echo "✅ Package looks good"
echo ""

# Step 7: Show what will be published
echo "📋 Step 7: Package contents:"
ls -lh dist/
echo ""

# Step 8: Ask for confirmation
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "⚠️  About to publish version $VERSION to $TARGET"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi
echo ""

# Step 9: Upload
echo "📤 Step 9: Uploading to $TARGET..."
if [ "$TARGET" = "pypi" ]; then
    echo "🚨 Publishing to PRODUCTION PyPI!"
    read -p "Are you ABSOLUTELY sure? (yes/N) " -r
    echo
    if [[ ! $REPLY = "yes" ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
    uv run twine upload dist/*
elif [ "$TARGET" = "testpypi" ]; then
    uv run twine upload --repository testpypi dist/*
else
    echo "❌ Invalid target: $TARGET (use 'testpypi' or 'pypi')"
    exit 1
fi

echo ""
echo "✅ Successfully published to $TARGET!"
echo ""

# Step 10: Next steps
if [ "$TARGET" = "testpypi" ]; then
    echo "📝 Next steps:"
    echo "1. Test installation:"
    echo "   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rencom"
    echo ""
    echo "2. If everything works, publish to PyPI:"
    echo "   ./scripts/publish.sh pypi"
elif [ "$TARGET" = "pypi" ]; then
    echo "📝 Next steps:"
    echo "1. Check PyPI page: https://pypi.org/project/rencom/"
    echo "2. Test installation: pip install rencom"
    echo "3. Create GitHub release: git tag v$VERSION && git push origin v$VERSION"
    echo "4. Announce the release!"
fi

echo ""
echo "🎉 Done!"
