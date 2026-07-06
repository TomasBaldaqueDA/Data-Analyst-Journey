#!/usr/bin/env python3
"""
Wimbledon 07 Jul 2026 — Day 9 full schedule Monte Carlo.
MS Bo5 / WS Bo3 / MD WD XD Bo3 · Betclic 1.30-1.50 · filter ≥75%.
Sources: TennisConnected Day 9, ATP/WTA, BBC, Betclic Jul 6-7.
"""

import math
import random

random.seed(20260707)
N = 50_000


def simulate_bo5(p_win, p_30, p_31, p_32):
    if random.random() > p_win:
        r = random.random()
        if r < 0.4:
            return _o(False, '2-3', False)
        if r < 0.7:
            return _o(False, '1-3', False)
        return _o(False, '0-3', False)
    r = random.random()
    if r < p_30:
        return _o(True, '3-0', True)
    if r < p_30 + p_31:
        return _o(True, '3-1', True)
    return _o(True, '3-2', False)


def _o(fw, sc, m2):
    return {'fw': fw, 'sc': sc, 'straight': fw and sc == '3-0',
            'm2plus': fw and sc in ('3-0', '3-1'), 'wset': fw or sc in ('2-3', '1-3')}


def simulate_bo3(pw, p20, p21=0.12):
    if random.random() > pw:
        return {'fw': False, 'sc': '1-2' if random.random() < 0.62 else '0-2',
                'straight': False, 'm2plus': False, 'wset': False}
    if random.random() < p20:
        return {'fw': True, 'sc': '2-0', 'straight': True, 'm2plus': True, 'wset': True}
    return {'fw': True, 'sc': '2-1', 'straight': False, 'm2plus': False, 'wset': True}


def pct(res, fn):
    return sum(1 for r in res if fn(r)) / len(res) * 100


def ci(p):
    p /= 100
    z, n = 1.96, N
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


def scores(p, odd, mt):
    impl = 100 / odd
    st = {'ml': 18, 'hcap': 22, 'set': 28, '1st': 32, 'dbl': 20}.get(mt, 35)
    vol = max(0, min(100, 100 - p + st * 0.3))
    risk = max(0, min(100, vol + (100 - p) * 0.45))
    conf = max(0, min(100, p - abs(p - impl) * 0.28 - st * 0.15))
    return round(risk), round(vol), round(conf)


# (match, fav, dog, ev, pw, ps, pm, pl, odds{BETCLIC est.})
MATCHES = [
    # === MS QF — Tue 7 Jul ===
    ('Sinner vs Struff', 'Sinner', 'Struff', 'MS', 0.91, 0.46, 0.32, 0.13, {
        'ML': 1.14, '-1.5_sets': 1.42, '1st_set': 1.28, '3-0': 1.95,
    }),
    ('Djokovic vs FAA', 'Djokovic', 'FAA', 'MS', 0.66, 0.28, 0.26, 0.12, {
        'ML': 1.52, '-1.5_sets': 2.05, '1st_set': 1.58, 'wins_set': 1.38,
    }),
    ('Pegula vs Gauff', 'Gauff', 'Pegula', 'WS', 0.54, 0.26, 0.18, 0, {
        'ML': 1.68, '2-0': 2.45, '1st_set': 1.62,
    }),
    ('Osaka vs Muchova', 'Osaka', 'Muchova', 'WS', 0.58, 0.30, 0.20, 0, {
        'ML': 1.62, '2-0': 2.35, '1st_set': 1.55,
    }),
    # === MD QF ===
    ('Heli/Patten vs A/G', 'Heli/Patten', 'A/G', 'MD', 0.829, 0.48, 0, 0, {
        'ML': 1.22, '2-0': 1.55, '1st_set': 1.32,
    }),
    ('Krawietz/Puetz vs ?', 'Kra/Pue', 'TBD', 'MD', 0.76, 0.50, 0, 0, {
        'ML': 1.32, '2-0': 1.52,
    }),
    ('Harrison/Skupski vs ?', 'Har/Sku', 'TBD', 'MD', 0.74, 0.48, 0, 0, {
        'ML': 1.35, '2-0': 1.58,
    }),
    ('Cash/Glasspool vs ?', 'Cash/GP', 'TBD', 'MD', 0.72, 0.46, 0, 0, {
        'ML': 1.38,
    }),
    # === WD R16 ===
    ('Siniak/Townsend vs Stoll/Muham', 'Sin/Tow', 'Sto/Muh', 'WD', 0.80, 0.52, 0, 0, {
        'ML': 1.30, '2-0': 1.48, '1st_set': 1.35,
    }),
    ('Krejcikova/partner vs ?', 'Kre/part', 'TBD', 'WD', 0.73, 0.46, 0, 0, {
        'ML': 1.36,
    }),
    # === XD SF ===
    ('Stollar/Pavic vs Pol/Hunt', 'Sto/Pav', 'Pol/Hun', 'XD', 0.62, 0.32, 0, 0, {
        'ML': 1.58,
    }),
]

