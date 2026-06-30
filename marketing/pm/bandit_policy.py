"""
경량 정책선택(multi-armed bandit) — 어떤 arm(채널/소재/카테고리)에 다음 노출을
배정할지 *결정론적으로* 고른다. 무거운 강화학습(torch 등) 없이 stdlib 폐형식만 쓴다.

madobi 철학 그대로: 산술(UCB 점수·평균보상)은 코드가 보장하고, arm 의 정의와
보상 신호를 *무엇으로 둘지* 는 LLM/사람이 판단한다. 이 파일은 점수 산식만 책임진다.

기본은 UCB1 (난수 0 → 같은 입력 같은 선택). UCB1 점수:
    score(arm) = mean_reward + sqrt(2 * ln(total_pulls) / pulls(arm))
  - 첫 항 = 활용(exploitation), 둘째 항 = 탐험(exploration) 보너스.
  - 적게 당긴 arm 일수록 보너스가 커서 최소 한 번은 시도된다(pulls=0 이면 +∞ → 우선).
epsilon-greedy 는 무작위 탐험이라 비결정적 → --seed(기본 42) 를 명시할 때만 켠다.

보상 신호의 정직한 출처 (왜 이 bandit 이 madobi 철학을 안 깨나):
  외부 마케팅 성과(ROAS 등)는 외생변수 노이즈로 '이 arm 이 정말 낫다'를 코드가
  보장 못 한다. 반면 *자기 검색 시스템의 내부 메트릭* — recall 이 색인 hit 으로
  답했나(=1.0) grep 폴백으로 떨어졌나(=0.5), 질의어 매칭 비율 — 은 100% 코드 산물
  이라 검산 가능하고 결정론적이다. arm=prefetch 할 카테고리, reward=그 회상 품질로
  두면 '쓸수록 똑똑해지는' 루프가 철학을 위반하지 않고 닫힌다. (search.py/recall.py 참고)

Usage:
  # arm 별 (보상합:시도수) 를 줘서 다음에 당길 arm 을 고른다 (UCB1, 결정론)
  python bandit_policy.py --arms "metrics:8.5:12, diagnostics:3.0:5, creative:0.0:0"

  # 같은 데이터를 epsilon-greedy 로 (난수 → --seed 고정 필수)
  python bandit_policy.py --arms "a:5:10, b:3:4" --policy egreedy --epsilon 0.1 --seed 42
"""
import argparse
import math
import random


def parse_arms(spec: str):
    """'name:reward_sum:pulls, ...' → [(name, reward_sum, pulls)]. 결정론(입력 순서 보존)."""
    arms = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = [p.strip() for p in chunk.split(":")]
        if len(parts) != 3:
            raise ValueError(f"arm 형식은 name:reward_sum:pulls — 받은 값: {chunk!r}")
        name, rsum, pulls = parts[0], float(parts[1]), int(parts[2])
        if pulls < 0 or rsum < 0:
            raise ValueError(f"reward_sum/pulls 는 음수 불가: {chunk!r}")
        # NaN/inf 는 음수 가드(nan<0=False)를 통과해 UCB 점수를 오염시키고 max() 타이브레이크를
        # 입력순서 의존으로 만든다(결정론 위반) → 명시적으로 거부.
        if math.isnan(rsum) or math.isinf(rsum):
            raise ValueError(f"reward_sum 은 유한값이어야 함(NaN/inf 불가): {chunk!r}")
        arms.append((name, rsum, pulls))
    if not arms:
        raise ValueError("arm 이 하나도 없습니다")
    return arms


def mean_reward(reward_sum: float, pulls: int) -> float:
    """평균 보상. 한 번도 안 당겼으면 0.0 (UCB 가 탐험 보너스로 끌어올린다)."""
    return reward_sum / pulls if pulls > 0 else 0.0


def ucb1_scores(arms):
    """각 arm 의 UCB1 점수. 결정론(난수 없음). pulls=0 인 arm 은 +inf(반드시 먼저 시도).

    반환: [(name, score, mean, bonus)], 입력 순서 유지.
    """
    total = sum(p for (_n, _r, p) in arms)
    out = []
    for name, rsum, pulls in arms:
        mean = mean_reward(rsum, pulls)
        if pulls == 0:
            score, bonus = float("inf"), float("inf")
        else:
            bonus = math.sqrt(2.0 * math.log(total) / pulls) if total > 0 else 0.0
            score = mean + bonus
        out.append((name, score, mean, bonus))
    return out


def select_ucb1(arms):
    """UCB1 으로 다음 arm 선택. 동점이면 입력 순서가 앞선 arm(결정론)."""
    scored = ucb1_scores(arms)
    best = max(range(len(scored)), key=lambda i: (scored[i][1], -i))
    return scored[best][0], scored


def select_egreedy(arms, epsilon: float, seed: int):
    """epsilon-greedy: 1-ε 확률로 평균보상 최대 arm, ε 확률로 무작위 탐험.

    무작위라 seed 고정 없이는 비결정적 → seed 를 항상 받는다(기본 42).
    """
    # 범위 밖 epsilon 은 조용히 퇴화(ε<0=전활용, ε>1=전탐험)한다 → 명시적으로 거부
    # (parse_arms 의 음수 거부 관례와 대칭).
    if not (0.0 <= epsilon <= 1.0):
        raise ValueError(f"epsilon 은 0~1 범위여야 함: {epsilon}")
    rng = random.Random(seed)
    means = [(name, mean_reward(rsum, pulls)) for (name, rsum, pulls) in arms]
    if rng.random() < epsilon:
        choice = rng.randrange(len(arms))          # 탐험
        mode = "explore"
    else:
        choice = max(range(len(arms)), key=lambda i: (means[i][1], -i))  # 활용
        mode = "exploit"
    return arms[choice][0], means, mode


