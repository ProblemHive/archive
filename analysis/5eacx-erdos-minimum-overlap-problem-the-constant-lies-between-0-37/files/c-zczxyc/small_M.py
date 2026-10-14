# small_M.py - exact M(n) for small n with OR-Tools CP-SAT.
# M(n) = min over subsets A of {1..2n} with |A| = n (B the complement) of max over k of
#        M_k = #{(a, b): a in A, b in B, a - b = k}.
# For a target m the model asks for A with every M_k <= m; M(n) is the least feasible m.
# Lower bound to start from: sum over k of M_k = n*n over at most 4n-2 nonzero k, and the known M(n) > n/4.
import sys, time
from ortools.sat.python import cp_model

def feasible(n, m, limit):
    N = 2 * n
    md = cp_model.CpModel()
    x = [md.NewBoolVar('x%d' % i) for i in range(N)]
    md.Add(sum(x) == n)
    md.Add(x[0] == 1)                                   # swapping A and B sends k to -k, so 1 in A without loss
    for k in range(-(N - 1), N):
        if k == 0: continue
        terms = []
        for i in range(N):                              # a = i, b = i - k
            j = i - k
            if 0 <= j < N:
                y = md.NewBoolVar('')
                md.Add(y >= x[i] - x[j])                # y = 1 if i in A and j in B
                terms.append(y)
        if len(terms) > m:
            md.Add(sum(terms) <= m)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = limit
    s.parameters.num_workers = 8
    r = s.Solve(md)
    if r in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        A = [i + 1 for i in range(N) if s.Value(x[i])]
        return True, A
    if r == cp_model.INFEASIBLE:
        return False, None
    return None, None

def overlap(n, A):
    S = set(A); B = [b for b in range(1, 2 * n + 1) if b not in S]
    cnt = {}
    for a in A:
        for b in B:
            cnt[a - b] = cnt.get(a - b, 0) + 1
    return max(cnt.values())

if __name__ == '__main__':
    nmax, limit = int(sys.argv[1]), float(sys.argv[2])
    import ortools; print('OR-Tools', ortools.__version__)
    print('  n  M(n)  M(n)/n   time_s  one optimal A')
    m = 1
    for n in range(1, nmax + 1):
        t = time.time()
        # start at the previous value; go down while feasible, up while infeasible, so that
        # the printed m is feasible and m - 1 was shown infeasible by the solver (no monotonicity assumed)
        A, lo_proved = None, False
        while True:
            ok, sol = feasible(n, m, limit) if m >= 1 else (False, None)
            if ok is None:
                print('%3d  undecided at m = %d within %.0f s' % (n, m, limit)); sys.exit()
            if ok:
                A = sol
                if lo_proved: break
                m -= 1
            else:
                lo_proved = True
                m += 1
                if A is not None: break
        assert overlap(n, A) <= m and len(A) == n
        print('%3d  %4d  %.4f  %7.1f  %s' % (n, m, m / n, time.time() - t, A), flush=True)
