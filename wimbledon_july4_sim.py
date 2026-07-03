#!/usr/bin/env python3
"""
Wimbledon 04 Jul 2026 — Day 6 full schedule Monte Carlo.
Men Bo5 / Women Bo3. Markets @ 1.30-1.50 for challenge filter.
"""

import random
import math

random.seed(20260704)
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
        return _out(True, '3-0', 3, 0, 26 + random.randint(0, 8), 7 + random.randint(0, 6))
    if r < p_30 + p_31:
        return _out(True, '3-1', 3, 1, 32 + random.randint(-2, 10), 4 + random.randint(0, 5))
    return _out(True, '3-2', 3, 2, 38 + random.randint(0, 12), 1 + random.randint(0, 3))


def _out(fav_w, score, sf, sd, tg, gm=0):
    return {
        'fav_wins': fav_w, 'score': score, 'sets_fav': sf, 'sets_dog': sd,
        'straight': fav_w and sd == 0, 'margin_2plus': fav_w and sd <= 1,
        'total_games': tg, 'game_margin': gm if fav_w else -abs(gm or 2),
        'wins_set': fav_w,
    }


def simulate_bo3(p_win, p_20, p_21=0.12):
    if random.random() > p_win:
        r = random.random()
        if r < 0.55:
            return {'fav_wins': False, 'score': '1-2', 'straight': False, 'margin_2plus': False,
                    'total_games': 26 + random.randint(0, 8), 'game_margin': -random.randint(1, 4),
                    'wins_set': False}
        return {'fav_wins': False, 'score': '0-2', 'straight': False, 'margin_2plus': False,
                'total_games': 18 + random.randint(0, 6), 'game_margin': -random.randint(3, 7),
                'wins_set': False}
    if random.random() < p_20:
        return {'fav_wins': True, 'score': '2-0', 'straight': True, 'margin_2plus': True,
                'total_games': 18 + random.randint(0, 8), 'game_margin': 5 + random.randint(0, 6),
                'wins_set': True}
    return {'fav_wins': True, 'score': '2-1', 'straight': False, 'margin_2plus': False,
            'total_games': 26 + random.randint(0, 10), 'game_margin': 2 + random.randint(0, 4),
            'wins_set': True}


def pct(res, fn):
    return sum(1 for r in res if fn(r)) / len(res) * 100


def ci(p):
    p /= 100
    z, n = 1.96, N
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


# (match, fav, dog, gender, pw, p_straight, p_mid, p_long, markets)
# Sources: ATP/WTA ranks, grass records, H2H, Opta-style estimates, market consensus
MATCHES = [
    # MEN — Day 6 singles 3R (AiScore / CBS confirmed)
    ('Zverev vs Giron', 'Zverev', 'Giron', 'M', 0.92, 0.52, 0.30, 0.10, {
        'ML': 1.14, '-1.5_sets': 1.36, '3-0': 1.55, '1st_set': 1.22,
    }),
    ('De Minaur vs Svajda', 'De Minaur', 'Svajda', 'M', 0.88, 0.45, 0.32, 0.11, {
        'ML': 1.18, '-1.5_sets': 1.40, '3-0': 1.65,
    }),
    ('Cobolli vs Khachanov', 'Cobolli', 'Khachanov', 'M', 0.62, 0.22, 0.28, 0.12, {
        'ML': 1.55,
    }),
    ('Lehecka vs Munar', 'Lehecka', 'Munar', 'M', 0.70, 0.30, 0.28, 0.12, {
        'ML': 1.42, '-1.5_sets': 1.85,
    }),
    ('Berrettini vs Dimitrov', 'Berrettini', 'Dimitrov', 'M', 0.54, 0.20, 0.22, 0.12, {
        'ML': 1.75,
    }),
    ('Bublik vs Tiafoe', 'Bublik', 'Tiafoe', 'M', 0.53, 0.18, 0.22, 0.13, {
        'ML': 1.72,
    }),
    ('Bergs vs Fery', 'Bergs', 'Fery', 'M', 0.58, 0.24, 0.22, 0.12, {
        'ML': 1.62,
    }),
    ('Fritz vs Sonego', 'Fritz', 'Sonego', 'M', 0.80, 0.38, 0.30, 0.12, {
        'ML': 1.28, '-1.5_sets': 1.48, '3-0': 1.95,
    }),
    # WOMEN — Day 6 singles 3R
    ('Swiatek vs Eala', 'Swiatek', 'Eala', 'W', 0.88, 0.62, 0.26, 0, {
        'ML': 1.22, '2-0': 1.36, '1st_set': 1.28, '-4.5_games': 1.45,
    }),
    ('Rybakina vs Mertens', 'Rybakina', 'Mertens', 'W', 0.90, 0.68, 0.22, 0, {
        'ML': 1.15, '2-0': 1.38, '1st_set': 1.20,
    }),
    ('Noskova vs Cristian', 'Noskova', 'Cristian', 'W', 0.66, 0.38, 0.28, 0, {
        'ML': 1.32, '2-0': 1.72,
    }),
    ('Paolini vs Sakkari', 'Paolini', 'Sakkari', 'W', 0.65, 0.35, 0.30, 0, {
        'ML': 1.48, '2-0': 2.10,
    }),
    ('Anisimova vs Keys', 'Anisimova', 'Keys', 'W', 0.58, 0.32, 0.26, 0, {
        'ML': 1.52,
    }),
    ('Bouzkova vs Samsonova', 'Bouzkova', 'Samsonova', 'W', 0.62, 0.32, 0.30, 0, {
        'ML': 1.55,
    }),
    ('Navarro vs Kostyuk', 'Navarro', 'Kostyuk', 'W', 0.55, 0.28, 0.27, 0, {
        'ML': 1.58,
    }),
    ('Krueger vs Snigur', 'Krueger', 'Snigur', 'W', 0.58, 0.30, 0.28, 0, {
        'ML': 1.52,
    }),
]

