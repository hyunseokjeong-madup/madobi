"""
pm 도구 공통 유틸 — 빈 데이터 우아한 처리(IndexError 방지).

배경: 78개 pm 도구 중 다수가 `rows=list(csv.DictReader(...))` 직후 rows[0] 등 첫 행을 가정해,
빈/헤더만 있는 CSV(필터로 0행이 된 export 등)에 IndexError 로 크래시했다. 마케터가 빈 데이터를
던져도 traceback 대신 "데이터 없음" 한 줄로 우아하게 끝나야 한다("숫자 안 틀린다"의 신뢰).

순수 stdlib. 정상 데이터엔 투명(rows 그대로 반환) → 기존 테스트 영향 0.
"""
import csv
import sys
from pathlib import Path
from statistics import median


def _read_text(csv_path):
    """CSV 텍스트를 읽어 반환. 엑셀 한국어 기본 저장(cp949)까지 지원.

    utf-8-sig(BOM 제거 + utf-8 호환) 우선, UnicodeDecodeError 시 cp949 1회 재시도,
    파일 없으면 한 줄 안내 후 종료(exit 0). 둘 다 실패 시 한 줄 에러 후 종료.
    """
    p = Path(csv_path)
    try:
        raw = p.read_bytes()
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {csv_path}")
        sys.exit(0)
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return raw.decode("cp949")
        except UnicodeDecodeError:
            print(f"[오류] 인코딩 판별 실패: {csv_path} (utf-8/cp949 모두 실패)")
            sys.exit(0)


def load_rows(csv_path, empty_msg="데이터 없음 — 입력 CSV에 데이터 행이 없습니다.", exit_on_empty=True):
    """CSV를 DictReader 로 읽어 rows 리스트 반환. 비어있으면 메시지 출력 후 종료(exit 0).

    정상 데이터면 rows 를 그대로 반환하므로 기존 도구 로직은 변경 없이 동작한다.
    exit_on_empty=False 면 빈 경우 [] 를 반환(호출부가 직접 처리)."""
    rows = list(csv.DictReader(_read_text(csv_path).splitlines()))
    if not rows:
        if exit_on_empty:
            print(empty_msg)
            sys.exit(0)
        return []
    return rows


def expected_cycle(freq, span, repeat_cycles):
    """구매 기대주기 추정 — freq=1(1회 구매) 고객의 주기 퇴화 방지.

    freq>=2 고객: 관측기간/(freq-1) = 평균 구매간격.
    freq=1  고객: 주기 추정 불가 → 재구매(freq>=2) 고객들의 중앙값 구매주기로 폴백.
                 재구매 고객이 0명이면 None 반환(위험비 산출 불가 라벨 처리).

    repeat_cycles: 재구매 고객들의 평균 구매간격 리스트(호출부가 사전 계산해 전달).
    반환: 기대주기(일) 또는 None(추정 불가).
    """
    if freq >= 2:
        return span / (freq - 1)
    # freq==1 → 재구매 고객 중앙값 폴백
    if repeat_cycles:
        return median(repeat_cycles)
    return None
