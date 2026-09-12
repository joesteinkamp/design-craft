#!/usr/bin/env python3
"""Run this skill's fixtures. STUB — fill it in.

Usage: check_fixtures.py [FIXTURE_ROOT]    exit non-zero on any fixture failure

Part 3.4, mandatory. Not in M1's stated file list, but the shape spec requires a
fixture checker of every skill, so a skeleton without one could not pass
check_shape.py — a template that fails its own spec is not a template.

From M2 this delegates to the pack's lib/fixtures.py rather than reimplementing
must_find / must_not_find / caps / tolerances.

Exits 2 (not configured) rather than 0: a fixture checker that passes because it
ran nothing is the exact failure fixtures exist to prevent.
"""
import sys


def main():
    print("check_fixtures: STUB — no fixtures run yet.", file=sys.stderr)
    print("  Wire this to lib/fixtures.py (M2) and ship at least one clean control "
          "(Part 4.6), then remove this notice.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
