"""네이밍 규칙 검증. 소재/캠페인명이 {campaign}_{angle}_{format}_{hook}_v## 규칙을 따르는지 점검.
(분석 시 차원 분해·정합성의 전제) CSV 첫 열 또는 --names 사용."""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
PAT=re.compile(r"^[A-Za-z0-9]+_[A-Za-z-]+_[A-Za-z0-9]+_[A-Za-z0-9]+_v\d+$")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv_pos", nargs="?", help="점검할 이름 CSV 경로 (positional; --csv 와 동일)")
    ap.add_argument("--csv"); ap.add_argument("--names")
    a=ap.parse_args()
    csv_path=a.csv or a.csv_pos
    names=[]
    if a.names: names=[x.strip() for x in a.names.split(",")]
    elif csv_path:
        rows=load_rows(csv_path)
        col=list(rows[0])[0]
        names=[(r.get(col) or "").strip() for r in rows if not re.search(r"total|합계|총계",(r.get(col) or ""),re.I)]
    bad=[n for n in names if not PAT.match(n)]
    print(f"\n=== NAMING CHECK ({len(names)}개) ===")
    print(f"규칙: campaign_angle_format_hook_v## (예: CMP_benefit_video_number_v01)")
    if bad:
        print(f"⚠️ 비규칙 {len(bad)}개:")
        for n in bad: print(f"  - {n}")
        print("→ 네이밍 정정 권고(분석 차원분해·정합성 보장).")
    else:
        print("✅ 전부 규칙 준수")
if __name__=="__main__": main()
