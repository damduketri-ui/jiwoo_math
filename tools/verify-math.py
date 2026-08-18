#!/usr/bin/env python3
"""자료에 실린 값과 주장을 식으로 되짚어 확인한다.

    python3 tools/verify-math.py

표준 라이브러리만 쓴다(설치 없이 돌아가야 한다).
새 챕터를 쓰면 check_NN_...() 를 만들어 main() 에 등록할 것.

확인 방식은 두 가지다.
  1. 대수 항등식  — 여러 x에 대입해 좌변과 우변이 같은지
  2. 완력 표본    — 최대·최소라고 게시한 값이 정말 그 구간의 최대·최소인지
     (공식을 다시 쓰는 게 아니라, 공식을 안 쓰고 세어 보는 방식이라야 검산이 된다)
"""

import math

TOL = 1e-9


def frange(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


def ok_mark(hit):
    return '✓' if hit else '✗ 불일치'


# ══════════ 01 이차함수의 최대·최소 ════════════════════════════════
# 근거: 2022 개정 교육과정 「공통수학1」 방정식과 부등식
#       완전제곱식  ax²+bx+c = a(x + b/2a)² − (b²−4ac)/4a   (a ≠ 0)

def vertex(a, b, c):
    """꼭짓점 (−b/2a, −D/4a) — 자료가 유도한 공식 그대로"""
    d = b * b - 4 * a * c
    return -b / (2 * a), -d / (4 * a)


def brute_extreme(a, b, c, lo, hi, n=400_000):
    """공식을 쓰지 않고 구간을 훑어 최대·최소를 찾는다 (검산의 기준선)"""
    best = worst = None
    for x in frange(lo, hi, n):
        y = a * x * x + b * x + c
        if best is None or y > best[1]:
            best = (x, y)
        if worst is None or y < worst[1]:
            worst = (x, y)
    return best, worst


# 자료에 게시된 값 ─────────────────────────────────────────────
PUB_VERTEX = (3.0, -4.0)          # y = x²−6x+5 → (x−3)²−4
PUB_ROOTS = (1.0, 5.0)
PUB_D = 16.0

# (범위, 최댓값, 최댓값의 x, 최솟값, 최솟값의 x)
PUB_RANGES = [
    ((0, 2),  5.0, 0.0, -3.0, 2.0),
    ((2, 6),  5.0, 6.0, -4.0, 3.0),
    ((4, 6),  5.0, 6.0, -3.0, 4.0),
]

# 그림에 손으로 박아 넣은 픽셀 좌표 — 매핑식으로 되짚는다
#   그림1  X(x) = 140 + 30x, Y(y) = 240 − 30y
#   그림3  X(x) =  76 + 30x, Y(y) = 240 − 30y
PUB_PIXELS = [
    ("그림1 꼭짓점 (0,0)",   1, (0, 0),   (140, 240)),
    ("그림1 꼭짓점 (3,−4)",  1, (3, -4),  (230, 360)),
    ("그림1 근 (1,0)",       1, (1, 0),   (170, 240)),
    ("그림1 근 (5,0)",       1, (5, 0),   (290, 240)),
    ("그림1 y절편 (0,5)",    1, (0, 5),   (140, 90)),
    ("그림3 꼭짓점 (3,−4)",  3, (3, -4),  (166, 360)),
    ("그림3 f(0)=5",         3, (0, 5),   (76, 90)),
    ("그림3 f(2)=−3",        3, (2, -3),  (136, 330)),
    ("그림3 f(6)=5",         3, (6, 5),   (256, 90)),
    ("그림3 원점",           3, (0, 0),   (76, 240)),
]


def check_01_identity():
    """① ax²+bx+c 와 완전제곱식이 정말 같은 식인가"""
    ok = True
    print("\n[01] 완전제곱식 항등 확인 — 두 표현이 모든 x에서 같은 값인가")
    cases = [(1, -6, 5), (1, 0, 0), (2, 5, -3), (-1, 4, 1), (-0.5, 3, 7), (3, -7, 2)]
    for a, b, c in cases:
        p, q = vertex(a, b, c)
        worst = max(abs((a * x * x + b * x + c) - (a * (x - p) ** 2 + q))
                    for x in frange(-12, 12, 2000))
        hit = worst < 1e-9
        ok &= hit
        print(f"  a={a:>5} b={b:>5} c={c:>5} → y = {a}(x − {p:.4g})² + {q:.4g}"
              f"   최대오차 {worst:.2e}  {ok_mark(hit)}")
    return ok


def check_01_vertex_is_extreme():
    """② 꼭짓점이 정말 최대·최소인가 — 공식을 안 쓰고 훑어서 확인"""
    ok = True
    print("\n[01] 꼭짓점 = 실수 전체에서의 최대·최소 (완력 표본과 대조)")
    for a, b, c in [(1, -6, 5), (2, 5, -3), (-1, 4, 1), (-0.5, 3, 7)]:
        p, q = vertex(a, b, c)
        best, worst = brute_extreme(a, b, c, p - 20, p + 20, 200_000)
        got = worst if a > 0 else best          # a>0 이면 최소, a<0 이면 최대
        hit = abs(got[0] - p) < 1e-3 and abs(got[1] - q) < 1e-6
        ok &= hit
        kind = '최솟값' if a > 0 else '최댓값'
        print(f"  a={a:>5} b={b:>5} c={c:>5} → 공식 {kind} {q:>9.4f} (x={p:.4f}) / "
              f"표본 {got[1]:>9.4f} (x={got[0]:.4f})  {ok_mark(hit)}")
    return ok


def check_01_discriminant():
    """③ q = −D/4a 이고, D의 부호가 x축과의 교점 수를 그대로 말하는가"""
    ok = True
    print("\n[01] 꼭짓점 y좌표와 판별식 — q = −D/4a,  a>0이면 (D>0 ⟺ q<0)")
    bad = 0
    for a in [x / 4 for x in range(-8, 9)]:
        if a == 0:
            continue
        for b in range(-6, 7):
            for c in range(-6, 7):
                d = b * b - 4 * a * c
                p, q = vertex(a, b, c)
                if abs(q - (-d / (4 * a))) > TOL:
                    bad += 1
                # a>0: 접시 바닥이 x축 아래(q<0) ⟺ 두 점에서 만난다(D>0)
                if a > 0 and (d > TOL) != (q < -TOL):
                    bad += 1
                if a < 0 and (d > TOL) != (q > TOL):
                    bad += 1
    hit = bad == 0
    ok &= hit
    print(f"  a·b·c 격자 {17 * 13 * 13 - 13 * 13}가지 전수 확인, 어긋난 경우 {bad}건  {ok_mark(hit)}")

    p, q = vertex(1, -6, 5)
    d = (-6) ** 2 - 4 * 1 * 5
    r = [(6 - math.sqrt(d)) / 2, (6 + math.sqrt(d)) / 2]
    for lab, got, want in [("게시 꼭짓점 x", p, PUB_VERTEX[0]),
                           ("게시 꼭짓점 y", q, PUB_VERTEX[1]),
                           ("게시 D", d, PUB_D),
                           ("게시 근 작은쪽", r[0], PUB_ROOTS[0]),
                           ("게시 근 큰쪽", r[1], PUB_ROOTS[1])]:
        h = abs(got - want) < 1e-9
        ok &= h
        print(f"  {lab:<16} {got:>8.4f}  게시 {want:<8} {ok_mark(h)}")
    return ok


def check_01_restricted():
    """④ 범위가 잘렸을 때의 표 — 게시한 최대·최소가 정말 그 구간의 값인가"""
    ok = True
    print("\n[01] 제한된 범위에서의 최대·최소 (y = x²−6x+5, 완력 표본과 대조)")
    for (lo, hi), pmax, pxmax, pmin, pxmin in PUB_RANGES:
        best, worst = brute_extreme(1, -6, 5, lo, hi, 400_000)
        hit = (abs(best[1] - pmax) < 1e-6 and abs(best[0] - pxmax) < 1e-4 and
               abs(worst[1] - pmin) < 1e-6 and abs(worst[0] - pxmin) < 1e-4)
        ok &= hit
        inside = lo <= PUB_VERTEX[0] <= hi
        print(f"  {lo} ≤ x ≤ {hi}  꼭짓점 {'안' if inside else '밖'}   "
              f"최대 {best[1]:>6.3f}(x={best[0]:.3f}) 게시 {pmax}(x={pxmax})   "
              f"최소 {worst[1]:>6.3f}(x={worst[0]:.3f}) 게시 {pmin}(x={pxmin})  {ok_mark(hit)}")

    # 자료의 주장: [0,2]와 [4,6]은 대칭축 x=3에 대해 거울상이라 값이 같다
    a1 = brute_extreme(1, -6, 5, 0, 2, 200_000)
    a2 = brute_extreme(1, -6, 5, 4, 6, 200_000)
    mirror = (abs(a1[0][1] - a2[0][1]) < 1e-6 and abs(a1[1][1] - a2[1][1]) < 1e-6 and
              abs((3 - a1[0][0]) - (a2[0][0] - 3)) < 1e-3)
    ok &= mirror
    print(f"  [0,2]와 [4,6]은 x=3에 대한 거울상 — 값 같고 위치 뒤바뀜  {ok_mark(mirror)}")

    # 자료의 주장: 꼭짓점이 범위 밖이면 답은 반드시 양 끝점에서 나온다
    off = 0
    for lo in range(-2, 3):
        for w in (1, 2, 3):
            hi = lo + w
            if lo <= 3 <= hi:
                continue
            best, worst = brute_extreme(1, -6, 5, lo, hi, 100_000)
            for x, _ in (best, worst):
                if min(abs(x - lo), abs(x - hi)) > 1e-4:
                    off += 1
    ok &= off == 0
    print(f"  꼭짓점 밖 구간에서 최대·최소는 항상 양 끝점 — 예외 {off}건  {ok_mark(off == 0)}")
    return ok


def check_01_pixels():
    """⑤ 그림에 박아 넣은 픽셀 좌표가 캡션의 매핑식과 맞는가"""
    ok = True
    print("\n[01] SVG 좌표 검산 — 그림1 X=140+30x · 그림3 X=76+30x · 공통 Y=240−30y")
    for lab, fig, (x, y), (px, py) in PUB_PIXELS:
        gx = (140 if fig == 1 else 76) + 30 * x
        gy = 240 - 30 * y
        hit = abs(gx - px) < 0.5 and abs(gy - py) < 0.5
        ok &= hit
        print(f"  {lab:<20} 계산 ({gx:>6.1f},{gy:>6.1f})  게시 ({px},{py})  {ok_mark(hit)}")
    return ok


# ══════════ b01 중선정리 ══════════════════════════════════════════
# 근거: M이 선분 BC의 중점이면  AB² + AC² = 2(AM² + BM²)
#       (평면 위의 점이기만 하면 되고, 삼각형이 아니어도 성립한다)
# 검산 방식: 정리를 다시 쓰지 않는다. 좌표에서 거리를 직접 재서 양변을 따로 계산한다.


def d2(p, q):
    """두 점 사이 거리의 제곱 — 피타고라스만 쓴다"""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def mid(p, q):
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


def tri_coords(ab, ac, bc):
    """세 변의 길이에서 좌표를 만든다 — B(0,0), C(bc,0), A는 거리 조건으로 결정
       x = (AB² − AC² + BC²)/(2·BC),  y = √(AB² − x²)   (중선 공식을 쓰지 않는다)"""
    x = (ab * ab - ac * ac + bc * bc) / (2 * bc)
    y = math.sqrt(ab * ab - x * x)
    return (x, y), (0.0, 0.0), (float(bc), 0.0)


def roots_of(g, lo, hi, n=200_000):
    """g(t) = 0 인 t를 완력으로 찾는다 (근의 공식을 쓰지 않는다)"""
    step, found, prev = (hi - lo) / n, [], g(lo)
    for i in range(1, n + 1):
        t = lo + (hi - lo) * i / n
        cur = g(t)
        if abs(cur) < 1e-12:
            found.append(t)
        elif prev * cur < 0:
            a, b = t - step, t
            for _ in range(80):
                m = (a + b) / 2
                if g(a) * g(m) <= 0:
                    b = m
                else:
                    a = m
            found.append((a + b) / 2)
        prev = cur
    out = []
    for r in found:
        if not any(abs(r - o) < 1e-6 for o in out):
            out.append(r)
    return sorted(out)


# 자료에 게시된 값 ─────────────────────────────────────────────
PUB_B01_T1 = (13.0, 9.0, 10.0, 10.0)        # AB, AC, BC, 중선 AM
PUB_B01_T1_SUM = 250.0                       # 양변의 값
PUB_B01_T1_XY = (9.4, 80.64)                 # A의 x좌표, y²  (그림1·그림3)
PUB_B01_WRONG = {                            # 자료가 "틀렸다"고 게시한 값들
    '길이끼리 더하기 AB+AC': 22.0,
    '길이끼리 더하기 2(AM+BM)': 30.0,
    '수선의 발 H로 2(AH²+BH²)': 338.0,
    'BM 자리에 BC 2(AM²+BC²)': 400.0,
    '올바른 다른 형태 2AM²+BC²/2': 250.0,
}
PUB_B01_MEDIANS = [                          # (AB, AC, BC, 게시한 AM²)
    (13, 9, 10, 100),
    (6, 8, 10, 25),
    (5, 5, 6, 16),
    (7, 5, 8, 21),
]
PUB_B01_T2 = ((8.0, 6.0), (0.0, 0.0), (6.0, 0.0))   # 그림4의 A, B, C
PUB_B01_T2_LHS = 140.0
PUB_B01_T2_ROWS = [                          # (t, BM, MC, AM², 오른쪽)
    (3, 3, 3, 61, 140),
    (4, 4, 2, 52, 136),
    (5, 5, 1, 45, 140),
    (0, 0, 6, 100, 200),
]
PUB_B01_T2_ROOTS = (3.0, 5.0)                # 등식이 성립하는 t — 자료가 두 개라고 주장
PUB_B01_PARA = (500.0, 500.0)                # 네 변의 제곱의 합 · 두 대각선의 제곱의 합

# 그림에 손으로 박아 넣은 픽셀 좌표 — 캡션·주석의 매핑식으로 되짚는다
#   그림1  X(x) =  60 + 30x,  Y(y) = 330 − 30y
#   그림2  X(x) = 230 + 30x,  Y(y) = 330 − 30y   (그림용 위치 m=5, A(1.5, 8))
#   그림3  X(x) =  60 + 20x,  Y(y) = 250 − 20y
#   그림4  X(x) =  90 + 36x,  Y(y) = 300 − 36y
_Y1 = math.sqrt(80.64)
PUB_B01_PIXELS = [
    ("그림1 B(0,0)",        60, 30, 330, 30, (0, 0),        (60, 330)),
    ("그림1 C(10,0)",       60, 30, 330, 30, (10, 0),       (360, 330)),
    ("그림1 M(5,0)",        60, 30, 330, 30, (5, 0),        (210, 330)),
    ("그림1 A(9.4,√80.64)", 60, 30, 330, 30, (9.4, _Y1),    (342, 60.6)),
    ("그림2 B(−5,0)",      230, 30, 330, 30, (-5, 0),       (80, 330)),
    ("그림2 M(0,0)",       230, 30, 330, 30, (0, 0),        (230, 330)),
    ("그림2 C(5,0)",       230, 30, 330, 30, (5, 0),        (380, 330)),
    ("그림2 A(1.5,8)",     230, 30, 330, 30, (1.5, 8),      (275, 90)),
    ("그림2 H(1.5,0)",     230, 30, 330, 30, (1.5, 0),      (275, 330)),
    ("그림3 B(0,0)",        60, 20, 250, 20, (0, 0),        (60, 250)),
    ("그림3 C(10,0)",       60, 20, 250, 20, (10, 0),       (260, 250)),
    ("그림3 M(5,0)",        60, 20, 250, 20, (5, 0),        (160, 250)),
    ("그림3 A(9.4,√80.64)", 60, 20, 250, 20, (9.4, _Y1),    (248, 70.4)),
    ("그림3 D(0.6,−√80.64)", 60, 20, 250, 20, (0.6, -_Y1),  (72, 429.6)),
    ("그림4 B(0,0)",        90, 36, 300, 36, (0, 0),        (90, 300)),
    ("그림4 C(6,0)",        90, 36, 300, 36, (6, 0),        (306, 300)),
    ("그림4 A(8,6)",        90, 36, 300, 36, (8, 6),        (378, 84)),
    ("그림4 중점(3,0)",     90, 36, 300, 36, (3, 0),        (198, 300)),
    ("그림4 반례(5,0)",     90, 36, 300, 36, (5, 0),        (270, 300)),
]


def check_b01_theorem():
    """① 중선정리 자체 — 격자점 배치를 전수로 훑어 양변을 따로 재서 비교"""
    print("\n[b01] 중선정리 전수 확인 — M이 BC의 중점이면 AB²+AC² = 2(AM²+BM²)")
    R = range(-3, 4)
    worst, total, degen = 0.0, 0, 0
    for ax in R:
        for ay in R:
            A = (ax, ay)
            for bx in R:
                for by in R:
                    B = (bx, by)
                    for cx in R:
                        for cy in R:
                            C = (cx, cy)
                            M = mid(B, C)
                            lhs = d2(A, B) + d2(A, C)
                            rhs = 2 * (d2(A, M) + d2(B, M))
                            worst = max(worst, abs(lhs - rhs))
                            total += 1
                            # 세 점이 한 직선 위에 있는 경우(삼각형이 아닌 경우)
                            if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) == 0:
                                degen += 1
    hit = worst < TOL
    print(f"  배치 {total}가지 (그중 삼각형이 아닌 일직선 배치 {degen}가지 포함)")
    print(f"  최대 오차 {worst:.2e}  {ok_mark(hit)}")
    print(f"  → 자료의 주장 '삼각형이 아니어도 성립한다'가 {degen}가지 배치에서 확인됨  {ok_mark(hit)}")
    return hit


