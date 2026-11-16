"""Reproduce the human-rating statistics from ratings.csv and items.csv (run from the package root: python analysis/analyze.py)."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
def kripp_alpha_ordinal(mat):
    """mat: units x raters array of ints 1..5 or nan. Krippendorff (2011) coincidence-matrix form."""
    vals = np.arange(1, 6)
    o = np.zeros((5, 5))
    for row in mat:
        v = row[~np.isnan(row)].astype(int)
        m = len(v)
        if m < 2:
            continue
        for a in range(m):
            for b in range(m):
                if a != b:
                    o[v[a] - 1, v[b] - 1] += 1.0 / (m - 1)
    nc = o.sum(1)
    n = nc.sum()
    if n <= 1:
        return np.nan
    delta = np.zeros((5, 5))
    for c in range(5):
        for k in range(5):
            lo, hi = min(c, k), max(c, k)
            delta[c, k] = (nc[lo:hi + 1].sum() - (nc[c] + nc[k]) / 2.0) ** 2
    do = (o * delta).sum()
    de = (np.outer(nc, nc) * delta).sum() / (n - 1)
    return np.nan if de == 0 else 1.0 - do / de


rat = pd.read_csv("ratings.csv"); it = pd.read_csv("items.csv")
it = it[it.role == "rated"]
rng = np.random.default_rng(0)
print(f"items rated: {rat.item_id.nunique()}, annotators: {sorted(rat.annotator.unique())}, ratings: {len(rat)}")
for dim in ("fidelity", "helpfulness"):
    m = rat.pivot_table(index="item_id", columns="annotator", values=dim)
    a = kripp_alpha_ordinal(m.values)
    boots = [kripp_alpha_ordinal(m.values[rng.integers(0, len(m), len(m))]) for _ in range(1000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    pairs = {f"{x}-{y}": round(spearmanr(m[x], m[y], nan_policy="omit")[0], 3) for x, y in (("A", "B"), ("A", "C"), ("B", "C"))}
    print(f"{dim}: Krippendorff alpha (ordinal) = {a:.3f} [{lo:.3f}, {hi:.3f}]; pairwise Spearman {pairs}")
mean = rat.groupby("item_id")[["fidelity", "helpfulness"]].mean()
df = it.set_index("item_id").join(mean)
df["gta_score"] = pd.to_numeric(df.gta_score, errors="coerce"); df["direct_score"] = pd.to_numeric(df.direct_score, errors="coerce")
both = df.dropna(subset=["gta_score", "direct_score"])
print("\nper model (fidelity/helpfulness over all rated items; accuracies over items with GtA results):")
out = df.groupby("model")[["fidelity", "helpfulness"]].mean().join(
    both.groupby("model").agg(n_with_gta=("gta_score", "size"), gta_acc=("gta_score", "mean"), direct_acc=("direct_score", "mean")))
out["gta_minus_direct"] = out.gta_acc - out.direct_acc
print(out.round(3).to_string())
