# Architecture Plan: Agentic LLM Core v0.1

## Overview
**Project:** Agentic LLM Core v0.1 MVP  
**Created:** 2024-09-24  
**Status:** Planning Phase  
**Target Features:** Ingest & Answer, Tool Exec MCP, Multimodal Inputs

## Core Feature Architecture

### 1. Ingest & Answer Pipeline

#### Architecture Pattern
**Pattern:** Linear Processing Pipeline with Async Processing  
**Design Principle:** Single Responsibility with Clear Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │───▶│  Process    │───▶│  Context    │───▶│   Answer    │
│ Ingestion   │    │  Pipeline   │    │  Analysis   │    │ Generation  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Validation  │    │ Multimodal  │    │ Qwen3-Omni  │    │ Output      │
│ & Type      │    │ Processing  │    │ Engine      │    │ Formatting  │
│ Safety      │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### Component Design

**1. Input Ingestion Layer**
```python
# Core responsibility: Accept and validate inputs
class InputIngestionService:
    def __init__(self, validator: PydanticValidator):
        self.validator = validator
        self.input_queue = asyncio.Queue(maxsize=100)
    
    async def ingest_text(self, content: str, metadata: dict) -> ProcessedInput:
        # Validate text input with strict Pydantic schemas
        validated = self.validator.validate_text_input(content, metadata)
        return await self._process_text(validated)
    
    async def ingest_image(self, data: bytes, metadata: dict) -> ProcessedInput:
        # Validate image with size/format constraints
        validated = self.validator.validate_image_input(data, metadata)
        return await self._process_image(validated)
    
    async def ingest_document(self, path: str, metadata: dict) -> ProcessedInput:
        # Validate document with type/size constraints
        validated = self.validator.validate_document_input(path, metadata)
        return await self._process_document(validated)
```

**2. Processing Pipeline**
```python
# Core responsibility: Process inputs through multimodal pipeline
class ProcessingPipeline:
    def __init__(self, multimodal_handler: MultimodalHandler):
        self.handler = multimodal_handler
        self.processors = {
            'text': self._process_text,
            'image': self._process_image,
            'document': self._process_document
        }
    
    async def process(self, input_data: ProcessedInput) -> UnifiedContext:
        # Route to appropriate processor based on input type
        processor = self.processors[input_data.input_type]
        return await processor(input_data)
```

**3. Context Analysis Engine**
```python
# Core responsibility: Analyze context and determine intent
class ContextAnalysisEngine:
    def __init__(self, qwen_engine: Qwen3OmniEngine):
        self.engine = qwen_engine
        self.analysis_cache = {}  # For deterministic results
    
    async def analyze(self, context: UnifiedContext) -> ContextAnalysis:
        # Use Qwen3-Omni for consistent context understanding
        cache_key = self._generate_cache_key(context)
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        analysis = await self.engine.analyze_context(context)
        self.analysis_cache[cache_key] = analysis
        return analysis
```

**4. Answer Generation Service**
```python
# Core responsibility: Generate structured answers
class AnswerGenerationService:
    def __init__(self, qwen_engine: Qwen3OmniEngine, tool_engine: MCPToolEngine):
        self.engine = qwen_engine
        self.tool_engine = tool_engine
    
    async def generate_answer(self, analysis: ContextAnalysis) -> FinalAnswer:
        # Generate base answer
        base_answer = await self.engine.generate_answer(analysis, [])
        
        # Execute tools if needed
        if analysis.required_tools:
            tool_results = await self.tool_engine.execute_tools(analysis.required_tools)
            final_answer = await self._integrate_tool_results(base_answer, tool_results)
        else:
            final_answer = base_answer
        
        return final_answer
```

### 2. Tool Exec MCP Architecture

#### Architecture Pattern
**Pattern:** Plugin-based Tool System with Strict Interface Contracts  
**Design Principle:** Interface Segregation with Type Safety

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Tool      │───▶│   Tool      │───▶│   Tool      │───▶│   Tool      │
│ Discovery   │    │ Selection   │    │ Execution   │    │ Integration │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Registry    │    │ Schema      │    │ Sandboxed   │    │ Result      │
│ Management  │    │ Validation  │    │ Execution   │    │ Processing  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### Component Design

**1. MCP Tool Registry**
```python
# Core responsibility: Manage tool registration and discovery
class MCPToolRegistry:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.schemas: Dict[str, ToolSchema] = {}
    
    def register_tool(self, tool: MCPTool, schema: ToolSchema) -> None:
        # Strict schema validation to prevent drift
        validated_schema = self._validate_schema(schema)
        self.tools[tool.name] = tool
        self.schemas[tool.name] = validated_schema
    
    def discover_tools(self, context: ContextAnalysis) -> List[AvailableTool]:
        # Return tools that match context requirements
        return [tool for tool in self.tools.values() 
                if self._tool_matches_context(tool, context)]
```

