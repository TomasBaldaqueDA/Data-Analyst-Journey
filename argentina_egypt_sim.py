#!/usr/bin/env python3
"""Argentina vs Egypt — WC2026 R16 · 07/07/2026 · 100k MC · Betclic 1.30-1.50."""

import math
import random
from collections import Counter

random.seed(20260707)
N = 100_000

# Calibration: market ARG 1.33 / Draw 4.95 / EGY 10.50 → fav ~72-76% 90'
# ARG group: elite attack, Martinez in form; EGY: Salah, organized, 6 GF group
# R16 neutral venue (USA); knockout caution
LAMBDAS = [
    (1.95, 0.72),   # xG — ARG R16 fav, EGY counter threat (Salah)
    (1.82, 0.78),   # market-implied de-vigged (~72% ARG)
    (1.88, 0.70),   # knockout regression
    (2.05, 0.68),   # confirmed lineup: Messi + Alvarez
]
W = [0.30, 0.30, 0.25, 0.15]
PEN_ARG = 0.72
MESSI_SCORES = 0.68  # SuperSub proxy


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def pick_lam():
    i = random.choices(range(4), weights=W, k=1)[0]
    ax, ex = LAMBDAS[i]
    k = random.gauss(0.93, 0.04)
    return max(0.4, ax * k * random.gauss(1, 0.07)), max(0.25, ex * k * random.gauss(1, 0.08))


