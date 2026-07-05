#!/usr/bin/env python3
"""Monte Carlo: Mexico vs England — WC 2026 R16 @ Estadio Azteca."""

import random
import math
from collections import Counter

random.seed(20260705)
N = 25000

# Market: ENG ~2.40 (42%) / Draw ~3.15 (32%) / MEX ~3.10 (32%) — tight underdog home
# Mexico: 4-0 GF/GA in groups, Azteca fortress; England: cautious starts, Kane clutch
mex_xg = 1.05
eng_xg = 1.12
HOME_BOOST = 1.12  # altitude + Azteca


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate():
    m90 = poisson(mex_xg * HOME_BOOST)
    e90 = poisson(eng_xg)
    m1 = poisson(mex_xg * HOME_BOOST * 0.40)
    e1 = poisson(eng_xg * 0.38)

    r90 = 'D' if m90 == e90 else ('M' if m90 > e90 else 'E')
    mt, et = m90, e90
    qual = r90
    extra = False

    if r90 == 'D':
        extra = True
        met = poisson(mex_xg * HOME_BOOST * 0.28)
        eet = poisson(eng_xg * 0.28)
        mt, et = m90 + met, e90 + eet
        if mt == et:
            qual = 'E' if random.random() < 0.62 else 'M'
        elif mt > et:
            qual = 'M'
        else:
            qual = 'E'

    tg = mt + et
    m2 = max(0, m90 - m1)
    e2 = max(0, e90 - e1)
    tg_1h = m1 + e1
    tg_2h = m2 + e2

    eng_wins_ht = e1 > m1
    mex_wins_ht = m1 > e1
    eng_wins_2h = e2 > m2
    mex_wins_2h = m2 > e2
    eng_wins_both = eng_wins_ht and eng_wins_2h and e90 > m90
    mex_wins_both = mex_wins_ht and mex_wins_2h and m90 > e90

    return {
        'r90': r90, 'qual': qual, 'tg': tg, 'extra': extra,
        'u25': tg <= 2.5, 'u35': tg <= 3.5, 'o25': tg > 2.5,
        'btts': mt > 0 and et > 0,
        'eng_ml': r90 == 'E', 'eng_qual': qual == 'E',
        'eng_dc': r90 in ('E', 'D'),
        'mex_dc': r90 in ('M', 'D'),
        'eng_dc_u35': r90 in ('E', 'D') and tg <= 3.5,
        'mex_dc_u35': r90 in ('M', 'D') and tg <= 3.5,
        'eng_not_both': not eng_wins_both,
        'mex_not_both': not mex_wins_both,
        'draw_ht': m1 == e1,
        'u15_1h': tg_1h <= 1.5,
        'u15_2h': tg_2h <= 1.5,
        'mex_cs': et == 0,
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
print("MEXICO vs ENGLAND — 25,000 MC")
print(f"xG/90: MEX {mex_xg * HOME_BOOST:.2f} | ENG {eng_xg:.2f}")
print("=" * 72)
print(f"90m  MEX:{pct(lambda r:r['r90']=='M'):.1f}% Draw:{pct(lambda r:r['r90']=='D'):.1f}% ENG:{pct(lambda r:r['r90']=='E'):.1f}%")
print(f"Qualify ENG:{pct(lambda r:r['eng_qual']):.1f}% MEX:{pct(lambda r:r['qual']=='M'):.1f}%")

candidates = [
    ('Under 2.5 golos total', 1.40, lambda r: r['u25']),
    ('Under 3.5 golos total', 1.35, lambda r: r['u35']),
    ('MEX/Empate & Under 3.5', 1.38, lambda r: r['mex_dc_u35']),
    ('ENG/Empate & Under 3.5', 1.42, lambda r: r['eng_dc_u35']),
    ('Empate 1.a parte', 2.00, lambda r: r['draw_ht']),
    ('Under 1.5 golos 1.a parte', 1.45, lambda r: r['u15_1h']),
    ('ENG nao vence ambas (Nao)', 1.44, lambda r: r['eng_not_both']),
    ('MEX nao vence ambas (Nao)', 1.42, lambda r: r['mex_not_both']),
    ('ENG qualifica', 1.66, lambda r: r['eng_qual']),
    ('BTTS Nao', 1.55, lambda r: not r['btts']),
    ('MEX clean sheet', 3.50, lambda r: r['mex_cs']),
]

print("\nCANDIDATES @ 1.30-1.50:")
rows = []
for name, odd, fn in candidates:
    if not (1.30 <= odd <= 1.50):
        continue
    p = pct(fn)
    lo, hi = ci(p)
    flag = "PASS75" if p >= 75 else "----"
    rows.append((p, name, odd, flag))
    print(f"  {name:36s} @{odd:.2f} M:{p:5.1f}% [{lo:.0f}-{hi:.0f}] {flag}")

rows.sort(reverse=True)
if rows:
    print(f"\n>>> TOP: {rows[0][1]} @{rows[0][2]:.2f} — {rows[0][0]:.1f}%")

# Acca with BRA pick
bra_p = 91.5
if rows:
    best = rows[0]
    joint = bra_p/100 * best[0]/100
    print(f"\nACCA BRA nao ambas @1.42 + {best[1]} @{best[2]:.2f}:")
    print(f"  Odd conjunta ~{1.42*best[2]:.2f} | Prob ~{joint*100:.1f}%")

sc = Counter((r['r90']) for r in res)
print("\nRESULT 90m:", {k: v/N*100 for k,v in sc.items()})
