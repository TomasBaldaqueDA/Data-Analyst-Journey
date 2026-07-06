#!/usr/bin/env python3
"""Ensemble MC: USA vs Belgium — WC2026 R16, 07/07/2026 Lumen Field Seattle."""

import math
import random
from collections import Counter

random.seed(20260707)
N = 100_000

# Calibration sources: Betclic odds, FIFA ranks, home Seattle, WC knockout
# Market 90': USA 2.52 / Draw 3.37 / BEL 2.82 → USA ~38%, Draw ~28%, BEL ~34%
# Lumen Field home advantage material; Belgium #9 talent vs USA #17 + Pochettino
# Correct score market favours 1-1; moderate scoring expected

LAMBDAS = [
    (1.38, 1.22),   # xG + Seattle home (Pulisic, crowd, travel edge for BEL)
    (1.32, 1.28),   # market-implied de-vigged
    (1.25, 1.18),   # knockout regression
    (1.30, 1.35),   # Belgium quality / Courtois contrarian
]
WEIGHTS = [0.35, 0.30, 0.20, 0.15]

PEN_USA = 0.52  # home crowd penalty shootout edge
HOME_ET_BOOST = 1.08

CORNER_MEANS = [(4.8, 4.6), (5.2, 4.2), (4.5, 5.0)]
CORNER_W = [0.40, 0.35, 0.25]

SOT_MEANS = [(4.2, 4.0), (4.5, 3.8), (3.8, 4.3)]
SOT_W = [0.40, 0.35, 0.25]


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def pick_lambda():
    i = random.choices(range(len(LAMBDAS)), weights=WEIGHTS, k=1)[0]
    ux, bx = LAMBDAS[i]
    kf = random.gauss(0.91, 0.04)
    home = random.gauss(1.06, 0.03)  # Seattle variance
    return max(0.30, ux * kf * home * random.gauss(1.0, 0.07)), max(0.30, bx * kf * random.gauss(1.0, 0.07))


def simulate_match():
    ux, bx = pick_lambda()
    u90, b90 = poisson(ux), poisson(bx)
    u1, b1 = poisson(ux * 0.43), poisson(bx * 0.41)
    u2, b2 = poisson(ux * 0.57), poisson(bx * 0.59)
    tg1 = u1 + b1
    tg2 = u2 + b2
    res90 = 'U' if u90 > b90 else ('B' if b90 > u90 else 'D')
    res1 = 'U' if u1 > b1 else ('B' if b1 > u1 else 'D')
    res2 = 'U' if u2 > b2 else ('B' if b2 > u2 else 'D')

    uet = bet = 0
    qual = res90
    if res90 == 'D':
        uet = poisson(ux * 0.36 * HOME_ET_BOOST)
        bet = poisson(bx * 0.36)
        ut, bt = u90 + uet, b90 + bet
        if ut > bt:
            qual = 'U'
        elif bt > ut:
            qual = 'B'
        else:
            qual = 'U' if random.random() < PEN_USA else 'B'

    tg = u90 + b90
    usa_wins_both = res1 == 'U' and res2 == 'U'
    bel_wins_both = res1 == 'B' and res2 == 'B'

    return {
        'u90': u90, 'b90': b90, 'tg': tg,
        'u1': u1, 'b1': b1, 'u2': u2, 'b2': b2,
        'tg1': tg1, 'tg2': tg2,
        'res90': res90, 'qual': qual,
        'res1': res1, 'res2': res2,
        'btts': u90 > 0 and b90 > 0,
        'u_o05': u90 >= 1, 'b_o05': b90 >= 1,
        'u_u15': u90 <= 1, 'b_u15': b90 <= 1,
        'x2_usa': res90 in ('U', 'D'),
        'x2_bel': res90 in ('B', 'D'),
        'x12': res90 in ('U', 'B'),
        'usa_dnb': res90 == 'U',
        'bel_dnb': res90 == 'B',
        'usa_qual': qual == 'U',
        'bel_qual': qual == 'B',
        'usa_handicap_p1': res90 in ('U', 'D'),  # USA +1
        'bel_handicap_p1': res90 in ('B', 'D'),  # BEL +1
        'bel_handicap_p1_1h': res1 in ('B', 'D'),
        'usa_not_both': not usa_wins_both,
        'bel_not_both': not bel_wins_both,
        'usa_win_either': res1 == 'U' or res2 == 'U',
        'bel_win_either': res1 == 'B' or res2 == 'B',
        'o05': tg >= 1, 'o15': tg >= 2, 'o25': tg >= 3,
        'u15': tg <= 1, 'u25': tg <= 2, 'u35': tg <= 3, 'u45': tg <= 4,
        'tg1_o05': tg1 >= 1, 'tg1_u15': tg1 <= 1,
        'tg2_u15': tg2 <= 1,
        'btts_or_o25': (u90 > 0 and b90 > 0) or tg >= 3,
        'usa_o05_2h': u2 >= 1,
        'bel_o05_2h': b2 >= 1,
        'u1_u15_1h': u1 <= 1,
        'b1_u05_1h': b1 == 0,
    }