def simulate():
    ax, ex = pick_lam()
    a90, e90 = poisson(ax), poisson(ex)
    a1, e1 = poisson(ax * 0.43), poisson(ex * 0.41)
    a2, e2 = max(0, a90 - a1), max(0, e90 - e1)

    r90 = 'A' if a90 > e90 else ('E' if e90 > a90 else 'D')
    at, et = a90, e90
    qual = r90
    extra = False
    if r90 == 'D':
        extra = True
        aet, eet = poisson(ax * 0.30), poisson(ex * 0.28)
        at, et = a90 + aet, e90 + eet
        if at > et:
            qual = 'A'
        elif et > at:
            qual = 'E'
        else:
            qual = 'A' if random.random() < PEN_ARG else 'E'

    tg = at + et
    tg1, tg2 = a1 + e1, a2 + e2

    arg_wins_1h = a1 > e1
    arg_wins_2h = a2 > e2
    egy_wins_1h = e1 > a1
    egy_wins_2h = e2 > a2
    arg_wins_both = arg_wins_1h and arg_wins_2h
    egy_wins_both = egy_wins_1h and egy_wins_2h
    arg_wins_either = arg_wins_1h or arg_wins_2h
    egy_wins_either = egy_wins_1h or egy_wins_2h

    lead_2 = False
    # Early Win: 2 goal lead at any point OR win match
    if at - et >= 2:
        lead_2 = True
    elif a1 - e1 >= 2:
        lead_2 = True
    elif (a1 + a2) - (e1 + e2) >= 2 and qual == 'A':
        lead_2 = True
    early_win = lead_2 or qual == 'A'

    messi = random.random() < MESSI_SCORES if at > 0 else random.random() < 0.12

    return {
        'r90': r90, 'qual': qual, 'at': at, 'et': et, 'tg': tg,
        'a1': a1, 'e1': e1, 'a2': a2, 'e2': e2, 'tg1': tg1, 'tg2': tg2,
        'extra': extra,
        'arg_ml': r90 == 'A', 'egy_ml': r90 == 'E',
        'x1': r90 in ('A', 'D'), 'x2': r90 in ('E', 'D'), 'x12': r90 != 'D',
        'arg_dnb': r90 == 'A', 'egy_dnb': r90 == 'E',
        'btts': at > 0 and et > 0,
        'u15': tg <= 1, 'u25': tg <= 2, 'u35': tg <= 3, 'u45': tg <= 4,
        'o05': tg >= 1, 'o15': tg >= 2, 'o25': tg > 2.5,
        'tg1_o05': tg1 >= 1, 'tg1_u15': tg1 <= 1,
        'tg2_o05': tg2 >= 1, 'tg2_u15': tg2 <= 1,
        'arg_o05': at >= 1, 'arg_o15': at >= 2, 'arg_u25': at <= 2,
        'egy_o05': et >= 1, 'egy_u05_1h': e1 == 0,
        'arg_o05_1h': a1 >= 1, 'arg_o05_2h': a2 >= 1,
        'arg_not_both': not arg_wins_both,
        'egy_not_both': not egy_wins_both,
        'arg_wins_either': arg_wins_either,
        'egy_wins_either': egy_wins_either,
        'egy_not_either': not egy_wins_either,
        'x1_u35': r90 in ('A', 'D') and tg <= 3,
        'arg_egy_btts_no': r90 in ('A', 'E') and not (at > 0 and et > 0),
        'early_win': early_win,
        'messi': messi,
        'arg_cs': et == 0,
        'egy_cs': at == 0,
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
    st = {'ml': 22, 'dc': 14, 'goals': 20, 'half': 24, 'combo': 26, 'prop': 35}.get(mt, 22)
    conf = max(0, min(100, p - abs(p - impl) * 0.28 - st * 0.12))
    risk = max(0, min(100, 100 - p + st * 0.3 + (100 - p) * 0.4))
    vol = max(0, min(100, 100 - p + st * 0.35))
    return round(risk), round(vol), round(conf)


res = [simulate() for _ in range(N)]

print('=' * 95)
print('ARGENTINA vs EGYPT — WC2026 R16 — 07/07/2026 17:00 PT — 100,000 MC')
print('=' * 95)
print(f"90' ARG:{pct(res, lambda r: r['r90']=='A'):.1f}% | Draw:{pct(res, lambda r: r['r90']=='D'):.1f}% | EGY:{pct(res, lambda r: r['r90']=='E'):.1f}%")
print(f"Qualify ARG:{pct(res, lambda r: r['qual']=='A'):.1f}% | EGY:{pct(res, lambda r: r['qual']=='E'):.1f}%")
print(f"Média golos:{sum(r['tg'] for r in res)/N:.2f}")

MARKETS = [
    ('Argentina ML', 1.33, lambda r: r['arg_ml'], 'ml'),
    ('Argentina EarlyWin', 1.32, lambda r: r['early_win'], 'ml'),
    ('ARG/Emp & Under 3.5', 1.34, lambda r: r['x1_u35'], 'combo'),
    ('Egito não vence ambas — Não', 1.01, lambda r: r['egy_not_both'], 'half'),
    ('ARG não vence ambas — Não', 1.29, lambda r: r['arg_not_both'], 'half'),
    ('Egito não ganha uma parte — Não', 1.13, lambda r: r['egy_not_either'], 'half'),
    ('Over 0.5 golos 1ª parte', 1.34, lambda r: r['tg1_o05'], 'goals'),
    ('Under 1.5 golos 1ª parte', 1.34, lambda r: r['tg1_u15'], 'goals'),
    ('Under 3.5 golos FT', 1.29, lambda r: r['u35'], 'goals'),
    ('BTTS Não', 1.51, lambda r: not r['btts'], 'goals'),
    ('Argentina Over 1.5 golos', 1.48, lambda r: r['arg_o15'], 'goals'),
    ('Argentina Under 2.5 golos', 1.42, lambda r: r['arg_u25'], 'goals'),
    ('Argentina Over 0.5 1ª parte', 1.43, lambda r: r['arg_o05_1h'], 'half'),
    ('Argentina Over 0.5 2ª parte', 1.33, lambda r: r['arg_o05_2h'], 'half'),
    ('Under 1.5 golos 2ª parte', 1.49, lambda r: r['tg2_u15'], 'half'),
    ('Egito Under 0.5 1ª parte', 1.17, lambda r: r['egy_u05_1h'], 'half'),
    ('ARG/EGY & BTTS Não', 1.65, lambda r: r['arg_egy_btts_no'], 'combo'),
    ('Argentina clean sheet', 1.56, lambda r: r['arg_cs'], 'goals'),
    ('Total remates à baliza Under 9.5', 1.45, lambda r: r['tg'] <= 3 and r['at'] >= 1, 'prop'),  # rough proxy
    ('ARG remates à baliza Over 5.5', 1.42, lambda r: r['at'] >= 2, 'prop'),  # proxy
    ('L. Messi / J. Alvarez SuperSub', 1.26, lambda r: r['messi'] or r['at'] >= 2, 'prop'),
    ('L. Messi / E. Fernández SuperSub', 1.40, lambda r: r['messi'] or r['at'] >= 1, 'prop'),
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
print('\nALL CANDIDATES 1.30-1.50:')
print(f"{'#':<3} {'Pick':<36} {'Odd':>5} {'Model':>7} {'CI95':>11} {'Edge':>7} {'Conf':>5} {'75%':>5}")
for i, c in enumerate(cands, 1):
    print(f"{i:<3} {c['pick']:<36} @{c['odd']:.2f} {c['prob']:>6.1f}% "
          f"[{c['lo']:.0f}-{c['hi']:.0f}] {c['edge']:>+6.1f}pp {c['conf']:>5} "
          f"{'YES' if c['pass75'] else 'NO':>5}")

p75 = [c for c in cands if c['pass75']]
print(f'\nPASS75: {len(p75)}')
for c in p75:
    print(f"  ★ {c['pick']} @{c['odd']:.2f} → {c['prob']:.1f}%")

if p75:
    struct = [c for c in p75 if c['mt'] in ('half', 'combo', 'goals', 'ml')]
    b = max(struct, key=lambda x: (x['conf'], x['edge']))
    print(f"\n>>> BEST: {b['pick']} @{b['odd']:.2f} — {b['prob']:.1f}% conf {b['conf']}")

sc = Counter((r['at'], r['et']) for r in res)
print('\nTOP SCORES:')
for (a, e), n in sc.most_common(6):
    print(f"  {a}-{e}: {n/N*100:.1f}%")
