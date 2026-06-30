"""
놀리지 그래프 JSON 에미터 — link_related.py 의 결정론 그래프를 노드/에지 JSON 으로 직렬화.

새 그래프 계산은 하지 않는다. link_related.collect()(카테고리별 노트) + related_for()
(노트의 형제 링크)의 *기존 결정론 산출물* 을 그대로 직렬화만 한다 → Obsidian 이 보는
그래프와 이 JSON 이 항상 일치(진실 분기 없음). 순수 stdlib(json) · 결정론 · 부작용 0.

.xmind 같은 proprietary 포맷은 의도적으로 만들지 않는다(외부 zip 규약·도구 의존).
related[] 는 이미 옵시디언이 렌더하므로 이 JSON 은 보조(에이전트/외부 뷰어가 쓸 수 있게).

사용:
  python viz.py                      # 그래프 요약(노드/에지 수, 카테고리)
  python viz.py --json               # 그래프 전체를 JSON 으로 stdout
  python viz.py --json --out g.json  # 파일로 저장
  python viz.py --selftest           # 비대화 검증(종료코드 0/1)
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import link_related  # 같은 폴더, stdlib only — 그래프 진실의 단일 출처


def build_graph():
    """노드/에지 그래프(dict). 노드=노트, 에지=related 링크(무방향, 중복 제거).

    전부 link_related 의 결정론 함수에서 파생 → 같은 레포 상태면 항상 같은 그래프.
    """
    by_cat = link_related.collect()
    # note_id(=basename) 가 여러 카테고리에 중복될 수 있다(예: bidding/portfolio 와
    # budget_models/portfolio). 에지는 bare id 로 참조하므로 id 당 노드 1개로 dedup 하되,
    # 어느 카테고리들에 속하는지는 categories 배열로 보존(소비자가 충돌을 알 수 있게).
    node_cats, edges, seen = {}, [], set()
    for cat in sorted(by_cat):
        notes = by_cat[cat]
        for p in notes:
            nid = link_related.note_id(p)
            node_cats.setdefault(nid, set()).add(cat)
            for tgt in link_related.related_for(p, notes):
                key = tuple(sorted((nid, tgt)))   # 무방향 에지 — (a,b)/(b,a) 한 번만
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"source": key[0], "target": key[1], "category": cat})
    nodes = [{"id": nid, "categories": sorted(cats)} for nid, cats in node_cats.items()]
    nodes.sort(key=lambda n: n["id"])                       # 결정론 정렬(id 유니크)
    edges.sort(key=lambda e: (e["category"], e["source"], e["target"]))
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),                       # 유니크 id 수
            "edge_count": len(edges),
            "category_count": len(by_cat),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="놀리지 그래프 JSON 에미터(link_related 재사용)")
    ap.add_argument("--json", action="store_true", help="그래프 전체를 JSON 으로 출력")
    ap.add_argument("--out", metavar="FILE", help="JSON 을 이 파일로 저장")
    ap.add_argument("--selftest", action="store_true", help="비대화 검증(종료코드 0/1)")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    g = build_graph()
    if a.out:
        Path(a.out).write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"GRAPH JSON → {a.out}  (노드 {g['stats']['node_count']} · 에지 {g['stats']['edge_count']})")
    elif a.json:
        print(json.dumps(g, ensure_ascii=False, indent=2))
    else:
        s = g["stats"]
        print("\n=== KNOWLEDGE GRAPH ===")
        print(f"노드(노트) {s['node_count']}개 · 에지(related 링크) {s['edge_count']}개 · 카테고리 {s['category_count']}개")
        print("  · link_related.py 의 결정론 그래프를 그대로 직렬화(Obsidian 그래프와 일치).")
        print("  · 전체 JSON: --json | 파일저장: --json --out graph.json")
    return 0


def _selftest():
    g = build_graph()
    s = g["stats"]
    assert s["node_count"] > 0, "노드 0개"
    assert s["node_count"] == len(g["nodes"]), "노드 카운트 불일치"
    # id 가 진짜 유니크해야 한다 — 에지가 bare id 로 참조하므로 중복 id 는 노드 병합 버그.
    ids_all = [n["id"] for n in g["nodes"]]
    assert len(ids_all) == len(set(ids_all)), "노드 id 중복(같은 basename 다른 카테고리 병합)"
    assert s["edge_count"] == len(g["edges"]), "에지 카운트 불일치"
    # 결정론: 두 번 빌드 → 완전 동일(JSON 직렬화까지)
    assert json.dumps(build_graph(), sort_keys=True) == json.dumps(g, sort_keys=True), "그래프 비결정적"
    # 에지 무결성: 모든 에지의 양끝이 실제 노드 + 자기루프 없음
    ids = {n["id"] for n in g["nodes"]}
    for e in g["edges"]:
        assert e["source"] in ids and e["target"] in ids, f"에지가 없는 노드 참조: {e}"
        assert e["source"] != e["target"], f"자기루프 에지: {e}"
    print(f"KNOWLEDGE GRAPH self-test: PASS  (노드 {s['node_count']} · 에지 {s['edge_count']} · 결정론·무결성)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
