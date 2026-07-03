#!/usr/bin/env python3
"""Monte Carlo: Colombia vs Ghana — WC 2026 R32 @ Arrowhead Stadium."""

import random
import math
from collections import Counter

random.seed(20260704)
N = 25000

# Opta supercomputer calibration (The Analyst): COL 68.9% / Draw 19.5% / GHA 11.6%
# Colombia group: 4 GF, 1 GA — defensive solidity, low conversion vs POR/Congo
# Ghana group: 2 GF, 3 GA — low block, 36.1% possession, Queiroz defensive
COL_ATTACK = 1.72
GHA_ATTACK = 0.52
COL_DEFENSE = 0.74
GHA_DEFENSE = 1.06
KNOCKOUT = 0.93

col_xg = COL_ATTACK * GHA_DEFENSE * KNOCKOUT  # ~1.70
gha_xg = GHA_ATTACK * COL_DEFENSE * KNOCKOUT * 0.90  # ~0.32

# Scorer props — Colombia spread goals across Munoz, Diaz, Suarez, Cordoba
COL_SCORER_RATE = 0.78  # Colombia scores at least once
CORDOBA_SUAREZ_RATE = 0.52  # either Cordoba or Suarez SuperSub


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate():
    a90 = poisson(col_xg)
    g90 = poisson(gha_xg)
    a1 = poisson(col_xg * 0.44)
    g1 = poisson(gha_xg * 0.38)

    r90 = 'D' if a90 == g90 else ('C' if a90 > g90 else 'G')
    at, gt = a90, g90
    et = False
    qual = r90

    if r90 == 'D':
        et = True
        aet = poisson(col_xg * 0.28)
        get = poisson(gha_xg * 0.22)
        at, gt = a90 + aet, g90 + get
        if at == gt:
            qual = 'C' if random.random() < 0.72 else 'G'
        elif at > gt:
            qual = 'C'
        else:
            qual = 'G'

    tg = at + gt
    # 2H regular time only (exclude ET for half markets)
    a2_90 = max(0, a90 - a1)
    g2_90 = max(0, g90 - g1)
    goals_2h = a2_90 + g2_90
    goals_1h = a1 + g1

    col_wins_ht = a1 > g1
    gha_wins_ht = g1 > a1
    col_wins_2h = a2_90 > g2_90
    gha_wins_2h = g2_90 > a2_90
    col_wins_both = col_wins_ht and col_wins_2h and a90 > g90

    col_scores = at > 0
    gha_scores = gt > 0

    # First / last goal team (90 min)
    if a90 == 0 and g90 == 0:
        col_first = col_last = False
    elif g90 == 0:
        col_first = col_last = True
    elif a90 == 0:
        col_first = col_last = False
    else:
        col_first = random.random() < col_xg / (col_xg + gha_xg)
        if a90 > g90:
            col_last = True
        elif g90 > a90:
            col_last = False
        else:
            col_last = random.random() < 0.55  # slight COL edge at 1-1

    cordoba_suarez = False
    if col_scores:
        cordoba_suarez = random.random() < CORDOBA_SUAREZ_RATE
        if not cordoba_suarez:
            cordoba_suarez = random.random() < 0.35

    # Early win: 2 goal lead OR win at 90
    col_early = (at - gt >= 2) or (qual == 'C' and r90 != 'D')

    return {
        'r90': r90, 'qual': qual, 'at': at, 'gt': gt, 'tg': tg,
        'a1': a1, 'g1': g1, 'a2': a2_90, 'g2': g2_90,
        'et': et, 'ht': 'D' if a1 == g1 else ('C' if a1 > g1 else 'G'),
        'col_wins_both': col_wins_both,
        'col_not_both': not col_wins_both,
        'col_or_gha_1h': a1 != g1,
        'btts': col_scores and gha_scores,
        'gha_scores': gha_scores,
        'col_scores': col_scores,
        'col_first': col_first,
        'col_last': col_last,
        'u35': tg <= 3.5,
        'u25': tg <= 2.5,
        'o15': tg > 1.5,
        'col_dc_u35': r90 in ('C', 'D') and tg <= 3.5,
        'col_dc_o15': r90 in ('C', 'D') and tg > 1.5,
        'col_ml': qual == 'C',
        'col_90': r90 == 'C',
        'col_early': col_early,
        'gha_u05': gt == 0,
        'col_u25': at <= 2.5,
        'o05_1h': goals_1h >= 1,
        'u15_1h': goals_1h <= 1.5,
        'u15_2h': goals_2h <= 1.5,
        'cordoba_suarez': cordoba_suarez,
        'col_ganha_uma_parte': col_wins_ht or col_wins_2h,
    }


