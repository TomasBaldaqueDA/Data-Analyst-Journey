#!/usr/bin/env python3
"""
Wimbledon 05 Jul 2026 — Day 7 (R16 Day 1) full schedule Monte Carlo.
Men Bo5 / Women Bo3 / Doubles Bo3.
Markets @ 1.30-1.50 for challenge filter.
Sources: Sky Sports OOP, Wimbledon.com, ATP/WTA, market consensus Jul 4-5.
"""

import random
import math

random.seed(20260705)
N = 25000


def simulate_bo5(p_win, p_30, p_31, p_32):
    if random.random() > p_win:
        r = random.random()
        if r < 0.4:
            return _out(False, '2-3', 2, 3, 32)
        if r < 0.7:
            return _out(False, '1-3', 1, 3, 28)
        return _out(False, '0-3', 0, 3, 22)
    r = random.random()
    if r < p_30:
        return _out(True, '3-0', 3, 0, 26 + random.randint(0, 8))
    if r < p_30 + p_31:
        return _out(True, '3-1', 3, 1, 32 + random.randint(-2, 10))
    return _out(True, '3-2', 3, 2, 38 + random.randint(0, 12))


def _out(fav_w, score, sf, sd, tg):
    return {
        'fav_wins': fav_w, 'score': score,
        'straight': fav_w and sd == 0,
        'margin_2plus': fav_w and sd <= 1,
        'wins_set': fav_w,
    }


def simulate_bo3(p_win, p_20, p_21=0.12):
    if random.random() > p_win:
        r = random.random()
        if r < 0.55:
            return {'fav_wins': False, 'score': '1-2', 'straight': False,
                    'margin_2plus': False, 'wins_set': False}
        return {'fav_wins': False, 'score': '0-2', 'straight': False,
                'margin_2plus': False, 'wins_set': False}
    if random.random() < p_20:
        return {'fav_wins': True, 'score': '2-0', 'straight': True,
                'margin_2plus': True, 'wins_set': True}
    return {'fav_wins': True, 'score': '2-1', 'straight': False,
            'margin_2plus': False, 'wins_set': True}


def simulate_doubles(p_win, p_20=0.55):
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


# (match, fav, dog, event, pw, p_straight, p_mid, p_long, odds_dict)
# pw = base match win prob; calibrated from rank, grass, H2H, form, load
MATCHES = [
    # === MEN SINGLES — Centre / confirmed R16 Jul 5 ===
    ('Djokovic vs Safiullin', 'Djokovic', 'Safiullin', 'MS', 0.90, 0.48, 0.30, 0.12, {
        'ML': 1.12, '-1.5_sets': 1.38, '3-0': 1.48, '1st_set': 1.25,
    }),
    ('Sinner vs Mochizuki', 'Sinner', 'Mochizuki', 'MS', 0.96, 0.72, 0.18, 0.06, {
        'ML': 1.04, '-1.5_sets': 1.32, '3-0': 1.35, '1st_set': 1.12,
    }),
    ('FAA vs Davidovich Fokina', 'FAA', 'ADF', 'MS', 0.78, 0.42, 0.28, 0.08, {
        'ML': 1.28, '-1.5_sets': 1.55, '3-0': 1.85, '1st_set': 1.32,
    }),
    ('Hurkacz vs Struff', 'Hurkacz', 'Struff', 'MS', 0.62, 0.28, 0.22, 0.12, {
        'ML': 1.55, '-1.5_sets': 2.10,
    }),
    # === WOMEN SINGLES ===
    ('Sabalenka vs Osaka', 'Sabalenka', 'Osaka', 'WS', 0.68, 0.38, 0.22, 0, {
        'ML': 1.42, '2-0': 1.95, '1st_set': 1.48,
    }),
    ('Pegula vs Jovic', 'Pegula', 'Jovic', 'WS', 0.76, 0.48, 0.22, 0, {
        'ML': 1.32, '2-0': 1.62, '1st_set': 1.38,
    }),
    ('Gauff vs Bencic', 'Gauff', 'Bencic', 'WS', 0.72, 0.40, 0.24, 0, {
        'ML': 1.38, '2-0': 1.85, '1st_set': 1.42,
    }),
    ('Muchova vs Krejcikova', 'Muchova', 'Krejcikova', 'WS', 0.52, 0.22, 0.18, 0, {
        'ML': 1.72, '2-0': 2.40,
    }),
    # === MEN DOUBLES R3 ===
    ('Heliovaara/Patten vs Pavlasek/Rikl', 'Heli/Patten', 'Pav/Rikl', 'MD', 0.78, 0.52, 0, 0, {
        'ML': 1.30, '2-0': 1.55,
    }),
    # === LADIES DOUBLES R2 (notable) ===
    ('Siniakova/Townsend vs ?', 'Siniak/Town', 'TBD', 'WD', 0.74, 0.48, 0, 0, {
        'ML': 1.35,
    }),
]

