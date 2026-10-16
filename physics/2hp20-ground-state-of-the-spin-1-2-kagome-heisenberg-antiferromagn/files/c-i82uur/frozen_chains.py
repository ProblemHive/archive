"""What a Monte Carlo energy estimate gives when single-spin-flip chains freeze.

Uses the exact ground state psi of the 18-site torus (2x3, Sz = 0 sector, from
kagome_ed.py). A single spin flip leaves the Sz = 0 sector, where psi = 0, so
every Metropolis proposal is rejected and each chain stays at its start s.
The energy estimate is then the average of the local energy
E_loc(s) = (H psi)(s) / psi(s) over the starting configurations.

Printed: E0; the |psi|^2-weighted mean of E_loc (must equal E0); the spread of
E_loc over the sector; the share of configurations with E_loc < E0; and the
estimate from 1000 frozen chains started uniformly at random (seed 7).
Also: a full dense diagonalisation of the 12-site torus as a check of eigsh.
"""
import numpy as np
from kagome_ed import bonds, lowest, sector_states, hamiltonian

# check eigsh against dense diagonalisation, 12 sites, Sz = 0
N, B = bonds(2, 2)
st = sector_states(N, N // 2)
Hd = hamiltonian(N, B, st).toarray()
print(f"12 sites, dense eigvalsh: E0 = {np.linalg.eigvalsh(Hd)[0]:.10f}")

N, B = bonds(2, 3)
w, v, st, H = lowest(N, B, N // 2, k=1)
E0, psi = w[0], v[:, 0]
Hpsi = H @ psi
mask = np.abs(psi) > 1e-6 * np.abs(psi).max()
Eloc = Hpsi[mask] / psi[mask]
p = psi[mask] ** 2
print(f"18 sites: E0 = {E0:.10f}; configurations in sector = {len(st)}, with psi != 0: {mask.sum()}")
print(f"sum |psi|^2 E_loc = {np.sum(p * Eloc):.10f} (equals E0: the estimator is exact under perfect sampling)")
print(f"max |E_loc - E0| over configurations = {np.abs(Eloc - E0).max():.3e}  (exact eigenstate: E_loc = E0 everywhere)")

# a near-eigenstate, as a trained network would be: psi + small error
rng = np.random.default_rng(7)
for eps in [1e-3, 1e-2, 1e-1]:
    phi = psi + eps * rng.normal(size=psi.size) / np.sqrt(psi.size)
    phi /= np.linalg.norm(phi)
    Evar = phi @ (H @ phi)
    El = (H @ phi) / phi
    starts = rng.integers(0, psi.size, 1000)
    est_uniform = El[starts].mean()
    w2 = phi ** 2
    # frozen chains started from |phi|^2 (perfect starts)
    starts2 = rng.choice(psi.size, 1000, p=w2 / w2.sum())
    est_perfect = El[starts2].mean()
    print(f"eps={eps:g}: variational E = {Evar:.6f} (>= E0 = {E0:.6f}); "
          f"share of configs with E_loc < E0: {(El < E0).mean():.3f}; min E_loc = {El.min():.3g}; "
          f"1000 frozen chains, uniform starts: {est_uniform:.4g}; starts from |phi|^2: {est_perfect:.6f}")
