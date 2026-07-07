#!/usr/bin/env python3
"""UCL 2026/27 Q1 — 07 Jul 2026 first legs · 100k MC · Betclic 1.30-1.50."""

import math
import random

random.seed(20260707)
N = 100_000


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate(hx, ax):
    kf = 0.92  # Q1 first-leg caution
    ha = 1.12
    lh = max(0.35, hx * ha * kf * random.gauss(1.0, 0.08))
    la = max(0.30, ax * kf * random.gauss(1.0, 0.08))
    h, a = poisson(lh), poisson(la)
    h1, a1 = poisson(lh * 0.44), poisson(la * 0.42)
    tg = h + a
    return {
        'h': h, 'a': a, 'tg': tg, 'h1': h1, 'a1': a1,
        'hw': h > a, 'aw': a > h, 'dr': h == a,
        'x1': h >= a, 'x2': a >= h, 'x12': h != a,
        'btts': h > 0 and a > 0,
        'u25': tg <= 2, 'u35': tg <= 3,
        'tg1_o05': h1 + a1 >= 1,
        'margin': h - a,
    }


def pct(res, fn):
    return sum(fn(r) for r in res) / len(res) * 100


def ci(p):
    p /= 100
    z, n = 1.96, N
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return max(0, (c - m) * 100), min(100, (c + m) * 100)


def add(cands, match, pick, odd, prob, mtype='dc'):
    if not (1.30 <= odd <= 1.50):
        return
    impl = 100 / odd
    st = {'ml': 20, 'dc': 12, 'dnb': 18, 'goals': 22, 'ah': 25, 'btts': 24}.get(mtype, 20)
    conf = max(0, min(100, prob - abs(prob - impl) * 0.28 - st * 0.12))
    risk = max(0, min(100, 100 - prob + st * 0.35 + (100 - prob) * 0.35))
    lo, hi = ci(prob)
    cands.append({
        'match': match, 'pick': pick, 'odd': odd, 'prob': prob,
        'lo': lo, 'hi': hi, 'impl': impl, 'edge': prob - impl,
        'conf': round(conf), 'risk': round(risk), 'pass75': prob >= 75, 'mtype': mtype,
    })