def check_b01_numbers():
    """② 자료에 실린 삼각형 (13, 9, 10) 의 값들"""
    ok = True
    print("\n[b01] 게시한 삼각형 AB=13 · AC=9 · BC=10 — 세 변에서 좌표를 만들고 거리를 직접 잰다")
    ab, ac, bc, am = PUB_B01_T1
    A, B, C = tri_coords(ab, ac, bc)
    M = mid(B, C)

    tri = (ab + ac > bc) and (ac + bc > ab) and (bc + ab > ac)
    ok &= tri
    print(f"  삼각형이 되는가 (두 변의 합 > 나머지 한 변)  {ok_mark(tri)}")

    for lab, got, want in [("A의 x좌표", A[0], PUB_B01_T1_XY[0]),
                           ("A의 y²", A[1] ** 2, PUB_B01_T1_XY[1]),
                           ("AB", math.sqrt(d2(A, B)), ab),
                           ("AC", math.sqrt(d2(A, C)), ac),
                           ("BC", math.sqrt(d2(B, C)), bc),
                           ("중선 AM", math.sqrt(d2(A, M)), am),
                           ("BM", math.sqrt(d2(B, M)), bc / 2)]:
        h = abs(got - want) < 1e-9
        ok &= h
        print(f"  {lab:<10} 잰 값 {got:>10.5f}  게시 {want:<8} {ok_mark(h)}")

    lhs, rhs = d2(A, B) + d2(A, C), 2 * (d2(A, M) + d2(B, M))
    for lab, got in [("왼쪽 AB²+AC²", lhs), ("오른쪽 2(AM²+BM²)", rhs)]:
        h = abs(got - PUB_B01_T1_SUM) < 1e-9
        ok &= h
        print(f"  {lab:<18} {got:>10.5f}  게시 {PUB_B01_T1_SUM}  {ok_mark(h)}")

    # 자료가 '틀렸다'고 게시한 값들 — 정말 그 값이 나오고, 정말 250과 다른가
    H = (A[0], 0.0)                                  # A에서 BC에 내린 수선의 발
    calc = {
        '길이끼리 더하기 AB+AC': ab + ac,
        '길이끼리 더하기 2(AM+BM)': 2 * (am + bc / 2),
        '수선의 발 H로 2(AH²+BH²)': 2 * (d2(A, H) + d2(B, H)),
        'BM 자리에 BC 2(AM²+BC²)': 2 * (d2(A, M) + bc * bc),
        '올바른 다른 형태 2AM²+BC²/2': 2 * d2(A, M) + bc * bc / 2,
    }
    for lab, want in PUB_B01_WRONG.items():
        got = calc[lab]
        same_as_250 = abs(got - PUB_B01_T1_SUM) < 1e-9
        should_match = lab.startswith('올바른')
        h = abs(got - want) < 1e-9 and (same_as_250 == should_match)
        ok &= h
        print(f"  {lab:<26} {got:>8.2f}  게시 {want:<7} "
              f"{'250과 같음' if same_as_250 else '250과 다름'}  {ok_mark(h)}")
    return ok


