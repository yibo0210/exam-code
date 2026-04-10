from pydantic import BaseModel, Field
from typing import List


class AbilityDelta(BaseModel):
    """神谕输出的稀疏增量模型 (配合 main.py 中的合并逻辑)"""
    node_id: str = Field(..., description="原子能力ID，如 '145'")
    score_delta: float = Field(..., description="得分增量，如 0.85")


class RadarChartItem(BaseModel):
    """动态雷达图维度 (推翻原版硬编码的4个字段，实现完全动态化)"""
    dimension: str = Field(..., description="能力维度名称，如 '容灾降级'")
    score: float = Field(..., ge=0, le=1, description="归一化得分 0~1")


class CertificationReport(BaseModel, extra='forbid'):
    """最终交付前端的极客认证报告"""
    candidate_id: str
    assessment_id: str = Field(..., description="战役评估ID，关联 question_ability_scores 账本")
    # 防伪确权标识
    anti_tamper_hash: str
    ledger_version: str = Field("v1.0-ema-decay", description="底层数据快照版本，对应 DDL 中的 ledger_version")
    # 雷达图多维数据 (动态生成，拒绝硬编码)
    radar_chart: List[RadarChartItem]
    # 1024 维向量 (保留你原来的极简强校验，这个非常好)
    vector_1024: List[float] = Field(..., min_length=1024, max_length=1024)
    # 裁决 (强约束枚举，严禁出现 PASS/FAIL 等非标输出)
    final_verdict: str = Field(..., pattern="^(SURVIVED|FALLEN)$", description="战役最终裁决")