def simulate_corners():
    i = random.choices(range(len(CORNER_MEANS)), weights=CORNER_W, k=1)[0]
    um, bm = CORNER_MEANS[i]
    noise = random.gauss(1.0, 0.11)
    uc = poisson(max(2.0, um * noise))
    bc = poisson(max(2.0, bm * noise))
    tc = uc + bc
    if random.random() < 0.25:
        tc += poisson(1.6)
        uc += poisson(0.8)
        bc += poisson(0.8)
    return {'uc': uc, 'bc': bc, 'tc': tc}


def simulate_sot():
    i = random.choices(range(len(SOT_MEANS)), weights=SOT_W, k=1)[0]
    us, bs = SOT_MEANS[i]
    noise = random.gauss(1.0, 0.10)
    usot = poisson(max(1.5, us * noise))
    bsot = poisson(max(1.5, bs * noise))
    return {'us': usot, 'bs': bsot, 'ts': usot + bsot}


res = [simulate_match() for _ in range(N)]
corners = [simulate_corners() for _ in range(N)]
sots = [simulate_sot() for _ in range(N)]


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


MARKETS = [
    ('Under 3.5 golos — 90\'', 1.45, lambda r: r['u35'], 10),
    ('Under 1.5 golos — 1.ª parte', 1.44, lambda r: r['tg1_u15'], 14),
    ('BTTS ou Acima 2.5 — Sim', 1.35, lambda r: r['btts_or_o25'], 18),
    ('BTTS — Sim', 1.47, lambda r: r['btts'], 22),
    ('EUA (+1) handicap', 1.40, lambda r: r['usa_handicap_p1'], 12),
    ('Bélgica (+1) handicap', 1.48, lambda r: r['bel_handicap_p1'], 12),
    ('Bélgica (+1) handicap — 1.ª parte', 1.31, lambda r: r['bel_handicap_p1_1h'], 16),
    ('EUA não vence ambas as partes — Não', 1.04, lambda r: r['usa_not_both'], 5),
    ('Bélgica não vence ambas as partes — Não', 1.03, lambda r: r['bel_not_both'], 5),
    ('Bélgica ganha uma das partes — Sim', 1.65, lambda r: r['bel_win_either'], 18),
    ('EUA Over 0.5 golos — 2.ª parte', 1.50, lambda r: r['usa_o05_2h'], 18),
    ('Acima 0.5 golos — 1.ª parte', 1.28, lambda r: r['tg1_o05'], 14),
    ('EUA Abaixo 1.5 golos', 1.68, lambda r: r['u_u15'], 14),
    ('Bélgica Abaixo 1.5 golos', 1.60, lambda r: r['b_u15'], 14),
]

CORNER_MARKETS = [
    ('EUA cantos Acima 4.5', 1.40, lambda c: c['uc'] > 4.5, 30),
    ('Bélgica cantos Acima 4.5', 1.45, lambda c: c['bc'] > 4.5, 30),
    ('Total cantos Acima 9.5', 1.28, lambda c: c['tc'] > 9.5, 28),
]

SOT_MARKETS = [
    ('Total remates à baliza Abaixo 10.5', 1.48, lambda s: s['ts'] < 10.5, 26),
    ('EUA remates à baliza Abaixo 5.5', 1.42, lambda s: s['us'] < 5.5, 24),
    ('Bélgica remates à baliza Abaixo 5.5', 1.32, lambda s: s['bs'] < 5.5, 24),
]

