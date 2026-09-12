#!/usr/bin/env python3
"""Validate this skill's output against its own contract. STUB — fill it in.

Usage: validate_output.py OUTPUT_FILE      exit 1 with one line per violation

Part 3.3 (mandatory) and Part 6.5. This is the script that makes the rubric real:
a rubric nothing can falsify is advice. Enforce, at minimum, the consistency
constraints in references/rubric.md and the shape in references/output-contract.md.

Stdlib only — this is on the gate path (Part 3.6).

It exits 2 (not configured) rather than 0 on purpose. A validator that passes
because it checks nothing is worse than no validator: it reports success.
"""
import sys


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    print("validate_output: STUB — no checks implemented yet.", file=sys.stderr)
    print("  Implement references/output-contract.md and the rubric's consistency "
          "constraints, then remove this notice.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