def _fmt(x: float) -> str:
    if x == float("inf"):
        return "  +inf"
    return f"{x:6.3f}"


def main():
    ap = argparse.ArgumentParser(description="경량 정책선택 — UCB1(결정론) / epsilon-greedy")
    ap.add_argument("--arms", required=True,
                    help="'name:reward_sum:pulls, ...' (예: 'metrics:8.5:12, creative:0:0')")
    ap.add_argument("--policy", choices=["ucb1", "egreedy"], default="ucb1")
    ap.add_argument("--epsilon", type=float, default=0.1, help="egreedy 탐험 확률")
    ap.add_argument("--seed", type=int, default=42, help="egreedy 난수 시드(결정론 위해 고정)")
    a = ap.parse_args()

    arms = parse_arms(a.arms)
    print("\n=== BANDIT POLICY ===")

    if a.policy == "ucb1":
        choice, scored = select_ucb1(arms)
        print(f"정책: UCB1 (결정론 · 난수 0) · arm {len(arms)}개")
        print(f"{'arm':<16}{'score':>8}{'mean':>8}{'bonus':>8}{'pulls':>7}")
        pulls_by = {n: p for (n, _r, p) in arms}
        for name, score, mean, bonus in scored:
            print(f"{name:<16}{_fmt(score):>8}{_fmt(mean):>8}{_fmt(bonus):>8}{pulls_by[name]:>7}")
        print(f"→ 다음 당길 arm: **{choice}**  (UCB1 = 평균보상 + √(2·ln N / n))")
        print("  · 점수는 폐형식이라 재계산으로 검산 가능. 보상=코드 산물(예: 회상 품질)일 때만 정직.")
    else:
        choice, means, mode = select_egreedy(arms, a.epsilon, a.seed)
        print(f"정책: epsilon-greedy ε={a.epsilon} seed={a.seed} ({mode}) · arm {len(arms)}개")
        print(f"{'arm':<16}{'mean':>8}{'pulls':>7}")
        pulls_by = {n: p for (n, _r, p) in arms}
        for name, mean in means:
            print(f"{name:<16}{_fmt(mean):>8}{pulls_by[name]:>7}")
        print(f"→ 다음 당길 arm: **{choice}**  ({mode}; seed 고정해야 재현됨)")


def _selftest():
    """결정론·산식 검증 — needle smoke 가 아니라 정확한 선택/점수를 단언한다(verify_bench 스타일)."""
    # 1) pulls=0 arm 은 UCB 가 무조건 먼저 시도 (+inf)
    arms = [("a", 9.0, 10), ("b", 0.0, 0)]
    choice, scored = select_ucb1(arms)
    assert choice == "b", f"미시도 arm 우선 실패: {choice}"

    # 2) 폐형식 검산: 모두 시도된 경우 점수를 손으로 재계산한 값과 일치
    arms = [("x", 8.0, 8), ("y", 3.0, 4)]   # mean x=1.0, y=0.75; total=12
    choice, scored = select_ucb1(arms)
    total = 12
    exp_x = 1.0 + math.sqrt(2 * math.log(total) / 8)
    exp_y = 0.75 + math.sqrt(2 * math.log(total) / 4)
    got = {n: s for (n, s, _m, _b) in scored}
    assert abs(got["x"] - exp_x) < 1e-9 and abs(got["y"] - exp_y) < 1e-9, "UCB 점수 산식 불일치"
    assert choice == ("x" if exp_x > exp_y else "y"), "UCB 선택이 점수와 불일치"

    # 3) 결정론: 같은 입력 두 번 → 같은 선택
    assert select_ucb1(arms)[0] == select_ucb1(arms)[0], "UCB 비결정적"

    # 4) egreedy seed 고정 → 재현
    a1 = select_egreedy(arms, 0.5, 42)[0]
    a2 = select_egreedy(arms, 0.5, 42)[0]
    assert a1 == a2, "egreedy seed 고정인데 비재현"

    # 5) 경계 epsilon: 0=전활용(평균최대), 1=전탐험. 범위 밖은 거부.
    assert select_egreedy([("a", 9, 10), ("b", 0, 1)], 0.0, 42)[2] == "exploit", "ε=0 인데 탐험"
    assert select_egreedy([("a", 9, 10), ("b", 0, 1)], 1.0, 42)[2] == "explore", "ε=1 인데 활용"
    for bad in (-0.1, 1.5):
        try:
            select_egreedy(arms, bad, 42); assert False, f"ε={bad} 거부 안 됨"
        except ValueError:
            pass

    # 6) NaN/inf reward 거부 (결정론 타이브레이크 오염 방지)
    for bad in ("a:nan:5, b:3:4", "a:inf:5, b:3:4"):
        try:
            parse_arms(bad); assert False, f"{bad!r} 거부 안 됨"
        except ValueError:
            pass

    print("BANDIT POLICY self-test: PASS  (UCB1 폐형식 + 미시도우선 + 결정론 + egreedy 재현 + 입력가드)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        _selftest()
    else:
        main()
