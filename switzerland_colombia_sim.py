#!/usr/bin/env python3
"""Switzerland vs Colombia — WC2026 R16 · 07/07/2026 · 100k MC · Betclic 1.30-1.50."""

import math
import random
from collections import Counter

random.seed(20260707)
N = 100_000

# Market: SUI 3.50 / Draw 3.10 / COL 2.25 → de-vig ~27/31/42%
# SUI group: solid, beat Canada at BC Place; COL: strong, Diaz, unbeaten streak
# R16 neutral Vancouver; COL slight fav; tight knockout expected
LAMBDAS = [
    (1.28, 1.48),   # xG — COL edge in attack
    (1.22, 1.42),   # market-implied
    (1.25, 1.38),   # knockout caution (low-scoring)
    (1.30, 1.52),   # COL form / Diaz
]
W = [0.30, 0.30, 0.25, 0.15]
PEN_COL = 0.58
VENUE_SUI = 1.02  # BC Place familiarity


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def pick_lam():
    i = random.choices(range(4), weights=W, k=1)[0]
    sx, cx = LAMBDAS[i]
    k = random.gauss(0.92, 0.04)
    return (max(0.35, sx * VENUE_SUI * k * random.gauss(1, 0.07)),
            max(0.35, cx * k * random.gauss(1, 0.07)))


