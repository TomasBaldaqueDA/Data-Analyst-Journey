#!/usr/bin/env python3
"""
Wimbledon 06 Jul 2026 — Day 8 full schedule Monte Carlo.
Men Bo5 / Women Bo3 / Doubles Bo3 / Mixed Bo3.
Betclic odds @ 1.30-1.50 — challenge filter ≥75%.
Sources: TennisConnected Day 8, 365scores, StatsInsider, market Jul 5-6.
"""

import random
import math

random.seed(20260706)
N = 25000


def simulate_bo5(p_win, p_30, p_31, p_32):
    if random.random() > p_win:
        r = random.random()
        if r < 0.4:
            return _bo5(False, '2-3', margin_2plus=False)
        if r < 0.7:
            return _bo5(False, '1-3', margin_2plus=False)
        return _bo5(False, '0-3', margin_2plus=False)
    r = random.random()
    if r < p_30:
        return _bo5(True, '3-0', margin_2plus=True)
    if r < p_30 + p_31:
        return _bo5(True, '3-1', margin_2plus=True)
    return _bo5(True, '3-2', margin_2plus=False)


def _bo5(fav_w, score, margin_2plus):
    return {'fav_wins': fav_w, 'score': score, 'straight': fav_w and score == '3-0',
            'margin_2plus': margin_2plus and fav_w, 'wins_set': fav_w or score in ('2-3', '1-3')}


def simulate_bo3(p_win, p_20, p_21=0.12):
    if random.random() > p_win:
        return {'fav_wins': False, 'score': '0-2' if random.random() < 0.55 else '1-2',
                'straight': False, 'margin_2plus': False, 'wins_set': False}
    if random.random() < p_20:
        return {'fav_wins': True, 'score': '2-0', 'straight': True, 'margin_2plus': True, 'wins_set': True}
    return {'fav_wins': True, 'score': '2-1', 'straight': False, 'margin_2plus': False, 'wins_set': True}


def simulate_doubles(p_win, p_20=0.52):
    return simulate_bo3(p_win, p_20, 0.10)


def pct(res, fn):
    return sum(1 for r in res if fn(r)) / len(res) * 100


def ci(p):
    p /= 100
    z, n = 1.96, N
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


def risk_scores(p, odd, mtype):
    impl = 100 / odd
    struct = {'ml': 20, 'hcap': 25, 'set': 30, '1st': 35, 'games': 45, 'prop': 65}.get(mtype, 40)
    vol = max(0, min(100, 100 - p + struct * 0.3))
    risk = max(0, min(100, vol + (100 - p) * 0.5))
    conf = max(0, min(100, p - abs(p - impl) * 0.3 - struct * 0.2))
    return round(risk), round(vol), round(conf)


# (match, fav, dog, event, pw, p_straight, p_mid, p_long, odds_dict)
# pw calibrated: rank, grass Elo, H2H, form, load, surface
MATCHES = [
    # === MEN SINGLES R16 — Mon 6 Jul ===
    ('De Minaur vs Cobolli', 'De Minaur', 'Cobolli', 'MS', 0.78, 0.38, 0.28, 0.12, {
        'ML': 1.35, '-1.5_sets': 1.48, '1st_set': 1.42, '3-0': 2.20,
    }),
    ('Fritz vs Bublik', 'Fritz', 'Bublik', 'MS', 0.65, 0.32, 0.22, 0.11, {
        'ML': 1.57, '-1.5_sets': 1.85, '1st_set': 1.72,
    }),
    ('Zverev vs Lehecka', 'Zverev', 'Lehecka', 'MS', 0.71, 0.35, 0.26, 0.10, {
        'ML': 1.41, '-1.5_sets': 1.52, '1st_set': 1.45, '3-0': 2.10,
    }),
    ('Dimitrov vs Fery', 'Dimitrov', 'Fery', 'MS', 0.72, 0.30, 0.28, 0.14, {
        'ML': 1.38, '-1.5_sets': 1.62, '1st_set': 1.40,
    }),
    # === WOMEN SINGLES R16 — Mon 6 Jul ===
    ('Kostyuk vs Krueger', 'Kostyuk', 'Krueger', 'WS', 0.74, 0.45, 0.22, 0, {
        'ML': 1.44, '2-0': 1.95, '1st_set': 1.53,
    }),
    ('Paolini vs Eala', 'Paolini', 'Eala', 'WS', 0.44, 0.18, 0.16, 0, {
        'ML': 2.30,  # Eala fav market — skip as fav pick
    }),
    ('Eala vs Paolini', 'Eala', 'Paolini', 'WS', 0.56, 0.28, 0.20, 0, {
        'ML': 1.61, '2-0': 2.40, '1st_set': 1.66,
    }),
    ('Keys vs Noskova', 'Keys', 'Noskova', 'WS', 0.58, 0.30, 0.20, 0, {
        'ML': 1.62, '2-0': 2.35, '1st_set': 1.55,
    }),
    ('Bouzkova vs Mertens', 'Bouzkova', 'Mertens', 'WS', 0.54, 0.26, 0.18, 0, {
        'ML': 1.68, '2-0': 2.50,
    }),
    # === MEN DOUBLES R3 (notable) ===
    ('Cabal/Munar vs ?', 'Cabal/Munar', 'TBD', 'MD', 0.76, 0.50, 0, 0, {
        'ML': 1.32, '2-0': 1.55,
    }),
    ('Koolhof/Skupski vs ?', 'Koolhof/Skupski', 'TBD', 'MD', 0.80, 0.52, 0, 0, {
        'ML': 1.28, '2-0': 1.48,
    }),
    ('Heliovaara/Patten vs next', 'Heli/Patten', 'TBD', 'MD', 0.82, 0.54, 0, 0, {
        'ML': 1.30, '2-0': 1.50,
    }),
    # === WOMEN DOUBLES R3 ===
    ('Siniakova/Townsend vs ?', 'Siniak/Town', 'TBD', 'WD', 0.78, 0.50, 0, 0, {
        'ML': 1.34, '2-0': 1.58,
    }),
    ('Krejcikova/Siniakova vs ?', 'Kre/Sin', 'TBD', 'WD', 0.75, 0.48, 0, 0, {
        'ML': 1.36,
    }),
    # === MIXED DOUBLES QF ===
    ('Top seed MD XD vs ?', 'Fav XD', 'TBD', 'XD', 0.72, 0.46, 0, 0, {
        'ML': 1.38,
    }),
]

