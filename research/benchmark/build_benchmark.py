"""
Self-verifying benchmark generator.
Each problem's ground-truth answer is COMPUTED here, so scoring is deterministic.
Outputs: benchmark/problems.json  (prompt shown to agents)
         benchmark/answers.json   (ground truth, kept hidden from agents)
"""
import json, math, itertools
from fractions import Fraction
from pathlib import Path

problems = []   # {id, group, prompt, format}
answers = {}    # id -> canonical answer string

def add(pid, group, prompt, fmt, answer):
    problems.append({"id": pid, "group": group, "prompt": prompt, "format": fmt})
    answers[pid] = str(answer)

# ---- P1: number theory ----
s = sum(p for p in range(2, 5000)
        if all(p % d for d in range(2, int(p**0.5)+1)) and p % 7 == 3)
add("P1", "number_theory",
    "5000 미만의 소수(prime) 중에서 7로 나눈 나머지가 3인 것들을 모두 더한 값은?",
    "정수 하나만 출력", s)

# ---- P2: exact probability ----
# 공정한 6면체 주사위 4개를 굴린다. 정확히 세 개의 눈이 같을 확률(기약분수 a/b).
# 'exactly three equal' = three-of-a-kind but not four-of-a-kind, and the 4th differs.
total = 6**4
count = 0
for roll in itertools.product(range(1,7), repeat=4):
    from collections import Counter
    c = Counter(roll)
    if sorted(c.values()) == [1,3]:
        count += 1
fr = Fraction(count, total)
add("P2", "probability",
    "공정한 6면체 주사위 4개를 동시에 굴린다. '정확히 세 개'의 주사위 눈이 서로 같을 "
    "(나머지 한 개는 다른 값) 확률을 기약분수로 구하라.",
    "기약분수 a/b 형식 (예: 5/18)", f"{fr.numerator}/{fr.denominator}")

# ---- P3: logic puzzle (uniquely deducible) ----
# 5 houses, deduce who owns the fish style but small & unique. We compute the unique answer.
# Constraints over positions 1..5 for color order. We just need a single deducible fact.
# Houses left->right 1..5. Each has unique color, drink, pet.
colors = ["red","green","blue","yellow","white"]
drinks = ["tea","coffee","milk","juice","water"]
pets   = ["dog","cat","bird","fish","horse"]
def right_of(a,b): return a == b+1
def next_to(a,b): return abs(a-b)==1
sol=None
import itertools as it
for cperm in it.permutations(colors):
  cpos={col:i+1 for i,col in enumerate(cperm)}
  # 1: green is immediately right of red
  if not right_of(cpos["green"], cpos["red"]): continue
  # 2: blue is at position 1
  if cpos["blue"]!=1: continue
  for dperm in it.permutations(drinks):
    dpos={d:i+1 for i,d in enumerate(dperm)}
    # 3: milk in the middle (pos 3)
    if dpos["milk"]!=3: continue
    # 4: coffee is in the green house
    if dpos["coffee"]!=cpos["green"]: continue
    # 5: the white house drinks tea
    if dpos["tea"]!=cpos["white"]: continue
    for pperm in it.permutations(pets):
      ppos={p:i+1 for i,p in enumerate(pperm)}
      # 6: dog is in the red house
      if ppos["dog"]!=cpos["red"]: continue
      # 7: cat is immediately right of fish
      if ppos["cat"]!=ppos["fish"]+1: continue
      # 8: bird owner drinks coffee
      if dpos["coffee"]!=ppos["bird"]: continue
      # 9: yellow house is immediately right of blue(pos1) -> pos2? only if consistent
      if cpos["yellow"]!=2: continue
      # 10: horse is at position 5
      if ppos["horse"]!=5: continue
      fp=[i+1 for i,p in enumerate(pperm) if p=="fish"][0]
      fc=cperm[fp-1]
      if sol is None: sol=set()
      sol.add(fc)
