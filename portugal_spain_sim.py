#!/usr/bin/env python3
"""Ensemble MC: Portugal vs Spain — WC2026 R16, 06/07/2026 AT&T Stadium."""

import math
import random
from collections import Counter

random.seed(20260706)
N = 100_000

# --- Calibration (WC2026 group + knockout + market + H2H) ---
# Spain: 3-0-0, 7GF 0GA; xG dominance; unbeaten 34 competitive
# Portugal: 2-1-0, beat Croatia 2-1 R32; xG solid; Nations League final pens vs ESP
# Market 90': ESP 1.98 / Draw 3.40 / POR 4.35 → fav ESP ~50%, draw ~29%, POR ~23%
# Knockout Iberian derby: lower variance, tactical caution, ET/pens common

LAMBDAS = [
    (1.18, 1.42),   # xG + tournament form (Spain elite defense)
    (1.05, 1.55),   # market-implied de-vigged
    (1.12, 1.38),   # knockout regression (tighter)
    (1.22, 1.35),   # H2H / derby (more balanced, pens 2025)
]
WEIGHTS = [0.30, 0.30, 0.25, 0.15]

# Penalty shootout: slight Spain edge in quality depth
PEN_ESP = 0.54

# Corner model (incl. ET per Betclic "Prolongamento incluído")
CORNER_MEANS = [
    (4.2, 5.8, 10.0),   # possession-dominant Spain
    (4.5, 5.5, 10.0),   # balanced
    (3.8, 6.2, 10.0),   # Spain heavy territorial
]
CORNER_W = [0.40, 0.35, 0.25]

# Shots on target model
SOT_MEANS = [(2.8, 4.8), (3.0, 5.0), (2.6, 5.2)]
SOT_W = [0.40, 0.35, 0.25]


def poisson(lam):
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def pick_goals_lambda():
    i = random.choices(range(len(LAMBDAS)), weights=WEIGHTS, k=1)[0]
    px, sx = LAMBDAS[i]
    kf = random.gauss(0.90, 0.04)  # knockout intensity
    return max(0.30, px * kf * random.gauss(1.0, 0.07)), max(0.30, sx * kf * random.gauss(1.0, 0.07))


def simulate_match():
  px, sx = pick_goals_lambda()
  p90, s90 = poisson(px), poisson(sx)
  p1, s1 = poisson(px * 0.44), poisson(sx * 0.42)
  p2, s2 = poisson(px * 0.56), poisson(sx * 0.58)
  tg1 = p1 + s1
  tg2 = p2 + s2
  res90 = 'P' if p90 > s90 else ('S' if s90 > p90 else 'D')
  res1 = 'P' if p1 > s1 else ('S' if s1 > p1 else 'D')
  res2 = 'P' if p2 > s2 else ('S' if s2 > p2 else 'D')

  # ET if draw
  pet = set_ = 0
  qual = res90
  if res90 == 'D':
    pet = poisson(px * 0.38)
    set_ = poisson(sx * 0.38)
    pt, st = p90 + pet, s90 + set_
    if pt > st:
      qual = 'P'
    elif st > pt:
      qual = 'S'
    else:
      qual = 'S' if random.random() < PEN_ESP else 'P'

  tg = p90 + s90
  tg_et = tg + pet + set_

  return {
    'p90': p90, 's90': s90, 'tg': tg, 'tg_et': tg_et,
    'p1': p1, 's1': s1, 'p2': p2, 's2': s2, 'tg1': tg1, 'tg2': tg2,
    'res90': res90, 'qual': qual,
    'res1': res1, 'res2': res2,
    'btts': p90 > 0 and s90 > 0,
    'p_o05': p90 >= 1, 's_o05': s90 >= 1,
    'p_u15': p90 <= 1, 's_u15': s90 <= 1,
    'x2': res90 in ('S', 'D'),
    'x12': res90 in ('P', 'S'),
    'x1': res90 in ('P', 'D'),
    'esp_dnb': res90 == 'S',
    'esp_dnb1': res1 == 'S',
    'esp_dnb2': res2 == 'S',
    'esp_win_either_half': res1 == 'S' or res2 == 'S',
    'por_win_either_half': res1 == 'P' or res2 == 'P',
    'esp_qual': qual == 'S',
    'o05': tg >= 1, 'o15': tg >= 2, 'o25': tg >= 3,
    'u15': tg <= 1, 'u25': tg <= 2, 'u35': tg <= 3, 'u45': tg <= 4,
    'u55': tg <= 5,
    'tg1_o05': tg1 >= 1, 'tg1_u15': tg1 <= 1,
    'tg2_o05': tg2 >= 1,
    'btts_or_o25': (p90 > 0 and s90 > 0) or tg >= 3,
    'x2_o15': res90 in ('S', 'D') and tg >= 2,
    'x2_u45': res90 in ('S', 'D') and tg <= 4,
    'x12_o15': res90 in ('P', 'S') and tg >= 2,
    'x12_u45': res90 in ('P', 'S') and tg <= 4,
    'x2_u35': res90 in ('S', 'D') and tg <= 3,
  }