print("=" * 85)
print("WIMBLEDON 06/07/2026 — DAY 8 — 25,000 MC per match")
print("=" * 85)

all_candidates = []

for name, fav, dog, event, pw, ps, pm, pl, odds in MATCHES:
    if event == 'MS':
        res = [simulate_bo5(pw, ps, pm, pl) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_hcap = pct(res, lambda r: r['margin_2plus'])
        p_30 = pct(res, lambda r: r['straight'])
        p_1st = p_ml * 0.85
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '-1.5_sets': (p_hcap, f'{fav} -1.5 sets'),
            '3-0': (p_30, f'{fav} vence 3-0'),
            '1st_set': (p_1st, f'{fav} 1.º set'),
        }
        print(f"\n{name} [Bo5] — {fav} pw={pw*100:.0f}% → ML:{p_ml:.1f}% -1.5:{p_hcap:.1f}%")
    elif event == 'WS':
        res = [simulate_bo3(pw, ps, pm) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_20 = pct(res, lambda r: r['straight'])
        p_1st = p_ml * 0.82
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '2-0': (p_20, f'{fav} vence 2-0'),
            '1st_set': (p_1st, f'{fav} 1.º set'),
        }
        print(f"\n{name} [Bo3 WS] — {fav} pw={pw*100:.0f}% → ML:{p_ml:.1f}% 2-0:{p_20:.1f}%")
    else:
        res = [simulate_doubles(pw, ps) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_20 = pct(res, lambda r: r['straight'])
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '2-0': (p_20, f'{fav} vence 2-0'),
        }
        print(f"\n{name} [Bo3 {event}] — {fav} pw={pw*100:.0f}% → ML:{p_ml:.1f}%")

    for key, odd in odds.items():
        if key not in market_map:
            continue
        prob, label = market_map[key]
        if not (1.30 <= odd <= 1.50):
            continue
        lo, hi = ci(prob)
        mtype = 'ml' if key == 'ML' else ('hcap' if 'sets' in key else '1st' if '1st' in key else 'set')
        risk, vol, conf = risk_scores(prob, odd, mtype)
        all_candidates.append({
            'match': name, 'pick': label, 'odd': odd, 'prob': prob,
            'lo': lo, 'hi': hi, 'imp': 100 / odd, 'edge': prob - 100 / odd,
            'pass75': prob >= 75, 'event': event, 'fav': fav,
            'risk': risk, 'vol': vol, 'conf': conf,
        })

print("\n" + "=" * 85)
print("TOP 10 BETCLIC @ 1.30-1.50 (full day)")
print("=" * 85)
all_candidates.sort(key=lambda x: -x['prob'])
print(f"{'#':<3} {'Pick':<28} {'Match':<26} {'Odd':>5} {'Model':>7} {'CI':>11} {'Risk':>5} {'Vol':>5} {'Conf':>5} {'75%':>5}")
for i, c in enumerate(all_candidates[:10], 1):
    print(f"{i:<3} {c['pick']:<28} {c['match']:<26} @{c['odd']:.2f} {c['prob']:>6.1f}% "
          f"[{c['lo']:.0f}-{c['hi']:.0f}] {c['risk']:>5} {c['vol']:>5} {c['conf']:>5} "
          f"{'YES' if c['pass75'] else 'NO':>5}")

pass75 = [c for c in all_candidates if c['pass75']]
print(f"\nTotal in range: {len(all_candidates)} | PASS75: {len(pass75)}")
if pass75:
    b = pass75[0]
    print(f"\n>>> BEST: {b['pick']} | {b['match']} @{b['odd']:.2f} — {b['prob']:.1f}%")
else:
    print("\n>>> NO BET — nenhum mercado passa 75% na gama 1.30-1.50")
