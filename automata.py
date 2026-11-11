"""Tiny DFA toolkit used by Task 2 (explicit transition tables, no regex library)."""

from collections import deque

class DFA:
    def __init__(self, name, alphabet, states, start, accepts, delta, classify):
        self.name, self.alphabet = name, list(alphabet)
        self.states, self.start, self.accepts = set(states), start, set(accepts)
        self.delta, self.classify = delta, classify   # delta: (state, symbol) -> state

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

    # ------------------------------------------------------------------
    # Additions: a step-by-step trace and DFA minimisation
    # ------------------------------------------------------------------
    def trace(self, s):
        """Return (accepted?, lines) describing every move delta(q, symbol) = q'."""
        q, lines = self.start, []
        for i, ch in enumerate(s, 1):
            sym = self.classify(ch)
            nq = self.delta.get((q, sym)) if sym is not None else None
            shown = sym if sym is not None else "outside alphabet"
            if nq is None:
                lines.append(f"{i:>3}. d({q}, {ch!r} -> {shown}) = DEAD")
                return False, lines
            lines.append(f"{i:>3}. d({q}, {ch!r} -> {shown}) = {nq}")
            q = nq
        return q in self.accepts, lines

    def minimise(self):
        """Return an equivalent DFA with the fewest states (partition refinement).

        Idea: start with two groups (accepting / not accepting). Keep splitting a
        group while two of its states send some symbol to different groups.
        When no group can be split any more, each group becomes one state.
        States that can never reach an accepting state are merged into the
        implicit dead state, so they are not counted.
        """
        dead = "__DEAD__"
        syms = self.alphabet

        # 1. keep only the states reachable from the start state
        reach, stack = {self.start}, [self.start]
        while stack:
            q = stack.pop()
            for sym in syms:
                n = self.delta.get((q, sym))
                if n is not None and n not in reach:
                    reach.add(n)
                    stack.append(n)
        states = reach | {dead}

        def step(q, sym):
            return dead if q == dead else self.delta.get((q, sym), dead)

        # 2. refine the partition until it stops changing
        block = {q: int(q in self.accepts) for q in states}
        while True:
            signature = {q: (block[q],) + tuple(block[step(q, s)] for s in syms) for q in states}
            ids, new = {}, {}
            for q in sorted(states, key=repr):
                new[q] = ids.setdefault(signature[q], len(ids))
            same = len(set(new.values())) == len(set(block.values()))
            block = new
            if same:
                break

        # 3. build the minimal DFA, numbering states in breadth-first order
        dead_block = block[dead]
        rep = {}
        for q in states:
            rep.setdefault(block[q], q)
        if block[self.start] == dead_block:            # empty language
            return DFA(self.name + "(min)", syms, {"m0"}, "m0", set(), {}, self.classify)
        names = {block[self.start]: "m0"}
        queue, delta = deque([block[self.start]]), {}
        while queue:
            b = queue.popleft()
            for sym in syms:
                nb = block[step(rep[b], sym)]
                if nb == dead_block:
                    continue
                if nb not in names:
                    names[nb] = f"m{len(names)}"
                    queue.append(nb)
                delta[(names[b], sym)] = names[nb]
        accepts = {names[b] for b in names if rep[b] in self.accepts}
        return DFA(self.name + "(min)", syms, set(names.values()), "m0", accepts, delta, self.classify)


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
