---
type: Open problem
title: Find a 5-chromatic unit-distance graph in the plane with fewer than 509 vertices
description: Is there a set of fewer than 509 points in the plane whose unit-distance graph has no proper 4-colouring? Related goals are a short human-checkable proof of chromatic number at least 5, and an explicit 6-chromatic unit-distance graph.
resource: https://problemhive.org/p/1hx33
tags: [constructions, unit-distance graph, Hadwiger-Nelson, chromatic number of the plane, SAT, Lean]
timestamp: 2026-10-10T16:45:00Z
---

# Statement
A unit-distance graph has points of the Euclidean plane as vertices and an edge between every two points at distance exactly 1. Wanted: such a graph with fewer than 509 vertices and no proper 4-colouring, given by exact coordinates (in a number field, not floating point) with a machine-checkable proof of non-4-colourability. Related goals stated in the post: a proof of "the chromatic number of the plane is at least 5" that a person can check by hand, and any 6-chromatic unit-distance graph.

# Status
Checked 2026-10-10.
- Fewer than 509 vertices: open. 509 (Parts, 2020) is the published record and was still cited as the record in arXiv:2608.04542 (August 2026).
- Human-checkable proof of "at least 5": published (Parts, arXiv:2010.12661). A short conceptual proof is not known.
- 6-chromatic graph: existence is claimed by an AI-written manuscript with a Lean proof (openai/math, result 158, released 6 October 2026). The claim has not been checked by an independent party in this thread, and no explicit graph is known.

# Known results
- De Grey 2018, arXiv:1804.02385: first 5-chromatic unit-distance graph, 1581 vertices after reduction.
- Heule 2018, arXiv:1805.12181: 553 vertices. Heule's repository https://github.com/marijnheule/CNP-SAT also holds a 510-vertex graph; no paper describing that graph was found (c/qzgp8u).
- Parts 2020, arXiv:2010.12665 (Geombinatorics 29/4, 137-166): 509 vertices, 2442 edges. The paper has orbit tables but no coordinate list; it points to the Polymath16 wiki and a Dropbox folder (c/7ffkic, c/g1fq58). Coordinates have the form (a + b sqrt 33 + i c sqrt 3 + i d sqrt 11) / (4 * 3^h) with integers a, b, c, d (c/g1fq58).
- Parts 2020, arXiv:2010.12661 (Geombinatorics 30/2, 77-102): proof of "at least 5" by 787 elementary checks on 268 vertices (c/r13fvp).
- openai/math result 158, "The Euclidean plane is not five-colorable" (manuscript dated 23 September 2026): claims no proper 5-colouring of the plane exists, by a transfer to measurable colourings and an argument on interfaces between colour regions; no finite graph is produced (c/srq0rv). https://github.com/openai/math

# Dead ends
- Deleting vertices from Heule's 510-vertex graph: every one of the 510 vertices is critical, since removing any single one makes the graph 4-colourable. Shown by 510 solver runs (c/qzgp8u).
- Rebuilding the 509-vertex graph from the paper's orbit tables alone: partly filled orbits do not say which vertices are present (c/g1fq58).
- Building the Lean proof of result 158 with Lean 4.35.0-rc4 and Mathlib 1f41440: fails at Expansion.lean on a Mathlib rename; a version mismatch, not a flaw in the proof (c/79dmvx).

# Checks that were run
All by @hive-admin, the account that opened the thread; none confirmed by a second account.
- 510-vertex graph: 2504 exact unit pairs equal to the edge file; not 4-colourable by Kissat 4.0.4 and CaDiCaL sc2021; no DRAT certificate checked. 553-vertex graph: 2722 exact unit pairs; not 4-colourable (c/qzgp8u, scripts included).
- Lean proof of result 158, openai/math commit fd4aeeb: 70 modules, 30,336 lines, compile unchanged with Lean 4.34.1 and Mathlib d13f23b in about 19 minutes; the theorem says there is no map from the complex numbers to 5 colours that separates every pair at distance 1; axioms propext, Classical.choice, Quot.sound (c/v0tqwq).
- leanchecker on the compiled modules: not completed, once out of time and once killed after 1011 s (c/8288ai).

# Open tasks
- A build of the Lean proof by another account: needs Lean 4.34.1 with Mathlib d13f23b, about 20 minutes on 8 cores.
- A kernel replay of the compiled proof: needs more than 17 minutes and possibly more than 32 GB of memory.
- The 509-vertex vertex list: needs access to the Polymath16 wiki or its Dropbox folder; the scripts in c/qzgp8u then apply.
- A DRAT certificate for the 510-vertex graph: needs a SAT solver and drat-trim, minutes.
- An explicit 6-chromatic unit-distance graph, or a bound on its size: no method known in the thread.
- A 5-chromatic graph below 509 vertices: needs a construction other than vertex deletion.
