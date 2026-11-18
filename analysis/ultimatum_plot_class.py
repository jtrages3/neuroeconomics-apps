"""Plot class Ultimatum Game results in the style of Sanfey et al. (2003), Fig. 1B.

Input: JSON from the Firestore REST list endpoint for the `ultimatum` collection.
Usage: python plot_class.py docs.json out.png [--all-plays]
By default only each browser's first play (play == 1) is used.
"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OFFERS = [("o55", r"\$5:\$5"), ("o73", r"\$7:\$3"), ("o82", r"\$8:\$2"), ("o91", r"\$9:\$1")]
PAPER = {"human": [100, 95, 53, 40], "computer": [100, 95, 84, 67]}  # approx., read from Fig. 1B


def load(path, all_plays=False):
    docs = json.load(open(path)).get("documents", [])
    rows = []
    for d in docs:
        f = d["fields"]
        play = int(f["play"]["integerValue"])
        if not all_plays and play != 1:
            continue
        get = lambda side: [float(f[side]["mapValue"]["fields"][k]["integerValue"]) for k, _ in OFFERS]
        rows.append({"human": get("human"), "computer": get("computer")})
    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    all_plays = "--all-plays" in sys.argv
    src, out = args[0], args[1]
    rows = load(src, all_plays)
    n = len(rows)
    H = np.array([r["human"] for r in rows])
    C = np.array([r["computer"] for r in rows])
    hm, cm = H.mean(0), C.mean(0)
    hse = H.std(0, ddof=1) / np.sqrt(n) if n > 1 else np.zeros(4)
    cse = C.std(0, ddof=1) / np.sqrt(n) if n > 1 else np.zeros(4)

    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=200)
    x = np.arange(4); w = 0.36
    ax.bar(x - w/2, hm, w, yerr=hse, color="black", edgecolor="black", capsize=3, label="Human", error_kw=dict(lw=1))
    ax.bar(x + w/2, cm, w, yerr=cse, color="white", edgecolor="black", capsize=3, label="Computer", error_kw=dict(lw=1))
    # Paper values as small markers for comparison
    ax.scatter(x - w/2, PAPER["human"], marker="_", s=260, color="#c0392b", zorder=5, linewidths=2.2)
    ax.scatter(x + w/2, PAPER["computer"], marker="_", s=260, color="#c0392b", zorder=5, linewidths=2.2,
               label="Sanfey et al. 2003 (approx.)")
    ax.set_xticks(x, [lab for _, lab in OFFERS], fontweight="bold")
    ax.set_xlabel("Offer", fontweight="bold")
    ax.set_ylabel("Acceptance rates", fontweight="bold")
    ax.set_ylim(0, 105); ax.set_yticks(range(0, 101, 10))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8)
    plays = "all plays" if all_plays else "first play per student"
    ax.set_title(f"Class Ultimatum Game results (n = {n}, {plays}; mean ± SEM)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out)

    print(f"n = {n}")
    print("offer   human   computer   (paper human / computer)")
    for i, (_, lab) in enumerate(OFFERS):
        print(f"{lab.replace(chr(92), ''):6} {hm[i]:6.1f}   {cm[i]:6.1f}      ({PAPER['human'][i]} / {PAPER['computer'][i]})")
    if n > 1:
        # Paired comparison on the unfair offers ($8:$2 and $9:$1), mean per student
        diff = C[:, 2:].mean(1) - H[:, 2:].mean(1)
        t = diff.mean() / (diff.std(ddof=1) / np.sqrt(n)) if diff.std(ddof=1) > 0 else float("nan")
        print(f"Unfair ($8:$2, $9:$1) acceptance, computer minus human: {diff.mean():.1f} points; paired t({n-1}) = {t:.2f}")


if __name__ == "__main__":
    main()
