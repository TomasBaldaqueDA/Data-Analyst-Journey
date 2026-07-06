#!/usr/bin/env python3
"""Wimbledon MD QF: Heliovaara/Patten vs Andreozzi/Guinard — 07/07/2026."""

import math
import random

random.seed(20260707)
N = 100_000


def simulate_bo3_doubles(pw, p_20):
    """Best-of-3 doubles. Returns fav win, score, straight sets."""
    if random.random() > pw:
        r = random.random()
        score = '1-2' if r < 0.62 else '0-2'
        return {'fav_w': False, 'score': score, 'straight': False, 'wins_set': False}
    if random.random() < p_20:
        return {'fav_w': True, 'score': '2-0', 'straight': True, 'wins_set': True}
    return {'fav_w': True, 'score': '2-1', 'straight': False, 'wins_set': True}


def pct(res, fn):
    return sum(1 for r in res if fn(r)) / len(res) * 100


def ci(p):
    p /= 100
    z, n = 1.96, N
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


# Calibration scenarios
# Heli/Patten: #1, 2024 champs, 11-1 Wimbledon record, but 2 straight 3-setters (vulnerable)
# Andreozzi/Guinard: #8 seeds, cleaner R3 win 7-6, 6-4
SCENARIOS = [
    (0.82, 0.48, 'Base — #1 seeds, grass, H2H 1-1'),
    (0.78, 0.44, 'Conservative — 2x 3-setters + A/G #3 team'),
    (0.86, 0.52, 'Dominant — 2024 champs at home'),
    (0.76, 0.40, 'Contrarian — A/G beat them Shanghai QF'),
]

BETCLIC = {
    'ML': 1.22,
    '2-0': 1.55,      # estimate — check Betclic +15 markets
    '1st_set': 1.32,  # estimate
    'wins_set': 1.12, # estimate — likely below range
}

print('=' * 90)
print('HELIÖVAARA/PATTEN vs ANDREOZZI/GUINARD — Wimbledon MD QF | 07/07/2026 14:10')
print('=' * 90)

all_ml = []
all_20 = []
all_1st = []

for pw, p20, label in SCENARIOS:
    res = [simulate_bo3_doubles(pw, p20) for _ in range(N)]
    p_ml = pct(res, lambda r: r['fav_w'])
    p_20 = pct(res, lambda r: r['straight'])
    p_1st = p_ml * 0.84  # fav wins 1st set ~84% of match wins (doubles)
    p_wset = 1 - (1 - p_ml) - (p_ml - p_20) * 0.5  # approx wins at least 1 set
    all_ml.append(p_ml)
    all_20.append(p_20)
    all_1st.append(p_1st)
    print(f"\n{label} (pw={pw})")
    print(f"  ML: {p_ml:.1f}% | 2-0: {p_20:.1f}% | 1.º set: {p_1st:.1f}%")

# Weighted consensus
weights = [0.40, 0.30, 0.20, 0.10]
w_ml = sum(p * w for p, w in zip(all_ml, weights))
w_20 = sum(p * w for p, w in zip(all_20, weights))
w_1st = sum(p * w for p, w in zip(all_1st, weights))

print('\n' + '=' * 90)
print('WEIGHTED CONSENSUS')
print(f"  ML: {w_ml:.1f}% [range {min(all_ml):.1f}-{max(all_ml):.1f}%]")
print(f"  2-0: {w_20:.1f}% [range {min(all_20):.1f}-{max(all_20):.1f}%]")
print(f"  1.º set: {w_1st:.1f}%")

# Use base scenario for score distribution
res = [simulate_bo3_doubles(0.84, 0.50) for _ in range(N)]
from collections import Counter
sc = Counter(r['score'] for r in res if r['fav_w'])
print('\nScore distribution (fav wins):')
for s, c in sc.most_common():
    print(f"  {s}: {c/sum(sc.values())*100:.1f}%")
sc_loss = Counter(r['score'] for r in res if not r['fav_w'])
print('Score distribution (fav loses):')
for s, c in sc_loss.most_common():
    print(f"  {s}: {c/sum(sc_loss.values())*100:.1f}%")

print('\n' + '=' * 90)
print('BETCLIC ANALYSIS @ 1.30-1.50')
print('=' * 90)
markets = [
    ('Heli/Patten ML', BETCLIC['ML'], w_ml, 'ml'),
    ('Heli/Patten vence 2-0', BETCLIC['2-0'], w_20, 'set'),
    ('Heli/Patten 1.º set', BETCLIC['1st_set'], w_1st, '1st'),
]
for name, odd, prob, _ in markets:
    impl = 100 / odd
    edge = prob - impl
    in_range = '✓' if 1.30 <= odd <= 1.50 else '✗ fora gama'
    pass75 = 'YES' if prob >= 75 else 'NO'
    print(f"{name:<28} @{odd:.2f} | Model {prob:.1f}% | Impl {impl:.1f}% | Edge {edge:+.1f}pp | 75%:{pass75} | {in_range}")
