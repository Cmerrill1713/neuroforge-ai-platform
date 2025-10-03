# 🚀 Production RAG Integration - Drop-In Replacement

## What Changed

Your evolutionary optimizer was referencing PostgreSQL vectors, but your **live production stack** uses:

✅ **Weaviate** - Vector search (ports 8080 HTTP, 50051 gRPC)
✅ **Elasticsearch** - BM25/keyword search  
✅ **Redis** - Caching  
✅ **PostgreSQL** - Doc registry/metadata only (NO vectors)
✅ **Cross-encoder** - Reranking

This guide shows the **clean delta** to ship today.

---

## Architecture: Before vs After

### Before (Incorrect)
```
Evolutionary Optimizer
        ↓
PostgreSQL pgvector
```

### After (Correct - Your Live Stack)
```
Evolutionary Optimizer
        ↓
Production RAG Service
        ↓
    ┌───┴───┬──────────┬────────┐
    ↓       ↓          ↓        ↓
Weaviate  ES    Redis      PG
(vectors) (BM25) (cache) (registry)
        ↓
RRF Fusion → Reranker → Top-K
```

---

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `src/core/retrieval/vector_store.py` | Abstract interface | 60 |
| `src/core/retrieval/weaviate_store.py` | Weaviate adapter | 200 |
| `src/core/retrieval/hybrid_retriever.py` | Hybrid search + RRF + reranker | 400 |
| `src/core/retrieval/rag_service.py` | Unified RAG service | 250 |
| `src/core/prompting/rag_integration_patch.py` | Integration guide | 150 |
| `src/core/monitoring/evolutionary_metrics.py` | Prometheus metrics | 300 |

**Total:** ~1,360 lines of production-ready code

---

## Integration: 2-Line Change

### Option 1: Minimal Change (Recommended)

In `src/core/prompting/dual_backend_integration.py`:

**Line ~8 (imports):**
```python
# OLD:
from src.core.memory.vector_pg import PostgreSQLVectorStore

# NEW:
from src.core.retrieval.rag_service import create_rag_service
```

**Line ~82 (initialization):**
```python
# OLD:
self.vector_store = PostgreSQLVectorStore()
logger.info("✅ Vector store initialized")

# NEW:
self.rag_service = create_rag_service(env="production")
logger.info("✅ RAG service initialized (Weaviate + ES + Reranker)")
```

**That's it!** The RAG service is now plugged in.

### Option 2: Enhanced Integration (RAG-aware prompts)

Add this to your executor methods to enrich prompts with retrieved context:

```python
async def executor(self, spec, genome):
    # Enrich prompt with RAG context if genome uses RAG
    if hasattr(genome, 'use_rag') and genome.use_rag:
        rag_context = await self.rag_service.query_with_context(
            query_text=spec.prompt,
            k=3,
            method="hybrid"
        )
        enriched_prompt = f"{spec.prompt}\n\n{rag_context}"
    else:
        enriched_prompt = spec.prompt
    
    # Continue with normal execution...
```

---

## Environment Variables

Add to your `.env` or docker-compose:

```bash
# Weaviate
WEAVIATE_HOST=weaviate
WEAVIATE_HTTP=8080
WEAVIATE_GRPC=50051
WEAVIATE_CLASS=DocChunk

# Elasticsearch
ELASTIC_URL=http://elasticsearch:9200
ELASTIC_INDEX=docs

# Redis
REDIS_URL=redis://redis:6379/0

# Models
EMBEDDER_MODEL=BAAI/bge-small-en-v1.5
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

---

## Smoke Test (15 minutes)

### 1. Verify Stack is Running

```bash
# Check Weaviate
curl http://localhost:8080/v1/.well-known/ready

# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check Redis
redis-cli ping
```

### 2. Test RAG Service

```python
# test_rag.py
import asyncio
from src.core.retrieval.rag_service import create_rag_service

async def test():
    rag = create_rag_service(env="production")
    
    # Test query
    response = await rag.query(
        query_text="What are the safety requirements for widget installation?",
        k=5,
        method="hybrid"
    )
    
    print(f"✅ Found {response.num_results} results in {response.latency_ms:.0f}ms")
    for i, result in enumerate(response.results, 1):
        print(f"  {i}. {result.text[:100]}... (score: {result.score:.3f})")
    
    # Check metrics
    metrics = rag.get_metrics()
    print(f"\n📊 Metrics:")
    print(f"  Cache hit ratio: {metrics['hybrid']['cache_hit_ratio']:.2%}")
    print(f"  Avg latency: {metrics['hybrid']['avg_latency_ms']:.0f}ms")

asyncio.run(test())
```

```bash
python test_rag.py
```

**Expected Output:**
```
✅ Found 5 results in 247ms
  1. Widget installation requires proper grounding and... (score: 0.856)
  2. Safety specifications mandate the following steps... (score: 0.823)
  ...

