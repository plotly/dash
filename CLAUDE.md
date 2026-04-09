# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Required Reading

**At the start of each session, read the documentation in `.ai/` before making changes:**

1. `.ai/COMMANDS.md` - Build, test, lint commands
2. `.ai/ARCHITECTURE.md` - Backend, callbacks, pages, assets, errors, background callbacks, Jupyter, config, stores, async, security
3. `.ai/RENDERER.md` - Frontend, crawlLayout, Redux store, clientside API, component API
4. `.ai/COMPONENTS.md` - Component system, generation, resources
5. `.ai/TESTING.md` - Testing framework, fixtures, patterns, type compliance
6. `.ai/TROUBLESHOOTING.md` - Common errors and solutions

## Project Overview

Dash is a Python framework for building reactive web-based data visualization applications. Built on Plotly.js, React, and Flask.

## Quick Reference

```bash
# Setup
pip install -e .[ci,dev,testing,celery,diskcache] && npm ci

# Build
npm run build                                    # Linux/Mac
npm run first-build                              # Windows (use Bash)
dash-update-components "dash-core-components"    # Single component

# Test
pytest tests/unit                                # Unit tests
pytest tests/integration                         # Integration tests
pytest -k test_name                              # Specific test

# Lint
npm run lint                                     # All linters
npm run private::format.black                    # Auto-format Python
```

## Key Files

- `dash/dash.py` - Main Dash app class, layout, callbacks, routing
- `dash/_callback.py` - `@callback` decorator and execution
- `dash/dependencies.py` - `Input`, `Output`, `State`, wildcards
- `dash/development/base_component.py` - Component base class, `to_plotly_json()`
- `dash/dash-renderer/` - TypeScript/React frontend
- `components/` - Component packages (dcc, html, table)
