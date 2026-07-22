# Copilot Instructions

This file provides guidance to GitHub Copilot when working with this repository.

For detailed documentation, see the [`.ai/`](../.ai/) directory:
- [Commands](../.ai/COMMANDS.md) - Build, test, lint
- [Architecture](../.ai/ARCHITECTURE.md) - Backend, layout, callbacks
- [Components](../.ai/COMPONENTS.md) - Component system, generation, resources

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
