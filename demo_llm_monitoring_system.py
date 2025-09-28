#!/usr/bin/env python3
"""
LLM Monitoring System Demonstration
Shows how the grading system monitors LLMs and determines when fine-tuning is needed
"""

import sys
import time
import json
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from core.monitoring.llm_monitoring_system import (
    LLMMonitoringSystem, 
    LLMPerformanceMetrics,
    MonitoringLevel
)
from core.monitoring.auto_finetuning_system import AutoFineTuningSystem
from core.training.sakana_ai_methods import SakanaAIIntegration
from core.training.finetuning_grading_system import FinetuningGradingSystem

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simulate_model_degradation():
    """Simulate a model's performance degrading over time"""
    logger.info("🎭 Starting LLM Monitoring System Demonstration")
    logger.info("=" * 60)
    
    # Initialize monitoring system
    monitor = LLMMonitoringSystem()
    sakana_ai = SakanaAIIntegration()
    grading_system = FinetuningGradingSystem()
    auto_system = AutoFineTuningSystem(monitor, sakana_ai, grading_system)
    
    model_id = "demo-model-gpt4"
    model_path = "microsoft/DialoGPT-small"
    
    logger.info(f"📊 Monitoring Model: {model_id}")
    logger.info(f"🔧 Model Path: {model_path}")
    logger.info("")
    
    # Phase 1: Excellent Performance
    logger.info("🌟 PHASE 1: EXCELLENT PERFORMANCE")
    logger.info("-" * 40)
    
    for i in range(15):
        excellent_metrics = LLMPerformanceMetrics(
            response_relevance=0.95,
            response_accuracy=0.92,
            response_completeness=0.94,
            response_coherence=0.93,
            response_time=1.2,
            token_generation_rate=150.0,
            memory_usage=1.5,
            cpu_usage=25.0,
            code_quality=0.96,
            reasoning_accuracy=0.94,
            factual_accuracy=0.93,
            creative_quality=0.91,
            user_rating=4.8,
            correction_frequency=0.05,
            clarification_requests=0.02,
            unknown_queries=0.01,
            outdated_information=0.03
        )
        
        monitor.record_metrics(model_id, excellent_metrics)
        
        if i % 5 == 0:
            logger.info(f"   📈 Recorded excellent metrics batch {i//5 + 1}")
            time.sleep(0.1)
    
    # Analyze performance
    recommendation = monitor.analyze_performance(model_id)
    if recommendation:
        logger.info(f"   ⚠️  Recommendation: {recommendation.recommendation_level}")
    else:
        logger.info("   ✅ No issues detected - performance excellent")
    
    health_summary = monitor.get_model_health_summary(model_id)
    logger.info(f"   📊 Health Score: {health_summary['health_score']:.2f}")
    logger.info(f"   🎯 Fine-tuning Needed: {health_summary['fine_tuning_needed']}")
    logger.info("")
    
    # Phase 2: Gradual Degradation
    logger.info("📉 PHASE 2: GRADUAL DEGRADATION")
    logger.info("-" * 40)
    
    for i in range(20):
        # Gradual degradation
        degradation_factor = 1.0 - (i * 0.02)  # 2% degradation per batch
        
        degrading_metrics = LLMPerformanceMetrics(
            response_relevance=0.95 * degradation_factor,
            response_accuracy=0.92 * degradation_factor,
            response_completeness=0.94 * degradation_factor,
            response_coherence=0.93 * degradation_factor,
            response_time=1.2 + (i * 0.1),  # Getting slower
            token_generation_rate=150.0 * degradation_factor,
            memory_usage=1.5 + (i * 0.05),  # More memory usage
            cpu_usage=25.0 + (i * 1.0),     # More CPU usage
            code_quality=0.96 * degradation_factor,
            reasoning_accuracy=0.94 * degradation_factor,
            factual_accuracy=0.93 * degradation_factor,
            creative_quality=0.91 * degradation_factor,
            user_rating=4.8 - (i * 0.1),    # Lower ratings
            correction_frequency=0.05 + (i * 0.01),  # More corrections
            clarification_requests=0.02 + (i * 0.005),
            unknown_queries=0.01 + (i * 0.002),
            outdated_information=0.03 + (i * 0.005)
        )
        
        monitor.record_metrics(model_id, degrading_metrics)
        
        if i % 5 == 0:
            logger.info(f"   📉 Recorded degrading metrics batch {i//5 + 1} (degradation: {i*2}%)")
            
            # Check for recommendations
            recommendation = monitor.analyze_performance(model_id)
            if recommendation:
                logger.info(f"      ⚠️  Status: {recommendation.recommendation_level}")
                logger.info(f"      🎯 Confidence: {recommendation.confidence_score:.2f}")
                logger.info(f"      🚨 Urgency: {recommendation.urgency_score:.2f}")
                logger.info(f"      📈 Estimated Improvement: {recommendation.estimated_improvement:.2f}")
            
            time.sleep(0.2)
    
    # Phase 3: Critical Performance Issues
    logger.info("🚨 PHASE 3: CRITICAL PERFORMANCE ISSUES")
    logger.info("-" * 40)
    
    for i in range(15):
        critical_metrics = LLMPerformanceMetrics(
            response_relevance=0.35,  # Very poor
            response_accuracy=0.28,   # Very poor
            response_completeness=0.45,
            response_coherence=0.38,  # Poor
            response_time=8.5,        # Very slow
            token_generation_rate=45.0,  # Very slow
            memory_usage=3.2,         # High memory
            cpu_usage=85.0,           # High CPU
            code_quality=0.25,        # Very poor code
            reasoning_accuracy=0.22,  # Very poor reasoning
            factual_accuracy=0.31,    # Poor accuracy
            creative_quality=0.28,    # Poor creativity
            user_rating=2.1,          # Low rating
            correction_frequency=0.75, # Many corrections needed
            clarification_requests=0.35,
            unknown_queries=0.25,
            outdated_information=0.18,
            domain_weaknesses=["code_generation", "mathematical_reasoning", "creative_writing"]
        )
        
        monitor.record_metrics(model_id, critical_metrics)
        
        if i % 3 == 0:
            logger.info(f"   🚨 Recorded critical metrics batch {i//3 + 1}")
            
            # Check for recommendations
            recommendation = monitor.analyze_performance(model_id)
            if recommendation:
                logger.info(f"      🚨 Status: {recommendation.recommendation_level}")
                logger.info(f"      🎯 Confidence: {recommendation.confidence_score:.2f}")
                logger.info(f"      ⚡ Urgency: {recommendation.urgency_score:.2f}")
                logger.info(f"      📈 Estimated Improvement: {recommendation.estimated_improvement:.2f}")
                logger.info(f"      🔍 Primary Issues: {', '.join(recommendation.primary_issues[:3])}")
                logger.info(f"      🛠️  Suggested Skills: {', '.join(recommendation.suggested_skills[:3])}")
            
            time.sleep(0.3)
    
    # Final Analysis
    logger.info("📊 FINAL ANALYSIS")
    logger.info("=" * 60)
    
    health_summary = monitor.get_model_health_summary(model_id)
    logger.info(f"Model ID: {health_summary['model_id']}")
    logger.info(f"Status: {health_summary['status']}")
    logger.info(f"Health Score: {health_summary['health_score']:.2f}")
    logger.info(f"Metrics Count: {health_summary['metrics_count']}")
    logger.info(f"Fine-tuning Needed: {health_summary['fine_tuning_needed']}")
    
    if health_summary['latest_recommendation']:
        rec = health_summary['latest_recommendation']
        logger.info("")
        logger.info("🎯 LATEST FINE-TUNING RECOMMENDATION:")
        logger.info(f"   Level: {rec['recommendation_level']}")
        logger.info(f"   Confidence: {rec['confidence_score']:.2f}")
        logger.info(f"   Urgency: {rec['urgency_score']:.2f}")
        logger.info(f"   Estimated Improvement: {rec['estimated_improvement']:.2f}")
        logger.info("")
        logger.info("🔍 PRIMARY ISSUES:")
        for issue in rec['primary_issues']:
            logger.info(f"   • {issue}")
        logger.info("")
        logger.info("🛠️  SUGGESTED SKILLS:")
        for skill in rec['suggested_skills']:
            logger.info(f"   • {skill}")
    
    # Auto Fine-tuning Trigger
    logger.info("")
    logger.info("🤖 AUTO FINE-TUNING SYSTEM")
    logger.info("-" * 40)
    
    # Process recommendations
    results = auto_system.process_monitoring_recommendations(model_id, model_path)
    
    if results:
        result = results[0]
        logger.info(f"🎯 Auto Fine-tuning Result:")
        logger.info(f"   Success: {result['success']}")
        logger.info(f"   Method: {result['method_used']}")
        logger.info(f"   Duration: {result['duration']:.2f}s")
        
        if result['success']:
            logger.info(f"   Grade: {result['grading']['overall_grade']}")
            logger.info(f"   Overall Score: {result['grading']['overall_score']:.2f}")
            logger.info("")
            logger.info("📈 EXPECTED IMPROVEMENTS:")
            improvements = result['improvement_metrics']
            for metric, improvement in improvements.items():
                if metric != 'skill_coverage':
                    logger.info(f"   • {metric}: {improvement:+.1%}")
                else:
                    logger.info(f"   • {metric}: {improvement:.1%}")
        else:
            logger.info(f"   Error: {result['error']}")
    else:
        logger.info("   No auto fine-tuning triggered (criteria not met)")
    
    # Export reports
    logger.info("")
    logger.info("📄 EXPORTING REPORTS")
    logger.info("-" * 40)
    
    # Export monitoring report
    monitoring_report_path = "llm_monitoring_report.json"
    monitor.export_monitoring_report(model_id, monitoring_report_path)
    logger.info(f"📊 Monitoring report exported to: {monitoring_report_path}")
    
    # Export auto fine-tuning report
    auto_report_path = "auto_finetuning_report.json"
    auto_system.export_auto_finetuning_report(model_id, auto_report_path)
    logger.info(f"🤖 Auto fine-tuning report exported to: {auto_report_path}")
    
    # Summary
    logger.info("")
    logger.info("🎯 DEMONSTRATION SUMMARY")
    logger.info("=" * 60)
    logger.info("✅ Successfully demonstrated:")
    logger.info("   • Real-time LLM performance monitoring")
    logger.info("   • Automatic performance degradation detection")
    logger.info("   • Intelligent fine-tuning recommendations")
    logger.info("   • Auto fine-tuning system integration")
    logger.info("   • Comprehensive grading and reporting")
    logger.info("")
    logger.info("🔧 Key Features Shown:")
    logger.info("   • Continuous metrics collection")
    logger.info("   • Multi-level alert system (HEALTHY → WARNING → CRITICAL)")
    logger.info("   • Confidence and urgency scoring")
    logger.info("   • Skill-specific improvement suggestions")
    logger.info("   • Sakana AI integration for instant fine-tuning")
    logger.info("   • Comprehensive grading system (A+ to F)")
    logger.info("")
    logger.info("📈 This system ensures your LLMs maintain optimal performance")
    logger.info("   by automatically detecting issues and triggering fine-tuning")
    logger.info("   when needed, using our revolutionary Sakana AI methods!")

