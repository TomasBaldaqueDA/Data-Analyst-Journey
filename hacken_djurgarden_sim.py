#!/usr/bin/env python3
"""Ensemble MC: Häcken vs Djurgården — Allsvenskan 06/07/2026."""

import math
import random
from collections import Counter

random.seed(20260706)
N = 100_000

# Calibration inputs (sources: Transfermarkt, WorldSoccerData, SportsGambler, FotMob)
# Häcken: 2nd, 5W-5D-0L, 2.0 gpg / 1.4 gaa; home 2.40 gpg; unbeaten home 8
# Djurgården: 8th, 4W-1D-4L, 2.11 gpg; away 2.0 gpg / 1.33 gaa
# H2H: Djurg 16-12-7 overall; unbeaten last 6; 6-1 at this venue Jul 2025
# Injuries: Häcken missing Engdahl, Berisha, Öhman, Väisänen; Agbonifo suspended
HXG_BASE, DXG_BASE = 1.52, 1.38
HOME_ADV = 0.18
H2H_DIF = 0.12  # Djurgården tactical edge historically
HACK_INJ = -0.08

# Ensemble weights across 4 calibrated lambdas
LAMBDAS = [
    (HXG_BASE + HOME_ADV + HACK_INJ, DXG_BASE + H2H_DIF),          # xG model
    (1.48, 1.42),                                                     # market-implied (~2.45/2.70/3.50)
    (1.55, 1.35),                                                     # home/away season splits
    (1.40, 1.55),                                                     # H2H-heavy contrarian
]
WEIGHTS = [0.35, 0.30, 0.25, 0.10]


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def pick_lambda():
    i = random.choices(range(len(LAMBDAS)), weights=WEIGHTS, k=1)[0]
    hx, dx = LAMBDAS[i]
    # minor game-state noise
    return max(0.35, hx * random.gauss(1.0, 0.08)), max(0.35, dx * random.gauss(1.0, 0.08))


def simulate():
    hx, dx = pick_lambda()
    h = poisson(hx)
    d = poisson(dx)
    h1 = poisson(hx * 0.44)
    d1 = poisson(dx * 0.42)
    tg = h + d
    res = 'H' if h > d else ('D' if h == d else 'A')
    return {
        'h': h, 'd': d, 'tg': tg, 'res': res,
        'h1': h1, 'd1': d1, 'tg1': h1 + d1,
        'btts': h > 0 and d > 0,
        'h_dc': res in ('H', 'D'),
        'd_dc': res in ('A', 'D'),
        'h_o05': h >= 1,
        'd_o05': d >= 1,
        'o05': tg >= 1,
        'o15': tg >= 2,
        'o25': tg >= 3,
        'u15': tg <= 1,
        'u25': tg <= 2,
        'u35': tg <= 3,
        'u45': tg <= 4,
        'h_u15': h <= 1,
        'd_u15': d <= 1,
        'draw_ht': h1 == d1,
        'h_win_ht': h1 > d1,
    }


res = [simulate() for _ in range(N)]


def pct(fn):
    return sum(1 for r in res if fn(r)) / N * 100


def ci(p):
    p /= 100
    z = 1.96
    d = 1 + z * z / N
    c = (p + z * z / (2 * N)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * N)) / N) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


def scores(risk_struct, p, odd):
    impl = 100 / odd
    vol = max(0, min(100, 100 - p + risk_struct * 0.35))
    risk = max(0, min(100, vol + (100 - p) * 0.45))
    conf = max(0, min(100, p - abs(p - impl) * 0.25 - risk_struct * 0.15))
    return round(risk), round(vol), round(conf)


# Betclic-style markets @ 1.30-1.50 (SportsGambler / typical SE market proxy)
MARKETS = [
    ('Häcken/Empate (Dupla Hipótese 1X)', 1.38, 'h_dc', 12),
    ('BTTS Sim', 1.45, 'btts', 35),
    ('Over 1.5 golos', 1.40, 'o15', 18),
    ('Häcken Over 0.5 golos', 1.33, 'h_o05', 15),
    ('Djurgården Over 0.5 golos', 1.36, 'd_o05', 15),
    ('Under 3.5 golos', 1.42, 'u35', 20),
    ('Under 4.5 golos', 1.32, 'u45', 12),
    ('Over 0.5 golos 1.ª parte', 1.48, lambda r: r['tg1'] >= 1, 22),
    ('Empate 1.ª parte', 1.50, 'draw_ht', 28),
    ('Häcken Under 1.5 golos', 1.45, 'h_u15', 25),
    ('Djurgården Under 1.5 golos', 1.43, 'd_u15', 25),
    ('Under 2.5 golos', 1.48, 'u25', 22),
]

print('=' * 90)
print('HÄCKEN vs DJURGÅRDEN — ENSEMBLE MC N=100,000 | 06/07/2026 Nordic Wellness Arena')
print('=' * 90)
print(f"Häcken W/D/L: {pct(lambda r:r['res']=='H'):.1f}% / {pct(lambda r:r['res']=='D'):.1f}% / {pct(lambda r:r['res']=='A'):.1f}%")
print(f"Avg goals: H {sum(r['h'] for r in res)/N:.2f} | D {sum(r['d'] for r in res)/N:.2f} | Total {sum(r['tg'] for r in res)/N:.2f}")
print(f"BTTS: {pct(lambda r:r['btts']):.1f}% | O2.5: {pct(lambda r:r['o25']):.1f}% | U2.5: {pct(lambda r:r['u25']):.1f}% | U3.5: {pct(lambda r:r['u35']):.1f}%")

sc = Counter((r['h'], r['d']) for r in res)
print('\nTOP SCORELINES:')
for (h, d), c in sc.most_common(8):
    print(f'  {h}-{d}: {c/N*100:.1f}%')

rows = []
for name, odd, key, struct in MARKETS:
    if callable(key):
        fn = key
    else:
        fn = lambda r, k=key: r[k]
    p = pct(fn)
    lo, hi = ci(p)
    impl = 100 / odd
    risk, vol, conf = scores(struct, p, odd)
    rows.append((p, name, odd, lo, hi, impl, risk, vol, conf, p >= 75))

rows.sort(reverse=True)
print('\nBETCLIC RANGE 1.30-1.50 — RANKING')
print(f"{'#':<3} {'Market':<38} {'Odd':>5} {'Model':>7} {'CI95':>12} {'Impl':>6} {'Risk':>5} {'Vol':>5} {'Conf':>5} {'75%':>5}")
for i, r in enumerate(rows, 1):
    p, name, odd, lo, hi, impl, risk, vol, conf, ok = r
    print(f"{i:<3} {name:<38} {odd:>5.2f} {p:>6.1f}% [{lo:.0f}-{hi:.0f}] {impl:>5.1f}% {risk:>5} {vol:>5} {conf:>5} {'YES' if ok else 'NO':>5}")

pass75 = [r for r in rows if r[9]]
print(f'\nPASS75: {len(pass75)}')
for r in pass75:
    print(f"  >> {r[1]} @{r[2]:.2f} — {r[0]:.1f}%")