assert sol is not None and len(sol)==1, f"answer not unique: {sol}"
fish_color=next(iter(sol))
add("P3","logic",
    "왼쪽부터 1~5번 위치에 집 5채가 있다. 각 집은 색(red,green,blue,yellow,white), "
    "음료(tea,coffee,milk,juice,water), 애완동물(dog,cat,bird,fish,horse)이 모두 서로 다르다. "
    "단서: (1) green 집은 red 집 바로 오른쪽이다. (2) blue 집은 1번이다. (3) milk는 3번 집이 마신다. "
    "(4) coffee는 green 집이 마신다. (5) white 집은 tea를 마신다. (6) dog는 red 집에 있다. "
    "(7) cat은 fish 집 바로 오른쪽이다. (8) bird 주인은 coffee를 마신다. (9) yellow 집은 2번이다. "
    "(10) horse는 5번 집에 있다. 질문: fish를 키우는 집의 '색'은 무엇인가?",
    "색 이름 영어 소문자 단어 하나 (예: red)", fish_color)

# ---- P4: algorithmic (deterministic simulation) ----
# Collatz-like: f(n): if even n/2 else 3n+1. Count total steps to reach 1, summed over n=1..200.
def collatz_steps(n):
    s=0
    while n!=1:
        n = n//2 if n%2==0 else 3*n+1
        s+=1
    return s
tot=sum(collatz_steps(n) for n in range(1,201))
add("P4","algorithm",
    "함수 f(n)은 n이 짝수면 n/2, 홀수면 3n+1 이다. 어떤 양의 정수 n에서 시작해 "
    "f를 반복 적용하여 1에 도달할 때까지의 적용 횟수를 steps(n)이라 하자(steps(1)=0). "
    "n=1부터 200까지의 steps(n)을 모두 더한 값은?",
    "정수 하나만 출력", tot)

# ---- P5: precise counting / careful reading ----
text = ("The strategy meeting started at eleven, and the team reviewed the "
        "quarterly results, the regional results, and the preliminary results "
        "before agreeing that the results were better than the last results.")
# count occurrences of the exact word "results" (lowercase, whole word)
import re
cnt=len(re.findall(r"\bresults\b", text))
add("P5","careful_reading",
    "다음 문단에서 정확히 'results'라는 단어(소문자, 단어 단위)가 몇 번 나오는지 세어라. "
    "문단: \"" + text + "\"",
    "정수 하나만 출력", cnt)

# ---- P6: base-rate / counterintuitive exact ----
# Disease prevalence 1/1000. Test sensitivity 99%, specificity 95%.
# P(disease | positive) as reduced fraction.
p_d=Fraction(1,1000); sens=Fraction(99,100); spec=Fraction(95,100)
num=sens*p_d
den=sens*p_d + (1-spec)*(1-p_d)
post=num/den
add("P6","reasoning_trap",
    "어떤 병의 유병률은 1000명 중 1명이다. 검사의 민감도(sensitivity)는 99%, "
    "특이도(specificity)는 95%다. 무작위로 검사한 사람이 '양성'이 나왔을 때 실제로 그 병에 "
    "걸렸을 확률을 기약분수로 구하라.",
    "기약분수 a/b 형식", f"{post.numerator}/{post.denominator}")

# ---- P7: small exact optimization (0/1 knapsack) ----
items=[(2,3),(3,4),(4,5),(5,6),(9,10),(7,8),(1,1),(6,7)]  # (weight,value)
W=15
best=0
n=len(items)
for mask in range(1<<n):
    w=v=0
    for i in range(n):
        if mask>>i & 1:
            w+=items[i][0]; v+=items[i][1]
    if w<=W: best=max(best,v)
add("P7","optimization",
    "물건 8개의 (무게,가치)는 다음과 같다: (2,3),(3,4),(4,5),(5,6),(9,10),(7,8),(1,1),(6,7). "
    "배낭 용량(무게 합 한도)은 15다. 각 물건은 0개 또는 1개만 담을 수 있다. "
    "담을 수 있는 최대 가치 합은?",
    "정수 하나만 출력", best)

