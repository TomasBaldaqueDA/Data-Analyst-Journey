#!/usr/bin/env python3
"""Monte Carlo: Canada vs Morocco — WC 2026 R16 @ NRG Stadium Houston."""

import random
import math
from collections import Counter

random.seed(20260704)
N = 25000

# Opta calibration: MAR 51.8% / Draw 25.6% / CAN 21.7% (90 min)
# Morocco WC2026: 0.8 xGA/game, 8.3 shots against
# Canada: first R16, 1-0 vs RSA late, co-host energy
CAN_ATTACK = 1.05
MAR_ATTACK = 1.25
CAN_DEFENSE = 1.05
MAR_DEFENSE = 0.82  # elite defensive tournament
KNOCKOUT = 0.92
HOME_BOOST = 1.08  # Canada co-host, Houston

can_xg = CAN_ATTACK * MAR_DEFENSE * KNOCKOUT * HOME_BOOST  # ~0.86
mar_xg = MAR_ATTACK * CAN_DEFENSE * KNOCKOUT * 0.95       # ~1.12


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate():
    c90 = poisson(can_xg)
    m90 = poisson(mar_xg)
    c1 = poisson(can_xg * 0.44)
    m1 = poisson(mar_xg * 0.42)

    r90 = 'D' if c90 == m90 else ('C' if c90 > m90 else 'M')
    ct, mt = c90, m90
    et = False
    qual = r90

    if r90 == 'D':
        et = True
        cet = poisson(can_xg * 0.28)
        met = poisson(mar_xg * 0.30)
        ct, mt = c90 + cet, m90 + met
        if ct == mt:
            qual = 'M' if random.random() < 0.58 else 'C'  # Morocco pens edge post-NED
        elif ct > mt:
            qual = 'C'
        else:
            qual = 'M'

    tg = ct + mt
    c2 = max(0, c90 - c1)
    m2 = max(0, m90 - m1)

    mar_wins_ht = m1 > c1
    can_wins_ht = c1 > m1
    mar_wins_2h = m2 > c2
    can_wins_2h = c2 > m2
    mar_wins_both = mar_wins_ht and mar_wins_2h and mt > ct

    return {
        'r90': r90, 'qual': qual, 'ct': ct, 'mt': mt, 'tg': tg,
        'c1': c1, 'm1': m1, 'et': et,
        'btts': ct > 0 and mt > 0,
        'u25': tg <= 2.5,
        'u35': tg <= 3.5,
        'mar_ml': qual == 'M',
        'mar_90': r90 == 'M',
        'can_ml': qual == 'C',
        'mar_not_both': not mar_wins_both,
        'can_not_both': not (can_wins_ht and can_wins_2h and ct > mt),
        'mar_dc_u35': r90 in ('M', 'D') and tg <= 3.5,
        'can_dc_u35': r90 in ('C', 'D') and tg <= 3.5,
        'mar_dc': r90 in ('M', 'D'),
        'can_dc': r90 in ('C', 'D'),
        'mar_u15': mt <= 1.5,
        'can_u05': ct == 0,
        'mar_u05': mt == 0,
        'o05_1h': (c1 + m1) >= 1,
        'u15_1h': (c1 + m1) <= 1.5,
        'draw_90': r90 == 'D',
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
print("CANADA vs MOROCCO — 25,000 MC")
print(f"xG/90: CAN {can_xg:.2f} | MAR {mar_xg:.2f}")
print("=" * 72)
print(f"90m  CAN:{pct(lambda r:r['r90']=='C'):.1f}% Draw:{pct(lambda r:r['r90']=='D'):.1f}% MAR:{pct(lambda r:r['r90']=='M'):.1f}%")
print(f"Qualify MAR:{pct(lambda r:r['qual']=='M'):.1f}% CAN:{pct(lambda r:r['qual']=='C'):.1f}%")

candidates = [
    ('Under 2.5 golos', 1.50, lambda r: r['u25']),
    ('Under 3.5 golos', 1.28, lambda r: r['u35']),
    ('BTTS Nao', 1.48, lambda r: not r['btts']),
    ('MAR/Empate & Under 3.5', 1.38, lambda r: r['mar_dc_u35']),
    ('CAN/Empate & Under 3.5', 1.55, lambda r: r['can_dc_u35']),
    ('MAR nao vence ambas (Nao)', 1.42, lambda r: r['mar_not_both']),
    ('CAN nao vence ambas (Nao)', 1.28, lambda r: r['can_not_both']),
    ('MAR/Empate (DC)', 1.22, lambda r: r['mar_dc']),
    ('MAR ML (TR)', 1.85, lambda r: r['mar_90']),
    ('MAR qualifica', 1.45, lambda r: r['qual'] == 'M'),
    ('Under 1.5 golos 1.ª parte', 1.40, lambda r: r['u15_1h']),
    ('Over 0.5 golos 1.ª parte', 1.35, lambda r: r['o05_1h']),
    ('MAR Under 1.5 golos equipa', 1.45, lambda r: r['mar_u15']),
    ('CAN Under 0.5 golos', 1.55, lambda r: r['can_u05']),
    ('Empate TR', 3.20, lambda r: r['draw_90']),
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

sc = Counter((r['ct'], r['mt']) for r in res)
print("\nTOP SCORES (90m):")
for (a, c), n in sc.most_common(10):
    print(f"  {a}-{c}: {n/N*100:.1f}%")

print("\nGAME SCRIPTS:")
print(f"  Low (U2.5):  {pct(lambda r: r['u25']):.1f}%")
print(f"  Open (O2.5): {pct(lambda r: r['tg']>2.5):.1f}%")
print(f"  BTTS No:     {pct(lambda r: not r['btts']):.1f}%")