def check_b01_median_formula():
    """③ 중선의 길이 공식 AM² = (2AB²+2AC²−BC²)/4 — 표의 네 줄을 거리로 되짚는다"""
    ok = True
    print("\n[b01] 중선의 길이 표 — 공식이 아니라 좌표에서 잰 거리와 대조")
    for ab, ac, bc, pub in PUB_B01_MEDIANS:
        A, B, C = tri_coords(ab, ac, bc)
        got = d2(A, mid(B, C))
        h = abs(got - pub) < 1e-9
        ok &= h
        print(f"  AB={ab:>2} AC={ac:>2} BC={bc:>2} → 잰 AM² {got:>8.4f}  게시 {pub:<5} "
              f"AM = {math.sqrt(got):.5f}  {ok_mark(h)}")

    # 자료의 주장: ∠A = 90° 이면 AM = BM = MC = BC/2
    A, B, C = tri_coords(6, 8, 10)
    M = mid(B, C)
    right = abs(d2(A, B) + d2(A, C) - d2(B, C)) < 1e-9
    same = abs(d2(A, M) - d2(B, M)) < 1e-9 and abs(math.sqrt(d2(A, M)) - 5) < 1e-9
    ok &= right and same
    print(f"  (6,8,10)은 ∠A=90° {ok_mark(right)} · 이때 AM = BM = MC = 5 {ok_mark(same)}")

    # 자료의 주장: 삼각형이 되는 세 수라면 2AB²+2AC²−BC² ≥ 0 이라 AM²이 음수가 되지 않는다
    bad = 0
    for ab in range(1, 15):
        for ac in range(1, 15):
            for bc in range(1, 15):
                if ab + ac > bc and ac + bc > ab and bc + ab > ac:
                    if 2 * ab * ab + 2 * ac * ac - bc * bc < 0:
                        bad += 1
    ok &= bad == 0
    print(f"  삼각형이 되는 세 수 전수 확인 — AM²이 음수가 되는 경우 {bad}건  {ok_mark(bad == 0)}")
    return ok


