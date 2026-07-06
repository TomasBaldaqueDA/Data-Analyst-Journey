#!/usr/bin/env python3
"""Ensemble MC: Brommapojkarna vs GAIS — Allsvenskan 06/07/2026 Grimsta IP."""

import math
import random
from collections import Counter

random.seed(20260706)
N = 100_000

# Allsvenskan 2026 league baselines (WorldSoccerData / Soccerstats)
# Avg 3.04 gpg | Home 1.77 | Away 1.27 | Home win 40% | Draw 31% | Away 29% | BTTS 60%
# Brommapojkarna: 8th, 15pts, 15:16, poor HOME record (soccerstats: 2pts from home)
# GAIS: 7th, 15pts, 16:11, solid GD, away competitive
# H2H: GAIS won 0-2 Oct 2025; 1-1 Apr 2025; Brom 2-0 Oct 2024
# Injuries GAIS: Lundgren, Holmén, Hermansen out
# Referee Victor Wolf: ~3.6 Y/match, low reds — neutral intensity

LAMBDAS = [
    (1.38, 1.32),   # league home/away baseline adjusted for Brom weak home
    (1.25, 1.45),   # market-challenged: GAIS slightly overpriced
    (1.45, 1.28),   # home advantage emphasis at Grimsta
    (1.30, 1.38),   # balanced — user hypothesis
]
WEIGHTS = [0.30, 0.35, 0.20, 0.15]


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate():
    i = random.choices(range(len(LAMBDAS)), weights=WEIGHTS, k=1)[0]
    hx, dx = LAMBDAS[i]
    hx = max(0.30, hx * random.gauss(1.0, 0.09))
    dx = max(0.30, dx * random.gauss(1.0, 0.09))
    h, d = poisson(hx), poisson(dx)
    h1, d1 = poisson(hx * 0.43), poisson(dx * 0.41)
    h2, d2 = max(0, h - h1), max(0, d - d1)
    tg = h + d
    res = 'H' if h > d else ('D' if h == d else 'A')
    return {
        'h': h, 'd': d, 'tg': tg, 'res': res,
        'h1': h1, 'd1': d1, 'h2': h2, 'd2': d2,
        'tg1': h1 + d1, 'tg2': h2 + d2,
        'btts': h > 0 and d > 0,
        'h_dc': res in ('H', 'D'),
        'd_dc': res in ('A', 'D'),
        'bn12': res != 'D',
        'o15': tg >= 2, 'o25': tg >= 3, 'u25': tg <= 2,
        'u35': tg <= 3, 'u45': tg <= 4,
        'h_o05': h >= 1, 'd_o05': d >= 1,
        'g_o05': tg >= 1,
        'g_o05_1h': (h1 + d1) >= 1,
        'u15_1h': (h1 + d1) <= 1,
        'btts_nn': not (h1 > 0 and d1 > 0) and not (h2 > 0 and d2 > 0),
        'x2_u45': res in ('A', 'D') and tg <= 4,
        'bn12_u45': res != 'D' and tg <= 4,
        'bn12_u35': res != 'D' and tg <= 3,
        'x2_u45_alt': res in ('A', 'D') and tg <= 4,
        'g_o05_2h': (h2 + d2) >= 1,
    }


res = [simulate() for _ in range(N)]


def pct(fn):
    if callable(fn):
        return sum(1 for r in res if fn(r)) / N * 100
    return sum(1 for r in res if r[fn]) / N * 100


def ci(p):
    p /= 100
    z = 1.96
    d = 1 + z * z / N
    c = (p + z * z / (2 * N)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * N)) / N) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


def scores(struct, p, odd):
    impl = 100 / odd
    vol = max(0, min(100, 100 - p + struct * 0.35))
    risk = max(0, min(100, vol + (100 - p) * 0.45))
    conf = max(0, min(100, p - abs(p - impl) * 0.25 - struct * 0.15))
    return round(risk), round(vol), round(conf)


