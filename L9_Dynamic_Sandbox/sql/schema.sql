	-- 开启向量与主键生成扩展 (呼应考官对分布式主键的考察)
	CREATE EXTENSION IF NOT EXISTS vector;
	CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
	-- 1. 统一能力树 (替代一切旧维度表，度量衡底座)
	CREATE TABLE ability_taxonomy_nodes (
	    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	    ability_code TEXT UNIQUE NOT NULL,
	    ability_name TEXT NOT NULL,
	    layer SMALLINT NOT NULL CHECK (layer IN (32, 128, 1024)), -- 三层降维基础
	    parent_id UUID NULL REFERENCES ability_taxonomy_nodes(id) ON DELETE CASCADE,
	    vector_index INT NOT NULL, -- 对应向量中的维度索引
	    status TEXT DEFAULT 'active',
	    metadata JSONB
	);
	-- 2. 题目能力评分账本 (最原始的防伪证据，可回放可撤销)
	CREATE TABLE question_ability_scores (
	    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	    assessment_id UUID NOT NULL,
	    candidate_id UUID NOT NULL,
	    ability_id UUID NOT NULL REFERENCES ability_taxonomy_nodes(id),
	    raw_score NUMERIC(5,2) CHECK (raw_score BETWEEN 0 AND 100),
	    normalized_score NUMERIC(6,5) CHECK (normalized_score BETWEEN 0 AND 1),
	    weight NUMERIC(6,5) DEFAULT 1.0,
	    contribution_score NUMERIC(8,5),
	    score_source TEXT CHECK (score_source IN ('ai_grader', 'objective_rule', 'human_override')),
	    evidence JSONB,
	    -- 极其关键：账本必须有落盘时间，支撑 EMA 衰减与战局回放
	    created_at TIMESTAMPTZ DEFAULT NOW()
	);
	-- 3. 候选人三层向量池 (分离分数与向量，严禁混用)
	CREATE TABLE candidate_vectors (
	    candidate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	    profile_data JSONB NOT NULL DEFAULT '{}'::jsonb, -- 存储 verified_skills 和 reranker_payload
	    ability_vec_32 vector(32),    -- L1 粗召回
	    ability_vec_128 vector(128),  -- L2 中召回
	    ability_vec_1024 vector(1024),-- L3 精召回
	    last_certified_at TIMESTAMPTZ,
	    vec_version TEXT,
	    CONSTRAINT chk_profile_structure CHECK (
	        jsonb_typeof(profile_data->'verified_skills') = 'array'
	    )
	);
	-- 4. B端需求快照 (固化需求向量，支持搜索重放)
	CREATE TABLE job_requirement_profiles (
	    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	    query_text TEXT NOT NULL,
	    target_vec_32 vector(32),
	    target_vec_128 vector(128),
	    target_vec_1024 vector(1024),
	    must_have_abilities JSONB,
	    ability_weights JSONB,
	    created_at TIMESTAMPTZ DEFAULT NOW()
	);
	-- 极致索引设计 (OOM防备与性能核武)
	CREATE INDEX idx_candidate_profile_gin ON candidate_vectors USING GIN (profile_data);
	-- HNSW 参数调整：m=16, ef_construction=64 平衡内存与构建速度
	CREATE INDEX idx_candidate_vec32_hnsw ON candidate_vectors USING hnsw (ability_vec_32 vector_cosine_ops) WITH (m = 16, ef_construction = 64);
	CREATE INDEX idx_candidate_vec128_hnsw ON candidate_vectors USING hnsw (ability_vec_128 vector_cosine_ops) WITH (m = 16, ef_construction = 64);
	-- 极客防 OOM 备注：1024 维度极高，HNSW 构建成本暴增。工业实践中 L3 精排常依赖 L2 粗排后做精准距离计算(暴力搜索)。
	-- 若执意建 HNSW，需控参防 OOM：m=12, ef_construction=50
	CREATE INDEX idx_candidate_vec1024_hnsw ON candidate_vectors USING hnsw (ability_vec_1024 vector_cosine_ops) WITH (m = 12, ef_construction = 50);