**2. Tool Execution Engine**
```python
# Core responsibility: Execute tools with strict I/O validation
class MCPToolExecutionEngine:
    def __init__(self, registry: MCPToolRegistry, validator: PydanticValidator):
        self.registry = registry
        self.validator = validator
        self.execution_history = []  # For deterministic behavior
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        # Validate input schema strictly
        tool_schema = self.registry.schemas[tool_call.tool_name]
        validated_input = self.validator.validate_tool_input(
            tool_call.parameters, tool_schema.input_schema
        )
        
        # Execute with sandboxing
        result = await self._sandboxed_execution(tool_call.tool_name, validated_input)
        
        # Validate output schema strictly
        validated_output = self.validator.validate_tool_output(
            result, tool_schema.output_schema
        )
        
        # Log for reproducibility
        self.execution_history.append({
            'tool': tool_call.tool_name,
            'input': validated_input,
            'output': validated_output,
            'timestamp': datetime.utcnow()
        })
        
        return validated_output
```

**3. Tool Integration Service**
```python
# Core responsibility: Integrate tool results into answers
class ToolIntegrationService:
    def __init__(self, qwen_engine: Qwen3OmniEngine):
        self.engine = qwen_engine
    
    async def integrate_results(self, 
                               base_answer: str, 
                               tool_results: List[ToolResult]) -> FinalAnswer:
        # Use Qwen3-Omni to intelligently integrate tool results
        integration_prompt = self._create_integration_prompt(base_answer, tool_results)
        integrated_answer = await self.engine.generate_answer(integration_prompt)
        
        return FinalAnswer(
            answer=integrated_answer,
            confidence=self._calculate_confidence(tool_results),
            tools_used=[result.tool_name for result in tool_results],
            processing_time=self._calculate_processing_time(tool_results),
            metadata=self._extract_metadata(tool_results)
        )
```

### 3. Multimodal Inputs Architecture

#### Architecture Pattern
**Pattern:** Adapter Pattern with Unified Processing Pipeline  
**Design Principle:** Open/Closed Principle for Input Types

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │───▶│   Input     │───▶│   Feature   │───▶│  Unified    │
│ Adapters    │    │ Processors  │    │ Extractors  │    │ Context     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Text        │    │ Validation  │    │ Embedding   │    │ Context     │
│ Image       │    │ Normalize   │    │ Generation  │    │ Fusion      │
│ Document    │    │ Transform   │    │ Similarity  │    │ Scoring     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### Component Design

**1. Input Adapters**
```python
# Core responsibility: Handle different input types uniformly
class InputAdapter(ABC):
    @abstractmethod
    async def process(self, raw_input: Any) -> ProcessedInput:
        pass
    
    @abstractmethod
    def validate(self, raw_input: Any) -> bool:
        pass

class TextInputAdapter(InputAdapter):
    async def process(self, raw_input: str) -> ProcessedInput:
        # Extract text features and metadata
        return ProcessedInput(
            input_type="text",
            content=raw_input,
            metadata=self._extract_text_metadata(raw_input),
            timestamp=datetime.utcnow()
        )
    
    def validate(self, raw_input: str) -> bool:
        # Strict validation with Pydantic schemas
        return len(raw_input) <= 10000 and isinstance(raw_input, str)

class ImageInputAdapter(InputAdapter):
    async def process(self, raw_input: bytes) -> ProcessedInput:
        # Extract image features and metadata
        return ProcessedInput(
            input_type="image",
            content=raw_input,
            metadata=self._extract_image_metadata(raw_input),
            timestamp=datetime.utcnow()
        )
    
    def validate(self, raw_input: bytes) -> bool:
        # Validate image format and size
        try:
            image = Image.open(io.BytesIO(raw_input))
            return (image.size[0] <= 2048 and image.size[1] <= 2048 
                   and len(raw_input) <= 10 * 1024 * 1024)
        except Exception:
            return False

class DocumentInputAdapter(InputAdapter):
    async def process(self, raw_input: str) -> ProcessedInput:
        # Extract document content and metadata
        return ProcessedInput(
            input_type="document",
            content=await self._extract_document_content(raw_input),
            metadata=self._extract_document_metadata(raw_input),
            timestamp=datetime.utcnow()
        )
    
    def validate(self, raw_input: str) -> bool:
        # Validate file path and type
        return (os.path.exists(raw_input) and 
                os.path.getsize(raw_input) <= 50 * 1024 * 1024 and
                raw_input.lower().endswith(('.pdf', '.docx', '.txt', '.md')))
```

