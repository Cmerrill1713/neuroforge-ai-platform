# Agentic LLM Core v0.1

A sophisticated **agentic LLM framework** designed for local-first AI agent systems with comprehensive tool integration, multimodal capabilities, and enterprise-grade security.

## 🚀 Overview

This project implements a complete **agentic LLM core system** with:

- **🧠 Multimodal AI**: Qwen3-Omni integration for text, image, audio, and video processing
- **🔧 Tool Catalog**: 14 comprehensive tools across 7 categories with safety levels and permissions
- **🔒 Security-First**: Advanced redaction, audit trails, and access control
- **📊 MCP Integration**: Model Context Protocol adapter for tool execution
- **🏗️ Agentic Architecture**: Planner, Reviewer, and Runner components for autonomous task execution
- **💾 Vector Storage**: PostgreSQL and Weaviate integration for knowledge management
- **📈 Performance**: Apple Silicon optimization with < 50ms latency targets

## 📁 Project Structure

```
├── src/core/                    # Core system components
│   ├── chat/                   # Multimodal chat system
│   ├── mcp/                    # Model Context Protocol integration
│   ├── memory/                 # Vector storage (PostgreSQL, Weaviate)
│   ├── models/                 # Data contracts and schemas
│   ├── providers/              # LLM providers (Qwen3)
│   ├── runtime/                # Agentic components (Planner, Reviewer, Runner)
│   ├── security/               # Security policies and redaction
│   ├── tools/                  # Tool catalog and MCP adapter
│   └── vision/                 # Vision processing system
├── configs/                    # Configuration files
│   ├── policies.yaml          # Tool catalog and security policies
│   └── samples/               # Sample configurations
├── tests/                      # Comprehensive test suite (318 tests)
├── examples/                   # Usage examples
├── specs/                      # System specifications
├── plans/                      # Architecture and milestone plans
└── tasks/                      # Milestone definitions
```

## 🛠️ Tool Catalog

The system includes **14 production-ready tools** across **7 categories**:

### File Operations (3 tools)
- `file_read` - Read file contents (🟢 Safe)
- `file_write` - Write content to files (🟡 Moderate)  
- `file_delete` - Delete files (🟠 Dangerous)

### Database Operations (2 tools)
- `db_query` - Execute SELECT queries (🟡 Moderate)
- `db_execute` - Execute INSERT/UPDATE/DELETE (🟠 Dangerous)

### Network Operations (2 tools)
- `http_get` - HTTP GET requests (🟡 Moderate)
- `http_post` - HTTP POST requests (🟡 Moderate)

### Text Processing (2 tools)
- `text_extract` - Extract text from various formats (🟢 Safe)
- `text_summarize` - Generate text summaries (🟢 Safe)

### Data Analysis (1 tool)
- `data_analyze` - Analyze structured data (🟢 Safe)

### Security Operations (2 tools)
- `encrypt_data` - Encrypt sensitive data (🔴 Critical)
- `decrypt_data` - Decrypt encrypted data (🔴 Critical)

### Utility Operations (2 tools)
- `uuid_generate` - Generate UUIDs (🟢 Safe)
- `timestamp_now` - Get current timestamps (🟢 Safe)

## 🔧 Quick Start

