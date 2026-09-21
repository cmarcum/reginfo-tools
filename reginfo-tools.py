#!/usr/bin/env python
"""
reginfo-tools.py

Single command-line entry point for the reginfo.gov scraper toolkit. It dispatches to the
four standalone scripts already in this repository without modifying any of them:

    icr-search     -> pra-icr-search.py    (PRA ICR search)              see codebook.md
    icr-download   -> pra-icr-download.py  (PRA ICR document downloader)
    reg-search     -> eo-reg-search.py     (EO 12866 Reg Review search)  see eo-review-codebook.md
    reg-download   -> eo-reg-download.py   (EO 12866 Reg Review RIN downloader)

Each subcommand execs the matching script as a subprocess and passes every remaining
command-line argument straight through unchanged, so all the flags, positional key=value
search fields, and exit codes already documented in README.md for each script behave
identically here. This is a thin dispatcher, not a reimplementation - it just saves you from
remembering four separate script filenames.

Usage:
    python reginfo-tools.py <tool> [tool-specific args...]
    python reginfo-tools.py <tool> --help
    python reginfo-tools.py --list

Last updated: 9.21.2026
"""
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TOOLS = {
    'icr-search': {
        'script': 'pra-icr-search.py',
        'help': "Search PRA Information Collection Requests (ICRs) - codebook.md",
    },
    'icr-download': {
        'script': 'pra-icr-download.py',
        'help': "Download documents attached to a specific ICR reference number",
    },
    'reg-search': {
        'script': 'eo-reg-search.py',
        'help': "Search EO 12866 Regulatory Reviews (rules) - eo-review-codebook.md",
    },
    'reg-download': {
        'script': 'eo-reg-download.py',
        'help': "Download the full public record for a RIN under EO 12866 review",
    },
}

# A hand-rolled arg dispatcher, not argparse subparsers, on purpose: argparse's
# nargs=REMAINDER has a long-standing bug (https://bugs.python.org/issue17050) where an
# option-like token (e.g. "--help") immediately after a subparser name gets swallowed by the
# parent parser instead of being forwarded, which is exactly the case this tool needs to get
# right (python reginfo-tools.py reg-search --help must reach eo-reg-search.py's own --help,
# not this dispatcher's).

def print_usage():
    print("usage: reginfo-tools.py <tool> [tool-specific args...]")
    print("       reginfo-tools.py <tool> --help")
    print("       reginfo-tools.py --list")
    print()
    print("Single entry point for the reginfo.gov scraper toolkit (PRA/ICR side and EO 12866 Reg Review side).")

def print_tool_list():
    print("\nAvailable tools:\n")
    for name, meta in TOOLS.items():
        print(f"  {name:<14} {meta['help']}")
    print("\nRun 'python reginfo-tools.py <tool> --help' for that tool's own arguments.")

def main():
    argv = sys.argv[1:]

    if not argv or argv[0] in ('-h', '--help'):
        print_usage()
        print_tool_list()
        sys.exit(0 if argv else 1)

    if argv[0] == '--list':
        print_tool_list()
        sys.exit(0)

    tool_name = argv[0]
    if tool_name not in TOOLS:
        print(f"[!] Error: unknown tool '{tool_name}'.")
        print_tool_list()
        sys.exit(2)

    script_path = os.path.join(SCRIPT_DIR, TOOLS[tool_name]['script'])
    if not os.path.isfile(script_path):
        print(f"[!] Error: expected script not found: {script_path}")
        sys.exit(1)

    cmd = [sys.executable, script_path] + argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
