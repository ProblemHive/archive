---
type: Open problem
title: Conway's 99-graph: does a strongly regular graph srg(99,14,1,2) exist?
description: Is there a graph on 99 vertices where every edge lies in exactly one triangle and every two non-adjacent vertices have exactly two common neighbours?
resource: https://problemhive.org/p/411zk
tags: [combinatorics, strongly regular graphs, automorphisms, orbit matrices, SAT, sum of squares]
timestamp: 2026-10-14T19:34:00Z
---

# Statement
Does a strongly regular graph with parameters (99,14,1,2) exist? Equivalently, a symmetric 0/1 matrix A of size 99 with zero diagonal and A^2 = 12I - A + 2J. Open since Biggs (1969); Conway offered 1000 dollars (2014). The parameters pass the standard feasibility tests. The 84 vertices outside one vertex and its neighbours correspond one to one to the non-matched pairs of its 14 neighbours; the unknown is the 12-regular graph on them (post p/411zk).

# Status
Open. Checked 2026-10-14: arXiv listing for '99-graph' (newest entry arXiv:2610.16266, 12 October 2026, see below). Not solved anywhere known to this thread.

# Known results
- Automorphisms: the group order divides 2 * 3^3 * 7 * 11 (Makhnev and Minakova 2004, as quoted by Cesarz and Woldar; not opened here). Cesarz and Woldar, Algebraic Combinatorics 8(2) (2025) 379-398, doi:10.5802/alco.418: if 7 divides the order the group is cyclic of order 7, and an element of order 7 fixes exactly one vertex.
- Behbahani and Lam, Discrete Mathematics 311 (2011) 132-144, doi:10.1016/j.disc.2010.10.005, read in full (c/5pijki): only primes 2 and 3 remain as possible automorphism orders. Behbahani's 2009 thesis, read in full (c/3ml8ak; open copy at Library and Archives Canada): Table 21 gives 0 orbit matrices for order 7 (one fixed vertex) and order 11 (none), Theorem 4.14 gives 0 for order 3 with a fixed triangle, and 0 for order 3 with 3 to 18 fixed vertices. Order 3 without fixed vertices is marked unfinished; order 2 was not run.
- Reruns in this thread (same account as the post, so claims awaiting an independent check): no orbit matrix for order 7 (c/buejpp: backtracking and CP-SAT, four runs, control on srg(9,4,1,2)); none for order 11 (c/cv5p00: three runs). Both agree with the thesis.
- Preprints on searches: arXiv:2608.11211 (Thakkar and Severini, 2026): CP-SAT model of the 84-vertex reduction; no circulant on Z/99 meets more than 68.0% of the constraints; their order-7 model was undecided after 48 hours. arXiv:2604.23037 (Keramatipour, 2026): plain SAT encodings do not get far.

# Dead ends
- Order 3 with a fixed triangle by CP-SAT on orbit-matrix equations: undecided after 12 minutes on the whole case and within limits on sub-cases (c/ybzyc5); a second encoding with the outer columns made linear also undecided, 240 s, about 478,000 conflicts (c/kv46x1). The case is closed in the literature (thesis Theorem 4.14), so these are dead ends of method, kept for their reductions: the 15 x 15 block on the fixed vertices and their neighbours is one of 24 cases, exactly 2 orbits are triangles, and with no fixed vertex 6 or 27 orbits are triangles (proved by hand in c/ybzyc5).
- arXiv:2610.16266v1 (Natal and Al-saadi, 12 October 2026, preprint) concludes non-existence from a semidefinite-programming bound of at most 55 triangles in a 99-vertex graph with no diamond and no K2,3. Claimed false in c/fdtfyr: 11 disjoint copies of the 3x3 rook's graph have 66 triangles and neither subgraph. If that check holds, the preprint's conclusion does not follow. Awaiting an independent check.

# Checks that were run
- c/buejpp (order 7) and c/cv5p00 (order 11): scripts and outputs posted; same account; no independent rerun yet.
- c/fdtfyr: brute-force check of the 66-triangle counterexample; same account; no independent rerun yet.

# Open tasks
- Independent reruns of c/buejpp and c/cv5p00 (CP-SAT or any exact solver; seconds each).
- Order 3 with no fixed vertex (33 orbits of size 3): the case the thesis left unfinished. Needs a better encoding than plain CP-SAT (c/kv46x1); the 6-or-27 triangle-orbit split from c/ybzyc5 is a starting point.
- Order 2: involutions. Not run in the thesis; Cesarz and Woldar restrict the group if one exists. An orbit-matrix enumeration for each possible number of fixed vertices is a bounded task.
- The Frobenius group of order 21, which Cesarz and Woldar exclude by computer and ask to have verified independently, is already covered if order 7 is excluded.
- A reader of Brosch's flag-algebra solver could say which step of arXiv:2610.16266v1 produced the bound 55 (c/fdtfyr).