print('=' * 95)
print('USA vs BELGIUM — ENSEMBLE MC N=100,000 | WC2026 R16 | Lumen Field 07/07/2026')
print('=' * 95)

uw = pct(lambda r: r['res90'] == 'U')
dw = pct(lambda r: r['res90'] == 'D')
bw = pct(lambda r: r['res90'] == 'B')
print(f"90' Result: USA {uw:.1f}% | Draw {dw:.1f}% | Belgium {bw:.1f}%")
print(f"USA qualify: {pct(lambda r: r['usa_qual']):.1f}% | Belgium qualify: {pct(lambda r: r['bel_qual']):.1f}%")
print(f"Avg goals: USA {sum(r['u90'] for r in res)/N:.2f} | BEL {sum(r['b90'] for r in res)/N:.2f} | Total {sum(r['tg'] for r in res)/N:.2f}")
print(f"BTTS: {pct(lambda r: r['btts']):.1f}% | O2.5: {pct(lambda r: r['o25']):.1f}% | U2.5: {pct(lambda r: r['u25']):.1f}% | U3.5: {pct(lambda r: r['u35']):.1f}% | U4.5: {pct(lambda r: r['u45']):.1f}%")

sc = Counter((r['u90'], r['b90']) for r in res)
print('\nTOP SCORELINES (90\'):')
for (u, b), c in sc.most_common(10):
    print(f'  {u}-{b}: {c/N*100:.1f}%')

d1 = Counter(r['tg1'] for r in res)
print('\n1ST HALF GOAL DISTRIBUTION:')
for g in sorted(d1):
    print(f'  {g} golos 1H: {d1[g]/N*100:.1f}%')

rows = []
for name, odd, fn, struct in MARKETS:
    if odd < 1.30 or odd > 1.50:
        continue
    p = pct(fn)
    lo, hi = ci(p)
    impl = 100 / odd
    risk, vol, conf = scores(struct, p, odd)
    rows.append((p, name, odd, lo, hi, impl, risk, vol, conf, p >= 75))

for name, odd, fn, struct in CORNER_MARKETS:
    if odd < 1.30 or odd > 1.50:
        continue
    p = sum(1 for c in corners if fn(c)) / N * 100
    lo, hi = ci(p)
    impl = 100 / odd
    risk, vol, conf = scores(struct, p, odd)
    rows.append((p, name, odd, lo, hi, impl, risk, vol, conf, p >= 75))

for name, odd, fn, struct in SOT_MARKETS:
    if odd < 1.30 or odd > 1.50:
        continue
    p = sum(1 for s in sots if fn(s)) / N * 100
    lo, hi = ci(p)
    impl = 100 / odd
    risk, vol, conf = scores(struct, p, odd)
    rows.append((p, name, odd, lo, hi, impl, risk, vol, conf, p >= 75))

rows.sort(reverse=True)
print('\nBETCLIC RANGE 1.30-1.50 — RANKING')
print(f"{'#':<3} {'Market':<42} {'Odd':>5} {'Model':>7} {'CI95':>12} {'Impl':>6} {'Risk':>5} {'Vol':>5} {'Conf':>5} {'75%':>5}")
for i, r in enumerate(rows, 1):
    p, name, odd, lo, hi, impl, risk, vol, conf, ok = r
    print(f"{i:<3} {name:<42} {odd:>5.2f} {p:>6.1f}% [{lo:.0f}-{hi:.0f}] {impl:>5.1f}% {risk:>5} {vol:>5} {conf:>5} {'YES' if ok else 'NO':>5}")

pass75 = [r for r in rows if r[9]]
print(f'\nPASS75: {len(pass75)}')
for r in pass75:
    print(f"  ★ {r[1]} @ {r[2]:.2f} → {r[0]:.1f}%")

if pass75:
    best = pass75[0]
    print(f'\nBEST BET: {best[1]} @ {best[2]:.2f} | Model {best[0]:.1f}% | Implied {best[5]:.1f}%')
else:
    print('\nNO BET — no market in 1.30-1.50 reaches 75% model probability')
