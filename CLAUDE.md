# Dash Development Guide for Claude

## Project Overview

**Dash** is a Python framework for building reactive web applications, particularly for data science and ML applications. It's built on top of Flask (backend), React (frontend), and Plotly.js (visualization), allowing developers to create interactive web apps using only Python.

- **Repository**: Plotly Dash (main repository)
- **Language**: Python + JavaScript/TypeScript (hybrid project)
- **Architecture**: Monorepo with multiple components
- **Framework**: Flask backend, React frontend, Plotly.js for charts
- **Package Manager**: uv (Python) + npm (JavaScript)

## Project Structure

```
dash/
├── dash/                           # Main Python package
│   ├── dash.py                    # Core Dash class
│   ├── dash-renderer/             # Frontend React components (TypeScript/JS)
│   ├── dcc/                       # Dash Core Components (Python wrappers)
│   ├── html/                      # HTML components (Python wrappers)
│   ├── dash_table/                # DataTable component
│   └── development/               # Component generation tools
├── components/                     # Source code for component packages
│   ├── dash-core-components/      # Charts, inputs, layouts
│   ├── dash-html-components/      # HTML elements
│   └── dash-table/                # DataTable implementation
├── @plotly/                       # NPM packages and test components
├── tests/                         # Comprehensive test suite
├── requirements/                  # Python dependencies by category
└── build/                         # Build artifacts
```

## Development Setup

### Prerequisites
- Python 3.9+ 
- Node.js (latest LTS) installed via nvm
- Git Bash terminal (especially on Windows)
- uv (modern Python package manager) - install from https://docs.astral.sh/uv/

### Initial Setup
```bash
# Clone and enter repository
git clone <your-fork>
cd dash

# Create virtual environment and sync dependencies using uv
uv venv .venv --python 3.9
uv sync --extra ci --extra dev --extra testing --extra celery --extra diskcache --extra build

# Install JavaScript dependencies
npm ci

# Build all components (first time)
npm run build          # Linux/Mac
npm run first-build    # Windows

# Build and install test components
npm run setup-tests.py

# Verify installation
pip list | grep dash
```

### Development Build Commands

```bash
# Full build (all components)
npm run build

# Build specific component
dash-update-components "dash-core-components"
dash-update-components "dash-html-components" 
dash-update-components "dash-table"

# Renderer-specific builds
cd dash/dash-renderer
renderer build          # Full build
renderer build local    # With source maps for debugging
renderer clean          # Clean build artifacts
```

## Testing

### Test Setup
- **Framework**: pytest (Python) + jest (JavaScript)
- **Browser**: Chrome via Selenium (ChromeDriver required)
- **Parallel testing**: Supported via pytest-xdist

### Running Tests
```bash
# All tests
npm run test

# Python unit tests only
pytest tests/unit
npm run private::test.unit-dash

# Integration tests
pytest tests/integration
npm run private::test.integration-dash

# Renderer unit tests (JavaScript)
cd dash/dash-renderer && npm run test

# Specific test patterns
pytest -k "test_name_pattern"
pytest tests/integration/callbacks/
```

### Test Structure
- `tests/unit/` - Fast unit tests
- `tests/integration/` - Browser-based integration tests
- `tests/async_tests/` - Async callback tests
- `tests/background_callback/` - Long-running callback tests

## Code Quality & Linting

### Python Tools
- **Black**: Code formatting (`black dash tests --exclude metadata_test.py`)
- **Flake8**: Style guide enforcement 
- **Pylint**: Static analysis with custom rules

### JavaScript Tools
- **ESLint**: Linting for renderer and components
- **Prettier**: Code formatting
- **TypeScript**: Type checking in dash-renderer

### Linting Commands
```bash
# Format code
npm run format

# Run all linters
npm run lint

# Individual linting
npm run private::lint.black
npm run private::lint.flake8
npm run private::lint.pylint-dash
npm run private::lint.renderer
```

### Configuration Files
- `.pylintrc` - Pylint rules with Dash-specific customizations
- `.flake8` - Flake8 configuration
- `components/*/babel.config.js` - Babel configuration per component

## Package Building & Distribution

### Modern Build System
- **Build Backend**: Hatchling (modern, fast Python build system)
- **Package Manager**: uv (fast Python package installer and resolver)
- **Configuration**: pyproject.toml (PEP 621 compliant)

