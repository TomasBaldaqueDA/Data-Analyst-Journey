#!/usr/bin/env python3
"""Wimbledon 07/07/2026 — Betclic OFFICIAL odds · 50k MC."""

import math
import random

random.seed(20260707)
N = 50_000


def bo3(pw, p20, p21=0.12):
  if random.random() > pw:
    return {
      'sc': '1-2' if random.random() < 0.62 else '0-2',
      'tg': (26 + random.randint(0, 8)) if random.random() < 0.62 else (16 + random.randint(0, 6)),
      'gm': -random.randint(1, 5),
      'tb': random.random() < 0.22,
    }
  if random.random() < p20:
    return {'sc': '2-0', 'tg': 18 + random.randint(0, 8), 'gm': 5 + random.randint(0, 6), 'tb': False}
  return {'sc': '2-1', 'tg': 26 + random.randint(0, 10), 'gm': 2 + random.randint(0, 4), 'tb': random.random() < 0.35}


def bo5(pw, p30, p31):
  if random.random() > pw:
    r = random.random()
    if r < 0.4:
      return {'sc': '2-3', 'tg': 32 + random.randint(0, 10), 'wset': True, 'm2': False}
    if r < 0.7:
      return {'sc': '1-3', 'tg': 28 + random.randint(0, 8), 'wset': True, 'm2': False}
    return {'sc': '0-3', 'tg': 22 + random.randint(0, 6), 'wset': False, 'm2': False}
  r = random.random()
  if r < p30:
    return {'sc': '3-0', 'tg': 26 + random.randint(0, 8), 'wset': True, 'm2': True}
  if r < p30 + p31:
    return {'sc': '3-1', 'tg': 32 + random.randint(-2, 10), 'wset': True, 'm2': True}
  return {'sc': '3-2', 'tg': 38 + random.randint(0, 12), 'wset': True, 'm2': False}


def run_bo3(pw, p20, n=N):
  return [bo3(pw, p20) for _ in range(n)]


def run_bo5(pw, p30, p31, n=N):
  return [bo5(pw, p30, p31) for _ in range(n)]


def pct(res, fn):
  return sum(fn(r) for r in res) / len(res) * 100


def ci(p):
  p /= 100
  z, n = 1.96, N
  d = 1 + z * z / n
  c = (p + z * z / (2 * n)) / d
  m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
  return max(0, (c - m) * 100), min(100, (c + m) * 100)


def add(rows, pick, match, odd, prob, mtype='set'):
  if not (1.30 <= odd <= 1.50):
    return
  impl = 100 / odd
  struct = {'ml': 18, 'hcap': 22, 'set': 28, 'games': 38, '1st': 32}.get(mtype, 30)
  vol = max(0, min(100, 100 - prob + struct * 0.3))
  conf = max(0, min(100, prob - abs(prob - impl) * 0.28 - struct * 0.15))
  lo, hi = ci(prob)
  rows.append({
    'pick': pick, 'match': match, 'odd': odd, 'prob': prob,
    'lo': lo, 'hi': hi, 'impl': impl, 'edge': prob - impl, 'conf': round(conf),
    'pass75': prob >= 75, 'risk': round(vol + (100 - prob) * 0.45), 'mtype': mtype,
  })


rows = []

# WD R16 — Dabrowski/Stefani ML @1.30 (Betclic)
s = run_bo3(0.77, 0.48)
add(rows, 'Dabrowski/Stefani ML', 'Dab/Stef–McN/Hunt', 1.30, pct(s, lambda r: r['sc'].startswith('2')), 'ml')

# WS QF — Osaka (ML 1.74) vs Muchova (ML 1.98)
s = run_bo3(0.58, 0.30)
add(rows, 'Muchova +1.5 sets', 'Osaka–Muchova', 1.40,
    pct(s, lambda r: r['sc'] in ('0-2', '1-2', '2-1')), 'hcap')
add(rows, 'Osaka +1.5 sets', 'Osaka–Muchova', 1.30,
    pct(s, lambda r: r['sc'] in ('2-0', '2-1', '1-2')), 'hcap')
add(rows, 'Under 2.5 sets', 'Osaka–Muchova', 1.49,
    pct(s, lambda r: r['sc'] in ('2-0', '0-2')), 'set')
add(rows, 'Sem tie-break', 'Osaka–Muchova', 1.40,
    pct(s, lambda r: not r['tb']), 'set')
add(rows, 'Over 20.5 jogos', 'Osaka–Muchova', 1.37,
    pct(s, lambda r: r['tg'] > 20.5), 'games')
add(rows, 'Over 21.5 jogos', 'Osaka–Muchova', 1.49,
    pct(s, lambda r: r['tg'] > 21.5), 'games')
add(rows, 'Under 26.5 jogos', 'Osaka–Muchova', 1.40,
    pct(s, lambda r: r['tg'] < 26.5), 'games')
add(rows, 'Under 25.5 jogos', 'Osaka–Muchova', 1.50,
    pct(s, lambda r: r['tg'] < 25.5), 'games')
