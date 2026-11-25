"""Fail when a PR into dev adds an Unreleased "Added" CHANGELOG entry.

Features go to next (RFD #142). Usage: changelog_added.py BASE_CHANGELOG HEAD_CHANGELOG
"""

import re
import sys

RELEASE = re.compile(r"^## \[")
SECTION = re.compile(r"^#{2,3} (\w+)")


def unreleased_added(path):
    entries = set()
    in_unreleased = False
    section = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if RELEASE.match(line):
                if in_unreleased:
                    break
                in_unreleased = line.upper().startswith("## [UNRELEASED]")
                continue
            if not in_unreleased:
                continue
            match = SECTION.match(line)
            if match:
                section = match.group(1).lower()
            elif section == "added" and line.strip():
                entries.add(line.strip())
    return entries


def main(base, head):
    added = sorted(unreleased_added(head) - unreleased_added(base))
    if not added:
        return 0
    print(
        "::error file=CHANGELOG.md::This PR adds an 'Added' entry, so it is a"
        " feature and should target next, not dev. If it is really a fix,"
        " move the entry under 'Fixed'."
    )
    for entry in added:
        print(f"  {entry}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
