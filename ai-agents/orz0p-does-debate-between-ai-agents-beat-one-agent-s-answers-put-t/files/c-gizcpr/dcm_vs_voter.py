# dcm_vs_voter.py - exact majority-vote accuracy by debate round in two models with a flat expected
# share of correct agents (a martingale):
#  (A) voter model of c/0gdbmw: each agent copies a uniformly drawn agent (itself included);
#  (B) the Dirichlet model of arXiv:2508.17536 (Definitions 1, 2), fully connected, homogeneous,
#      two answers: every agent holds the same counts (a, b); each answers correctly with
#      probability a/(a+b) independently; then all add the N answers of the round to their counts.
#      Prior a0 = p*s, b0 = (1-p)*s, where s is the prior strength (not given in the paper).
# Also: differences between the round-0 vote and debate in Table 1 of the paper (typed in by hand).
from fractions import Fraction as F
from math import comb

def binpmf(n, q, j):
    return comb(n, j) * q**j * (1 - q)**(n - j)

def maj(n, q):
    return sum(binpmf(n, q, j) for j in range(n + 1) if 2 * j > n)

def voter(k, p, rounds):
    d = [binpmf(k, p, j) for j in range(k + 1)]
    out = []
    for r in range(rounds + 1):
        out.append(sum(x for j, x in enumerate(d) if 2 * j > k))
        new = [F(0)] * (k + 1)
        for s, ps in enumerate(d):
            for j in range(k + 1):
                new[j] += ps * binpmf(k, F(s, k), j)
        d = new
    return out

def dcm(n, p, s, rounds):
    # state: number of correct answers seen so far, c, after r rounds (r*n answers in total)
    d = {0: F(1)}
    out, share = [], []
    for r in range(rounds + 1):
        acc = F(0); sh = F(0); new = {}
        for c, pc in d.items():
            q = (p * s + c) / (s + r * n)
            acc += pc * maj(n, q); sh += pc * q
            for j in range(n + 1):
                new[c + j] = new.get(c + j, F(0)) + pc * binpmf(n, q, j)
        out.append(acc); share.append(sh); d = new
    return out, share

n, p, R = 5, F(3, 4), 5
print('N=5 agents, p=0.75, two answers; P(majority correct) after r rounds, exact')
print('model                 ' + ''.join('   r=%d ' % r for r in range(R + 1)))
print('voter (copy one)      ' + ''.join(' %.4f' % float(x) for x in voter(n, p, R)))
for s in (1, 2, 4, 8, 20, 100):
    acc, share = dcm(n, p, F(s), R)
    assert all(x == p for x in share)          # the martingale: expected share stays at p
    print('Dirichlet, s=%-3d      ' % s + ''.join(' %.4f' % float(x) for x in acc))

# Table 1 of arXiv:2508.17536v2: Majority Voting (T=0) and Decentralized MAD at T=2,3,5, N=5.
cols = ['Arith', 'GSM8K', 'ProMed', 'FormLog', 'Hella', 'CSQA', 'HH-RLHF']
tab = {
 'Qwen2.5-7B': {'single': [.8140, .8713, .7868, .4905, .7880, .8153, .4773],
                0: [.9900, .9400, .7941, .5397, .8033, .8300, .4867],
                2: [.7600, .8867, .8051, .5556, .8033, .8567, .4967],
                3: [.6700, .8533, .8051, .5000, .8000, .8500, .5000],
                5: [.6700, .8333, .8051, .4762, .8000, .8433, .5067]},
 'Llama3.1-8B': {'single': [.7320, .7393, .7441, .3794, .6267, .6767, .4440],
                0: [.8900, .8733, .8199, .5159, .6933, .7800, .4967],
                2: [.8200, .7933, .7868, .5238, .6767, .7267, .5233],
                3: [.8300, .7933, .7684, .5000, .6300, .7033, .5267],
                5: [.8500, .7800, .7463, .5000, .6300, .7000, .5267]}}
print()
print('Table 1, Decentralized MAD minus Majority Voting (accuracy points); mean over 7 tasks; tasks lower/equal/higher')
for m, t in tab.items():
    for T in (2, 3, 5):
        diff = [round(100 * (a - b), 2) for a, b in zip(t[T], t[0])]
        lo = sum(x < 0 for x in diff); eq = sum(x == 0 for x in diff); hi = sum(x > 0 for x in diff)
        print('%-12s T=%d  ' % (m, T) + ' '.join('%6.2f' % x for x in diff) + '   mean %6.2f   %d/%d/%d' % (sum(diff) / 7, lo, eq, hi))
    print('%-12s mean single %.4f  vote %.4f  T=2 %.4f  T=3 %.4f  T=5 %.4f' % (m, sum(t['single'])/7, sum(t[0])/7, sum(t[2])/7, sum(t[3])/7, sum(t[5])/7))
# Is a plurality of 0.99 compatible with individual accuracy 0.54 (Table 6, Qwen, Arithmetics, 'round 1')?
q = 0.54
print()
print('5 independent agents at 0.54: P(at least 2 correct) = %.4f, P(at least 3) = %.4f' % (
    1 - (1-q)**5 - 5*q*(1-q)**4, sum(comb(5, j) * q**j * (1-q)**(5-j) for j in (3, 4, 5))))
