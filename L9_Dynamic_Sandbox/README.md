	# 归心 L9 动态沙盒与混合检索管线引擎
	> 最高纪律：严禁 Elasticsearch，严禁静态题库，严禁硬编码。PostgreSQL + pgvector 一体化打穿。
	## 核心架构拓扑
	```text
	[Candidate Resume] 
	      │ 
	      ▼
	┌─────────────────────────────────────────────────┐
	│            L9 Combat Engine (C端深渊战役)          │
	│                                                 │
	│  [Ingestion] ──> [Battlefield] ──> [X-RAG]     │
	│  DNA提取        私有框架残卷渲染    绞肉机防伪注入   │
	│                                                 │
	│                   │                             │
	│                   ▼                             │
	│            [Oracle Judge]                       │
	│   强制输出 1024d Vector + 防伪 Hash + 雷达图       │
	└─────────────────────────────────────────────────┘
	      │ (Write Path - 账本落盘)
	      ▼
	┌─────────────────────────────────────────────────┐
	│        Supabase PostgreSQL (底层度量衡)            │
	│  ability_library (1024 Atoms)                   │
	│  candidate_dnas (vector(1024) + HNSW Index)     │
	└─────────────────────────────────────────────────┘
	      │ (Read Path - B端检索)
	      ▼
	┌─────────────────────────────────────────────────┐
	│        Hybrid Search Pipeline (降维检索管线)       │
	│                                                 │
	│  L1(32d粗召) + L2(128d中召) + L3(1024d精召)      │
	│       │             │              │             │
	│       └─────────────┴──────────────┘             │
	│                     │                           │
	│             [ RRF 倒数秩融合 ]                     │
	│            (k=60, 纯内存计算)                     │
	│                     │                           │
	│             [ Cross-Encoder ]                   │
	│             Top 3 绝杀输出                        │
	└─────────────────────────────────────────────────┘


uvicorn app.main:api_app --reload --port 8024


http://127.0.0.1:8024/docs
找到 /v1/sandbox/execute Try it out Execute 

vector_1024 和 anti_tamper_hash 极客认证报告

找到 /v1/search/hybrid Try it out Execute

rrf_score 降维召回漏斗数据。