**2. Feature Extraction Pipeline**
```python
# Core responsibility: Extract features from multimodal inputs
class FeatureExtractionPipeline:
    def __init__(self, text_processor: TextProcessor, 
                 image_processor: ImageProcessor,
                 document_processor: DocumentProcessor):
        self.processors = {
            'text': text_processor,
            'image': image_processor,
            'document': document_processor
        }
    
    async def extract_features(self, input_data: ProcessedInput) -> FeatureSet:
        processor = self.processors[input_data.input_type]
        features = await processor.extract(input_data)
        
        # Generate embeddings for similarity matching
        embedding = await self._generate_embedding(features)
        
        return FeatureSet(
            features=features,
            embedding=embedding,
            confidence_scores=self._calculate_confidence_scores(features),
            metadata=input_data.metadata
        )
```

**3. Context Fusion Engine**
```python
# Core responsibility: Combine multimodal features into unified context
class ContextFusionEngine:
    def __init__(self, qwen_engine: Qwen3OmniEngine):
        self.engine = qwen_engine
        self.fusion_cache = {}  # For deterministic results
    
    async def fuse_context(self, features: List[FeatureSet]) -> UnifiedContext:
        # Create cache key for deterministic fusion
        cache_key = self._generate_fusion_cache_key(features)
        if cache_key in self.fusion_cache:
            return self.fusion_cache[cache_key]
        
        # Use Qwen3-Omni for intelligent context fusion
        fused_context = await self.engine.fuse_multimodal_context(features)
        
        # Cache for reproducibility
        self.fusion_cache[cache_key] = fused_context
        return fused_context
```

## Risk Mitigation Architecture

### 1. Model Context Risk Mitigation

#### Problem: Model context inconsistency and drift
#### Solution: Deterministic Context Management

```python
class DeterministicContextManager:
    def __init__(self, cache_size: int = 1000):
        self.context_cache = {}
        self.cache_size = cache_size
        self.context_history = []
    
    def get_context_key(self, input_data: ProcessedInput) -> str:
        # Generate deterministic key based on input content
        content_hash = hashlib.sha256(str(input_data.content).encode()).hexdigest()
        return f"{input_data.input_type}_{content_hash}"
    
    async def get_or_create_context(self, input_data: ProcessedInput) -> UnifiedContext:
        cache_key = self.get_context_key(input_data)
        
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]
        
        # Create new context deterministically
        context = await self._create_deterministic_context(input_data)
        
        # Cache with size limit
        if len(self.context_cache) >= self.cache_size:
            self._evict_oldest_cache_entry()
        
        self.context_cache[cache_key] = context
        self.context_history.append({
            'key': cache_key,
            'context': context,
            'timestamp': datetime.utcnow()
        })
        
        return context
```

### 2. Tool I/O Schema Drift Mitigation

#### Problem: Tool input/output schemas changing over time
#### Solution: Strict Schema Validation and Versioning

```python
class SchemaDriftPrevention:
    def __init__(self):
        self.schema_registry = {}
        self.schema_versions = {}
        self.validation_log = []
    
    def register_schema(self, tool_name: str, schema: ToolSchema, version: str) -> None:
        # Register schema with version tracking
        if tool_name not in self.schema_registry:
            self.schema_registry[tool_name] = {}
            self.schema_versions[tool_name] = []
        
        self.schema_registry[tool_name][version] = schema
        self.schema_versions[tool_name].append(version)
    
    def validate_schema_compatibility(self, 
                                    tool_name: str, 
                                    input_data: dict, 
                                    expected_version: str) -> ValidationResult:
        # Check if input matches expected schema version
        if tool_name not in self.schema_registry:
            return ValidationResult(
                valid=False,
                error=f"Tool {tool_name} not found in schema registry"
            )
        
        if expected_version not in self.schema_registry[tool_name]:
            return ValidationResult(
                valid=False,
                error=f"Schema version {expected_version} not found for tool {tool_name}"
            )
        
        schema = self.schema_registry[tool_name][expected_version]
        
        try:
            # Strict validation with Pydantic
            validated_data = schema.input_schema.model_validate(input_data)
            return ValidationResult(valid=True, data=validated_data)
        except ValidationError as e:
            self.validation_log.append({
                'tool': tool_name,
                'version': expected_version,
                'error': str(e),
                'timestamp': datetime.utcnow()
            })
            return ValidationResult(valid=False, error=str(e))
    
    def detect_schema_drift(self, tool_name: str) -> List[DriftWarning]:
        # Analyze validation logs to detect schema drift patterns
        warnings = []
        recent_failures = [log for log in self.validation_log 
                          if log['tool'] == tool_name and 
                          log['timestamp'] > datetime.utcnow() - timedelta(hours=24)]
        
        if len(recent_failures) > 10:  # Threshold for drift detection
            warnings.append(DriftWarning(
                tool_name=tool_name,
                severity="high",
                message=f"High validation failure rate: {len(recent_failures)} failures in 24h",
                recommended_action="Review and update schema"
            ))
        
        return warnings
```

