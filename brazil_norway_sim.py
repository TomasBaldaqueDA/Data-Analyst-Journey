#!/usr/bin/env python3
"""Monte Carlo: Brazil vs Norway — WC 2026 R16 @ MetLife / East Rutherford."""

import random
import math
from collections import Counter

random.seed(20260705)
N = 25000

# Market calibration (Opta/bet365 05/07): BRA ~52% / Draw ~25% / NOR ~23% · O2.5 ~60%
# Brazil 2-1 Japan (slow 1H); Norway 2-1 CIV (Haaland); analysts lean BTTS + O2.5
bra_xg = 1.70
nor_xg = 1.06


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate():
    b90 = poisson(bra_xg)
    n90 = poisson(nor_xg)
    b1 = poisson(bra_xg * 0.44)
    n1 = poisson(nor_xg * 0.42)

    r90 = 'D' if b90 == n90 else ('B' if b90 > n90 else 'N')
    bt, nt = b90, n90
    et = False
    qual = r90

    if r90 == 'D':
        et = True
        bet = poisson(bra_xg * 0.30)
        net = poisson(nor_xg * 0.28)
        bt, nt = b90 + bet, n90 + net
        if bt == nt:
            qual = 'B' if random.random() < 0.68 else 'N'
        elif bt > nt:
            qual = 'B'
        else:
            qual = 'N'

    tg = bt + nt
    b2 = max(0, b90 - b1)
    n2 = max(0, n90 - n1)
    tg_2h = b2 + n2
    tg_1h = b1 + n1

    bra_wins_ht = b1 > n1
    nor_wins_ht = n1 > b1
    bra_wins_2h = b2 > n2
    nor_wins_2h = n2 > b2
    bra_wins_both = bra_wins_ht and bra_wins_2h and b90 > n90
    nor_wins_both = nor_wins_ht and nor_wins_2h and n90 > b90
    nor_wins_one = nor_wins_ht or nor_wins_2h

    return {
        'r90': r90, 'qual': qual, 'b90': b90, 'n90': n90, 'bt': bt, 'nt': nt,
        'b1': b1, 'n1': n1, 'b2': b2, 'n2': n2, 'tg': tg, 'et': et,
        'btts': bt > 0 and nt > 0,
        'btts_90': b90 > 0 and n90 > 0,
        'u25': tg <= 2.5,
        'u35': tg <= 3.5,
        'u45': tg <= 4.5,
        'o25': tg > 2.5,
        'bra_ml': r90 == 'B',
        'bra_qual': qual == 'B',
        'nor_ml': qual == 'N',
        'bra_dc': r90 in ('B', 'D'),
        'nor_dc': r90 in ('N', 'D'),
        'bra_dc_u35': r90 in ('B', 'D') and tg <= 3.5,
        'bra_dc_u45': r90 in ('B', 'D') and tg <= 4.5,
        'nor_dc_u35': r90 in ('N', 'D') and tg <= 3.5,
        'bra_wins_both': bra_wins_both,
        'nor_wins_both': nor_wins_both,
        'bra_not_both': not bra_wins_both,
        'nor_not_both': not nor_wins_both,
        'nor_wins_one': nor_wins_one,
        'bra_o15': b90 >= 2,
        'bra_o15_ft': bt >= 2,
        'u15_1h': tg_1h <= 1.5,
        'u15_2h': tg_2h <= 1.5,
        'no_et': not et,
        'bra_cs': nt == 0,
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
print("BRAZIL vs NORWAY — 25,000 MC (recalibrated 05/07)")
print(f"xG/90: BRA {bra_xg:.2f} | NOR {nor_xg:.2f}")
print("=" * 72)
print(f"90m  BRA:{pct(lambda r:r['r90']=='B'):.1f}% Draw:{pct(lambda r:r['r90']=='D'):.1f}% NOR:{pct(lambda r:r['r90']=='N'):.1f}%")
print(f"Qualify BRA:{pct(lambda r:r['bra_qual']):.1f}% NOR:{pct(lambda r:r['nor_ml']):.1f}%")

# Odds: Betclic where known; other books as reference (confirm Betclic live)
candidates = [
    ('Brasil nao vence ambas (Nao)', 1.42, lambda r: r['bra_not_both']),
    ('Noruega nao vence ambas (Nao)', 1.44, lambda r: r['nor_not_both']),
    ('Brasil qualifica (Para classificar)', 1.44, lambda r: r['bra_qual']),
    ('Under 3.5 golos total', 1.40, lambda r: r['u35']),
    ('Brasil/Empate & Under 4.5', 1.32, lambda r: r['bra_dc_u45']),
    ('Brasil/Empate & Under 3.5', 1.38, lambda r: r['bra_dc_u35']),
    ('Under 1.5 golos 1.a parte', 1.43, lambda r: r['u15_1h']),
    ('Noruega ganha uma das partes (Sim)', 1.46, lambda r: r['nor_wins_one']),
    ('Brasil/Empate (DC)', 1.28, lambda r: r['bra_dc']),
    ('BTTS Sim', 1.75, lambda r: r['btts']),
    ('Over 2.5 golos', 1.80, lambda r: r['o25']),
    ('Brasil ML 90m', 1.88, lambda r: r['bra_ml']),
    ('Prolongamento Nao', 1.22, lambda r: r['no_et']),
    ('Under 2.5 golos total', 2.20, lambda r: r['u25']),
]

print("\nBETCLIC / MERCADO @ 1.30-1.50:")
rows = []
for name, odd, fn in candidates:
    if not (1.30 <= odd <= 1.50):
        continue
    p = pct(fn)
    lo, hi = ci(p)
    impl = 100 / odd
    edge = p - impl
    flag = "PASS75" if p >= 75 else "----"
    rows.append((p, name, odd, lo, hi, impl, edge, flag))
    print(f"  {name:38s} @{odd:.2f} M:{p:5.1f}% [{lo:.0f}-{hi:.0f}] impl:{impl:.1f}% edge:{edge:+.1f} {flag}")

rows.sort(reverse=True)
pass75 = [r for r in rows if r[0] >= 75]
print(f"\n>>> TOP: {rows[0][1]} @{rows[0][2]:.2f} — {rows[0][0]:.1f}%")
if pass75:
    print(f">>> PASS75 ({len(pass75)}):")
    for r in pass75:
        print(f"    {r[1]} @{r[2]:.2f} — {r[0]:.1f}%")
else:
    print(">>> NENHUM PASS75 na gama 1.30-1.50 → NO BET ou esperar MEX/ENG")

print("\nCONVICTION (fora regra 75%):")
for name, odd, fn in candidates:
    p = pct(fn)
    if name in ('Brasil qualifica (Para classificar)', 'Brasil ML 90m', 'BTTS Sim', 'Over 2.5 golos'):
        print(f"  {name:38s} @{odd:.2f} M:{p:5.1f}%")

sc = Counter((r['b90'], r['n90']) for r in res)
print("\nTOP SCORES (90m):")
for (b, n), cnt in sc.most_common(8):
    print(f"  {b}-{n}: {cnt/N*100:.1f}%")

print("\nGAME SCRIPTS:")
print(f"  U3.5:                {pct(lambda r: r['u35']):.1f}%")
print(f"  O2.5:                {pct(lambda r: r['o25']):.1f}%")
print(f"  BTTS:                {pct(lambda r: r['btts']):.1f}%")
print(f"  BRA wins both halves:{pct(lambda r: r['bra_wins_both']):.1f}%")