# ---- P8: string state machine ----
# Brackets: process a string, output max nesting depth that is balanced overall.
sm="(()((())())(()))(())((((()))))"
depth=0;mx=0;bal=True
for ch in sm:
    if ch=='(':
        depth+=1; mx=max(mx,depth)
    else:
        depth-=1
        if depth<0: bal=False
if depth!=0: bal=False
add("P8","algorithm",
    f"다음 괄호 문자열의 최대 중첩 깊이(maximum nesting depth)를 구하라: {sm}",
    "정수 하나만 출력", mx)

# ---- P9: multi-step word problem (rate) ----
# Two pipes fill, one drains. A fills tank in 6h, B in 8h, drain C empties in 12h.
# All open. Time to fill in hours as reduced fraction.
A=Fraction(1,6); B=Fraction(1,8); C=Fraction(1,12)
rate=A+B-C
t=1/rate
add("P9","reasoning",
    "수조에 파이프 A는 6시간 만에 가득 채우고, B는 8시간 만에 채운다. 배수구 C는 가득 찬 수조를 "
    "12시간 만에 비운다. 빈 수조에서 A,B,C를 동시에 열면 수조가 가득 차는 데 걸리는 시간(시간 단위)을 "
    "기약분수로 구하라.",
    "기약분수 a/b 형식 (정수면 a/1)", f"{t.numerator}/{t.denominator}")

# ---- P10: combinatorics exact ----
# Number of distinct arrangements of letters in "BANANA" -> 60; ask MISSISSIPPI
from math import factorial
def perms(word):
    from collections import Counter
    c=Counter(word); d=factorial(len(word))
    for v in c.values(): d//=factorial(v)
    return d
mp=perms("MISSISSIPPI")
add("P10","combinatorics",
    "단어 'MISSISSIPPI'의 글자들을 일렬로 배열하는 서로 다른 경우의 수는?",
    "정수 하나만 출력", mp)

# ===== Extended set P11-P20 (more nodes, more discrimination) =====
from math import gcd

# P11 number theory: count of n in [1,100000] coprime to 30
c=sum(1 for n in range(1,100001) if gcd(n,30)==1)
add("P11","number_theory",
    "1부터 100000까지의 정수 중에서 30과 서로소(coprime, 최대공약수가 1)인 정수의 개수는?",
    "정수 하나만 출력", c)

# P12 probability: two dice, given sum even, P(sum>=8) reduced
ev=[(a,b) for a in range(1,7) for b in range(1,7) if (a+b)%2==0]
fav=[1 for a,b in ev if a+b>=8]
fr=Fraction(len(fav),len(ev))
add("P12","probability",
    "공정한 6면체 주사위 2개를 굴렸더니 눈의 합이 짝수였다. 이 조건에서 눈의 합이 8 이상일 "
    "조건부확률을 기약분수로 구하라.",
    "기약분수 a/b 형식", f"{fr.numerator}/{fr.denominator}")

# P13 logic: 4 people in a line, unique deducible
names=["A","B","C","D"]
sols=set()
for perm in itertools.permutations(names):
    pos={p:i+1 for i,p in enumerate(perm)}
    if pos["A"]==1: continue            # A is not first
    if pos["C"]!=pos["B"]+1: continue   # B immediately before C
    if pos["D"]!=4: continue            # D is last
    sols.add(perm[0])                   # who is first
assert len(sols)==1, f"P13 not unique: {sols}"
add("P13","logic",
    "A,B,C,D 네 사람이 1~4번 자리에 일렬로 선다. 조건: (1) A는 1번이 아니다. "
    "(2) B 바로 뒤(오른쪽)에 C가 선다. (3) D는 4번(맨 뒤)이다. 1번 자리에 서는 사람은 누구인가?",
    "사람 이름 한 글자 (A/B/C/D)", next(iter(sols)))