# (home, away, hx, ax, betclic markets list of (label, odd, key, mtype))
FIXTURES = [
    ('Sabah', 'TNS', 1.55, 0.72, [
        ('Sabah ML', 1.40, 'hw', 'ml'),
        ('Sabah DNB', 1.28, 'hdnb', 'dnb'),
        ('1X', 1.10, 'x1', 'dc'),
        ('U2.5', 1.38, 'u25', 'goals'),
        ('U3.5', 1.32, 'u35', 'goals'),
        ('BTTS Não', 1.48, 'nbtts', 'btts'),
        ('TNS +1.5 AH', 1.35, 'a+1.5', 'ah'),
    ]),
    ('Kauno Žalgiris', 'Drita', 1.18, 1.05, [
        ('KŽ ML', 1.91, 'hw', 'ml'),
        ('KŽ DNB', 1.45, 'hdnb', 'dnb'),
        ('1X', 1.28, 'x1', 'dc'),
        ('X2', 1.55, 'x2', 'dc'),
        ('U2.5', 1.42, 'u25', 'goals'),
        ('Drita +1 AH', 1.38, 'a+1', 'ah'),
        ('BTTS Não', 1.45, 'nbtts', 'btts'),
        ('U3.5', 1.36, 'u35', 'goals'),
    ]),
    ('Ararat-Armenia', 'Riga', 1.12, 1.08, [
        ('1X', 1.38, 'x1', 'dc'),
        ('X2', 1.35, 'x2', 'dc'),
        ('12', 1.32, 'x12', 'dc'),
        ('U2.5', 1.44, 'u25', 'goals'),
        ('U3.5', 1.40, 'u35', 'goals'),
        ('BTTS Não', 1.46, 'nbtts', 'btts'),
    ]),
    ('Lincoln', 'Inter Escaldes', 1.25, 0.95, [
        ('Lincoln 1X', 1.33, 'x1', 'dc'),
        ('Lincoln DNB', 1.42, 'hdnb', 'dnb'),
        ('Inter +1 AH', 1.40, 'a+1', 'ah'),
        ('U2.5', 1.36, 'u25', 'goals'),
        ('BTTS Não', 1.44, 'nbtts', 'btts'),
        ('U3.5', 1.30, 'u35', 'goals'),
        ('12', 1.38, 'x12', 'dc'),
    ]),
    ('Vardar', 'KuPS', 1.05, 1.15, [
        ('KuPS DNB', 1.45, 'adnb', 'dnb'),
        ('KuPS X2', 1.38, 'x2', 'dc'),
        ('1X', 1.42, 'x1', 'dc'),
        ('U2.5', 1.40, 'u25', 'goals'),
        ('U3.5', 1.34, 'u35', 'goals'),
        ('BTTS Não', 1.48, 'nbtts', 'btts'),
        ('12', 1.35, 'x12', 'dc'),
        ('Vardar +1 AH', 1.32, 'h+1', 'ah'),
    ]),
    ('Floriana', 'Shamrock', 0.82, 1.38, [
        ('Shamrock ML', 1.73, 'aw', 'ml'),
        ('Shamrock DNB', 1.40, 'adnb', 'dnb'),
        ('Shamrock X2', 1.22, 'x2', 'dc'),
        ('Floriana +1 AH', 1.45, 'h+1', 'ah'),
        ('U2.5', 1.36, 'u25', 'goals'),
        ('BTTS Não', 1.42, 'nbtts', 'btts'),
        ('U3.5', 1.30, 'u35', 'goals'),
        ('Shamrock O0.5', 1.38, 'a>=1', 'goals'),
    ]),
    ('Tre Fiori', 'Larne', 0.65, 1.52, [
        ('Larne ML', 1.41, 'aw', 'ml'),
        ('Larne DNB', 1.32, 'adnb', 'dnb'),
        ('Larne X2', 1.12, 'x2', 'dc'),
        ('Tre Fiori +1.5 AH', 1.38, 'h+1.5', 'ah'),
        ('U2.5', 1.45, 'u25', 'goals'),
        ('BTTS Não', 1.50, 'nbtts', 'btts'),
        ('U3.5', 1.35, 'u35', 'goals'),
    ]),
    ('Borac', 'Levski', 0.95, 1.22, [
        ('Levski ML', 2.40, 'aw', 'ml'),
        ('Levski DNB', 1.48, 'adnb', 'dnb'),
        ('Levski X2', 1.30, 'x2', 'dc'),
        ('Borac +1 AH', 1.42, 'h+1', 'ah'),
        ('U2.5', 1.38, 'u25', 'goals'),
        ('BTTS Não', 1.44, 'nbtts', 'btts'),
        ('U3.5', 1.32, 'u35', 'goals'),
    ]),
    ('KÍ', 'Atert Bissen', 1.42, 0.68, [
        ('KÍ ML', 1.50, 'hw', 'ml'),
        ('KÍ DNB', 1.35, 'hdnb', 'dnb'),
        ('KÍ 1X', 1.18, 'x1', 'dc'),
        ('Atert +1.5 AH', 1.32, 'a+1.5', 'ah'),
        ('U2.5', 1.40, 'u25', 'goals'),
        ('BTTS Não', 1.46, 'nbtts', 'btts'),
        ('U3.5', 1.33, 'u35', 'goals'),
        ('Atert +1 AH', 1.38, 'a+1', 'ah'),
    ]),
    ('Víkingur', 'Győri ETO', 1.35, 1.02, [
        ('Víkingur ML', 1.85, 'hw', 'ml'),
        ('Víkingur DNB', 1.42, 'hdnb', 'dnb'),
        ('Víkingur 1X', 1.28, 'x1', 'dc'),
        ('Győr +1 AH', 1.40, 'a+1', 'ah'),
        ('Győr +1.5 AH', 1.30, 'a+1.5', 'ah'),
        ('U2.5', 1.38, 'u25', 'goals'),
        ('BTTS Não', 1.45, 'nbtts', 'btts'),
        ('U3.5', 1.34, 'u35', 'goals'),
        ('12', 1.36, 'x12', 'dc'),
    ]),
]

