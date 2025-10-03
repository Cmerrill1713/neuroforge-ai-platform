# 🤝 Contributing to Agentic LLM Core v0.1

**Guidelines for contributing to the production-ready multimodal AI system.**

---

## 🎯 **Development Philosophy**

The Agentic LLM Core follows a **validation-first, production-ready** development approach:

- **Functional Experiments**: All changes must pass comprehensive functional testing
- **Acceptance Criteria**: Features must meet defined acceptance criteria before merging
- **Performance Validation**: Changes must maintain or improve performance metrics
- **Documentation**: All features must be documented and tested

---

## 🚀 **Quick Start for Contributors**

### Prerequisites
- Python 3.9+
- Git
- Docker (optional, for full testing)

### Setup
```bash
# Fork and clone
git clone https://github.com/your-username/prompt-engineering.git
cd prompt-engineering

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run functional validation (ensure system works)
python3 functional_experiment_suite.py

# Start development server
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔄 **Development Workflow**

### 1. **Choose or Create an Issue**
- Check existing issues for features/bugs to work on
- Create new issues for bugs or feature requests
- All work must have an associated issue

### 2. **Development Process**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes following the architecture
# Run functional experiments to validate
python3 functional_experiment_suite.py

# Run acceptance tests
python3 src/core/testing/acceptance_testing_framework.py

# Test your specific changes
python3 -m pytest tests/ -v

# Update documentation if needed
# Commit with clear messages
```

### 3. **Code Quality Standards**
- **Type Hints**: Use Pydantic models and type annotations
- **Docstrings**: Comprehensive docstrings for all public functions
- **Error Handling**: Proper exception handling and logging
- **Performance**: Consider caching and optimization implications
- **Testing**: Unit tests for new functionality

### 4. **Testing Requirements**
- **Functional Experiments**: Must pass all 6 phases
- **Acceptance Testing**: Must meet all 5 criteria
- **Unit Tests**: New code must have corresponding tests
- **Performance**: Must not degrade existing performance metrics

### 5. **Documentation Updates**
- Update `README.md` for user-facing changes
- Update `docs/PROJECT_README.md` for technical details
- Update `docs/AGENTIC_LLM_CORE_STATUS.md` for system status
- Add API documentation for new endpoints

---

## 🧪 **Testing & Validation**

### **Functional Testing**
```bash
# Comprehensive system validation
python3 functional_experiment_suite.py

# Results should show: 6/6 phases completed, 100% success
```

### **Acceptance Testing**
```bash
# Component-level validation
python3 src/core/testing/acceptance_testing_framework.py

# Results should show: 5/5 criteria passed, 100% success rate
```

### **Unit Testing**
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_specific_module.py -v
```

### **Performance Validation**
- Response times: <50ms for cached operations
- Cache hit rate: >95%
- System health: All monitoring active
- Memory usage: Within acceptable limits

---

## 📋 **Architecture Guidelines**

### **Core Module Structure**
```
src/core/
├── processors/          # Feature extraction (OCR, visual analysis)
├── cache/              # Multi-level caching (Redis + Memory)
├── validation/         # Schema validation and evolution
├── monitoring/         # Real-time monitoring and drift detection
└── testing/            # Acceptance testing framework
```

### **Key Principles**
- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Use factory functions for component creation
- **Async/Await**: All I/O operations are asynchronous
- **Error Resilience**: Graceful degradation and comprehensive error handling
- **Performance First**: Caching and optimization built-in

### **Pydantic Models**
- Use Pydantic v2 for all data models
- Include comprehensive validation
- Add meaningful descriptions and examples
- Use Field() for additional constraints

### **Logging Standards**
```python
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Warning conditions")
logger.error("Error conditions")
logger.critical("Critical failures")
```

---

## 🔧 **Common Contribution Patterns**

### **Adding a New Processor**
1. Create module in `src/core/processors/`
2. Implement factory function: `create_your_processor()`
3. Add to functional experiment validation
4. Update documentation

### **Adding API Endpoints**
1. Add route in `src/api/`
2. Update schema validation if needed
3. Add WebSocket support if real-time
4. Update API documentation

### **Performance Improvements**
1. Measure current performance
2. Implement optimization with caching
3. Validate with functional experiments
4. Update performance metrics documentation

### **Schema Changes**
1. Update Pydantic models in `src/core/schemas/`
2. Check compatibility with existing data
3. Update validation framework
4. Test with acceptance framework

---

## 🚢 **Deployment & Production**

### **Local Development**
```bash
# Development server
python3 -m uvicorn src.api.main:app --reload

# With specific host/port
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Docker Development**
```bash
# Start development stack
docker-compose up -d

# View logs
docker-compose logs -f

# Stop stack
docker-compose down
```

### **Production Deployment**
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Or use deployment script
./deploy.production.sh
```

---

## 📊 **Monitoring & Debugging**

### **Health Checks**
```bash
# System health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status

# Monitoring dashboard
curl http://localhost:8000/api/v1/monitor
```

### **WebSocket Monitoring**
```javascript
// Connect to real-time monitoring
const ws = new WebSocket('ws://localhost:8000/ws/monitor');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('System update:', data);
};
```

### **Debug Logging**
```bash
# View application logs
docker-compose logs -f app

# View all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f redis
```

---

## 🔒 **Security Guidelines**

### **Code Security**
- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all inputs thoroughly
- Implement proper error handling

### **API Security**
- Input validation on all endpoints
- Rate limiting where appropriate
- Proper error messages (no sensitive data)
- CORS configuration for web clients

### **Data Protection**
- No sensitive data in logs
- Proper data sanitization
- Secure defaults for all configurations
- Regular dependency updates

---

## 📝 **Commit Guidelines**

### **Commit Message Format**
```
type(scope): description

[optional body]

[optional footer]
```

### **Types**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

### **Examples**
```
feat(processors): add OCR capability to feature extractor
fix(validation): resolve ValidationError in schema validation
docs(readme): update API endpoint documentation
test(acceptance): add new acceptance criteria for caching
```

---

## 🆘 **Getting Help**

### **Resources**
- **README.md**: Main project documentation
- **docs/PROJECT_README.md**: Technical system guide
- **docs/AGENTIC_LLM_CORE_STATUS.md**: Current system status
- **Functional Experiments**: `python3 functional_experiment_suite.py`

### **Issue Reporting**
- Use GitHub issues for bugs and features
- Include functional experiment results
- Provide clear reproduction steps
- Tag appropriately (bug, enhancement, question)

### **Code Review Process**
- All PRs require functional experiment validation
- Acceptance testing must pass
- Performance must not degrade
- Documentation must be updated

---

## 🎉 **Recognition**

Contributors are recognized in:
- GitHub contributor statistics
- CHANGELOG.md for significant features
- Release notes for major versions

**Thank you for contributing to the Agentic LLM Core! Your work helps advance multimodal AI capabilities.** 🚀
