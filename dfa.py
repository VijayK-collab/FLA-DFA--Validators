"""Tiny DFA toolkit used by Task 2 (explicit transition tables, no regex library)."""
from collections import deque


class DFA:
    def __init__(self, name, alphabet, states, start, accepts, delta, classify):
        self.name, self.alphabet = name, list(alphabet)
        self.states, self.start, self.accepts = set(states), start, set(accepts)
        self.delta, self.classify = delta, classify  # delta: (state, symbol) -> state

    def run(self, s):
        """Return (accepted?, list of visited states). A missing move = implicit dead state."""
        q, path = self.start, [self.start]
        for ch in s:
            sym = self.classify(ch)
            nq = self.delta.get((q, sym)) if sym is not None else None
            if nq is None:
                return False, path + ["DEAD"]
            q = nq
            path.append(q)
        return q in self.accepts, path

    def accepts_string(self, s):
        return self.run(s)[0]


def intersect(name, dfas):
    """Product construction for the intersection of DFAs over the same symbol classes."""
    ref = dfas[0]
    start = tuple(d.start for d in dfas)
    delta, seen, queue = {}, {start}, deque([start])
    while queue:
        q = queue.popleft()
        for sym in ref.alphabet:
            nxt = []
            for qi, d in zip(q, dfas):
                n = d.delta.get((qi, sym))
                if n is None:
                    break
                nxt.append(n)
            else:
                nq = tuple(nxt)
                delta[(q, sym)] = nq
                if nq not in seen:
                    seen.add(nq)
                    queue.append(nq)
    accepts = {q for q in seen if all(qi in d.accepts for qi, d in zip(q, dfas))}
    return DFA(name, ref.alphabet, seen, start, accepts, delta, ref.classify)
