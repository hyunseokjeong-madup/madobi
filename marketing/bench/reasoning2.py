"""마케팅 추론 벤치 확대 — 코드검증 문제 ~40종(파라미터 변주 + 함정). 각 문제 = 한 사이클."""
import json
from pathlib import Path
from fractions import Fraction
OUT=Path(__file__).parent/"reasoning2"; OUT.mkdir(parents=True,exist_ok=True)
P=[]; A={}
def add(pid,prompt,fmt,ans): P.append({"id":pid,"group":"marketing","prompt":prompt,"format":fmt}); A[pid]=str(ans)
i=0
def nid():
    global i; i+=1; return f"X{i:02d}"

# CTR / CPC / CPM 변주
for sp,ck,im in [(900000,1800,90000),(1250000,2500,100000),(450000,900,30000)]:
    add(nid(),f"광고비 {sp:,}원, 클릭 {ck:,}회, 노출 {im:,}회일 때 CPC(원)는?","정수(원)",sp//ck)
    add(nid(),f"광고비 {sp:,}원, 노출 {im:,}회일 때 CPM(원)은?","정수(원)",sp*1000//im)
    add(nid(),f"클릭 {ck:,}회, 노출 {im:,}회일 때 CTR(%)는? 소수 둘째자리.","퍼센트 소수 둘째",f"{ck/im*100:.2f}")
# CVR / CPA / ROAS
for sp,cv,ck,rv in [(1800000,180,3600,5400000),(900000,60,1200,2700000),(600000,40,800,1500000)]:
    add(nid(),f"클릭 {ck:,}, 전환 {cv}일 때 CVR(%)는? 소수 둘째자리.","퍼센트 소수 둘째",f"{cv/ck*100:.2f}")
    add(nid(),f"광고비 {sp:,}원, 전환 {cv}건일 때 CPA(원)는?","정수(원)",sp//cv)
    add(nid(),f"매출 {rv:,}원, 광고비 {sp:,}원일 때 ROAS(배수)? 소수 둘째.","소수 둘째",f"{rv/sp:.2f}")
# POAS / ROI / AOV
for rv,sp,mg in [(5400000,1800000,0.3),(3000000,1250000,0.5)]:
    add(nid(),f"매출 {rv:,}원, 광고비 {sp:,}원, 마진율 {mg:.0%}일 때 POAS(=매출×마진/광고비)? 소수 둘째.","소수 둘째",f"{rv*mg/sp:.2f}")
for rv,sp in [(5400000,1800000),(2700000,900000)]:
    add(nid(),f"매출 {rv:,}원, 광고비 {sp:,}원일 때 ROI(%)? (ROI=(매출-비용)/비용)","정수(%)",int((rv-sp)/sp*100))
for rv,od in [(5400000,180),(3000000,100)]:
    add(nid(),f"매출 {rv:,}원, 주문 {od}건일 때 AOV(객단가, 원)는?","정수(원)",rv//od)
# frequency
for im,rc in [(600000,150000),(450000,90000)]:
    add(nid(),f"노출 {im:,}, 도달 {rc:,}일 때 빈도(frequency)는?","정수",im//rc)
# blended ROAS / CTR (Simpson 함정)
for (a_im,a_ck),(b_im,b_ck) in [((100000,2000),(300000,3000)),((50000,2500),(150000,1500))]:
    add(nid(),f"A(노출 {a_im:,} 클릭 {a_ck:,}), B(노출 {b_im:,} 클릭 {b_ck:,})의 '가중' CTR(%)? 소수 둘째. (단순평균 금지)","퍼센트 소수 둘째",f"{(a_ck+b_ck)/(a_im+b_im)*100:.2f}")
# budget pacing days
for bg,dly in [(30000000,1500000),(21000000,1500000),(40000000,2000000)]:
    add(nid(),f"총예산 {bg:,}원, 하루 {dly:,}원 일정 소진 시 며칠 만에 소진?","정수(일)",bg//dly)
# max CPC from CPA*CVR
for cpa,cvr in [(8000,0.04),(10000,0.05)]:
    add(nid(),f"목표 CPA {cpa:,}원, 전환율 {cvr:.0%}일 때 허용 최대 CPC(원)?","정수(원)",int(cpa*cvr))
# reconciliation discrepancy
for parts,rep in [([1200000,900000,1250000,150000],3600000),([800000,700000,500000],2100000),([1000000,1000000,1000000],3100000)]:
    add(nid(),f"채널별 광고비 {','.join(f'{x:,}' for x in parts)}원, 보고 총합 {rep:,}원. 실제합과의 차이(절대값, 원)?","정수(원)",abs(rep-sum(parts)))
# payback / breakeven margin
for cac,arpu,mg in [(30000,15000,0.5),(50000,20000,0.4)]:
    add(nid(),f"CAC {cac:,}원, 월 ARPU {arpu:,}원, 공헌마진 {mg:.0%}일 때 페이백(개월)? 소수 첫째.","소수 첫째",f"{cac/(arpu*mg):.1f}")
for rv,sp in [(5000000,2000000),(3000000,1500000)]:
    add(nid(),f"매출 {rv:,}원, 광고비 {sp:,}원일 때 손익분기 마진율(%)? (광고비/매출) 정수.","정수(%)",round(sp/rv*100))

(OUT/"problems.json").write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"answers.json").write_text(json.dumps(A,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"built {len(P)} marketing problems (v2)")