def check_b01_converse():
    """④ 역 — '등식이 성립하면 중점'이 거짓이라는 것과 그 반례"""
    ok = True
    print("\n[b01] 역의 검토 — A(8,6) · B(0,0) · C(6,0) 에서 M(t,0)을 직선 위로 훑는다")
    A, B, C = PUB_B01_T2
    lhs = d2(A, B) + d2(A, C)
    h = abs(lhs - PUB_B01_T2_LHS) < 1e-9
    ok &= h
    print(f"  왼쪽 AB²+AC² = {lhs}  게시 {PUB_B01_T2_LHS} (M과 무관)  {ok_mark(h)}")

    def g(t):
        M = (t, 0.0)
        return 2 * (d2(A, M) + d2(B, M)) - lhs

    rs = roots_of(g, -20, 20)
    h = (len(rs) == 2 and abs(rs[0] - PUB_B01_T2_ROOTS[0]) < 1e-6
                     and abs(rs[1] - PUB_B01_T2_ROOTS[1]) < 1e-6)
    ok &= h
    print(f"  등식이 성립하는 t를 완력으로 탐색 → {[round(r, 6) for r in rs]}  게시 {list(PUB_B01_T2_ROOTS)}  {ok_mark(h)}")

    midt = (B[0] + C[0]) / 2
    h = abs(rs[0] - midt) < 1e-9 and abs(rs[1] - midt) > 1e-6
    ok &= h
    print(f"  중점은 t = {midt} 하나뿐인데 성립하는 자리는 둘 → 역은 거짓  {ok_mark(h)}")

    # 반례 t = 5 — BM으로는 성립하지만 MC로는 성립하지 않는다 (그래서 중점이 아니다)
    M5 = (5.0, 0.0)
    with_bm = 2 * (d2(A, M5) + d2(B, M5))
    with_cm = 2 * (d2(A, M5) + d2(C, M5))
    h = abs(with_bm - lhs) < 1e-9 and abs(with_cm - 92) < 1e-9 and abs(with_cm - lhs) > 1e-6
    ok &= h
    print(f"  반례 M(5,0): BM으로 {with_bm} (= 왼쪽) · MC로 {with_cm} (≠ 왼쪽)  게시 92  {ok_mark(h)}")

    # 표의 네 줄
    for t, bm, mc, am2, rhs in PUB_B01_T2_ROWS:
        M = (float(t), 0.0)
        g_bm, g_mc = math.sqrt(d2(B, M)), math.sqrt(d2(C, M))
        g_am2, g_rhs = d2(A, M), 2 * (d2(A, M) + d2(B, M))
        h = (abs(g_bm - bm) < 1e-9 and abs(g_mc - mc) < 1e-9
             and abs(g_am2 - am2) < 1e-9 and abs(g_rhs - rhs) < 1e-9)
        ok &= h
        print(f"  t={t:<2} BM {g_bm:>4.1f}/{bm:<2} MC {g_mc:>4.1f}/{mc:<2} "
              f"AM² {g_am2:>6.1f}/{am2:<4} 오른쪽 {g_rhs:>6.1f}/{rhs:<4} {ok_mark(h)}")

    # 자료가 주석에 남긴 일반형: 근은 t = a/2 (중점) 과 t = h − a/2 두 개다
    # (근이 하나로 겹치는 A의 x좌표 = BC 인 경우도 목록에 넣는다 — 곡선이 0에 닿기만 하는 자리)
    off, tangent = 0, 0
    for hx in (-3, -1, 0, 2, 3, 5, 6, 8):
        for ky in (1, 3):
            for a in (1, 2, 3, 6, 8):
                AA, BB, CC = (float(hx), float(ky)), (0.0, 0.0), (float(a), 0.0)
                L = d2(AA, BB) + d2(AA, CC)
                gg = lambda t: 2 * (d2(AA, (t, 0.0)) + d2(BB, (t, 0.0))) - L
                want = sorted({a / 2, hx - a / 2})       # 겹치면 하나로 줄어든다
                if len(want) == 1:
                    tangent += 1
                got = roots_of(gg, -15, 15, 30_000)      # 눈금 0.001 — 반정수를 정확히 지난다
                if len(got) != len(want) or any(abs(x - y) > 1e-5 for x, y in zip(got, want)):
                    off += 1
    ok &= off == 0
    print(f"  일반형 확인 — 근은 언제나 t = BC/2 와 t = (A의 x좌표) − BC/2 "
          f"(둘이 겹치는 경우 {tangent}건 포함), 어긋난 경우 {off}건  {ok_mark(off == 0)}")
    return ok