print('=' * 92)
print('WIMBLEDON 07/07/2026 — DAY 9 — 50,000 MC per match · Betclic 1.30-1.50')
print('=' * 92)

cands = []
for name, fav, dog, ev, pw, ps, pm, pl, odds in MATCHES:
    if ev == 'MS':
        res = [simulate_bo5(pw, ps, pm, pl) for _ in range(N)]
        pmap = {
            'ML': (pct(res, lambda r: r['fw']), f'{fav} ML', 'ml'),
            '-1.5_sets': (pct(res, lambda r: r['m2plus']), f'{fav} -1.5 sets', 'hcap'),
            '3-0': (pct(res, lambda r: r['straight']), f'{fav} 3-0', 'set'),
            '1st_set': (pct(res, lambda r: r['fw']) * 0.86, f'{fav} 1.º set', '1st'),
            'wins_set': (pct(res, lambda r: r['wset']), f'{fav} ganha 1 set', 'set'),
        }
        print(f"\n{name} [Bo5] pw={pw:.0%} → ML {pmap['ML'][0]:.1f}% | -1.5 {pmap['-1.5_sets'][0]:.1f}%")
    else:
        res = [simulate_bo3(pw, ps, pm) for _ in range(N)]
        pmap = {
            'ML': (pct(res, lambda r: r['fw']), f'{fav} ML', 'ml'),
            '2-0': (pct(res, lambda r: r['straight']), f'{fav} 2-0', 'set'),
            '1st_set': (pct(res, lambda r: r['fw']) * 0.84, f'{fav} 1.º set', '1st'),
            'wins_set': (pct(res, lambda r: r['wset']), f'{fav} ganha 1 set', 'set'),
        }
        print(f"\n{name} [Bo3 {ev}] pw={pw:.0%} → ML {pmap['ML'][0]:.1f}% | 2-0 {pmap.get('2-0',(0,''))[0]:.1f}%")

    for k, odd in odds.items():
        if k not in pmap:
            continue
        prob, label, mt = pmap[k]
        if not (1.30 <= odd <= 1.50):
            continue
        lo, hi = ci(prob)
        risk, vol, conf = scores(prob, odd, mt)
        cands.append({
            'match': name, 'pick': label, 'odd': odd, 'prob': prob,
            'lo': lo, 'hi': hi, 'imp': 100/odd, 'edge': prob - 100/odd,
            'pass75': prob >= 75, 'risk': risk, 'vol': vol, 'conf': conf,
        })

cands.sort(key=lambda x: -x['prob'])
print('\n' + '=' * 92)
print('TOP 10 — BETCLIC 1.30-1.50')
print(f"{'#':<3} {'Pick':<26} {'Match':<24} {'Odd':>5} {'Model':>7} {'CI95':>11} {'Edge':>7} {'Risk':>5} {'Conf':>5} {'75%':>5}")
for i, c in enumerate(cands[:10], 1):
    print(f"{i:<3} {c['pick']:<26} {c['match']:<24} @{c['odd']:.2f} {c['prob']:>6.1f}% "
          f"[{c['lo']:.0f}-{c['hi']:.0f}] {c['edge']:>+6.1f}pp {c['risk']:>5} {c['conf']:>5} "
          f"{'YES' if c['pass75'] else 'NO':>5}")

p75 = [c for c in cands if c['pass75']]
print(f"\nTotal in range: {len(cands)} | PASS75: {len(p75)}")
if p75:
    b = max(p75, key=lambda x: x['conf'])
    print(f"\n>>> BEST: {b['pick']} | {b['match']} @{b['odd']:.2f} — {b['prob']:.1f}% conf {b['conf']}")
else:
    print('\n>>> NO BET')
