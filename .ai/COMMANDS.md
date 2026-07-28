# Commands

## Initial Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: source venv/scripts/activate

# Install Python dependencies
pip install -e .[ci,dev,testing,celery,diskcache]

# Install Node dependencies
npm ci
```

### Optional Backend Dependencies

```bash
# For Quart backend (ASGI async)
pip install dash[quart]

# For FastAPI backend (ASGI async)
pip install dash[fastapi]

# For async callbacks with Flask
pip install dash[async]
```

## Building

```bash
# Full build (Linux/Mac)
npm run build

# Full build (Windows - use Bash terminal, not PowerShell/CMD)
npm run first-build

# Build single component after changes
dash-update-components "dash-core-components"  # or dash-html-components, dash-table

# Build renderer only
cd dash/dash-renderer && renderer build
```

## Testing

Tests use pytest with Selenium/ChromeDriver. ChromeDriver must match your Chrome version. See [TESTING.md](TESTING.md) for fixtures, patterns, and detailed documentation.

```bash
# Run all tests
npm run test

# Unit tests only
pytest tests/unit

# Integration tests (requires ChromeDriver)
pytest tests/integration

# Run specific test by name
pytest -k test_name

# Run tests matching pattern
pytest -k cbcx  # runs all tests with "cbcx" in name

# Renderer unit tests (Jest)
cd dash/dash-renderer && npm run test

# Setup test components before running integration tests
npm run setup-tests.py
```

## Linting

Linting runs automatically on commit via husky pre-commit hook and lint-staged (`.lintstagedrc.js`). You typically don't need to run these manually.

**Pre-commit runs on staged files:**
- Python (`dash/`, `tests/`): pylint, flake8, black --check
- JavaScript/TypeScript: eslint, prettier --check (per component package)

**Manual commands** (if needed):

```bash
# Run all linters
npm run lint

# Individual linters
npm run private::lint.black       # Check Black formatting
npm run private::lint.flake8      # Flake8
npm run private::lint.pylint-dash # Pylint on dash/

# Auto-format Python with Black
npm run private::format.black
```
