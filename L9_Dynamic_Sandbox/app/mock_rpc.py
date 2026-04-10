import numpy as np
from typing import List, Dict


async def rpc_l1_sparse(query: str, tags: List[str]) -> List[str]:
    """
    Mock: L1 32维粗召回 (模拟 Supabase BM25/倒排索引召回)
    """
    # 模拟根据 tags 命中了 200 个候选人 ID
    return [f"candidate_{i}" for i in range(200)]


async def rpc_l2_dense(query_embedding: List[float], candidate_ids: List[str]) -> Dict[str, float]:
    """
    Mock: L2 128维中召回 (模拟 pgvector HNSW 128维索引的余弦相似度检索)
    """
    # 模拟 HNSW 漏斗过滤，只剩下 80 人，并返回距离得分
    scores = {cid: np.random.rand() for cid in candidate_ids[:80]}
    return scores


async def rpc_l3_exact(query_embedding: List[float], candidate_ids: List[str]) -> Dict[str, float]:
    """
    Mock: L3 1024维精排 (模拟全量 1024 维向量的极度精准重打分)
    """
    # 模拟精确计算，只剩下 40 人
    scores = {cid: np.random.rand() for cid in candidate_ids[:40]}
    return scores