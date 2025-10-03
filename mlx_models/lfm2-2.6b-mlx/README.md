---
library_name: mlx
license: other
license_name: lfm1.0
license_link: LICENSE
language:
- en
- ar
- zh
- fr
- de
- ja
- ko
- es
pipeline_tag: text-generation
tags:
- liquid
- lfm2
- edge
- mlx
base_model: LiquidAI/LFM2-2.6B
---

# LFM2-2.6B-bf16-mlx

This model [LFM2-2.6B-bf16-mlx](https://huggingface.co/LFM2-2.6B-bf16-mlx) was
converted to MLX format from [LiquidAI/LFM2-2.6B](https://huggingface.co/LiquidAI/LFM2-2.6B)
using mlx-lm version **0.28.0**.

## Use with mlx

```bash
pip install mlx-lm
```

```python
from mlx_lm import load, generate

model, tokenizer = load("LFM2-2.6B-bf16-mlx")

prompt = "hello"

if tokenizer.chat_template is not None:
    messages = [{"role": "user", "content": prompt}]
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True
    )

response = generate(model, tokenizer, prompt=prompt, verbose=True)
```