print("=" * 80)
print("WIMBLEDON 05/07/2026 — DAY 7 (R16) — 25,000 MC")
print("=" * 80)

all_candidates = []

for name, fav, dog, event, pw, ps, pm, pl, odds in MATCHES:
    if event == 'MS':
        res = [simulate_bo5(pw, ps, pm, pl) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_str = pct(res, lambda r: r['fav_wins'] and r['score'] == '3-0')
        p_hcap = pct(res, lambda r: r['fav_wins'] and r['margin_2plus'])
        p_1st = p_ml * 0.86
        print(f"\n{name} [Bo5 MS] — {fav} base {pw*100:.0f}%")
        print(f"  ML:{p_ml:.1f}% | 3-0:{p_str:.1f}% | -1.5 sets:{p_hcap:.1f}% | 1st~:{p_1st:.1f}%")
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '-1.5_sets': (p_hcap, f'{fav} -1.5 sets'),
            '3-0': (p_str, f'{fav} vence 3-0'),
            '1st_set': (p_1st, f'{fav} 1.º set'),
        }
    elif event in ('WS',):
        res = [simulate_bo3(pw, ps, pm) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_20 = pct(res, lambda r: r['fav_wins'] and r['score'] == '2-0')
        p_1st = p_ml * 0.83
        print(f"\n{name} [Bo3 WS] — {fav} base {pw*100:.0f}%")
        print(f"  ML:{p_ml:.1f}% | 2-0:{p_20:.1f}% | 1st~:{p_1st:.1f}%")
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '2-0': (p_20, f'{fav} vence 2-0'),
            '1st_set': (p_1st, f'{fav} 1.º set'),
        }
    else:
        res = [simulate_doubles(pw, ps) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_20 = pct(res, lambda r: r['fav_wins'] and r['score'] == '2-0')
        print(f"\n{name} [Bo3 {event}] — {fav} base {pw*100:.0f}%")
        print(f"  ML:{p_ml:.1f}% | 2-0:{p_20:.1f}%")
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '2-0': (p_20, f'{fav} vence 2-0'),
        }

    for key, odd in odds.items():
        if key not in market_map:
            continue
        prob, label = market_map[key]
        if 1.30 <= odd <= 1.50:
            lo, hi = ci(prob)
            all_candidates.append({
                'match': name, 'pick': label, 'odd': odd, 'prob': prob,
                'lo': lo, 'hi': hi, 'imp': 100 / odd,
                'edge': prob - 100 / odd,
                'pass75': prob >= 75,
                'event': event, 'fav': fav,
            })

print("\n" + "=" * 80)
print("ALL CANDIDATES @ 1.30-1.50")
print("=" * 80)
all_candidates.sort(key=lambda x: -x['prob'])
for i, c in enumerate(all_candidates, 1):
    st = "PASS75" if c['pass75'] else "FAIL"
    print(f"{i:2d}. {c['pick']:30s} | {c['match']:28s} @{c['odd']:.2f} "
          f"M:{c['prob']:5.1f}% [{c['lo']:.0f}-{c['hi']:.0f}] edge:{c['edge']:+.1f}pp {st}")

pass75 = [c for c in all_candidates if c['pass75']]
print(f"\nTotal in range: {len(all_candidates)} | Pass 75%: {len(pass75)}")
if pass75:
    b = pass75[0]
    print(f"\n>>> BEST: {b['pick']} | {b['match']} @{b['odd']:.2f} — {b['prob']:.1f}%")
else:
    print("\n>>> NO BET — nenhum mercado passa 75% na gama 1.30-1.50")

# Contrarian: joint acca top 2 (independence approx)
if len(pass75) >= 2:
    p_joint = pass75[0]['prob']/100 * pass75[1]['prob']/100
    odd_joint = pass75[0]['odd'] * pass75[1]['odd']
    print(f"\nAcca top2 (indép.): {pass75[0]['pick']} + {pass75[1]['pick']} "
          f"@{odd_joint:.2f} ~{p_joint*100:.1f}%")