📊 Metrics:
  Cache hit ratio: 0.0% (cold start)
  Avg latency: 247ms
```

### 3. Run Quick Evolution

```bash
# Build dataset
python scripts/build_golden_dataset.py

# Run 3 generations (quick test)
python -c "
import asyncio
import json
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration

async def test():
    integration = DualBackendEvolutionaryIntegration()
    await integration.initialize()
    
    with open('data/golden_dataset.json') as f:
        dataset = json.load(f)['examples'][:10]
    
    best = await integration.optimize_comprehensive(
        base_prompt='You are a helpful assistant.',
        golden_dataset=dataset,
        num_generations=3,
        use_mipro=False
    )
    
    print(f'✅ Best: temp={best.temp}, tokens={best.max_tokens}')

asyncio.run(test())
"
```

---

## Monitoring Setup

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'evolutionary_optimizer'
    static_configs:
      - targets: ['localhost:8000']  # Your API port
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard

Key panels to add:

#### 1. Evolution Performance
```promql
# Best score per generation
evo_generation_best_score

# Mean score trend
evo_generation_mean_score
```

#### 2. Bandit Performance
```promql
# Reward distribution
avg(bandit_reward_mean) by (genome_id)

# Pull distribution
sum(rate(bandit_pulls_total[5m])) by (genome_id)
```

#### 3. Retrieval Quality
```promql
# p95 latency
histogram_quantile(0.95, retrieval_latency_ms_bucket{method="hybrid"})

# Cache hit ratio
rate(reranker_cache_hit[5m]) / 
  (rate(reranker_cache_hit[5m]) + rate(reranker_cache_miss[5m]))

# Answer quality
answerable_at_k{k="10"}
exact_match_at_k{k="1"}
```

#### 4. System Health
```promql
# Error rate
sum(rate(execution_errors[5m])) by (backend, error_type)

# Cost per query
rate(execution_cost_usd_sum[5m]) / rate(execution_cost_usd_count[5m])
```

### Alert Rules

```yaml
groups:
  - name: evolutionary_optimizer
    rules:
      # Latency too high
      - alert: RetrievalLatencyHigh
        expr: histogram_quantile(0.95, retrieval_latency_ms_bucket) > 500
        for: 5m
        annotations:
          summary: "Retrieval p95 latency > 500ms"
      
      # Quality degradation
      - alert: AnswerQualityLow
        expr: exact_match_at_k{k="1"} < 0.7
        for: 10m
        annotations:
          summary: "Exact match @ 1 dropped below 70%"
      
      # Cache issues
      - alert: RerankerCacheLow
        expr: |
          rate(reranker_cache_hit[5m]) / 
          (rate(reranker_cache_hit[5m]) + rate(reranker_cache_miss[5m])) < 0.5
        for: 10m
        annotations:
          summary: "Reranker cache hit ratio < 50%"
```

---

## Bandit Deployment Strategy

### Phase 1: 10% Canary (Day 1-3)

```python
import random

@app.post("/chat")
async def chat(request: ChatRequest):
    # 10% evolutionary, 90% baseline
    if random.random() < 0.10:
        # Use evolutionary bandit
        result = await integration.production_route(
            user_query=request.message,
            context=request.context
        )
    else:
        # Use baseline
        result = await baseline_chat(request)
    
    return result
```

**Monitor:**
- Exact@1 not worse than baseline
- p95 latency not >10% worse
- User satisfaction scores

### Phase 2: 50% Rollout (Day 4-7)

If metrics are good:
- Increase to 50% traffic
- Monitor for 3 days
- Check for edge cases

### Phase 3: 100% (Day 8+)

If 50% is stable:
- Full rollout
- Keep baseline as fallback
- Bandit auto-optimizes

**Rollback Criteria:**
- Exact@1 drops >5%
- p95 latency increases >20%
- Error rate increases >10%

---

## Ingest Pipeline

When adding documents, ingest to ALL systems:

```python
# ingest_doc.py
import asyncio
from src.core.retrieval.weaviate_store import WeaviateStore
from elasticsearch import Elasticsearch
import psycopg2

