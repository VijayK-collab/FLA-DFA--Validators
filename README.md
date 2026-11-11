# Task 2 – Designing Automata for Real-Time Applications

**Course:** 21CSC301T Formal Language and Automata · CLA-2 · SRM IST Tiruchirappalli · B.Tech AIML, Sem V
**Student:** Vijay Bharath Simha Kollati (RA2411026050040)
**Faculty:** Dr. C. Gunasundari · **SDG 9** (Level 2 – Design alignment)

Deterministic finite automata (DFAs) for three everyday input checks. Pure Python 3.8+, no dependencies.

| # | Application | Design | Reachable states | Minimal states |
|---|-------------|--------|------------------|----------------|
| 1 | Password policy (≥ 8 chars, upper, lower, digit, special) | product of 5 small DFAs | 104 | 76 |
| 2 | E-mail format `local@domain` | hand-built DFA | 7 | 6 |
| 3 | ATM PIN (exactly 4 or 6 digits) | counting DFA | 7 | 7 |

The design report is [`docs/DESIGN_NOTE.md`](docs/DESIGN_NOTE.md); state diagrams are in [`docs/diagrams.md`](docs/diagrams.md).

## Run it

```bash
python3 -m fa_validators.cli                         # accept/reject table for every application
python3 -m fa_validators.cli email "john.doe@srm.edu"  # step-by-step trace of one string
python3 -m fa_validators.cli --stats                 # state counts before/after minimisation
python3 -m fa_validators.cli --limits                # what a finite automaton cannot check
python3 -m unittest discover -s tests -v             # run the tests
python3 tools/export_mermaid.py                      # rebuild docs/diagrams.md
```

Applications for the trace command: `password`, `email`, `atm_pin`.

## How it works

- Each DFA reads **symbol classes** instead of raw characters (for example `D` for any digit), which keeps the transition tables small. A character outside the alphabet sends the machine to an implicit dead state and the string is rejected.
- Regular languages are closed under intersection, so the password policy is five tiny DFAs (length, upper, lower, digit, special) combined with the **product construction** (`intersect`).
- `minimise()` merges states that behave identically, using partition refinement.

## Tests

`tests/test_validators.py` checks the listed accept/reject examples, then compares each DFA with an independently written rule (a regular expression or plain Python) on generated strings: all PINs over a small alphabet, every e-mail-like string up to length 7, and 20 000 random passwords. It also checks that minimisation does not change the accepted language.

## Limitations

The automata check *syntax* only. Whether a PIN belongs to a card, whether an e-mail domain exists, or whether a password has been leaked needs outside data, and rules that need unbounded counting are not regular. Details are in the design note.

## Layout

```
fa_validators/automata.py    DFA class (run, trace, minimise) and the product construction
fa_validators/validators.py  the three applications and their test strings
fa_validators/cli.py         command-line demo
tests/test_validators.py     unit tests
tools/export_mermaid.py      writes docs/diagrams.md
docs/                        DESIGN_NOTE.md and diagrams.md
```
