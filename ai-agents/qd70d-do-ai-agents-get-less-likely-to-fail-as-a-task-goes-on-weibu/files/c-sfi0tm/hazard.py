# hazard.py - does the declining hazard of AI agents (Weibull shape k < 1) survive a task-level random effect?
# Data: METR Time Horizon 1.1 runs.jsonl (https://github.com/METR/eval-analysis-public), not redistributed.
# Model A (marginal, per model): P(success | t) = exp(-(t/lam)^k)  <=>  cloglog(P(fail)) = k*log t - k*log lam.
#   Fitted as a binomial GLM on P(fail) with complementary log-log link; k is the slope on log t.
# Model B (conditional): the same, plus one random effect u_task ~ N(0, s^2) per task, shared by all models:
#   cloglog(P(fail_ij)) = a_model + k * log t_i + u_i. If the hazard per task is constant in t and the decline
#   is produced by tasks differing in difficulty at equal length, B gives k near 1 while A gives k < 1.
# Fits by maximum likelihood (Gauss-Hermite quadrature, 40 nodes), unweighted runs.
# usage: python hazard.py /data/agenthaz/runs.jsonl [baseline]
import sys
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import minimize
from scipy.special import log_expit

df = pd.read_json(sys.argv[1], lines=True)
df = df[(df["alias"] != "human") & df["human_minutes"].notna()].copy()
if len(sys.argv) > 2 and sys.argv[2] == "baseline":
    df = df[df["human_source"] == "baseline"].copy()
print("pandas", pd.__version__, "scipy", scipy.__version__, "numpy", np.__version__)
df["lt"] = np.log(df["human_minutes"])
df["y"] = df["score_binarized"].astype(float)  # 1 = success
# keep models with at least 20 successes and 20 failures
cnt = df.groupby("alias")["y"].agg(["sum", "count"])
keep = cnt[(cnt["sum"] >= 20) & (cnt["count"] - cnt["sum"] >= 20)].index
df = df[df["alias"].isin(keep)].copy()
models = sorted(keep)
mi = {m: i for i, m in enumerate(models)}
df["m"] = df["alias"].map(mi)
tasks = sorted(df["task_id"].unique())
ti = {t: i for i, t in enumerate(tasks)}
df["t"] = df["task_id"].map(ti)
print("runs", len(df), "models", len(models), "tasks", len(tasks))
lt_c = df["lt"].mean()
x = df["lt"].to_numpy() - lt_c
y = df["y"].to_numpy()
m = df["m"].to_numpy()
t = df["t"].to_numpy()
M, T = len(models), len(tasks)


def logp_success(eta):
    # P(fail) = 1 - exp(-exp(eta)); P(success) = exp(-exp(eta))
    return -np.exp(eta)


def logp_fail(eta):
    e = np.exp(eta)
    return np.log(-np.expm1(-e))


def ll_runs(eta):
    eta = np.clip(eta, -30, 6)
    return np.where(y == 1, logp_success(eta), logp_fail(eta))


# Model A per model: separate (a, k)
print("\nModel A, Weibull per model (no task effect): k = slope of cloglog(P fail) on log t")
kA = {}
for mm in models:
    s = df["m"].to_numpy() == mi[mm]
    xs, ys = x[s], y[s]

    def nll(b):
        eta = np.clip(b[0] + b[1] * xs, -30, 6)
        return -np.where(ys == 1, -np.exp(eta), np.log(-np.expm1(-np.exp(eta)))).sum()
    r = minimize(nll, np.array([0.0, 0.7]), method="BFGS")
    se = np.sqrt(np.diag(r.hess_inv))
    kA[mm] = (r.x[1], se[1])
# pooled A with per-model intercepts, one k


def nllA(p):
    eta = p[m] + p[M] * x
    return -ll_runs(eta).sum()


rA = minimize(nllA, np.r_[np.zeros(M), 0.7], method="BFGS")
print(f"  pooled, one k for all models: k = {rA.x[M]:.3f} (se {np.sqrt(rA.hess_inv[M, M]):.3f}), -logL = {rA.fun:.1f}")

# Model B: per-model intercepts, one k, task random effect, Gauss-Hermite
gh_x, gh_w = np.polynomial.hermite_e.hermegauss(40)  # probabilists': weight exp(-z^2/2)
gh_lw = np.log(gh_w / np.sqrt(2 * np.pi))
order = np.argsort(t, kind="stable")
bounds = np.r_[0, np.cumsum(np.bincount(t, minlength=T))]


def nllB(p):
    s = np.exp(p[M + 1])
    eta0 = p[m] + p[M] * x
    tot = 0.0
    # ll per run for each node, summed per task
    L = np.empty((T, len(gh_x)))
    for j, z in enumerate(gh_x):
        lr = ll_runs(eta0 + s * z)
        L[:, j] = np.bincount(t, weights=lr, minlength=T)
    A = L + gh_lw
    mx = A.max(axis=1, keepdims=True)
    tot = (mx[:, 0] + np.log(np.exp(A - mx).sum(axis=1))).sum()
    return -tot


rB = minimize(nllB, np.r_[rA.x, 0.0], method="L-BFGS-B")
# numerical se for k and log s
def hess_diag(f, p, i, h=1e-3):
    e = np.zeros_like(p); e[i] = h
    return (f(p + e) - 2 * f(p) + f(p - e)) / h ** 2
seB = 1 / np.sqrt(hess_diag(nllB, rB.x, M))
print(f"\nModel B, one k, per-model level, task effect N(0,s^2): k = {rB.x[M]:.3f} (se ~{seB:.3f}), s = {np.exp(rB.x[M+1]):.2f}, -logL = {rB.fun:.1f}")
print(f"  likelihood ratio B vs A: 2*dlogL = {2*(rA.fun-rB.fun):.1f} (1 extra parameter)")

# Model B': per-model k as well
def nllB2(p):
    s = np.exp(p[2 * M])
    eta0 = p[m] + p[M + m] * x
    L = np.empty((T, len(gh_x)))
    for j, z in enumerate(gh_x):
        L[:, j] = np.bincount(t, weights=ll_runs(eta0 + s * z), minlength=T)
    A = L + gh_lw
    mx = A.max(axis=1, keepdims=True)
    return -(mx[:, 0] + np.log(np.exp(A - mx).sum(axis=1))).sum()


rB2 = minimize(nllB2, np.r_[rB.x[:M], np.full(M, rB.x[M]), rB.x[M + 1]], method="L-BFGS-B")
print(f"\nModel B2, k per model with the task effect: s = {np.exp(rB2.x[2*M]):.2f}, -logL = {rB2.fun:.1f}")
print(f"{'model':36s} {'runs':>5s} {'k, no task effect':>20s} {'k, with task effect':>20s}")
for mm in models:
    k0, se0 = kA[mm]
    n = int((df['alias'] == mm).sum())
    print(f"{mm:36s} {n:5d} {k0:12.3f} ({se0:.3f}) {rB2.x[M + mi[mm]]:14.3f}")
