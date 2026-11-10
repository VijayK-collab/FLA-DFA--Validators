"""Task 2 - DFAs for three validation applications: password, e-mail format, ATM PIN."""
import os, sys
from dfa import DFA, intersect

# ---------------------------------------------------------------- 1. PASSWORD
SPECIALS = "!@#$%^&*"
PW_CLASSES = ["U", "l", "D", "S"]  # Upper, lower, Digit, Special


def pw_classify(ch):
    if "A" <= ch <= "Z": return "U"
    if "a" <= ch <= "z": return "l"
    if "0" <= ch <= "9": return "D"
    if ch in SPECIALS:   return "S"
    return None  # anything else (space, unicode...) is outside the alphabet -> reject


def has_class(c):
    """2-state DFA: accepts strings that contain at least one symbol of class c."""
    d = {}
    for s in PW_CLASSES:
        d[(0, s)] = 1 if s == c else 0
        d[(1, s)] = 1
    return DFA(f"has_{c}", PW_CLASSES, {0, 1}, 0, {1}, d, pw_classify)


def min_len(n):
    """(n+1)-state DFA: accepts strings of length >= n."""
    d = {(i, s): min(i + 1, n) for i in range(n + 1) for s in PW_CLASSES}
    return DFA(f"len>={n}", PW_CLASSES, range(n + 1), 0, {n}, d, pw_classify)


def build_password_dfa(min_length=8):
    comps = [min_len(min_length)] + [has_class(c) for c in PW_CLASSES]
    return intersect("password", comps)


# ---------------------------------------------------------------- 2. E-MAIL
# classes: A = ASCII letter/digit, '.', '_', '@'
def email_classify(ch):
    if ch.isascii() and ch.isalnum(): return "A"
    if ch in ".@_": return ch
    return None


def build_email_dfa():
    # q0 start | q1 in local part (after alnum) | q2 after '.'/'_' in local part
    # q3 just after '@' | q4 in first domain label | q5 after '.' in domain | q6 domain with >=1 dot (ACCEPT)
    d = {
        ("q0", "A"): "q1",
        ("q1", "A"): "q1", ("q1", "."): "q2", ("q1", "_"): "q2", ("q1", "@"): "q3",
        ("q2", "A"): "q1",
        ("q3", "A"): "q4",
        ("q4", "A"): "q4", ("q4", "."): "q5",
        ("q5", "A"): "q6",
        ("q6", "A"): "q6", ("q6", "."): "q5",
    }
    return DFA("email", ["A", ".", "_", "@"], {f"q{i}" for i in range(7)}, "q0", {"q6"}, d, email_classify)


# ---------------------------------------------------------------- 3. ATM PIN
def pin_classify(ch):
    return "D" if "0" <= ch <= "9" else None


def build_pin_dfa():
    # exactly 4 or exactly 6 decimal digits
    d = {(f"q{i}", "D"): f"q{i+1}" for i in range(6)}
    return DFA("atm_pin", ["D"], {f"q{i}" for i in range(7)}, "q0", {"q4", "q6"}, d, pin_classify)


# ---------------------------------------------------------------- test data
TESTS = {
    "password": (
        build_password_dfa(),
        ["Abcdef1!", "Zz9#Zz9#", "Passw0rd!", "Hello@2026", "aB3$aB3$aB3$"],
        ["abcdefg1!", "ABCDEFG1!", "Abcdefgh!", "Abcdefg1", "Ab1!", "Abcdef1! x"],
    ),
    "email": (
        build_email_dfa(),
        ["john.doe@srm.edu", "a_b@mail.com", "user123@gmail.co.in", "X@y.z", "first.last_name@a1.b2.c3"],
        ["john@@x.com", ".john@x.com", "john@x", "john@x.", "john..doe@x.com", "john doe@x.com", "john@.com", "@x.com"],
    ),
    "atm_pin": (
        build_pin_dfa(),
        ["1234", "0000", "987654", "0007", "123456"],
        ["123", "12345", "1234567", "12a4", "", "12 34", "-123"],
    ),
}

if __name__ == "__main__":
    for name, (dfa, good, bad) in TESTS.items():
        print(f"\n=== {name}  ({len(dfa.states)} reachable states) ===")
        for s in good:
            ok, _ = dfa.run(s)
            print(f"  ACCEPT-expected {s!r:30} -> {'ACCEPT' if ok else 'REJECT'}")
        for s in bad:
            ok, _ = dfa.run(s)
            print(f"  REJECT-expected {s!r:30} -> {'ACCEPT' if ok else 'REJECT'}")
