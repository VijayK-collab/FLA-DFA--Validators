"""Command-line demo.

    python -m fa_validators.cli                      accept/reject table for every application
    python -m fa_validators.cli email "x@y.co"       step-by-step trace for one string
    python -m fa_validators.cli --stats              state counts before and after minimisation
    python -m fa_validators.cli --limits             what a finite automaton cannot check
"""

import sys
from .validators import TESTS

LIMITS = [
    ("ATM PIN",  "Whether 1234 is THIS card's PIN needs the bank's records; the DFA only checks the shape."),
    ("E-mail",   "Whether the domain or mailbox exists needs DNS/SMTP; the DFA only checks the syntax."),
    ("Password", "A leaked-password list or 'differs from the last 5 passwords' needs stored data/history."),
    ("Any rule", "Rules that need unbounded counting (e.g. as many letters as digits) are not regular."),
]

def show_tables():
    for name, (dfa, good, bad) in TESTS.items():
        print(f"\n=== {name} ({len(dfa.states)} reachable states) ===")
        for s in good:
            print(f"  ACCEPT-expected {s!r:30} -> {'ACCEPT' if dfa.accepts_string(s) else 'REJECT'}")
        for s in bad:
            print(f"  REJECT-expected {s!r:30} -> {'ACCEPT' if dfa.accepts_string(s) else 'REJECT'}")

def show_trace(app, text):
    if app not in TESTS:
        sys.exit(f"unknown application {app!r}; choose from: {', '.join(TESTS)}")
    dfa = TESTS[app][0]
    ok, lines = dfa.trace(text)
    print(f"{app} on {text!r}  (start state {dfa.start})")
    print("\n".join(lines) if lines else "  (empty string)")
    print("result:", "ACCEPTED" if ok else "REJECTED")

def show_stats():
    print(f"{'application':<10} {'reachable states':>17} {'minimal states':>15}")
    for name, (dfa, _, _) in TESTS.items():
        print(f"{name:<10} {len(dfa.states):>17} {len(dfa.minimise().states):>15}")

def main(argv):
    if not argv:
        show_tables()
    elif argv[0] == "--stats":
        show_stats()
    elif argv[0] == "--limits":
        for who, text in LIMITS:
            print(f"{who:<9}: {text}")
    elif len(argv) == 2:
        show_trace(argv[0], argv[1])
    else:
        print(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:])
