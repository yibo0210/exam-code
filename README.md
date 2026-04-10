# exam-code
just for exam
	# 归心 L9 动态沙盒引擎 - 全链路重构版
	> 这不是一次代码提交，而是一次对 PRD 逻辑漏洞的推翻与重构。
	## 核心架构降维打击点
	1. **推翻 1024 维全量输出陷阱**：Oracle Judge 仅输出稀疏增量，由 Python 后端以 EMA 衰减合并至全零向量，彻底杜绝大模型 Token 截断与格式崩坏。
	2. **阻断信息泄露防线**：Battlefield Agent 物理隔离原始简历，仅接收脱敏 DNA，粉碎 AI 代写与八股文套作。
	3. **三层漏斗与 RRF 融合**：B 端检索实现 L1(32v)-L2(128v)-L3(1024v) 物理降维，手写 RRF 倒数秩融合算法合并异构召回。
	4. **账本溯源与防 OOM**：DDL 采用增量事件账本设计，并针对 1024 维 HNSW 索引进行参数降级防内存溢出。
	## 技术栈
	- Python FastAPI + Supabase PostgreSQL + pgvector
	## 启动方式
	```bash
	uvicorn app.main:api_app --reload --port 8024