KEY_FN = {
    'hw': lambda r: r['hw'],
    'aw': lambda r: r['aw'],
    'dr': lambda r: r['dr'],
    'x1': lambda r: r['x1'],
    'x2': lambda r: r['x2'],
    'x12': lambda r: r['x12'],
    'hdnb': lambda r: r['hw'] or r['dr'],
    'adnb': lambda r: r['aw'] or r['dr'],
    'u25': lambda r: r['u25'],
    'u35': lambda r: r['u35'],
    'nbtts': lambda r: not r['btts'],
    'tg1_o05': lambda r: r['tg1_o05'],
    'h+1': lambda r: r['margin'] > -1,
    'a+1': lambda r: r['margin'] < 1,
    'h+1.5': lambda r: r['margin'] > -1.5,
    'a+1.5': lambda r: r['margin'] < 1.5,
    'a>=1': lambda r: r['a'] >= 1,
}


print('=' * 100)
print('UCL 2026/27 — 1ª ELIMINATÓRIA 1.º PERNA — 07/07/2026 · 100k MC')
print('=' * 100)

all_cands = []
for home, away, hx, ax, markets in FIXTURES:
    res = [simulate(hx, ax) for _ in range(N)]
    match = f'{home}–{away}'
    ph = pct(res, lambda r: r['hw'])
    pd = pct(res, lambda r: r['dr'])
    pa = pct(res, lambda r: r['aw'])
    mtg = sum(r['tg'] for r in res) / N
    print(f"\n{match} | ML H {ph:.1f}% D {pd:.1f}% A {pa:.1f}% | média {mtg:.2f} golos")
    for label, odd, key, mtype in markets:
        add(all_cands, match, label, odd, pct(res, KEY_FN[key]), mtype)

all_cands = sorted(all_cands, key=lambda x: (-x['prob'], -x['conf']))

print('\n' + '=' * 100)
print('TOP 15 — BETCLIC 1.30–1.50')
hdr = f"{'#':<3} {'Pick':<28} {'Match':<22} {'Odd':>5} {'Model':>7} {'CI95':>11} {'Edge':>7} {'Conf':>5} {'75%':>5}"
print(hdr)
for i, c in enumerate(all_cands[:15], 1):
    print(f"{i:<3} {c['pick']:<28} {c['match']:<22} @{c['odd']:.2f} {c['prob']:>6.1f}% "
          f"[{c['lo']:.0f}-{c['hi']:.0f}] {c['edge']:>+6.1f}pp {c['conf']:>5} "
          f"{'YES' if c['pass75'] else 'NO':>5}")

p75 = [c for c in all_cands if c['pass75']]
print(f'\nTotal in range: {len(all_cands)} | PASS75: {len(p75)}')
for c in p75:
    print(f"  ★ {c['pick']:<28} {c['match']:<20} @{c['odd']:.2f} → {c['prob']:.1f}% (edge {c['edge']:+.1f}pp)")

if p75:
    struct = [c for c in p75 if c['mtype'] in ('dc', 'dnb', 'goals', 'ah', 'btts')]
    b = max(struct, key=lambda x: (x['conf'], x['edge']))
    print(f"\n>>> BEST: {b['pick']} | {b['match']} @{b['odd']:.2f} — {b['prob']:.1f}% conf {b['conf']}")
else:
    print('\n>>> NO BET')

# Acca pairs for step 9 planning (€115.54 stake)
print('\n--- ACCA 2 LEGS (cada perna ≥75%) ---')
legs = [c for c in p75]
for i, a in enumerate(legs):
    for b in legs[i + 1:]:
        if a['match'] == b['match']:
            continue
        joint = a['prob'] * b['prob'] / 100
        odd = a['odd'] * b['odd']
        if joint >= 75 and 1.30 <= odd <= 2.50:
            print(f"  {a['pick']} @{a['odd']:.2f} + {b['pick']} @{b['odd']:.2f} = @{odd:.2f} | joint {joint:.1f}%")