# P14: sum of decimal digits of 2^200
d=sum(int(ch) for ch in str(2**200))
add("P14","algorithm",
    "2의 200제곱(2^200)을 10진수로 적었을 때, 모든 자릿수의 숫자를 더한 값은?",
    "정수 하나만 출력", d)

# P15 careful reading: count 5-letter words
sent=("Seven brave miners found three large rocks below their dusty rural camp "
      "after seven hours of steady labor under bright skies near a small green river")
words=re.findall(r"[A-Za-z]+", sent)
c5=sum(1 for w in words if len(w)==5)
add("P15","careful_reading",
    "다음 문장에서 정확히 5글자(영문자 5개)로 이루어진 단어의 개수를 세어라. 문장: \""+sent+"\"",
    "정수 하나만 출력", c5)

# P16 reasoning trap: two-children problem
# A family has two children. Given at least one is a boy, P(both boys).
out16=[(a,b) for a in "BG" for b in "BG"]
cond=[x for x in out16 if "B" in x]
both=[x for x in cond if x==("B","B")]
fr=Fraction(len(both),len(cond))
add("P16","reasoning_trap",
    "어떤 가정에 아이가 둘 있다. 각 아이가 남(B)/녀(G)일 확률은 동일하고 독립이다. "
    "'적어도 한 명은 남자아이'라는 사실이 주어졌을 때, 두 아이가 모두 남자아이일 조건부확률을 "
    "기약분수로 구하라.",
    "기약분수 a/b 형식", f"{fr.numerator}/{fr.denominator}")

# P17 optimization: longest strictly increasing subsequence length
seq=[3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6,2,6]
def lis(a):
    import bisect
    tails=[]
    for x in a:
        i=bisect.bisect_left(tails,x)
        if i==len(tails): tails.append(x)
        else: tails[i]=x
    return len(tails)
add("P17","optimization",
    "다음 수열에서 '엄격히 증가하는' 가장 긴 부분수열(연속일 필요 없음)의 길이를 구하라: "
    "3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6,2,6",
    "정수 하나만 출력", lis(seq))

# P18 algorithm: edit distance
def edit(a,b):
    m,n=len(a),len(b)
    dp=[[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0]=i
    for j in range(n+1): dp[0][j]=j
    for i in range(1,m+1):
        for j in range(1,n+1):
            dp[i][j]=min(dp[i-1][j]+1,dp[i][j-1]+1,dp[i-1][j-1]+(a[i-1]!=b[j-1]))
    return dp[m][n]
ed=edit("intention","execution")
add("P18","algorithm",
    "두 문자열 'intention'과 'execution' 사이의 최소 편집 거리(Levenshtein distance; "
    "한 글자 삽입/삭제/교체를 1로 센다)를 구하라.",
    "정수 하나만 출력", ed)

# P19 combinatorics: coin change count for 100 with {1,5,10,25}
coins=[1,5,10,25]; target=100
ways=[0]*(target+1); ways[0]=1
for co in coins:
    for v in range(co,target+1):
        ways[v]+=ways[v-co]
add("P19","combinatorics",
    "1원, 5원, 10원, 25원 동전을 사용해 100원을 만드는 서로 다른 방법(동전 개수 제한 없음, "
    "순서 무관)의 가짓수는?",
    "정수 하나만 출력", ways[target])

# P20 number theory: trailing zeros of 100!
def trailing_zeros_factorial(n):
    z=0; p=5
    while p<=n:
        z+=n//p; p*=5
    return z
add("P20","number_theory",
    "100! (100 팩토리얼)을 10진수로 적었을 때 끝에 연속으로 붙는 0의 개수는?",
    "정수 하나만 출력", trailing_zeros_factorial(100))

out=Path(__file__).parent
(out/"problems.json").write_text(json.dumps(problems,ensure_ascii=False,indent=2),encoding="utf-8")
(out/"answers.json").write_text(json.dumps(answers,ensure_ascii=False,indent=2),encoding="utf-8")
print("built", len(problems), "problems")
for p in problems:
    print(p["id"], p["group"], "=>", answers[p["id"]])
