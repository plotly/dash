# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Building Components
```bash
# Build all components and renderer from source
npm run build

# CI build (includes tests)
npm run cibuild

# Sequential build (for systems with limited resources)
npm run build.sequential

# First-time setup and build
npm run first-build
```

### Testing
```bash
# Run Python unit tests
pytest tests/unit

# Run Python integration tests (requires setup)
npm run citest.integration

# Run all tests
npm test

# Run specific test suites
npm run private::test.unit-dash
npm run private::test.unit-renderer
```

### Code Quality
```bash
# Format code
npm run format

# Lint code
npm run lint

# Individual linting commands
npm run private::lint.black
npm run private::lint.flake8
npm run private::lint.pylint-dash
```

### Component Development
```bash
# Update all components
python dash/development/update_components.py 'all'

# Generate individual component packages
dash-generate-components <component-path>
```

### Testing Setup
```bash
# Set up test components for Python
npm run setup-tests.py

# Set up test components for R
npm run setup-tests.R
```

## Architecture Overview

### Core Structure
- **`dash/`**: Main Python package containing core framework
  - **`dash.py`**: Main Dash application class and Flask integration
  - **`_callback.py`**: Callback system implementation
  - **`dependencies.py`**: Input/Output/State dependency classes
  - **`development/`**: Component generation and build tools

### Component System
- **`components/dash-core-components/`**: Interactive components (graphs, dropdowns, etc.)
- **`components/dash-html-components/`**: HTML wrapper components
- **`components/dash-table/`**: Advanced table component with TypeScript
- **`dash/dash-renderer/`**: React-based frontend renderer

### Key Technologies
- **Backend**: Flask-based Python server with callback system
- **Frontend**: React components with TypeScript
- **Build System**: npm scripts with webpack, babel
- **Testing**: pytest (Python), karma/jest (JavaScript)

### Component Architecture
Components are built using:
1. **React/JavaScript source** (`src/components/`)
2. **Python wrappers** generated automatically
3. **TypeScript support** for complex components like dash-table
4. **Build process** converts JSX to browser-ready bundles

### Background Callbacks
- **`background_callback/`**: Long-running async callbacks
- **Managers**: Celery and Diskcache backends for job queuing
- **Integration**: Works with main callback system

### Multi-Page Apps
- **`_pages.py`**: Page registry and routing system
- **`page_container`**: Component for rendering pages
- **URL routing**: Automatic based on file structure or explicit registration

## Development Environment Setup

### Prerequisites
1. Python 3.8+ with pip
2. Node.js with npm
3. Git

### Initial Setup
```bash
# Install Python dependencies
pip install -e .[dev,testing,celery,diskcache]

# Install Node dependencies
npm ci

# Initialize renderer
npm run private::initialize.renderer

# First build
npm run first-build
```

### Running Tests
Tests are organized into:
- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Component tests**: Individual component directories

Use pytest for Python tests, npm test for JavaScript tests.

### Component Generation
The framework includes tools to generate new components:
- Use `dash-generate-components` CLI tool
- Components auto-generate Python wrappers from React PropTypes
- Supports TypeScript for type-safe component development
- The main directories we'll be focused on that contain the components are in components/dash-core-components/src/components and components/dash-core-components/src/fragments