# REAL BETCLIC ODDS from user screenshots
MARKETS = [
    ('Under 3.5 golos', 1.30, 'u35', 12),
    ('Empate ou GAIS (X2)', 1.35, 'd_dc', 12),
    ('GAIS +1 handicap (vitória EH)', 1.35, lambda r: (r['d'] + 1) > r['h'], 15),
    ('GAIS/Empate & Under 4.5', 1.40, 'x2_u45', 18),
    ('Brom/GAIS & Under 4.5 (12+U4.5)', 1.42, 'bn12_u45', 18),
    ('BTTS ou Over 2.5 Sim', 1.42, lambda r: r['btts'] or r['o25'], 25),
    ('Over 0.5 golos 1.ª parte', 1.30, 'g_o05_1h', 18),
    ('Under 1.5 golos 1.ª parte', 1.36, 'u15_1h', 20),
    ('Brom/GAIS & Over 1.5', 1.54, lambda r: r['bn12'] and r['o15'], 20),
    ('Brommapojkarna 1X', 1.57, 'h_dc', 12),
    ('BTTS Sim', 1.58, 'btts', 35),
    ('Over 2.5 golos', 1.67, 'o25', 30),
    ('Under 2.5 golos', 1.78, 'u25', 22),
    ('Under 4.5 golos', 1.09, 'u45', 8),
    ('Over 1.5 golos', 1.19, 'o15', 10),
    ('GAIS Over 0.5', 1.19, 'd_o05', 12),
    ('Brom Over 0.5', 1.26, 'h_o05', 12),
    ('BTTS Não/Não ambas partes', 1.54, 'btts_nn', 40),
]

print('=' * 92)
print('BROmmapojkarna vs GAIS — ENSEMBLE MC N=100,000 | 06/07/2026 Grimsta IP')
print('=' * 92)
print(f"Brom W/D/L: {pct(lambda r:r['res']=='H'):.1f}% / {pct(lambda r:r['res']=='D'):.1f}% / {pct(lambda r:r['res']=='A'):.1f}%")
print(f"Avg goals: Brom {sum(r['h'] for r in res)/N:.2f} | GAIS {sum(r['d'] for r in res)/N:.2f} | Total {sum(r['tg'] for r in res)/N:.2f}")
print(f"BTTS: {pct('btts'):.1f}% | O2.5: {pct('o25'):.1f}% | U2.5: {pct('u25'):.1f}% | U3.5: {pct('u35'):.1f}% | U4.5: {pct('u45'):.1f}%")

sc = Counter((r['h'], r['d']) for r in res)
print('\nTOP SCORELINES:')
for (h, d), c in sc.most_common(8):
    print(f'  {h}-{d}: {c/N*100:.1f}%')

rows = []
for name, odd, key, struct in MARKETS:
    p = pct(key)
    lo, hi = ci(p)
    impl = 100 / odd
    risk, vol, conf = scores(struct, p, odd)
    rows.append((p, name, odd, lo, hi, impl, risk, vol, conf, p >= 75, p - impl))

rows.sort(reverse=True)
print('\nBETCLIC — FULL RANKING')
print(f"{'#':<3} {'Market':<40} {'Odd':>5} {'Model':>7} {'CI':>11} {'Impl':>6} {'Edge':>7} {'Conf':>5} {'75%':>5}")
for i, r in enumerate(rows, 1):
    p, name, odd, lo, hi, impl, risk, vol, conf, ok, edge = r
    print(f"{i:<3} {name:<40} {odd:>5.2f} {p:>6.1f}% [{lo:.0f}-{hi:.0f}] {impl:>5.1f}% {edge:>+6.1f}pp {conf:>5} {'YES' if ok else 'NO':>5}")

print('\n--- RANGE 1.30-1.50 ---')
rng = [r for r in rows if 1.30 <= r[2] <= 1.50]
for i, r in enumerate(rng, 1):
    p, name, odd = r[0], r[1], r[2]
    print(f'{i}. {name} @{odd:.2f} — {p:.1f}% — PASS75: {"YES" if r[9] else "NO"}')

pass75 = [r for r in rng if r[9]]
print(f'\nPASS75 in 1.30-1.50: {len(pass75)}')
for r in pass75:
    print(f'  >> {r[1]} @{r[2]:.2f} — {r[0]:.1f}% conf={r[8]}')
