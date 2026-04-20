# Dash AI Agent Guide

This directory contains documentation for AI coding assistants working with the Dash codebase.

## Quick Links

- [Commands](./COMMANDS.md) - Build, test, and lint commands
- [Architecture](./ARCHITECTURE.md) - Backend, callbacks, pages, assets, errors, background callbacks, Jupyter, config, stores, async, security
- [Renderer](./RENDERER.md) - Frontend, crawlLayout, Redux store, clientside API, component API
- [Components](./COMPONENTS.md) - Component generation, package structure, resource system
- [Testing](./TESTING.md) - Testing framework, fixtures, patterns, type compliance
- [Troubleshooting](./TROUBLESHOOTING.md) - Common errors and solutions

## Project Overview

Dash is a Python framework for building reactive web-based data visualization applications. Built on Plotly.js, React, and Flask, it ties UI elements (dropdowns, sliders, graphs) directly to analytical Python code.

## Key Directories

```
dash/
├── dash/                    # Main Python package
│   ├── dash.py              # Core Dash app class
│   ├── _callback.py         # Callback registration/execution
│   ├── dependencies.py      # Input/Output/State classes
│   ├── _pages.py            # Multi-page app support
│   ├── development/         # Component generation tools
│   ├── dash-renderer/       # TypeScript/React frontend
│   └── dcc/, html/, dash_table/  # Built-in components
├── components/              # Component source packages (Lerna monorepo)
│   ├── dash-core-components/
│   ├── dash-html-components/
│   └── dash-table/
├── tests/
│   ├── unit/                # pytest unit tests
│   ├── integration/         # Selenium browser tests
│   ├── compliance/          # Type checking (pyright/mypy)
│   └── background_callback/ # Background callback tests
└── requirements/            # Modular dependency files
```

## Code Review Conventions

Emoji used in reviews:
- `:dancer:` - Can merge
- `:tiger2:` - Needs more tests
- `:snake:` - Security concern
- `:pill:` - Performance issue
