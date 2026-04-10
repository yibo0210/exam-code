import numpy as np
from typing import List, Dict, Any
# 核心架构动作：物理隔离底层 RPC 调用
from app.mock_rpc import rpc_l1_sparse, rpc_l2_dense, rpc_l3_exact


# --- 核心 RRF 算法 ---
def reciprocal_rank_fusion(rankings: List[List[str]], k: int = 60) -> Dict[str, float]:
    """
    手写 RRF 倒数秩融合算法
    公式: RRF_score(d) = sum(1.0 / (k + rank(d))) for each ranking
    """
    rrf_scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0.0
            rrf_scores[doc_id] += 1.0 / (k + rank)
    return rrf_scores


# --- 管线编排 ---
async def search_pipeline(query: str, tags: List[str]) -> Dict[str, Any]:
    # 1. L1 粗召回 (RPC 隔离)
    l1_ids = await rpc_l1_sparse(query, tags)
    # 2. L2 中召回 (RPC 隔离)
    l2_scores = await rpc_l2_dense([], l1_ids)
    l2_ranking = sorted(l2_scores.keys(), key=lambda x: l2_scores[x], reverse=True)
    # 3. L3 精排 (RPC 隔离)
    l3_scores = await rpc_l3_exact([], l2_ranking)
    l3_ranking = sorted(l3_scores.keys(), key=lambda x: l3_scores[x], reverse=True)
    # 4. RRF 融合绝杀 (纯内存计算，无 RPC)
    final_scores = reciprocal_rank_fusion(rankings=[l1_ids, l2_ranking, l3_ranking])
    # 取 Top 3
    top_candidates = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    return {
        "funnel": {
            "l1_count": len(l1_ids),
            "l2_count": len(l2_scores),
            "l3_count": len(l3_scores)
        },
        "final_candidates": [{"id": cid, "rrf_score": score} for cid, score in top_candidates]
    }