def simulate_corners():
  i = random.choices(range(len(CORNER_MEANS)), weights=CORNER_W, k=1)[0]
  pm, sm, _ = CORNER_MEANS[i]
  noise = random.gauss(1.0, 0.12)
  pc = poisson(max(1.5, pm * noise))
  sc = poisson(max(2.0, sm * noise))
  tc = pc + sc
  # ET boost ~15% corners if close game (simplified: always small boost in KO)
  if random.random() < 0.28:
    tc += poisson(1.8)
    sc += poisson(1.1)
    pc += poisson(0.7)
  return {'pc': pc, 'sc': sc, 'tc': tc}


def simulate_sot():
  i = random.choices(range(len(SOT_MEANS)), weights=SOT_W, k=1)[0]
  pm, sm = SOT_MEANS[i]
  noise = random.gauss(1.0, 0.10)
  ps = poisson(max(1.0, pm * noise))
  ss = poisson(max(2.0, sm * noise))
  return {'ps': ps, 'ss': ss, 'ts': ps + ss}


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


# Betclic odds from user screenshots (06/07/2026)
MARKETS = [
  # Result / DC
  ('Portugal ou Espanha (12) — 90\'', 1.31, lambda r: r['x12'], 8),
  ('Empate ou Espanha (X2) — 90\'', 1.22, lambda r: r['x2'], 6),
  ('Espanha DNB — tempo reg.', 1.34, lambda r: r['esp_dnb'], 10),
  ('Espanha qualifica', 1.50, lambda r: r['esp_qual'], 14),
  ('Espanha DNB — 1.ª parte', 1.35, lambda r: r['esp_dnb1'], 18),
  ('Espanha DNB — 2.ª parte', 1.38, lambda r: r['esp_dnb2'], 18),
  ('Espanha ganha uma das partes — Sim', 1.37, lambda r: r['esp_win_either_half'], 16),
  ('Portugal ganha uma das partes — Não', 1.45, lambda r: not r['por_win_either_half'], 14),
  # DC + goals combos
  ('Espanha/Empate & Acima 1.5 golos', 1.40, lambda r: r['x2_o15'], 14),
  ('Espanha/Empate & Abaixo 4.5 golos', 1.32, lambda r: r['x2_u45'], 10),
  ('Espanha/Empate & Abaixo 3.5 golos', 1.38, lambda r: r['x2_u35'], 11),
  ('Portugal/Espanha & Acima 1.5 golos', 1.50, lambda r: r['x12_o15'], 12),
  ('Portugal/Espanha & Abaixo 4.5 golos', 1.42, lambda r: r['x12_u45'], 9),
  # Goals
  ('Under 3.5 golos — 90\'', 1.36, lambda r: r['u35'], 12),
  ('BTTS ou Acima 2.5 — Sim', 1.42, lambda r: r['btts_or_o25'], 20),
  ('Acima 0.5 golos — 1.ª parte', 1.31, lambda r: r['tg1_o05'], 14),
  ('Abaixo 1.5 golos — 1.ª parte', 1.35, lambda r: r['tg1_u15'], 16),
  ('Portugal Acima 0.5 golos', 1.37, lambda r: r['p_o05'], 18),
  ('Portugal Abaixo 1.5 golos', 1.32, lambda r: r['p_u15'], 14),
  ('Portugal Abaixo 0.5 golos — 1.ª parte', 1.45, lambda r: r['p1'] == 0, 22),
  ('Espanha Acima 0.5 golos — 2.ª parte', 1.45, lambda r: r['s2'] >= 1, 20),
]