### 3. Acceptance Check Framework

#### Implementation: Automated Acceptance Testing

```python
class AcceptanceCheckFramework:
    def __init__(self, test_suite: TestSuite):
        self.test_suite = test_suite
        self.acceptance_criteria = {}
        self.check_history = []
    
    def define_acceptance_criteria(self, feature: str, criteria: List[AcceptanceCriterion]) -> None:
        self.acceptance_criteria[feature] = criteria
    
    async def run_acceptance_checks(self, feature: str, implementation: Any) -> AcceptanceResult:
        if feature not in self.acceptance_criteria:
            return AcceptanceResult(
                passed=False,
                error=f"No acceptance criteria defined for feature: {feature}"
            )
        
        criteria = self.acceptance_criteria[feature]
        results = []
        
        for criterion in criteria:
            try:
                result = await criterion.check(implementation)
                results.append(result)
            except Exception as e:
                results.append(AcceptanceCheckResult(
                    criterion=criterion.name,
                    passed=False,
                    error=str(e)
                ))
        
        all_passed = all(result.passed for result in results)
        
        acceptance_result = AcceptanceResult(
            passed=all_passed,
            feature=feature,
            checks=results,
            timestamp=datetime.utcnow()
        )
        
        self.check_history.append(acceptance_result)
        return acceptance_result
    
    def get_acceptance_report(self, feature: str = None) -> AcceptanceReport:
        if feature:
            history = [result for result in self.check_history if result.feature == feature]
        else:
            history = self.check_history
        
        return AcceptanceReport(
            total_checks=len(history),
            passed_checks=len([r for r in history if r.passed]),
            failed_checks=len([r for r in history if not r.passed]),
            success_rate=len([r for r in history if r.passed]) / len(history) if history else 0,
            last_check=history[-1] if history else None
        )
```

## Implementation Strategy

### Phase 1: Core Pipeline (Weeks 1-2)
1. **Input Ingestion Service**: Basic text/image/document input handling
2. **Pydantic Validation**: Strict schema validation for all inputs
3. **Processing Pipeline**: Multimodal processing with feature extraction
4. **Context Analysis**: Basic context understanding with Qwen3-Omni

### Phase 2: Tool Integration (Weeks 3-4)
1. **MCP Tool Registry**: Tool registration and discovery system
2. **Tool Execution Engine**: Sandboxed tool execution with validation
3. **Tool Integration**: Result integration into answer generation
4. **Schema Management**: Schema versioning and drift prevention

### Phase 3: Multimodal Enhancement (Weeks 5-6)
1. **Input Adapters**: Specialized adapters for each input type
2. **Feature Extraction**: Advanced feature extraction pipelines
3. **Context Fusion**: Intelligent multimodal context combination
4. **Acceptance Testing**: Comprehensive acceptance check framework

### Phase 4: Risk Mitigation (Weeks 7-8)
1. **Deterministic Context**: Context caching and reproducibility
2. **Schema Drift Detection**: Automated schema drift monitoring
3. **Acceptance Framework**: Full acceptance testing implementation
4. **Performance Optimization**: Apple Silicon optimization

## Success Metrics

### Functional Metrics
- [ ] 100% input validation success rate
- [ ] 95% tool execution success rate
- [ ] 90% multimodal context fusion accuracy
- [ ] < 5 second end-to-end processing time

### Quality Metrics
- [ ] 100% deterministic context generation
- [ ] 0% schema drift incidents
- [ ] 100% acceptance criteria compliance
- [ ] > 90% test coverage

### Performance Metrics
- [ ] < 1 second input processing
- [ ] < 100ms tool execution per tool
- [ ] < 3 second answer generation
- [ ] < 4GB memory usage

---

**Document Version:** 1.0  
**Last Updated:** 2024-09-24  
**Next Review:** 2024-10-01  
**Architecture Lead:** [To be assigned]  
**Technical Review:** [Pending]