async def ingest_document(doc_id: str, text: str, metadata: dict, embedding: list):
    # 1. Weaviate (vectors)
    weaviate = WeaviateStore()
    await weaviate.upsert([{
        "id": doc_id,
        "vector": embedding,  # Normalized!
        "properties": {
            "text": text,
            **metadata,
            "embedder": "bge-small-en-v1.5",
            "version": "1.0"
        }
    }])
    
    # 2. Elasticsearch (text + BM25)
    es = Elasticsearch("http://elasticsearch:9200")
    es.index(
        index="docs",
        id=doc_id,
        document={
            "text": text,
            **metadata
        }
    )
    
    # 3. PostgreSQL (registry only, NO vectors)
    conn = psycopg2.connect("...")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO docs (id, doc_type, created_at, metadata)
        VALUES (%s, %s, NOW(), %s)
    """, (doc_id, metadata.get("doctype"), json.dumps(metadata)))
    conn.commit()
    
    print(f"✅ Ingested {doc_id} to all systems")
```

**Important:**
- Normalize embeddings before Weaviate insert
- Store embedder version in metadata
- Keep embedder consistent across all docs

---

## Security & Ops

### 1. Rate Limiting

```python
# In nginx
limit_req_zone $binary_remote_addr zone=optimize:10m rate=10r/m;

location /optimize {
    limit_req zone=optimize burst=5;
    proxy_pass http://backend:8000;
}
```

### 2. Logging

```python
# Log genome IDs and hashes, NEVER raw prompts with secrets
logger.info(f"Genome {genome_id[:8]}... executed",
    extra={
        "genome_id": genome_id,
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
        "backend": backend,
        "latency_ms": latency
    }
)
```

### 3. Version Checks

```python
# Refuse mixed embedder versions
async def query(self, ...):
    results = await weaviate.query(...)
    
    versions = set(r.metadata.get("embedder") for r in results)
    if len(versions) > 1 and not allow_mixed:
        raise ValueError(f"Mixed embedder versions: {versions}")
```

---

## Troubleshooting

### Issue: Weaviate Connection Failed

**Error:** `ConnectionError: Weaviate not ready`

**Fix:**
```bash
# Check Weaviate is running
docker ps | grep weaviate

# Check ports
netstat -an | grep 8080
netstat -an | grep 50051

# Test connection
curl http://localhost:8080/v1/.well-known/ready
```

### Issue: No Results from Elasticsearch

**Error:** `IndexNotFoundException: no such index [docs]`

**Fix:**
```bash
# Create index
curl -X PUT "localhost:9200/docs" -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "text": {"type": "text"},
      "doc_id": {"type": "keyword"},
      "doctype": {"type": "keyword"}
    }
  }
}'

# Verify
curl "localhost:9200/docs/_count"
```

### Issue: Reranker Out of Memory

**Error:** `CUDA out of memory`

**Fix:**
```python
# Use CPU-only model
reranker_model = "cross-encoder/ms-marco-TinyBERT-L-2-v2"

# Or reduce batch size
reranker.predict(pairs, batch_size=8)  # Default is 32
```

### Issue: Redis Connection Timeout

**Fix:**
```bash
# Check Redis
redis-cli ping

# Increase timeout in config
redis_url = "redis://redis:6379/0?socket_timeout=5"
```

---

## Performance Tuning

### Optimize Weaviate

```yaml
# docker-compose.yml
weaviate:
  environment:
    QUERY_DEFAULTS_LIMIT: 100
    QUERY_MAXIMUM_RESULTS: 1000
    PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
  volumes:
    - weaviate_data:/var/lib/weaviate
```

### Optimize Elasticsearch

```yaml
elasticsearch:
  environment:
    ES_JAVA_OPTS: "-Xms2g -Xmx2g"  # Increase heap
    discovery.type: single-node
  ulimits:
    memlock:
      soft: -1
      hard: -1
```

### Optimize Redis

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save ""  # Disable persistence for cache-only
```

---

## Success Metrics (After 1 Week)

| Metric | Baseline | Target | Measure |
|--------|----------|--------|---------|
| **Exact@1** | 65% | 75%+ | `exact_match_at_k{k="1"}` |
| **Answerable@10** | 85% | 90%+ | `answerable_at_k{k="10"}` |
| **p95 Latency** | 800ms | <500ms | `histogram_quantile(0.95, retrieval_latency_ms_bucket)` |
| **Cache Hit Ratio** | N/A | >70% | `cache_hits / (cache_hits + cache_misses)` |
| **Cost/Query** | $0.05 | <$0.02 | `rate(execution_cost_usd_sum) / rate(execution_cost_usd_count)` |

---

## Next Steps

✅ **Today:** Apply 2-line patch, run smoke test
✅ **Tomorrow:** Ingest 10-20 docs, test hybrid retrieval
✅ **This Week:** Run full evolution with RAG context
✅ **Next Week:** Deploy with 10% bandit traffic
✅ **Week 3:** Scale to 100%, enable nightly daemon

---

## Summary

**What You Changed:**
- ✅ Swapped PostgreSQL vectors → Weaviate
- ✅ Added Elasticsearch BM25
- ✅ Added RRF fusion + reranking
- ✅ Added Redis caching
- ✅ Added Prometheus metrics

**Integration Effort:**
- **Code:** 2 lines changed in main file
- **Time:** 15 minutes smoke test
- **Risk:** Low (clean abstraction, easy rollback)

**Your evolutionary optimizer now uses your ACTUAL production stack!** 🎉

