# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repo.

## Project Overview

Dash is a Python framework for building reactive web-based data visualization applications. Built on Plotly.js, React, and Flask.

## Docs

Deeper reference lives in `.ai/`. Open the one that covers what you're touching, don't read them all up front:

- `COMMANDS.md` - build, test, lint commands
- `ARCHITECTURE.md` - backend, callbacks, pages, background callbacks, stores, async, security
- `RENDERER.md` - frontend, crawlLayout, Redux store, clientside API
- `COMPONENTS.md` - component system, generation, resources
- `TESTING.md` - test framework, fixtures, patterns
- `TROUBLESHOOTING.md` - common errors and fixes
- `PERFORMANCE.md` - benchmark harness, profiling, and performance findings

To find code, grep. Don't rely on a hand-kept file map, it goes stale.

## Writing Style

Applies to code comments, commit messages, PR descriptions, review comments, and CHANGELOG entries.

- **Comments are a last resort.** The code is Python and should read on its own. Write a comment only when the code cannot explain itself: a non-obvious why, a workaround, a gotcha. Never narrate what the next line already says. If in doubt, leave it out.
- **No em dashes or en dashes (`—` `–`).** Use a colon, comma, parentheses, or two sentences.
- **Straight ASCII only.** Straight quotes and apostrophes (`'` `"`), no curly ones. No ellipsis character (`…`); write three periods if you really need them. No decorative unicode.
- **Plain words.** Say the thing directly, in words most people know. No AI filler, no thesaurus vocabulary, no heavy styling. Short and to the point.

## Quality Gate

Before you say a change works:

1. **Prove it in a running app.** Write a small repro app in the scratchpad and drive it headless with `dash_duo` (a throwaway pytest test is the practical way, see `.ai/TESTING.md`). Watch the real behavior. "The code looks right" is not done.
2. **Leave a test behind.** Any behavior change or fix needs a test that stays in the tree: an integration/acceptance test under `tests/integration/`, or a renderer test for frontend-only work. It should fail before your change and pass after. Never run the whole integration suite at once, always a specific file or `-k`.
3. **Second-model review.** Before handing back, launch a review subagent on a different model (the Agent tool takes a `model` override, e.g. Sonnet when you're on Opus) to check the diff for correctness and cases you missed. Fold in what holds up. A fresh model catches what the author misses.