### Prerequisites
- Python 3.9+
- Apple Silicon Mac (optimized for M1/M2/M3)
- PostgreSQL (for vector storage)
- 16GB+ RAM (for Qwen3-Omni model)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd prompt-engineering
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   pip3 install pytest-asyncio  # For async test support
   ```

3. **Validate the system**
   ```bash
   # Validate tool catalog
   python3 src/core/tools/catalog.py configs/policies.yaml --validate --print-summaries
   
   # Run tests
   python3 -m pytest tests/ -v
   ```

4. **Run examples**
   ```bash
   # Multimodal chat example
   python3 examples/multimodal_chat.py
   
   # Task execution example
   python3 examples/runner_example.py
   ```

## ♻️ Continuous Improvement Loop

The self-iterating orchestrator monitors grading metrics and proposes upgrades automatically.

1. **Smoke Test**
   ```bash
   PYTHONPATH=. python3 - <<'PY'
   import asyncio
   from pathlib import Path
   from datetime import datetime

   from src.core.orchestration import SelfImprovementOrchestrator, TriggerConfig
   from src.core.training import (
       GradeRecord,
       ParallelDatasetBuilder,
       ParallelExecutionPolicy,
       ParallelR1Pipeline,
       ParallelRLTrainer,
       ParallelSFTTrainer,
       PromptRecycler,
   )

   grades = [
       GradeRecord(prompt="Check circuit", response="Path A...\n\nPath B...", score=0.78, metadata={"difficulty": "bench"}),
       GradeRecord(prompt="Explain RL stage", response="Detailed reasoning", score=0.81, metadata={"difficulty": "bench"}),
       GradeRecord(prompt="Summarise spec", response="Two paths", score=0.74, metadata={"difficulty": "bench"}),
   ]

   kb_dir = Path(".smoke_kb"); kb_dir.mkdir(exist_ok=True)
   (kb_dir / "parallel.md").write_text("Parallel reasoning quick reference", encoding="utf-8")

   pipeline = ParallelR1Pipeline(
       dataset_builder=ParallelDatasetBuilder(knowledge_base_dir=kb_dir, enable_vector_store=False),
       sft_trainer=ParallelSFTTrainer(Path(".smoke_out")),
       rl_trainer=ParallelRLTrainer(),
       execution_policy=ParallelExecutionPolicy(),
       recycler=PromptRecycler(),
   )

   orchestrator = SelfImprovementOrchestrator(
       pipeline=pipeline,
       grade_fetcher=lambda: grades,
       trigger_config=TriggerConfig(min_average_score=0.9, max_iterations_per_run=2),
       workdir=Path(".smoke_history"),
   )

   report = asyncio.run(orchestrator.run_once(last_run_timestamp=datetime.now().timestamp()))
   print("Triggered:", report.triggered)
   print("Reason:", report.reason)
   print("Promoted candidate:", report.promoted_candidate)
   print("History entry:", (Path(".smoke_history") / "orchestration_history.jsonl").read_text())
   PY
   ```

2. **Scheduling** – Run `SelfImprovementOrchestrator.run_once()` daily or when new grades land. Store history under `.self_improvement/` and monitor `monitoring_summary.jsonl`.

3. **Promotion Callback** – Attach a callback that snapshots the current config, applies promoted settings, notifies maintainers, and records rollback steps.

See `docs/contributing.md` for the full workflow.

## 📊 System Status

### ✅ **Compliance Score: 87%**

| Category | Score | Status |
|----------|-------|--------|
| **Specification Compliance** | 100% | ✅ EXCELLENT |
| **Security Compliance** | 100% | ✅ EXCELLENT |
| **Model Policy Compliance** | 100% | ✅ EXCELLENT |
| **Architecture Compliance** | 100% | ✅ EXCELLENT |
| **Test Coverage** | 4% | ❌ NEEDS IMPROVEMENT |
| **Code Quality** | 90% | ⚠️ GOOD |
| **Documentation** | 100% | ✅ EXCELLENT |
| **Configuration** | 100% | ✅ EXCELLENT |

### 🚨 **Critical Issues: 0** 🟢
- All core dependencies available
- Project structure compliant
- Security and model policies operational
- No blocking configuration errors

### ⚠️ **Areas for Improvement**
1. **Test Coverage**: Currently 4% → Target: 80%
2. **Pydantic V2 Migration**: Update deprecated `@validator` decorators
3. **Async Test Support**: Install `pytest-asyncio` for async test execution

## 🔒 Security Features

- **Data Redaction**: 6 pattern types (API keys, secrets, emails, credit cards, SSN, phone numbers)
- **Tool Access Control**: Allowlist/blocklist with permission system
- **Audit Trail**: 90-day retention with comprehensive logging
- **Side Effects Monitoring**: Real-time security event detection

## 🤖 Model Integration

- **Primary Model**: Qwen3-Omni-30B-A3B (multimodal, 128K context)
- **Fallback Model**: Qwen3-7B-Instruct (text-only, 32K context)
- **Intelligent Routing**: Resource-aware model selection
- **Performance Optimization**: Apple Silicon MPS acceleration

## 📈 Performance Targets

- **Latency**: < 50ms for critical operations
- **Memory**: < 16GB for primary model
- **Throughput**: 10+ concurrent requests
- **Availability**: 99.9% uptime target

## 🧪 Testing

The system includes **318 comprehensive tests** across all components:

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test suites
python3 -m pytest tests/test_contracts.py -v
python3 -m pytest tests/test_mcp_adapter.py -v
python3 -m pytest tests/test_planner.py -v
```

## 📚 Documentation

- **System Specifications**: `specs/system.md`
- **Architecture Plans**: `plans/architecture.md`
- **Security Policies**: `configs/policies.yaml`
- **Compliance Report**: `COMPLIANCE_REPORT.md`
- **Usage Examples**: `examples/` directory

## 🚀 Roadmap

### Phase 1: Test Coverage (Priority: HIGH)
- [ ] Implement comprehensive test suites for all modules
- [ ] Achieve 80%+ coverage target
- [ ] Set up automated coverage reporting

### Phase 2: Code Quality (Priority: MEDIUM)
- [ ] Migrate to Pydantic V2 (`@field_validator`)
- [ ] Add comprehensive docstrings
- [ ] Implement code quality checks in CI/CD

### Phase 3: Production Readiness (Priority: LOW)
- [ ] Performance optimization
- [ ] Advanced monitoring
- [ ] Load testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
- **Documentation**: Check the `specs/` and `plans/` directories
- **Examples**: See the `examples/` directory
- **Tests**: Run `python3 -m pytest tests/ -v` for system validation

---

**Agentic LLM Core v0.1** - Building the future of autonomous AI agents 🚀
