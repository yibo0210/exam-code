import asyncio
import math
import hashlib
import uuid
import numpy as np
from enum import Enum
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from app.search_pipeline import search_pipeline
from app.models import CertificationReport, RadarChartItem, AbilityDelta


class PipelineState(Enum):
    PROVISIONING = 1  # 捏造私有框架
    COMBAT_ACTIVE = 2  # 沙盒对抗
    EVALUATING = 3  # 快照与打分
    CERTIFIED = 4
    FAILED = 99


class SandboxOrchestrator:
    def __init__(self):
        self.state = PipelineState.PROVISIONING
        self.context = {}

    async def run_stage(self, agent_fn, input_data, next_state, timeout=15):
        try:
            # 引入 15 秒防线，超时直接降级或熔断
            res = await asyncio.wait_for(agent_fn(input_data), timeout=timeout)
            self.state = next_state
            return res
        except asyncio.TimeoutError:
            if self.state == PipelineState.PROVISIONING:
                # 降级到 Fallback_Blueprint 保证候选人体验
                print("[Circuit Breaker] Provisioning timeout, falling back to static blueprint.")
                self.state = PipelineState.COMBAT_ACTIVE
                return {"scene": "Fallback: Static Go Deadlock Blueprint"}
            self.state = PipelineState.FAILED
            raise RuntimeError(f"Circuit Breaker Triggered at {self.state.name}")
        except Exception as e:
            self.state = PipelineState.FAILED
            raise RuntimeError(f"Execution Failed: {e}")

    async def execute(self, resume_raw: str) -> CertificationReport:
        # 阶段一：DNA提取
        self.context['dna'] = await self.run_stage(self._mock_ingest, resume_raw, PipelineState.PROVISIONING)
        # 阶段二：深渊战役 - 超时设15秒
        self.context['scenario'] = await self.run_stage(self._mock_battlefield, self.context['dna'],
                                                        PipelineState.COMBAT_ACTIVE, timeout=15)
        # 阶段三：X-RAG 绞肉机
        self.context['interrogation'] = await self.run_stage(self._mock_xrag, self.context['scenario'],
                                                             PipelineState.EVALUATING)
        # 阶段四：神谕确权 (获取稀疏增量)
        oracle_result = await self.run_stage(self._mock_oracle, self.context, PipelineState.CERTIFIED)
        # 核心架构动作：后端受控合并稀疏增量，推翻 PRD 直接输出 1024 维的陷阱
        vector_1024 = self._merge_ability_deltas(oracle_result['deltas'])
        # 生成极客认证报告
        report = CertificationReport(
            candidate_id=self.context['dna']['candidate_id'],
            assessment_id=str(uuid.uuid4()),
            ledger_version="v1.0-ema-decay",
            anti_tamper_hash=oracle_result['evidence_hash'],
            radar_chart=oracle_result['radar_chart'],
            vector_1024=vector_1024.tolist(),
            final_verdict=oracle_result['verdict']
        )
        # 账本落盘逻辑模拟
        self._commit_to_ledger(report)
        return report

    def _merge_ability_deltas(self, deltas: List[Dict[str, Any]]) -> np.ndarray:
        """将 Oracle 输出的稀疏增量灌入全零向量，并应用 EMA 衰减"""
        vector_1024 = np.zeros(1024, dtype=np.float32)
        delta_t = 6  # 模拟距离上次认证已过 6 个月
        decay_factor = math.exp(-0.1 * delta_t)
        for delta in deltas:
            idx = int(delta['node_id']) - 1  # node_id 从 1 开始，索引从 0 开始
            vector_1024[idx] = delta['score_delta'] * decay_factor
        return vector_1024

    def _commit_to_ledger(self, report: CertificationReport):
        """实际工程中，这里负责写入 question_ability_scores 和 candidate_vectors"""
        print(f"[Ledger] Committing vectors for {report.candidate_id} with version {report.ledger_version}")

    # --- Mock Agent 函数 ---
    async def _mock_ingest(self, text: str) -> Dict:
        return {"candidate_id": str(uuid.uuid4()), "stack": ["Go", "Redis"]}

    async def _mock_battlefield(self, dna: Dict) -> Dict:
        return {"scene": "Deadlock in private RPC"}

    async def _mock_xrag(self, scene: Dict) -> Dict:
        return {"trap": "What if Redis master crashes?"}

    async def _mock_oracle(self, ctx: Dict) -> Dict:
        """Mock: 严禁直接输出 1024 维，只输出稀疏增量和防伪 Hash"""
        # 模拟大模型输出的稀疏增量
        deltas = [
            {"node_id": "43", "score_delta": 0.88},  # 容灾降级能力
            {"node_id": "101", "score_delta": -0.15}  # 八股文作弊嫌疑
        ]
        # 模拟雷达图数据 (强类型校验)
        radar_chart = [
            RadarChartItem(dimension="容灾降级", score=0.88),
            RadarChartItem(dimension="八股防范", score=0.95)
        ]
        payload = {"candidate_id": ctx['dna']['candidate_id'], "deltas": deltas}
        evidence_hash = hashlib.sha256(str(payload).encode()).hexdigest()
        return {
            "deltas": deltas,
            "evidence_hash": evidence_hash,
            "verdict": "SURVIVED",  # 必须是 SURVIVED 或 FALLEN，严禁 PASS
            "radar_chart": radar_chart
        }


# 挂载 FastAPI 实例 (只保留一个)
api_app = FastAPI(title="归心 L9 动态沙盒引擎", version="1.0.0")


@api_app.post("/v1/sandbox/execute", response_model=CertificationReport)
async def trigger_combat(resume_text: str = "5年Go经验，精通Redis微服务"):
    """
    C端触发：简历输入 -> 深渊战役 -> 神谕确权输出
    """
    orchestrator = SandboxOrchestrator()
    report = await orchestrator.execute(resume_text)
    return report


@api_app.post("/v1/search/hybrid")
async def trigger_search(
        query: str = Query("需要一个能在高并发下处理 Redis 分布式死锁的后端", description="HR搜索意图"),
        tags: List[str] = Query(["高并发", "Redis", "死锁"], description="意图降维硬标签")
):
    """
    B端触发：意图降维 -> 降维漏斗召回 -> RRF融合
    """
    results = await search_pipeline(query, tags)
    return JSONResponse(content=results)