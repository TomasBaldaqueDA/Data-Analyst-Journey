#!/usr/bin/env python3
"""Monte Carlo: Paraguay vs France — WC 2026 R16 @ Lincoln Financial Field."""

import random
import math
from collections import Counter

random.seed(20260704)
N = 25000

# Calibration: Betclic TR — FRA 1.19 (84%) / Draw 7.00 (14%) / PAR 15.50 (6%)
# France WC2026: 13 GF in 4 games (3.25/game); Paraguay: 6 GF, 5 GA in 5
# Paraguay deep block post-GER; France elite attack (Mbappé 6, Dembélé 4)
FRA_ATTACK = 2.55
PAR_ATTACK = 0.88
FRA_DEFENSE = 0.48
PAR_DEFENSE = 0.88
KNOCKOUT = 0.94
PAR_BLOCK = 0.82

fra_xg = 2.05  # calibrated → ~80% FRA TR (Betclic 1.19)
par_xg = 0.35


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate():
    f90 = poisson(fra_xg)
    p90 = poisson(par_xg)
    f1 = poisson(fra_xg * 0.46)
    p1 = poisson(par_xg * 0.38)

    r90 = 'D' if f90 == p90 else ('F' if f90 > p90 else 'P')
    ft, pt = f90, p90
    et = False
    qual = r90

    if r90 == 'D':
        et = True
        fet = poisson(fra_xg * 0.30)
        pet = poisson(par_xg * 0.22)
        ft, pt = f90 + fet, p90 + pet
        if ft == pt:
            qual = 'F' if random.random() < 0.72 else 'P'
        elif ft > pt:
            qual = 'F'
        else:
            qual = 'P'

    tg = ft + pt
    f2 = max(0, f90 - f1)
    p2 = max(0, p90 - p1)
    tg_2h = f2 + p2

    fra_wins_ht = f1 > p1
    par_wins_ht = p1 > f1
    fra_wins_2h = f2 > p2
    par_wins_2h = p2 > f2
    fra_wins_both = fra_wins_ht and fra_wins_2h and f90 > p90
    fra_wins_both = fra_wins_ht and fra_wins_2h and f90 > p90

    return {
        'r90': r90, 'qual': qual, 'f90': f90, 'p90': p90, 'ft': ft, 'pt': pt,
        'f1': f1, 'p1': p1, 'f2': f2, 'p2': p2, 'tg': tg, 'et': et,
        'btts': ft > 0 and pt > 0,
        'btts_90': f90 > 0 and p90 > 0,
        'u25': tg <= 2.5,
        'u35': tg <= 3.5,
        'u45': tg <= 4.5,
        'o15': tg >= 2,
        'fra_ml': qual == 'F',
        'fra_90': r90 == 'F',
        'par_ml': qual == 'P',
        'fra_dc': r90 in ('F', 'D'),
        'par_dc': r90 in ('P', 'D'),
        'fra_dc_u35': r90 in ('F', 'D') and tg <= 3.5,
        'fra_dc_u25': r90 in ('F', 'D') and tg <= 2.5,
        'fra_dc_o15': r90 in ('F', 'D') and tg >= 2,
        'pf_dc_u35': r90 in ('F', 'P') and tg <= 3.5,
        'fra_dc_btts_no': r90 in ('F', 'D') and not (ft > 0 and pt > 0),
        'pf_dc_btts_no': r90 in ('F', 'P') and not (ft > 0 and pt > 0),
        'fra_not_both': not fra_wins_both,
        'fra_wins_both': fra_wins_both,
        'par_not_both': not (par_wins_ht and par_wins_2h and p90 > f90),
        'par_u05': p90 == 0,
        'par_u05_ft': pt == 0,
        'fra_o15': f90 >= 2,
        'fra_o15_ft': ft >= 2,
        'fra_u15_1h': f1 <= 1.5,
        'u15_1h': (f1 + p1) <= 1.5,
        'u15_2h': tg_2h <= 1.5,
        'u35_total': tg <= 3.5,
        'no_et': not et,
        'draw_90': r90 == 'D',
        'fra_hcp_m1': (f90 - 1) > p90,
        'score_02': f90 == 2 and p90 == 0,
        'score_03': f90 == 3 and p90 == 0,
        'fra_cs': pt == 0,
        'btts_or_o25': (f90 > 0 and p90 > 0) or tg > 2.5,
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
print("PARAGUAY vs FRANCE — 25,000 MC")
print(f"xG/90: FRA {fra_xg:.2f} | PAR {par_xg:.2f}")
print("=" * 72)
print(f"90m  PAR:{pct(lambda r:r['r90']=='P'):.1f}% Draw:{pct(lambda r:r['r90']=='D'):.1f}% FRA:{pct(lambda r:r['r90']=='F'):.1f}%")
print(f"Qualify FRA:{pct(lambda r:r['qual']=='F'):.1f}% PAR:{pct(lambda r:r['qual']=='P'):.1f}%")

# Betclic odds from user screenshots
candidates = [
    ('Franca Over 1.5 golos equipa', 1.30, lambda r: r['fra_o15']),
    ('Franca Under 1.5 golos 1.a parte', 1.33, lambda r: r['fra_u15_1h']),
    ('Franca/Empate & Under 3.5', 1.44, lambda r: r['fra_dc_u35']),
    ('Under 3.5 golos total', 1.44, lambda r: r['u35_total']),
    ('Franca nao vence ambas (Nao)', 1.43, lambda r: r['fra_not_both']),
    ('BTTS Nao', 1.48, lambda r: not r['btts']),
    ('Franca/Empate & BTTS Nao', 1.54, lambda r: r['fra_dc_btts_no']),
    ('BTTS ou Over 2.5 Sim', 1.50, lambda r: r['btts_or_o25']),
    ('Paraguai/Fra & Under 3.5', 1.56, lambda r: r['pf_dc_u35']),
    ('Under 2.5 golos total', 2.12, lambda r: r['u25']),
    ('Franca/Empate & Under 2.5', 2.03, lambda r: r['fra_dc_u25']),
    ('Paraguai Under 0.5 golos', 1.52, lambda r: r['par_u05']),
    ('Franca -1 handicap', 1.55, lambda r: r['fra_hcp_m1']),
    ('Mbappe SuperSub marca', 1.45, lambda r: r['fra_o15']),  # proxy ~FRA scores 2+
    ('Prolongamento Nao', 1.07, lambda r: r['no_et']),
    ('Franca qualifica', 1.06, lambda r: r['qual'] == 'F'),
]

print("\nBETCLIC CANDIDATES @ 1.30-1.50:")
rows = []
for name, odd, fn in candidates:
    if not (1.30 <= odd <= 1.50):
        continue
    p = pct(fn)
    lo, hi = ci(p)
    impl = 100 / odd
    flag = "PASS75" if p >= 75 else "----"
    rows.append((p, name, odd, lo, hi, impl, flag))
    print(f"  {name:38s} @{odd:.2f} M:{p:5.1f}% [{lo:.0f}-{hi:.0f}] impl:{impl:.1f}% {flag}")

rows.sort(reverse=True)
if rows:
    print(f"\n>>> TOP: {rows[0][1]} @{rows[0][2]:.2f} — {rows[0][0]:.1f}%")

print("\nFORA DA GAMA / 2.00+:")
for name, odd, fn in candidates:
    if 1.30 <= odd <= 1.50:
        continue
    p = pct(fn)
    if odd >= 2.0 or odd < 1.30:
        print(f"  {name:38s} @{odd:.2f} M:{p:5.1f}%")

sc = Counter((r['f90'], r['p90']) for r in res)
print("\nTOP SCORES (90m):")
for (f, p), n in sc.most_common(12):
    print(f"  {f}-{p}: {n/N*100:.1f}%")

print("\nGAME SCRIPTS:")
print(f"  FRA clean sheet:     {pct(lambda r: r['fra_cs']):.1f}%")
print(f"  PAR scores:          {pct(lambda r: r['p90']>0):.1f}%")
print(f"  Low (U2.5):          {pct(lambda r: r['u25']):.1f}%")
print(f"  Open (O2.5):         {pct(lambda r: r['tg']>2.5):.1f}%")
print(f"  FRA wins both halves:{pct(lambda r: r['fra_wins_both']):.1f}%")