add(rows, 'Muchova +3.5 jogos HC', 'Osaka–Muchova', 1.46,
    pct(s, lambda r: r['gm'] < 3.5), 'games')
add(rows, 'Muchova +4.5 jogos HC', 'Osaka–Muchova', 1.30,
    pct(s, lambda r: r['gm'] < 4.5), 'games')
add(rows, 'Osaka +1.5 jogos 1º set', 'Osaka–Muchova', 1.45, 72.0, '1st')

# WS QF — Gauff (fav ~54%) vs Pegula
s = run_bo3(0.54, 0.26)
add(rows, 'Pegula +1.5 sets', 'Pegula–Gauff', 1.49,
    pct(s, lambda r: r['sc'] in ('2-1', '1-2', '0-2')), 'hcap')
add(rows, 'Sem tie-break', 'Pegula–Gauff', 1.40,
    pct(s, lambda r: not r['tb']), 'set')
add(rows, 'Over 20.5 jogos', 'Pegula–Gauff', 1.43,
    pct(s, lambda r: r['tg'] > 20.5), 'games')
add(rows, 'Under 25.5 jogos', 'Pegula–Gauff', 1.46,
    pct(s, lambda r: r['tg'] < 25.5), 'games')
add(rows, 'Under 26.5 jogos', 'Pegula–Gauff', 1.37,
    pct(s, lambda r: r['tg'] < 26.5), 'games')
add(rows, 'Gauff +4.5 jogos HC', 'Pegula–Gauff', 1.31,
    pct(s, lambda r: r['gm'] > -4.5), 'games')
add(rows, 'Pegula +1.5 jogos 1º set', 'Pegula–Gauff', 1.42, 70.0, '1st')

# MS QF — Sinner vs Struff
s = run_bo5(0.91, 0.46, 0.32)
add(rows, 'Sinner -1.5 sets', 'Sinner–Struff', 1.42,
    pct(s, lambda r: r['m2']), 'hcap')

# MS QF — Djokovic vs FAA
s = run_bo5(0.66, 0.28, 0.26)
add(rows, 'Djokovic ganha ≥1 set', 'Djokovic–FAA', 1.38,
    pct(s, lambda r: r['wset']), 'set')

# MD QF — Heli/Patten vs Andreozzi/Guinard
s = run_bo3(0.829, 0.48)
add(rows, 'Heli/Patten 1.º set', 'Heli/Patten–A/G', 1.32,
    pct(s, lambda r: r['sc'].startswith('2')) * 0.84, '1st')

# Dedupe
best = {}
for r in rows:
  k = (r['pick'], r['odd'], r['match'])
  if k not in best or r['prob'] > best[k]['prob']:
    best[k] = r
rows = sorted(best.values(), key=lambda x: (-x['prob'], -x['conf']))

print('=' * 105)
print('WIMBLEDON 07/07/2026 — BETCLIC OFICIAL · 1.30–1.50 · 50k MC')
print('=' * 105)
print(f"{'#':<3} {'Pick':<32} {'Match':<18} {'Odd':>5} {'Model':>7} {'CI95':>11} {'Edge':>7} {'Conf':>5} {'75%':>5}")
for i, r in enumerate(rows, 1):
  print(f"{i:<3} {r['pick']:<32} {r['match']:<18} @{r['odd']:.2f} {r['prob']:>6.1f}% "
        f"[{r['lo']:.0f}-{r['hi']:.0f}] {r['edge']:>+6.1f}pp {r['conf']:>5} "
        f"{'YES' if r['pass75'] else 'NO':>5}")

p75 = [r for r in rows if r['pass75']]
print(f'\nPASS75: {len(p75)}')
for r in p75:
  print(f"  ★ {r['pick']} @{r['odd']:.2f} → {r['prob']:.1f}% (edge {r['edge']:+.1f}pp, conf {r['conf']})")

if p75:
  # Prefer structural bets (ML/hcap/set) over games for "safest"
  struct = [r for r in p75 if r['mtype'] in ('ml', 'hcap', 'set')]
  pool = struct if struct else p75
  b = max(pool, key=lambda x: (x['conf'], x['edge']))
  print(f"\n>>> BEST (estrutural): {b['pick']} @{b['odd']:.2f} — {b['prob']:.1f}% | conf {b['conf']}")
  bg = max([r for r in p75 if r['mtype'] == 'games'] or p75, key=lambda x: (x['conf'], x['edge']))
  print(f">>> BEST jogos: {bg['pick']} @{bg['odd']:.2f} — {bg['prob']:.1f}% | conf {bg['conf']}")
else:
  print('\n>>> NO BET')

print('\n--- FORA DA GAMA 1.30–1.50 (info) ---')
print('Sin/Tow ML @1.05 (~92% modelo) | 2-0 @1.25 | -1.5 sets @1.25 | U2.5 sets @1.19')
print('Heli/Patten ML @1.22 (~83%) | Sinner ML ~1.14 (~91%) | Djokovic ML ~1.52')