def demonstrate_grading_criteria():
    """Demonstrate the grading criteria and thresholds"""
    logger.info("")
    logger.info("📚 GRADING SYSTEM CRITERIA")
    logger.info("=" * 60)
    
    logger.info("🎯 MONITORING LEVELS:")
    logger.info("   • EXCELLENT: All metrics above 0.9, no issues")
    logger.info("   • HEALTHY: All metrics above 0.8, minor issues")
    logger.info("   • ATTENTION: Some metrics below 0.7, monitor closely")
    logger.info("   • WARNING: Multiple metrics below 0.6, action needed")
    logger.info("   • CRITICAL: Critical metrics below 0.4, immediate action")
    logger.info("")
    
    logger.info("📊 KEY THRESHOLDS:")
    logger.info("   • Response Relevance: < 0.3 (Critical), < 0.5 (Warning)")
    logger.info("   • Response Accuracy: < 0.4 (Critical), < 0.6 (Warning)")
    logger.info("   • Response Time: > 10s (Critical), > 5s (Warning)")
    logger.info("   • User Rating: < 2.0 (Critical), < 3.0 (Warning)")
    logger.info("   • Correction Frequency: > 0.5 (Critical), > 0.3 (Warning)")
    logger.info("")
    
    logger.info("🤖 AUTO FINE-TUNING TRIGGERS:")
    logger.info("   • Confidence Score: ≥ 0.7")
    logger.info("   • Urgency Score: ≥ 0.5")
    logger.info("   • Recommendation Level: WARNING or CRITICAL")
    logger.info("   • Cooldown Period: 1 hour between attempts")
    logger.info("")
    
    logger.info("🎓 GRADING SCALE (A+ to F):")
    logger.info("   • A+ (90-100): Excellent performance, optimal metrics")
    logger.info("   • A (85-89): Very good performance, minor optimizations")
    logger.info("   • B+ (80-84): Good performance, some improvements needed")
    logger.info("   • B (75-79): Satisfactory, moderate improvements needed")
    logger.info("   • C (70-74): Needs improvement, significant work required")
    logger.info("   • D (60-69): Poor performance, major improvements needed")
    logger.info("   • F (<60): Failed, complete retraining required")

if __name__ == "__main__":
    try:
        simulate_model_degradation()
        demonstrate_grading_criteria()
        
        logger.info("")
        logger.info("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        logger.info("The LLM Monitoring System is now fully operational")
        logger.info("and ready to monitor your models in production!")
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