def pct(fn):
    return sum(1 for r in res if fn(r)) / N * 100


def ci(p):
    p /= 100
    z = 1.96
    d = 1 + z * z / N
    c = (p + z * z / (2 * N)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * N)) / N) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


res = [simulate() for _ in range(N)]

print("=" * 72)
print("COLOMBIA vs GHANA — 25,000 MC")
print(f"xG/90: COL {col_xg:.2f} | GHA {gha_xg:.2f}")
print("=" * 72)
print(f"90m  COL:{pct(lambda r:r['r90']=='C'):.1f}% Draw:{pct(lambda r:r['r90']=='D'):.1f}% GHA:{pct(lambda r:r['r90']=='G'):.1f}%")
print(f"Qualify COL:{pct(lambda r:r['qual']=='C'):.1f}%")

candidates = [
    ('Colombia ML (TR)', 1.45, lambda r: r['col_90']),
    ('Colombia qualifica', 1.16, lambda r: r['qual'] == 'C'),
    ('Colombia early win (2g/vence)', 1.43, lambda r: r['col_early']),
    ('COL/EMP & Under 3.5', 1.35, lambda r: r['col_dc_u35']),
    ('COL/EMP & Over 1.5', 1.33, lambda r: r['col_dc_o15']),
    ('COL ou GHA 1.ª parte', 1.41, lambda r: r['col_or_gha_1h']),
    ('COL nao vence ambas (Nao)', 1.21, lambda r: r['col_not_both']),
    ('COL vence ambas (Sim)', 2.82, lambda r: r['col_wins_both']),
    ('BTTS Nao', 1.54, lambda r: not r['btts']),
    ('Gana Under 0.5 golos', 1.72, lambda r: r['gha_u05']),
    ('Under 3.5 golos', 1.25, lambda r: r['u35']),
    ('Under 2.5 golos', 1.70, lambda r: r['u25']),
    ('Gana Under 0.5 golos', 1.72, lambda r: r['gha_u05']),
    ('COL Under 2.5 golos equipa', 1.32, lambda r: r['col_u25']),
    ('COL marca 1.º golo', 1.34, lambda r: r['col_first']),
    ('COL marca ultimo golo', 1.34, lambda r: r['col_last']),
    ('Over 0.5 golos 1.ª parte', 1.33, lambda r: r['o05_1h']),
    ('Under 1.5 golos 1.ª parte', 1.37, lambda r: r['u15_1h']),
    ('Under 1.5 golos 2.ª parte', 1.47, lambda r: r['u15_2h']),
    ('Cordoba/Suarez SuperSub', 1.48, lambda r: r['cordoba_suarez']),
    ('COL ganha uma das partes', 1.20, lambda r: r['col_ganha_uma_parte']),
    ('Prolongamento Nao', 1.17, lambda r: not r['et']),
]

print("\nCANDIDATES @ 1.30-1.50:")
rows = []
for name, odd, fn in candidates:
    if not (1.30 <= odd <= 1.50):
        continue
    p = pct(fn)
    lo, hi = ci(p)
    flag = "PASS75" if p >= 75 else "----"
    rows.append((p, name, odd, lo, hi, flag))
    print(f"  {name:32s} @{odd:.2f} M:{p:5.1f}% [{lo:.0f}-{hi:.0f}] {flag}")

sc = Counter((r['at'], r['gt']) for r in res)
print("\nTOP SCORES:")
for (a, c), n in sc.most_common(10):
    print(f"  {a}-{c}: {n/N*100:.1f}%")

print("\nGAME SCRIPTS:")
print(f"  Open (O2.5):     {pct(lambda r: r['tg']>2.5):.1f}%")
print(f"  Low (U2.5):      {pct(lambda r: r['u25']):.1f}%")
print(f"  0-0 at 90:       {pct(lambda r: r['r90']=='D' and r['at']==0):.1f}%")
print(f"  COL 1-0:         {pct(lambda r: r['at']==1 and r['gt']==0):.1f}%")
print(f"  COL 2-0:         {pct(lambda r: r['at']==2 and r['gt']==0):.1f}%")