def simulate():
    sx, cx = pick_lam()
    s90, c90 = poisson(sx), poisson(cx)
    s1, c1 = poisson(sx * 0.44), poisson(cx * 0.42)
    s2, c2 = max(0, s90 - s1), max(0, c90 - c1)

    r90 = 'S' if s90 > c90 else ('C' if c90 > s90 else 'D')
    st, ct = s90, c90
    qual = r90
    extra = False
    if r90 == 'D':
        extra = True
        set_, cet = poisson(sx * 0.32), poisson(cx * 0.32)
        st, ct = s90 + set_, c90 + cet
        if st > ct:
            qual = 'S'
        elif ct > st:
            qual = 'C'
        else:
            qual = 'C' if random.random() < PEN_COL else 'S'

    tg = st + ct
    tg1, tg2 = s1 + c1, s2 + c2

    h1 = 'S' if s1 > c1 else ('C' if c1 > s1 else 'D')
    h2 = 'S' if s2 > c2 else ('C' if c2 > s2 else 'D')
    sui_wins_both = s1 > c1 and s2 > c2
    col_wins_both = c1 > s1 and c2 > s2
    sui_wins_either = s1 > c1 or s2 > c2
    col_wins_either = c1 > s1 or c2 > s2

    lead2_col = (c90 - s90 >= 2) or (c1 - s1 >= 2) or (qual == 'C' and ct - st >= 2)
    early_col = lead2_col or qual == 'C'

    return {
        'r90': r90, 'qual': qual, 'st': st, 'ct': ct, 'tg': tg,
        's1': s1, 'c1': c1, 's2': s2, 'c2': c2, 'tg1': tg1, 'tg2': tg2,
        'extra': extra, 'h1': h1, 'h2': h2,
        'sui_ml': r90 == 'S', 'col_ml': r90 == 'C',
        'x1': r90 in ('S', 'D'), 'x2': r90 in ('C', 'D'), 'x12': r90 != 'D',
        'col_dnb': r90 == 'C', 'sui_dnb': r90 == 'S',
        'col_dnb_h1': c1 > s1, 'col_dnb_h2': c2 > s2,
        'btts': st > 0 and ct > 0,
        'u15': tg <= 1, 'u25': tg <= 2, 'u35': tg <= 3, 'u45': tg <= 4,
        'o15': tg >= 2, 'o25': tg > 2.5,
        'tg1_o05': tg1 >= 1, 'tg1_u15': tg1 <= 1,
        'tg2_u15': tg2 <= 1,
        'sui_o05': st >= 1, 'col_o05': ct >= 1,
        'sui_u05_1h': s1 == 0, 'col_u15': ct <= 1,
        'sui_u15': st <= 1,
        'col_not_both': not col_wins_both,
        'sui_not_either': not sui_wins_either,
        'col_not_either': not col_wins_either,
        'x2_u35': r90 in ('C', 'D') and tg <= 3,
        'x2_u45': r90 in ('C', 'D') and tg <= 4,
        'x1_u45': r90 in ('S', 'D') and tg <= 4,
        'x12_u35': r90 != 'D' and tg <= 3,
        'x12_u45': r90 != 'D' and tg <= 4,
        'early_col': early_col,
        'no_extra': not extra,
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


def scores(p, odd, mt):
    impl = 100 / odd
    st = {'ml': 22, 'dc': 14, 'dnb': 18, 'goals': 20, 'half': 24, 'combo': 26}.get(mt, 22)
    conf = max(0, min(100, p - abs(p - impl) * 0.28 - st * 0.12))
    risk = max(0, min(100, 100 - p + st * 0.3 + (100 - p) * 0.4))
    vol = max(0, min(100, 100 - p + st * 0.35))
    return round(risk), round(vol), round(conf)


res = [simulate() for _ in range(N)]

print('=' * 95)
print('SWITZERLAND vs COLOMBIA — WC2026 R16 — 07/07/2026 21:00 PT — 100k MC')
print('=' * 95)
print(f"90' SUI:{pct(res, lambda r: r['r90']=='S'):.1f}% | Draw:{pct(res, lambda r: r['r90']=='D'):.1f}% | COL:{pct(res, lambda r: r['r90']=='C'):.1f}%")
print(f"Qualify SUI:{pct(res, lambda r: r['qual']=='S'):.1f}% | COL:{pct(res, lambda r: r['qual']=='C'):.1f}%")
print(f"Média golos:{sum(r['tg'] for r in res)/N:.2f} | Prolongamento:{pct(res, lambda r: r['extra']):.1f}%")

MARKETS = [
    ('Colômbia ML', 2.25, lambda r: r['col_ml'], 'ml'),
    ('Colômbia EarlyWin', 2.20, lambda r: r['early_col'], 'ml'),
    ('Colômbia DNB', 1.49, lambda r: r['col_dnb'], 'dnb'),
    ('Colômbia DNB 1ª parte', 1.47, lambda r: r['col_dnb_h1'], 'dnb'),
    ('Colômbia DNB 2ª parte', 1.49, lambda r: r['col_dnb_h2'], 'dnb'),
    ('Colômbia qualifica', 1.55, lambda r: r['qual'] == 'C', 'ml'),
    ('COL/Emp & Under 3.5', 1.47, lambda r: r['x2_u35'], 'combo'),
    ('COL/Emp & Under 4.5', 1.27, lambda r: r['x2_u45'], 'combo'),
    ('SUI/COL & Under 4.5', 1.35, lambda r: r['x12_u45'], 'combo'),
    ('SUI/COL & Under 3.5', 1.54, lambda r: r['x12_u35'], 'combo'),
    ('SUI/Emp & Under 4.5', 1.47, lambda r: r['x1_u45'], 'combo'),
    ('Suíça não ganha uma parte — Não', 1.50, lambda r: r['sui_not_either'], 'half'),
    ('Colômbia não vence ambas — Não', 1.05, lambda r: r['col_not_both'], 'half'),
    ('Over 1.5 golos', 1.37, lambda r: r['o15'], 'goals'),
    ('Under 2.5 golos', 1.51, lambda r: r['u25'], 'goals'),
    ('Under 3.5 golos', 1.18, lambda r: r['u35'], 'goals'),
    ('Over 0.5 1ª parte', 1.47, lambda r: r['tg1_o05'], 'goals'),
    ('Under 1.5 1ª parte', 1.24, lambda r: r['tg1_u15'], 'goals'),
    ('Under 1.5 2ª parte', 1.39, lambda r: r['tg2_u15'], 'goals'),
    ('Suíça U0.5 1ª parte', 1.38, lambda r: r['sui_u05_1h'], 'half'),
    ('Suíça Over 0.5 golos', 1.46, lambda r: r['sui_o05'], 'goals'),
    ('Colômbia Under 1.5 golos', 1.46, lambda r: r['col_u15'], 'goals'),
    ('BTTS Não', 1.75, lambda r: not r['btts'], 'goals'),
    ('Sem prolongamento', 1.29, lambda r: r['no_extra'], 'goals'),
    ('Colômbia +1 AH', 1.29, lambda r: r['ct'] - r['st'] > -1, 'dc'),
    ('Suíça +1 AH', 1.58, lambda r: r['st'] - r['ct'] > -1, 'dc'),
]

cands = []
for name, odd, fn, mt in MARKETS:
    if not (1.30 <= odd <= 1.50):
        continue
    p = pct(res, fn)
    lo, hi = ci(p)
    risk, vol, conf = scores(p, odd, mt)
    cands.append({
        'pick': name, 'odd': odd, 'prob': p, 'lo': lo, 'hi': hi,
        'impl': 100 / odd, 'edge': p - 100 / odd,
        'risk': risk, 'vol': vol, 'conf': conf, 'pass75': p >= 75, 'mt': mt,
    })

cands.sort(key=lambda x: (-x['prob'], -x['conf']))
print('\nCANDIDATES 1.30-1.50:')
print(f"{'#':<3} {'Pick':<38} {'Odd':>5} {'Model':>7} {'CI95':>11} {'Edge':>7} {'Conf':>5} {'75%':>5}")
for i, c in enumerate(cands, 1):
    print(f"{i:<3} {c['pick']:<38} @{c['odd']:.2f} {c['prob']:>6.1f}% "
          f"[{c['lo']:.0f}-{c['hi']:.0f}] {c['edge']:>+6.1f}pp {c['conf']:>5} "
          f"{'YES' if c['pass75'] else 'NO':>5}")

p75 = [c for c in cands if c['pass75']]
print(f'\nPASS75: {len(p75)}')
for c in p75:
    print(f"  ★ {c['pick']} @{c['odd']:.2f} → {c['prob']:.1f}% (edge {c['edge']:+.1f}pp)")

if p75:
    struct = [c for c in p75 if c['mt'] in ('half', 'combo', 'goals', 'dnb', 'dc')]
    b = max(struct, key=lambda x: (x['conf'], x['edge']))
    print(f"\n>>> BEST: {b['pick']} @{b['odd']:.2f} — {b['prob']:.1f}% conf {b['conf']}")
else:
    print('\n>>> NO BET')

sc = Counter((r['st'], r['ct']) for r in res)
print('\nTOP SCORES:')
for (s, c), n in sc.most_common(6):
    print(f"  {s}-{c}: {n/N*100:.1f}%")
