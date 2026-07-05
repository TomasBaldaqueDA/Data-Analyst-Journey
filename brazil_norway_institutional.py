#!/usr/bin/env python3
"""Institutional MC: Brazil vs Norway — Betclic odds 05/07/2026."""

import random
import math
from collections import Counter

random.seed(20260705)
N = 25000

# Calibrated: Betclic 1X2 BRA 1.80 / Draw 3.58 / NOR 4.65 + O2.5 ~1.59 market
bra_xg = 1.70
nor_xg = 1.06
# Haaland/Vini scorer prop: P(at least one scores) ~88% (tournament rates)
P_STAR_SCORES = 0.88


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
    tg_1h = b1 + n1
    tg_2h = b2 + n2

    bra_wins_ht = b1 > n1
    nor_wins_ht = n1 > b1
    bra_wins_2h = b2 > n2
    nor_wins_2h = n2 > b2
    bra_wins_both = bra_wins_ht and bra_wins_2h and b90 > n90
    nor_wins_both = nor_wins_ht and nor_wins_2h and n90 > b90
    bra_wins_one = bra_wins_ht or bra_wins_2h
    nor_wins_one = nor_wins_ht or nor_wins_2h

    star_scores = (b90 > 0 or n90 > 0) and random.random() < P_STAR_SCORES

    return {
        'r90': r90, 'qual': qual, 'b90': b90, 'n90': n90, 'bt': bt, 'nt': nt,
        'b1': b1, 'n1': n1, 'b2': b2, 'n2': n2, 'tg': tg, 'et': et,
        'btts': bt > 0 and nt > 0,
        'u25': tg <= 2.5, 'u35': tg <= 3.5, 'u45': tg <= 4.5,
        'o15': tg >= 2, 'o25': tg > 2.5,
        'bra_ml': r90 == 'B', 'bra_qual': qual == 'B',
        'bra_dc': r90 in ('B', 'D'),
        'bra_dc_u45': r90 in ('B', 'D') and tg <= 4.5,
        'bra_dc_o15': r90 in ('B', 'D') and tg >= 2,
        'bra_not_both': not bra_wins_both,
        'nor_not_both': not nor_wins_both,
        'bra_wins_one': bra_wins_one,
        'nor_not_wins_one': not nor_wins_one,
        'bra_dnb_1h': b1 > n1,
        'bra_dnb_2h': b2 > n2,
        'u15_1h': tg_1h <= 1.5,
        'nor_u05_1h': n1 == 0,
        'bra_o05_2h': b2 >= 1,
        'nor_o05': n90 >= 1,
        'nor_u15': n90 <= 1,
        'bra_u25_team': b90 <= 2,
        'bn_win': r90 in ('B', 'N'),
        'bn_u45': r90 in ('B', 'N') and tg <= 4.5,
        'bn_o15': r90 in ('B', 'N') and tg >= 2,
        'nor_hcp2': (n90 + 2) > b90,
        'btts_or_o25': (bt > 0 and nt > 0) or tg > 2.5,
        'star_scores': star_scores,
        'no_et': not et,
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


def risk_scores(p, odd, market_type):
    """Lower risk = structurally stable + high p. Returns risk, vol, conf 0-100."""
    impl = 100 / odd
    struct = {'dc': 15, 'under': 25, 'half': 30, 'qual': 45, 'prop': 70, 'btts': 55}.get(market_type, 50)
    vol = max(0, min(100, 100 - p + struct * 0.3))
    risk = max(0, min(100, vol + (100 - p) * 0.5))
    conf = max(0, min(100, p - abs(p - impl) * 0.3 - struct * 0.2))
    return round(risk), round(vol), round(conf)


res = [simulate() for _ in range(N)]

# Betclic odds from user screenshots 05/07/2026
BETCLIC = [
    ('Noruega nao vence ambas (Nao)', 1.01, 'bra_not_both', 'dc'),  # ref only
    ('Brasil nao vence ambas (Nao)', 1.12, 'bra_not_both', 'dc'),
    ('Brasil ganha uma das partes (Sim)', 1.31, 'bra_wins_one', 'half'),
    ('Brasil DNB 1.a parte', 1.30, 'bra_dnb_1h', 'dc'),
    ('Brasil DNB 2.a parte', 1.33, 'bra_dnb_2h', 'dc'),
    ('Noruega ganha uma das partes (Nao)', 1.41, 'nor_not_wins_one', 'half'),
    ('Brasil qualifica', 1.34, 'bra_qual', 'qual'),
    ('Brasil/Empate & Over 1.5', 1.33, 'bra_dc_o15', 'dc'),
    ('Brasil/Empate & Under 4.5', 1.33, 'bra_dc_u45', 'dc'),
    ('Noruega +2 handicap', 1.35, 'nor_hcp2', 'dc'),
    ('BTTS ou Over 2.5 (Sim)', 1.38, 'btts_or_o25', 'btts'),
    ('Brasil Over 0.5 2.a parte', 1.38, 'bra_o05_2h', 'half'),
    ('Under 3.5 total', 1.44, 'u35', 'under'),
    ('Brasil/Noruega & Over 1.5', 1.42, 'bn_o15', 'dc'),
    ('Under 1.5 1.a parte', 1.42, 'u15_1h', 'under'),
    ('Brasil nao vence ambas (est.)', 1.42, 'bra_not_both', 'dc'),
    ('Brasil/Noruega & Under 4.5', 1.48, 'bn_u45', 'dc'),
    ('Noruega Under 0.5 1.a parte', 1.45, 'nor_u05_1h', 'under'),
    ('Vini Jr ou Haaland marca', 1.46, 'star_scores', 'prop'),
    ('Noruega Over 0.5 golos', 1.37, 'nor_o05', 'half'),
    ('Noruega Under 1.5 golos', 1.33, 'nor_u15', 'under'),
    ('Brasil Under 2.5 golos equipa', 1.31, 'bra_u25_team', 'under'),
]

print("=" * 80)
print("BRAZIL vs NORWAY — INSTITUTIONAL MC")
print(f"N={N} | xG BRA {bra_xg} NOR {nor_xg}")
print("=" * 80)
print(f"90m  BRA:{pct(lambda r:r['r90']=='B'):.1f}% D:{pct(lambda r:r['r90']=='D'):.1f}% NOR:{pct(lambda r:r['r90']=='N'):.1f}%")
print(f"Qual BRA:{pct(lambda r:r['bra_qual']):.1f}% | U3.5:{pct(lambda r:r['u35']):.1f}% O2.5:{pct(lambda r:r['o25']):.1f}% BTTS:{pct(lambda r:r['btts']):.1f}%")

print("\nBETCLIC @ 1.30-1.50 — FULL RANKING:")
rows = []
for name, odd, key, mtype in BETCLIC:
    if not (1.30 <= odd <= 1.50):
        continue
    fn = lambda r, k=key: r[k]
    p = pct(fn)
    lo, hi = ci(p)
    impl = 100 / odd
    risk, vol, conf = risk_scores(p, odd, mtype)
    pass75 = p >= 75
    rows.append((p, name, odd, lo, hi, impl, risk, vol, conf, pass75, mtype))

rows.sort(reverse=True)
print(f"{'Rank':<5} {'Market':<42} {'Odd':>5} {'Model':>7} {'CI':>12} {'Impl':>6} {'Risk':>5} {'Vol':>5} {'Conf':>5} {'75%':>5}")
for i, r in enumerate(rows, 1):
    p, name, odd, lo, hi, impl, risk, vol, conf, pass75, _ = r
    print(f"{i:<5} {name:<42} {odd:>5.2f} {p:>6.1f}% [{lo:.0f}-{hi:.0f}] {impl:>5.1f}% {risk:>5} {vol:>5} {conf:>5} {'YES' if pass75 else 'NO':>5}")

pass75_rows = [r for r in rows if r[9]]
print(f"\nPASS75 count: {len(pass75_rows)}")
if pass75_rows:
    for r in pass75_rows[:5]:
        print(f"  {r[1]} @{r[2]:.2f} — {r[0]:.1f}% risk={r[6]}")

sc = Counter((r['b90'], r['n90']) for r in res)
print("\nSCORE DISTRIBUTION (90m):")
for (b, n), c in sc.most_common(10):
    print(f"  {b}-{n}: {c/N*100:.1f}%")

# Mode score
mode = sc.most_common(1)[0]
print(f"\nMODE SCORE: {mode[0][0]}-{mode[0][1]} ({mode[1]/N*100:.1f}%)")