def check_b01_parallelogram():
    """⑤ 그림3 — 중선을 두 배로 늘린 D, 그리고 평행사변형 법칙"""
    ok = True
    print("\n[b01] 평행사변형 ABDC (D = 2M − A) — 네 변의 제곱의 합 = 두 대각선의 제곱의 합")
    A, B, C = tri_coords(*PUB_B01_T1[:3])
    M = mid(B, C)
    D = (2 * M[0] - A[0], 2 * M[1] - A[1])
    for lab, got, want in [("BD (= AC = 9)", math.sqrt(d2(B, D)), 9.0),
                           ("DC (= AB = 13)", math.sqrt(d2(D, C)), 13.0),
                           ("대각선 AD (= 2AM = 20)", math.sqrt(d2(A, D)), 20.0),
                           ("대각선 BC (= 2BM = 10)", math.sqrt(d2(B, C)), 10.0)]:
        h = abs(got - want) < 1e-9
        ok &= h
        print(f"  {lab:<22} {got:>9.5f}  게시 {want:<6} {ok_mark(h)}")

    sides = d2(A, B) + d2(B, D) + d2(D, C) + d2(C, A)
    diags = d2(A, D) + d2(B, C)
    h = (abs(sides - PUB_B01_PARA[0]) < 1e-9 and abs(diags - PUB_B01_PARA[1]) < 1e-9)
    ok &= h
    print(f"  네 변의 제곱의 합 {sides:.1f} · 두 대각선의 제곱의 합 {diags:.1f}  게시 {PUB_B01_PARA}  {ok_mark(h)}")

    # 격자점 전수 — D를 저렇게 잡으면 언제나 평행사변형 법칙이 성립하는가
    R = range(-3, 4)
    worst = 0.0
    for ax in R:
        for ay in R:
            for bx in R:
                for cx in R:
                    for cy in R:
                        A2, B2, C2 = (ax, ay), (bx, 0), (cx, cy)
                        M2 = mid(B2, C2)
                        D2 = (2 * M2[0] - A2[0], 2 * M2[1] - A2[1])
                        s = d2(A2, B2) + d2(B2, D2) + d2(D2, C2) + d2(C2, A2)
                        dg = d2(A2, D2) + d2(B2, C2)
                        worst = max(worst, abs(s - dg))
    hit = worst < TOL
    ok &= hit
    print(f"  격자점 전수 확인 — 최대 오차 {worst:.2e}  {ok_mark(hit)}")
    return ok


