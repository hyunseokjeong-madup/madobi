---
title: "Google Ads 플레이북"
category: channels
tags: [channels, google]
verified: true
status: stable
last_updated: 2026-06-28
related: []
---
# Google Ads 플레이북

## 캠페인 유형
- 검색(Search): 의도 높음 → CPA/ROAS. 키워드 매치(broad+스마트 입찰), 검색어 보고서로 네거티브 관리.
- PMax(Performance Max): 전 채널 자동화. 에셋 그룹+오디언스 시그널. 검색어/플레이스먼트 투명성 낮음 주의.
- 디스플레이/유튜브/쇼핑.

## 입찰
- tCPA / tROAS 스마트 입찰. 전환 데이터 충분해야(주 15~30+). 변경은 점진적(±10~20%).

## 일상 루틴
- **검색어 보고서 → 네거티브 키워드**(`pm/search_terms.py`): 지출 큰데 전환0 → 제외.
- 품질지수/광고관련성, 노출 점유율(IS), 손실 IS(예산/순위) 점검.
- tROAS/tCPA 가드레일 위반 → 입찰·예산 조정(`pm/guardrails.py`).

## 정합성/함정
- 어트리뷰션: 데이터기반(DDA) 기본. 전환 '집계' 기준일(클릭일 vs 전환일) 차이 → 보고 시 명시.
- PMax는 브랜드 검색 잠식 가능 → 브랜드 제외/실험으로 증분 확인.
- 통화·타임존, 전환 중복 카운트(여러 액션) 점검.