### Building Packages
```bash
# Build source distribution and wheel
uv run python -m build

# Build with uv (installs build dependencies automatically)
uv build

# Install in development mode
uv sync --dev

# Install with specific extras
uv sync --extra testing --extra dev
```

### Package Structure
- Dependencies managed via `requirements/*.txt` files
- Build dependencies defined in `requirements/build.txt`
- All extras available: async, ci, dev, testing, celery, diskcache, compress, build
- **setup.py is deprecated** - kept only for backward compatibility

## Architecture & Key Components

### Core Architecture
1. **Dash App (`dash/dash.py`)** - Main application class, Flask integration
2. **Dash Renderer (`dash/dash-renderer/`)** - React frontend that renders components
3. **Component Packages** - Individual packages for different component types
4. **Callback System** - Reactive programming model for interactivity

### Component Development
- Components are generated from React source code
- Python wrappers are auto-generated using `dash-generate-components`
- R bindings are also auto-generated from the same source

### Build System
- **Lerna** for JavaScript monorepo management
- **Webpack** for bundling JavaScript components
- **npm scripts** coordinate the entire build process
- Components built independently, then integrated into main package

## Common Development Tasks

### Adding New Components
1. Develop React component in appropriate package
2. Build component: `dash-update-components "package-name"`
3. Test integration with Python wrapper
4. Update any documentation

### Debugging Frontend Issues
```bash
# Build with source maps
cd dash/dash-renderer
renderer build local

# Run development server with hot reload
# (See individual component READMEs for details)
```

### Working with Callbacks
- Use `@app.callback` decorator for reactive functions
- Input/Output/State objects define component interactions
- Pattern-matching callbacks for dynamic UIs
- Background callbacks for long-running tasks

## Git Workflow

- **Main Branch**: `dev` (not `master`)
- **Feature Branches**: Create from `dev`, use descriptive names
- **Commit Style**: Emoji-enabled commit messages encouraged
- **PR Process**: Target `dev` branch, ensure all tests pass

### Useful Git Commands
```bash
# Create feature branch
git checkout -b feature/new-component

# Organized commits are preferred
# Use tools like GitKraken or GitHub Desktop for complex changes
```

## Key Files to Know

### Configuration
- `package.json` - Root build scripts and dependencies
- `pyproject.toml` - Modern Python package configuration (PEP 621)
- `setup.py` - Legacy Python package configuration (deprecated)
- `lerna.json` - Monorepo configuration
- `pytest.ini` - Test configuration
- `requirements/*.txt` - Dependency specifications by category

### Path handling
- Delete individual files, not directories.
- Do not cd into subdirectories unless necessary.
- If commands fails to find paths, cd back to project root.

### Entry Points
- `dash/__init__.py` - Main Python API
- `dash/dash.py` - Core Dash application class
- `dash/dash-renderer/src/index.js` - Frontend entry point

### Documentation
- `README.md` - Project overview and basic usage
- `CONTRIBUTING.md` - Detailed contributor guide
- Component-specific READMEs in `components/*/`

## Performance Considerations

- **Bundle Size**: Components are loaded asynchronously by default
- **Callback Optimization**: Use `prevent_initial_call` and `PreventUpdate` appropriately
- **Memory Management**: Large datasets should use `dash_table.DataTable` with pagination

## Testing Best Practices

- Add unit tests for new Python functionality
- Use integration tests for callback behavior
- Browser tests for component interaction
- Follow existing test naming conventions (e.g., `test_cbcx001_basic_callback`)

## Troubleshooting

### Common Issues
1. **Build Failures**: Ensure correct Node.js version via nvm
2. **Test Failures**: Check ChromeDriver version matches Chrome
3. **Import Errors**: Verify `pip install -e .` was successful
4. **Permission Errors**: Use Git Bash on Windows

### Debug Tools
- `renderer digest` - Check renderer build integrity
- Browser dev tools for frontend debugging
- Flask debug mode for backend issues

## Resources

- **Documentation**: https://dash.plotly.com/
- **Community Forum**: https://community.plotly.com/c/dash
- **Issue Tracker**: GitHub Issues
- **Examples**: `tests/assets/` directory