print("=" * 78)
print("WIMBLEDON 04/07/2026 — DAY 6 — 25,000 MC PER MATCH")
print("=" * 78)

all_candidates = []

for name, fav, dog, gender, pw, ps, pm, pl, odds in MATCHES:
    if gender == 'M':
        res = [simulate_bo5(pw, ps, pm, pl) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_str = pct(res, lambda r: r['fav_wins'] and r['score'] == '3-0')
        p_hcap = pct(res, lambda r: r['fav_wins'] and r['margin_2plus'])
        p_1st = p_ml * 0.87
        print(f"\n{name} [Bo5] — Fav: {fav} ({pw*100:.0f}% base)")
        print(f"  ML:{p_ml:.1f}% | 3-0:{p_str:.1f}% | -1.5 sets:{p_hcap:.1f}%")
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '3-0': (p_str, f'{fav} vence 3-0'),
            '-1.5_sets': (p_hcap, f'{fav} -1.5 sets'),
            '1st_set': (p_1st, f'{fav} 1.º set'),
        }
    else:
        res = [simulate_bo3(pw, ps, pm) for _ in range(N)]
        p_ml = pct(res, lambda r: r['fav_wins'])
        p_20 = pct(res, lambda r: r['fav_wins'] and r['score'] == '2-0')
        p_hcap = p_20
        p_1st = p_ml * 0.84
        print(f"\n{name} [Bo3] — Fav: {fav} ({pw*100:.0f}% base)")
        print(f"  ML:{p_ml:.1f}% | 2-0:{p_20:.1f}% | 1st set~:{p_1st:.1f}%")
        market_map = {
            'ML': (p_ml, f'{fav} ML'),
            '2-0': (p_20, f'{fav} vence 2-0'),
            '1st_set': (p_1st, f'{fav} 1.º set'),
            '-4.5_games': (pct(res, lambda r: r['fav_wins'] and r['game_margin'] >= 5), f'{fav} -4.5 jogos'),
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
                'gender': gender, 'fav': fav,
            })

# Acca scan: top ML favorites only
ml_favs = []
for name, fav, dog, gender, pw, ps, pm, pl, odds in MATCHES:
    if odds.get('ML', 99) > 1.30:
        continue
    if gender == 'M':
        res = [simulate_bo5(pw, ps, pm, pl) for _ in range(N)]
    else:
        res = [simulate_bo3(pw, ps, pm) for _ in range(N)]
    p = pct(res, lambda r: r['fav_wins'])
    ml_favs.append((p, fav, name, odds['ML']))

print("\n" + "=" * 78)
print("TOP MARKETS 1.30-1.50 (sorted by model probability)")
print("=" * 78)
all_candidates.sort(key=lambda x: -x['prob'])
for i, c in enumerate(all_candidates[:15], 1):
    st = "PASS75" if c['pass75'] else "FAIL"
    print(f"{i:2d}. {c['pick']:28s} | {c['match']:26s} @{c['odd']:.2f} "
          f"M:{c['prob']:5.1f}% [{c['lo']:.0f}-{c['hi']:.0f}] {st}")

print(f"\nTotal candidates in range: {len(all_candidates)}")
print(f"Pass 75%: {sum(1 for c in all_candidates if c['pass75'])}")