def check_b01_pixels():
    """⑥ 네 그림에 박아 넣은 픽셀 좌표가 주석의 매핑식과 맞는가"""
    ok = True
    print("\n[b01] SVG 좌표 검산 — 그림1 60+30x · 그림2 230+30x · 그림3 60+20x · 그림4 90+36x")
    for lab, x0, sx, y0, sy, (x, y), (px, py) in PUB_B01_PIXELS:
        gx, gy = x0 + sx * x, y0 - sy * y
        hit = abs(gx - px) < 0.5 and abs(gy - py) < 0.5
        ok &= hit
        print(f"  {lab:<22} 계산 ({gx:>6.1f},{gy:>6.1f})  게시 ({px},{py})  {ok_mark(hit)}")
    return ok



def main():
    print("고1 수학 직관 — 수치·주장 검산")
    ok = True
    ok &= check_01_identity()
    ok &= check_01_vertex_is_extreme()
    ok &= check_01_discriminant()
    ok &= check_01_restricted()
    ok &= check_01_pixels()
    ok &= check_b01_theorem()
    ok &= check_b01_numbers()
    ok &= check_b01_median_formula()
    ok &= check_b01_converse()
    ok &= check_b01_parallelogram()
    ok &= check_b01_pixels()
    print("\n전체:", "통과" if ok else "실패 — 자료의 값을 확인할 것")
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
