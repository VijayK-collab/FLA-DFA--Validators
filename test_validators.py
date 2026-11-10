import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from validators import TESTS

def test_all():
    for name, (dfa, good, bad) in TESTS.items():
        for s in good:
            assert dfa.accepts_string(s), (name, s)
        for s in bad:
            assert not dfa.accepts_string(s), (name, s)

if __name__ == "__main__":
    test_all(); print("Task 2: all test cases passed")
