#!/usr/bin/env python3
"""Consensus stress-test: USA vs Belgium — reconcile MC models across xG scenarios."""

import math
import random
from collections import Counter

random.seed(20260707)
N = 100_000

# Scenarios: (usa_xg, bel_xg, weight, label)
# Incorporates real intel: USA 2+ goals all WC games, BEL defensive fragility (3-2 vs SEN),
# but H2H BEL 5-2 March 2026 Atlanta + 6 straight H2H wins
SCENARIOS = [
    (1.28, 1.14, 0.25, 'MC_base (our 100k ensemble)'),
    (1.85, 1.45, 0.30, 'Alt_high_xG (research est.)'),
    (1.65, 1.65, 0.20, 'Equal_strength'),
    (1.50, 1.75, 0.15, 'BEL_favourite (H2H-weighted)'),
    (2.00, 1.30, 0.10, 'USA_dominant (home+Balogun)'),
]

PEN_USA = 0.52


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate(ux, bx, home_boost=1.06):
    ux *= home_boost
    u90, b90 = poisson(ux), poisson(bx)
    u1, b1 = poisson(ux * 0.43), poisson(bx * 0.41)
    tg = u90 + b90
    tg1 = u1 + b1
    res = 'U' if u90 > b90 else ('B' if b90 > u90 else 'D')
    margin = b90 - u90  # positive = BEL leads
    return {
        'res': res, 'tg': tg, 'tg1': tg1,
        'u90': u90, 'b90': b90,
        'usa_p1': margin < 2,              # USA +1: loses only if BEL wins by 2+
        'bel_p1': margin > -2,             # BEL +1: loses only if USA wins by 2+
        'x12': res in ('U', 'B'),
        'u35': tg <= 3,
        'u25': tg <= 2,
        'u15_1h': tg1 <= 1,
        'btts': u90 > 0 and b90 > 0,
        'bel_win_2plus': b90 - u90 >= 2,
        'usa_win_2plus': u90 - b90 >= 2,
    }


def run_scenario(ux, bx, label):
    res = [simulate(ux, bx) for _ in range(N)]

    def pct(k):
        if callable(k):
            return sum(1 for r in res if k(r)) / N * 100
        return sum(1 for r in res if r[k]) / N * 100

    sc = Counter((r['u90'], r['b90']) for r in res)
    top = sc.most_common(3)
    return {
        'label': label, 'ux': ux, 'bx': bx,
        'usa_w': pct(lambda r: r['res'] == 'U'),
        'draw': pct(lambda r: r['res'] == 'D'),
        'bel_w': pct(lambda r: r['res'] == 'B'),
        'usa_p1': pct('usa_p1'),
        'bel_p1': pct('bel_p1'),
        'x12': pct('x12'),
        'u35': pct('u35'),
        'u25': pct('u25'),
        'u15_1h': pct('u15_1h'),
        'btts': pct('btts'),
        'bel_2plus': pct('bel_win_2plus'),
        'usa_2plus': pct('usa_win_2plus'),
        'top': top,
    }


print('=' * 100)
print('USA vs BELGIUM — CONSENSUS STRESS-TEST | N=100,000 per scenario')
print('=' * 100)

results = []
for ux, bx, w, label in SCENARIOS:
    r = run_scenario(ux, bx, label)
    r['weight'] = w
    results.append(r)
    print(f"\n--- {label} (xG {ux:.2f}/{bx:.2f}) ---")
    print(f"  1X2: USA {r['usa_w']:.1f}% | Draw {r['draw']:.1f}% | BEL {r['bel_w']:.1f}%")
    print(f"  USA+1: {r['usa_p1']:.1f}% | BEL+1: {r['bel_p1']:.1f}% | 12: {r['x12']:.1f}%")
    print(f"  U3.5: {r['u35']:.1f}% | U2.5: {r['u25']:.1f}% | U1.5 1H: {r['u15_1h']:.1f}% | BTTS: {r['btts']:.1f}%")
    print(f"  BEL wins by 2+: {r['bel_2plus']:.1f}% (kills USA+1)")
    print(f"  Top scores: {', '.join(f'{u}-{b} ({c/N*100:.1f}%)' for (u,b),c in r['top'])}")

# Weighted consensus
print('\n' + '=' * 100)
print('WEIGHTED CONSENSUS (scenario weights sum to 1.0)')
print('=' * 100)
keys = ['usa_w', 'draw', 'bel_w', 'usa_p1', 'bel_p1', 'x12', 'u35', 'u25', 'u15_1h', 'btts', 'bel_2plus']
consensus = {}
for k in keys:
    consensus[k] = sum(r[k] * r['weight'] for r in results)

print(f"1X2: USA {consensus['usa_w']:.1f}% | Draw {consensus['draw']:.1f}% | BEL {consensus['bel_w']:.1f}%")
print(f"USA+1: {consensus['usa_p1']:.1f}% | BEL+1: {consensus['bel_p1']:.1f}% | 12: {consensus['x12']:.1f}%")
print(f"U3.5: {consensus['u35']:.1f}% | U2.5: {consensus['u25']:.1f}% | U1.5 1H: {consensus['u15_1h']:.1f}%")

# Betclic markets @ 1.30-1.50
MARKETS = [
    ('USA (+1) handicap', 1.40, 'usa_p1', 12),
    ('12 sem empate', 1.31, 'x12', 8),
    ('BEL (+1) handicap', 1.48, 'bel_p1', 12),
    ('Under 3.5', 1.45, 'u35', 10),
    ('Under 1.5 1H', 1.44, 'u15_1h', 14),
    ('BTTS Sim', 1.47, 'btts', 22),
]

print('\n' + '=' * 100)
print('MARKET ROBUSTNESS TABLE (Betclic 1.30-1.50)')
print('=' * 100)
print(f"{'Market':<22} {'Odd':>5} {'Cons.':>7} {'Min':>7} {'Max':>7} {'All≥75':>7} {'Edge':>7}")
rows = []
for name, odd, key, _ in MARKETS:
    probs = [r[key] for r in results]
    w = sum(p * r['weight'] for p, r in zip(probs, results))
    # weighted consensus from individual scenarios
    w2 = sum(r[key] * r['weight'] for r in results)
    mn, mx = min(probs), max(probs)
    impl = 100 / odd
    edge = w2 - impl
    ok = 'YES' if mn >= 75 else 'NO'
    rows.append((w2, mn, mx, name, odd, impl, edge, ok))
    print(f"{name:<22} {odd:>5.2f} {w2:>6.1f}% {mn:>6.1f}% {mx:>6.1f}% {ok:>7} {edge:>+6.1f}pp")

rows.sort(reverse=True)
print('\nRANKING BY WEIGHTED CONSENSUS:')
for i, (w, mn, mx, name, odd, impl, edge, ok) in enumerate(rows, 1):
    flag = ' ★PASS75 ALL SCENARIOS' if ok == 'YES' else (' ○PASS75 CONSENSUS' if w >= 75 else '')
    print(f"  {i}. {name} @ {odd:.2f} → cons. {w:.1f}% [range {mn:.1f}-{mx:.1f}%]{flag}")

# H2H adjustment note: 5-2 precedent → BEL 2+ win prob
bel_2plus_avg = consensus['bel_2plus']
print(f"\nBEL wins by 2+ (USA+1 killer): weighted avg {bel_2plus_avg:.1f}%")
print(f"H2H precedent 5-2 Atlanta Mar 2026: real outcome, model gives {results[3]['bel_2plus']:.1f}% in BEL_fav scenario")
