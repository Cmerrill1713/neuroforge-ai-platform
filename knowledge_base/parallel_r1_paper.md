# Parallel-R1: Towards Parallel Thinking via Reinforcement Learning

**Source**: https://arxiv.org/pdf/2509.07980  
**Authors**: Tong Zheng, Hongming Zhang, Wenhao Yu, Xiaoyang Wang, Runpeng Dai, Rui Liu, Huiwen Bao, Chengsong Huang, Heng Huang, Dong Yu  
**Institutions**: Tencent AI Lab Seattle, University of Maryland, University of North Carolina at Chapel Hill, City University of Hong Kong, Washington University in St. Louis  
**GitHub**: https://github.com/zhengkid/Parallel-R1

## Abstract

Parallel thinking has emerged as a novel approach for enhancing the reasoning capabilities of large language models (LLMs) by exploring multiple reasoning paths concurrently. However, activating such capabilities through training remains challenging, as existing methods predominantly rely on supervised fine-tuning (SFT) over synthetic data, which encourages teacher-forced imitation rather than exploration and generalization.

Different from them, we propose Parallel-R1, the first reinforcement learning (RL) framework that enables parallel thinking behaviors for complex real-world reasoning tasks. Our framework employs a progressive curriculum that explicitly addresses the cold-start problem in training parallel thinking with RL. We first use SFT on prompt-generated trajectories from easier tasks to instill the parallel thinking ability, then transition to RL to explore and generalize this skill on harder problems.

Experiments on various math benchmarks, including MATH, AMC23, and AIME, show that Parallel-R1 successfully instills parallel thinking, leading to 8.4% accuracy improvements over the sequential thinking model trained directly on challenging tasks with RL. Further analysis reveals a clear shift in the model's thinking behavior: at an early stage, it uses parallel thinking as an exploration strategy, while in a later stage, it uses the same capability for multi-perspective verification. Most significantly, we validate parallel thinking as a mid-training exploration scaffold, where this temporary exploratory phase unlocks a higher performance ceiling after RL, yielding a 42.9% improvement over the baseline on AIME25.

## Key Concepts

### Parallel Thinking
Parallel thinking involves jointly conducting both parallel and sequential thinking. During inference, the model generates in a standard auto-regressive fashion until it emits a special <Parallel> tag. At that point, it spawns multiple threads to explore different solution paths or perspectives, then summarizes their outputs. These contents are merged back into the main context, and generation continues.

### Progressive Curriculum
The approach first equips the model with parallel thinking ability on easy math problems and then progressively extends it to more general and difficult problems through reinforcement learning.

### Format Structure
```
<Parallel>
<Path>First reasoning path...</Path>
<Path>Second reasoning path...</Path>
</Parallel>
<Summary>Insights from all paths...</Summary>
```

## Technical Details

### Training Process
1. **SFT Phase**: Supervised fine-tuning on simpler problems using Parallel-GSM8K dataset
2. **RL Phase**: Reinforcement learning on more difficult tasks to explore and generalize
3. **Cold-start Solution**: High-quality parallel thinking data generated via simple prompting for easier tasks

### Performance Results
- **8.4% accuracy improvement** over sequential thinking models on challenging RL tasks
- **42.9% improvement** over baseline on AIME25 through mid-training exploration scaffold
- Tested on MATH, AMC23, and AIME mathematical benchmarks

### Behavioral Evolution
- **Early Stage**: Uses parallel thinking as exploration strategy
- **Late Stage**: Uses parallel thinking for multi-perspective verification
- **Scaffold Effect**: Temporary exploratory phase unlocks higher performance ceiling

## Challenges Addressed

1. **Cold-start Problem**: Current LLMs haven't seen parallel thinking behavior during pre-training and SFT
2. **Reward Function Design**: Balancing final correctness with thinking strategy quality
3. **Generalization**: Moving beyond pattern matching to intrinsic reasoning skills
4. **Data Quality**: High-quality parallel thinking data for complex problems is rare and difficult to synthesize

## Implementation Notes

The framework employs a progressive curriculum that explicitly addresses the cold-start problem in training parallel thinking with RL. It begins with supervised fine-tuning on simpler problems, for which high-quality parallel thinking data can be generated easily via simple prompting. This initial stage effectively teaches the model the basic format of parallel thinking before transitioning to reinforcement learning on more difficult tasks.

## Research Impact

This work demonstrates that parallel thinking can be effectively instilled in LLMs through reinforcement learning, providing a scalable approach that goes beyond test-time strategies. The progressive curriculum approach successfully addresses the cold-start problem, and the behavioral analysis reveals important insights about how models learn and utilize parallel thinking capabilities.

## Open Source

The authors plan to open-source their model, data, and code at https://github.com/zhengkid/Parallel-R1, making this research accessible for further development and application.
