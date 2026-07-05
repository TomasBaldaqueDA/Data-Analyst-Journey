#!/usr/bin/env python3
"""Monte Carlo: Brazil vs Norway — WC 2026 R16 @ MetLife / East Rutherford."""

import random
import math
from collections import Counter

random.seed(20260705)
N = 25000

# Calibration: bet365/Betclic TR — BRA ~1.75-1.85 (54%) / Draw ~3.50 (26%) / NOR ~4.00 (22%)
# Brazil: 2-1 vs Japan (slow start); Norway: 2-1 vs CIV, Haaland 5 goals, direct attack
# Analysts lean O2.5 + BTTS — open knockout, both have elite forwards
BRA_ATTACK = 1.95
NOR_ATTACK = 1.35
BRA_DEFENSE = 0.92
NOR_DEFENSE = 0.95
KNOCKOUT = 0.96

bra_xg = BRA_ATTACK * NOR_DEFENSE * KNOCKOUT  # ~1.78
nor_xg = NOR_ATTACK * BRA_DEFENSE * KNOCKOUT  # ~1.26


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
        'bra_ml': qual == 'B',
        'bra_90': r90 == 'B',
        'nor_ml': qual == 'N',
        'bra_dc': r90 in ('B', 'D'),
        'nor_dc': r90 in ('N', 'D'),
        'bra_dc_u35': r90 in ('B', 'D') and tg <= 3.5,
        'bra_dc_u45': r90 in ('B', 'D') and tg <= 4.5,
        'nor_dc_u35': r90 in ('N', 'D') and tg <= 3.5,
        'nor_dc_u45': r90 in ('N', 'D') and tg <= 4.5,
        'bn_dc_u35': r90 in ('B', 'N') and tg <= 3.5,
        'bn_dc_u45': r90 in ('B', 'N') and tg <= 4.5,
        'bra_wins_both': bra_wins_both,
        'nor_wins_both': nor_wins_both,
        'bra_not_both': not bra_wins_both,
        'nor_not_both': not nor_wins_both,
        'nor_wins_one': nor_wins_one,
        'bra_o15': b90 >= 2,
        'nor_o05': n90 >= 1,
        'bra_u15_1h': b1 <= 1.5,
        'u15_1h': tg_1h <= 1.5,
        'u15_2h': tg_2h <= 1.5,
        'no_et': not et,
        'draw_90': r90 == 'D',
        'bra_hcp_m1': (b90 - 1) > n90,
        'nor_hcp_p1': (n90 + 1) > b90,
        'nor_hcp_p15': (n90 + 1.5) > b90,
        'nor_hcp_p2': (n90 + 2) > b90,
        'bra_cs': nt == 0,
        'nor_cs': bt == 0,
        'btts_or_o25': (b90 > 0 and n90 > 0) or tg > 2.5,
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
print("BRAZIL vs NORWAY — 25,000 MC")
print(f"xG/90: BRA {bra_xg:.2f} | NOR {nor_xg:.2f}")
print("=" * 72)
print(f"90m  BRA:{pct(lambda r:r['r90']=='B'):.1f}% Draw:{pct(lambda r:r['r90']=='D'):.1f}% NOR:{pct(lambda r:r['r90']=='N'):.1f}%")
print(f"Qualify BRA:{pct(lambda r:r['qual']=='B'):.1f}% NOR:{pct(lambda r:r['qual']=='N'):.1f}%")

# Betclic odds — confirm live before betting
candidates = [
    ('Brasil/Empate & Under 4.5', 1.32, lambda r: r['bra_dc_u45']),
    ('Brasil/Empate & Under 3.5', 1.38, lambda r: r['bra_dc_u35']),
    ('Under 3.5 golos total', 1.40, lambda r: r['u35']),
    ('Brasil nao vence ambas (Nao)', 1.42, lambda r: r['bra_not_both']),
    ('Under 1.5 golos 1.a parte', 1.43, lambda r: r['u15_1h']),
    ('Noruega nao vence ambas (Nao)', 1.44, lambda r: r['nor_not_both']),
    ('Brasil/Empate & BTTS Nao', 1.45, lambda r: r['bra_dc'] and not r['btts']),
    ('Noruega ganha uma das partes (Sim)', 1.46, lambda r: r['nor_wins_one']),
    ('Brasil/Empate (DC)', 1.28, lambda r: r['bra_dc']),
    ('Under 1.5 golos 2.a parte', 1.48, lambda r: r['u15_2h']),
    ('BTTS Nao', 1.50, lambda r: not r['btts']),
    ('Brasil/BTTS Sim', 1.50, lambda r: r['bra_dc'] and r['btts']),
    ('Noruega/Empate & Under 3.5', 1.52, lambda r: r['nor_dc_u35']),
    ('Brasil/BTTS Sim (alt)', 1.55, lambda r: r['bra_90'] and r['btts_90']),
    ('Under 2.5 golos total', 2.05, lambda r: r['u25']),
    ('Brasil -1 handicap', 2.10, lambda r: r['bra_hcp_m1']),
    ('Brasil qualifica', 1.18, lambda r: r['qual'] == 'B'),
    ('Prolongamento Nao', 1.22, lambda r: r['no_et']),
    ('Over 2.5 golos', 1.72, lambda r: r['o25']),
    ('Brasil ML', 1.78, lambda r: r['bra_90']),
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
    print(f"\n>>> TOP @1.30-1.50: {rows[0][1]} @{rows[0][2]:.2f} — {rows[0][0]:.1f}%")
    pass75 = [r for r in rows if r[0] >= 75]
    if pass75:
        print(f">>> MELHOR PASS75: {pass75[0][1]} @{pass75[0][2]:.2f} — {pass75[0][0]:.1f}%")
    else:
        print(">>> NENHUM PASS75 na gama 1.30-1.50")

print("\nFORA DA GAMA / referencia:")
for name, odd, fn in candidates:
    if 1.30 <= odd <= 1.50:
        continue
    p = pct(fn)
    print(f"  {name:38s} @{odd:.2f} M:{p:5.1f}%")

sc = Counter((r['b90'], r['n90']) for r in res)
print("\nTOP SCORES (90m):")
for (b, n), cnt in sc.most_common(12):
    print(f"  {b}-{n}: {cnt/N*100:.1f}%")

print("\nGAME SCRIPTS:")
print(f"  Low (U2.5):          {pct(lambda r: r['u25']):.1f}%")
print(f"  Open (O2.5):         {pct(lambda r: r['o25']):.1f}%")
print(f"  BTTS Yes:            {pct(lambda r: r['btts']):.1f}%")
print(f"  BRA wins both halves:{pct(lambda r: r['bra_wins_both']):.1f}%")
print(f"  NOR wins both halves:{pct(lambda r: r['nor_wins_both']):.1f}%")
