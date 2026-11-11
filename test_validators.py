"""Tests for the Task 2 validators.  Run:  python3 -m unittest discover -s tests -v

Part A checks the listed accept/reject examples.
Part B compares each DFA with an independently written rule (regex / plain Python)
on thousands of generated strings, so the DFAs are checked against something other than themselves.
"""

import itertools
import os
import random
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fa_validators.validators import (TESTS, SPECIALS, build_email_dfa,
                                      build_password_dfa, build_pin_dfa)


def all_strings(alphabet, max_len):
    for n in range(max_len + 1):
        for tup in itertools.product(alphabet, repeat=n):
            yield "".join(tup)


class ListedExamples(unittest.TestCase):
    def test_every_listed_example(self):
        for name, (dfa, good, bad) in TESTS.items():
            for s in good:
                self.assertTrue(dfa.accepts_string(s), f"{name}: {s!r} should be accepted")
            for s in bad:
                self.assertFalse(dfa.accepts_string(s), f"{name}: {s!r} should be rejected")


class AgainstIndependentRules(unittest.TestCase):
    def test_pin_exhaustive(self):
        dfa = build_pin_dfa()
        rule = re.compile(r"[0-9]{4}|[0-9]{6}")
        for s in all_strings("07x", 8):
            self.assertEqual(dfa.accepts_string(s), bool(rule.fullmatch(s)), repr(s))

    def test_email_exhaustive(self):
        dfa = build_email_dfa()
        rule = re.compile(r"[A-Za-z0-9]+([._][A-Za-z0-9]+)*@[A-Za-z0-9]+(\.[A-Za-z0-9]+)+")
        for s in all_strings("a1._@", 7):
            self.assertEqual(dfa.accepts_string(s), bool(rule.fullmatch(s)), repr(s))

    def test_email_rejects_non_ascii_and_spaces(self):
        dfa = build_email_dfa()
        for s in ["jo\u00e9@x.com", "a b@x.com", "a@x.c\u00f6m"]:
            self.assertFalse(dfa.accepts_string(s), repr(s))

    def test_password_random(self):
        dfa = build_password_dfa(8)
        pool = "ABCxyz019" + SPECIALS + " ~\u00e9"        # includes characters outside the alphabet
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" + SPECIALS)
        rng = random.Random(2026)
        for _ in range(20000):
            s = "".join(rng.choice(pool) for _ in range(rng.randint(0, 14)))
            expected = (len(s) >= 8 and set(s) <= allowed
                        and any(c.isupper() for c in s) and any("a" <= c <= "z" for c in s)
                        and any("0" <= c <= "9" for c in s) and any(c in SPECIALS for c in s))
            self.assertEqual(dfa.accepts_string(s), expected, repr(s))


class MinimisationKeepsTheLanguage(unittest.TestCase):
    def test_minimised_dfa_accepts_the_same_strings(self):
        rng = random.Random(7)
        cases = {"email": "a1._@", "atm_pin": "07x", "password": "aA1!x "}
        for name, alphabet in cases.items():
            dfa = TESTS[name][0]
            small = dfa.minimise()
            self.assertLessEqual(len(small.states), len(dfa.states))
            for _ in range(5000):
                s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 12)))
                self.assertEqual(dfa.accepts_string(s), small.accepts_string(s), f"{name}: {s!r}")


if __name__ == "__main__":
    unittest.main()
