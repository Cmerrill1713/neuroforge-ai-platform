# Qwen3-Omni-30B-A3B-Instruct Experimentation Framework

This directory contains a comprehensive experimentation framework for the Qwen3-Omni-30B-A3B-Instruct model, including testing scripts, configuration files, and utilities.

## 📁 Files Overview

### Core Scripts
- **`quick_qwen_test.py`** - Simple verification script to test if the model loads and generates text
- **`qwen_experiments.py`** - Comprehensive experimentation suite with benchmarking and multimodal testing
- **`interactive_qwen.py`** - Interactive chat interface for testing the model with custom prompts

### Configuration Files
- **`qwen_config.yaml`** - Configuration file for various experimentation scenarios
- **`requirements_qwen.txt`** - Python dependencies for the experimentation framework

### Model Directory
- **`Qwen3-Omni-30B-A3B-Instruct/`** - The downloaded model files (~60GB)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_qwen.txt
```

### 2. Quick Model Test
```bash
python quick_qwen_test.py
```
This will verify the model loads correctly and run basic text generation tests.

### 3. Interactive Testing
```bash
python interactive_qwen.py
```
Start an interactive session where you can chat with the model and adjust generation parameters.

### 4. Comprehensive Experiments
```bash
python qwen_experiments.py --test comprehensive
```
Run the full test suite including performance benchmarks and multimodal testing.

## 🛠️ Usage Examples

### Basic Text Generation
```bash
python qwen_experiments.py --test basic --prompt "Explain quantum computing"
```

### Multimodal Testing
```bash
python qwen_experiments.py --test multimodal --prompt "Describe this image" --image samples/board.png
```

### Performance Benchmarking
```bash
python qwen_experiments.py --test benchmark
```

### Custom Configuration
```bash
python qwen_experiments.py --device cuda --quantization 4bit --max_memory 16
```

## ⚙️ Configuration Options

### Model Loading Options
- `--device`: Device to run on (auto, cpu, cuda, mps)
- `--quantization`: Quantization method (none, 4bit, 8bit)
- `--max_memory`: Maximum memory usage in GB

### Test Types
- `basic`: Simple text generation test
- `multimodal`: Test image, audio, video processing
- `benchmark`: Performance benchmarking
- `comprehensive`: Full test suite

## 📊 Experimentation Features

### Text Generation Testing
- Multiple prompt types (creative, technical, reasoning)
- Different generation parameters (temperature, top_p, etc.)
- Performance metrics (tokens/second, memory usage)
- Response quality analysis

### Multimodal Capabilities
- Image description and analysis
- Audio processing (when available)
- Video understanding (when available)
- Cross-modal reasoning

### Performance Monitoring
- Memory usage tracking
- Inference time measurement
- GPU utilization monitoring
- System resource monitoring

### Benchmarking
- Multiple iterations for statistical significance
- Different prompt categories
- Various generation configurations
- Performance comparison across settings

## 🎯 Test Scenarios

The framework includes several predefined test scenarios:

### Basic Text Generation
- Simple questions and answers
- Technical explanations
- Creative writing prompts

### Creative Writing
- Short stories
- Poetry
- Dialogue generation
- Descriptive writing

### Technical Analysis
- Programming concepts
- System architecture
- Security considerations
- Algorithm explanations

### Reasoning Tasks
- Mathematical problems
- Logical puzzles
- System design challenges
- Ethical considerations

## 📈 Performance Optimization

### Memory Optimization
- Quantization (4-bit, 8-bit)
- Gradient checkpointing
- Model sharding
- CPU offloading

### Speed Optimization
- Flash Attention (if available)
- XFormers integration
- Batch processing
- Optimized generation parameters

## 🔍 Monitoring and Logging

### Metrics Tracked
- Inference time per token
- Memory usage (RAM and GPU)
- Token generation rate
- Model loading time
- Error rates and types

### Log Files
- `qwen_experiments.log` - Detailed experiment logs
- `qwen_test_results_*.json` - Structured test results
- Performance metrics in JSON format

## 🛡️ Safety and Ethics

### Content Filtering
- Toxicity detection
- Bias analysis
- Content safety checks
- Ethical considerations

### Responsible AI Testing
- Fact-checking capabilities
- Hallucination detection
- Bias identification
- Fairness assessment

## 🔧 Troubleshooting

### Common Issues

#### Out of Memory Errors
```bash
# Try quantization
python qwen_experiments.py --quantization 4bit

# Limit memory usage
python qwen_experiments.py --max_memory 16

# Use CPU instead
python qwen_experiments.py --device cpu
```

#### Model Loading Issues
- Ensure model files are complete (check file sizes)
- Verify sufficient disk space
- Check Python environment and dependencies

#### CUDA Issues
- Verify CUDA installation
- Check GPU memory availability
- Try different device mapping

### Performance Tips
- Use quantization for memory-constrained systems
- Adjust generation parameters for speed vs. quality
- Monitor system resources during experiments
- Use appropriate batch sizes

## 📚 Advanced Usage

### Custom Test Scenarios
Modify `qwen_config.yaml` to add custom test scenarios:

```yaml
custom_tests:
  my_test:
    enabled: true
    prompts:
      - "Your custom prompt here"
      - "Another test prompt"
```

### Integration with Other Tools
- Weights & Biases logging
- TensorBoard integration
- Custom metrics collection
- API endpoint creation

## 🤝 Contributing

To add new test scenarios or improve the framework:

1. Add new test methods to `QwenExperimentSuite`
2. Update configuration files
3. Add documentation
4. Test thoroughly

## 📄 License

This experimentation framework is provided as-is for research and development purposes. Please refer to the original Qwen model license for usage terms.

## 🆘 Support

For issues with the experimentation framework:
1. Check the logs in `qwen_experiments.log`
2. Verify system requirements
3. Test with the quick verification script
4. Check model file integrity

For issues with the Qwen model itself, refer to the official Qwen documentation and community forums.