# Fix corner markets - need separate evaluation
CORNER_MARKETS = [
  ('Total cantos Acima 9.5', 1.32, lambda c: c['tc'] > 9.5, 28),
  ('Portugal cantos Acima 3.5', 1.35, lambda c: c['pc'] > 3.5, 30),
  ('Total cantos Abaixo 11.5', 1.42, lambda c: c['tc'] < 11.5, 26),
  ('Espanha cantos Acima 5.5', 1.52, lambda c: c['sc'] > 5.5, 32),
]

SOT_MARKETS = [
  ('Total remates à baliza Acima 8.5', 1.38, lambda s: s['ts'] > 8.5, 24),
  ('Espanha remates à baliza Abaixo 6.5', 1.38, lambda s: s['ss'] < 6.5, 26),
  ('Portugal remates à baliza Acima 2.5', 1.28, lambda s: s['ps'] > 2.5, 22),
]

print('=' * 95)
print('PORTUGAL vs SPAIN — ENSEMBLE MC N=100,000 | WC2026 R16 | AT&T Stadium 06/07/2026')
print('=' * 95)

pw = pct(lambda r: r['res90'] == 'P')
dw = pct(lambda r: r['res90'] == 'D')
sw = pct(lambda r: r['res90'] == 'S')
print(f"90' Result: Portugal {pw:.1f}% | Draw {dw:.1f}% | Spain {sw:.1f}%")
print(f"Spain qualify: {pct(lambda r: r['esp_qual']):.1f}%")
print(f"Avg goals: POR {sum(r['p90'] for r in res)/N:.2f} | ESP {sum(r['s90'] for r in res)/N:.2f} | Total {sum(r['tg'] for r in res)/N:.2f}")
print(f"BTTS: {pct(lambda r: r['btts']):.1f}% | O2.5: {pct(lambda r: r['o25']):.1f}% | U2.5: {pct(lambda r: r['u25']):.1f}% | U3.5: {pct(lambda r: r['u35']):.1f}% | U4.5: {pct(lambda r: r['u45']):.1f}%")

sc = Counter((r['p90'], r['s90']) for r in res)
print('\nTOP SCORELINES (90\'):')
for (p, s), c in sc.most_common(10):
  print(f'  {p}-{s}: {c/N*100:.1f}%')

avg_tc = sum(c['tc'] for c in corners) / N
print(f'\nAvg corners (ET incl.): POR {sum(c["pc"] for c in corners)/N:.2f} | ESP {sum(c["sc"] for c in corners)/N:.2f} | Total {avg_tc:.2f}')

rows = []
for name, odd, fn, struct in MARKETS:
  p = pct(fn)
  lo, hi = ci(p)
  impl = 100 / odd
  risk, vol, conf = scores(struct, p, odd)
  rows.append((p, name, odd, lo, hi, impl, risk, vol, conf, p >= 75))

for name, odd, fn, struct in CORNER_MARKETS:
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

rows = [r for r in rows if 1.30 <= r[2] <= 1.50]
rows.sort(reverse=True)

print('\nBETCLIC RANGE 1.30-1.50 — RANKING')
print(f"{'#':<3} {'Market':<42} {'Odd':>5} {'Model':>7} {'CI95':>12} {'Impl':>6} {'Risk':>5} {'Vol':>5} {'Conf':>5} {'75%':>5}")
for i, r in enumerate(rows, 1):
  p, name, odd, lo, hi, impl, risk, vol, conf, ok = r
  print(f"{i:<3} {name:<42} {odd:>5.2f} {p:>6.1f}% [{lo:.0f}-{hi:.0f}] {impl:>5.1f}% {risk:>5} {vol:>5} {conf:>5} {'YES' if ok else 'NO':>5}")

pass75 = [r for r in rows if r[9]]
print(f'\nPASS75 (>=75% model): {len(pass75)}')
for r in pass75:
  print(f"  ★ {r[1]} @ {r[2]:.2f} → {r[0]:.1f}%")

if pass75:
  best = pass75[0]
  print(f'\nBEST BET: {best[1]} @ {best[2]:.2f} | Model {best[0]:.1f}% | Implied {best[5]:.1f}%')
else:
  print('\nNO BET — no market in 1.30-1.50 reaches 75% model probability')
