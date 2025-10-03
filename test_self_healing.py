#!/usr/bin/env python3
"""
Test Self-Healing System
Tests the intelligent error detection and automatic fixing capabilities
"""

import requests
import json
import time

def test_self_healing_system():
    """Test the self-healing system capabilities"""
    
    base_url = "http://localhost:8004"
    
    print("🔧 Testing Intelligent Self-Healing System")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Self-Healing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/healing/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Self-Healing System: {health['status']}")
            print(f"   - Operational: {health['healing_system_operational']}")
            print(f"   - Known Error Patterns: {health['known_error_patterns']}")
            print(f"   - Total Attempts: {health['total_healing_attempts']}")
            print(f"   - Success Rate: {health['success_rate']:.1%}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Error Analysis
    print("\n2. Testing Error Analysis...")
    test_errors = [
        "Incompatible dimension for X and Y matrices: X.shape[1] == 384 while Y.shape[1] == 768",
        "'AdvancedRAGSystem' object has no attribute 'get_database_stats'",
        "cannot import name 'SimpleKnowledgeBase' from 'src.core.knowledge.simple_knowledge_base'",
        "No module named 'missing_module'",
        "Port 8004 is already in use",
        "Connection refused to localhost:8086"
    ]
    
    for i, error_msg in enumerate(test_errors[:3]):  # Test first 3
        try:
            response = requests.post(
                f"{base_url}/api/healing/analyze-and-heal",
                json={
                    "error_message": error_msg,
                    "context": {"test": True},
                    "auto_heal": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("error_analysis", {})
                healing = result.get("healing_result", {})
                
                error_type = analysis.get("error_type", "unknown")
                can_fix = analysis.get("can_fix", False)
                success = healing.get("success", False)
                
                status = "✅" if success else "⚠️" if can_fix else "❌"
                print(f"   {status} Error {i+1}: {error_type}")
                print(f"      Message: {error_msg[:50]}...")
                print(f"      Can Fix: {can_fix}")
                print(f"      Healed: {success}")
                if healing.get("details"):
                    print(f"      Details: {healing['details'][:80]}...")
            else:
                print(f"   ❌ Error {i+1}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error {i+1}: {e}")
    
    # Test 3: Healing Statistics
    print("\n3. Testing Healing Statistics...")
    try:
        response = requests.get(f"{base_url}/api/healing/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Healing Statistics:")
            print(f"   - Total Attempts: {stats['total_healing_attempts']}")
            print(f"   - Successful Heals: {stats['successful_heals']}")
            print(f"   - Failed Heals: {stats['failed_heals']}")
            print(f"   - Success Rate: {stats['success_rate']:.1%}")
            print(f"   - Known Error Types: {len(stats['known_error_types'])}")
            print(f"   - Successful Fixes: {', '.join(stats['successful_fixes'])}")
            
            if stats['recent_heals']:
                print(f"   - Recent Heals: {len(stats['recent_heals'])}")
                for heal in stats['recent_heals'][-2:]:  # Show last 2
                    print(f"     • {heal['error_type']}: {'✅' if heal['success'] else '❌'}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    # Test 4: Emergency Healing
    print("\n4. Testing Emergency Healing...")
    try:
        response = requests.post(f"{base_url}/api/healing/emergency-heal")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Emergency Healing:")
            print(f"   - Total Attempts: {result['total_attempts']}")
            print(f"   - Successful Fixes: {result['successful_fixes']}")
            print(f"   - Success Rate: {result['success_rate']:.1%}")
            
            print(f"   - Results:")
            for i, res in enumerate(result['results']):
                status = "✅" if res['success'] else "❌"
                print(f"     {i+1}. {status} {res['error_type']}")
                if res.get('details'):
                    print(f"        {res['details'][:60]}...")
        else:
            print(f"❌ Emergency healing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Emergency healing error: {e}")
    
    # Test 5: Comprehensive Health Check
    print("\n5. Testing Comprehensive Health Check...")
    try:
        response = requests.post(
            f"{base_url}/api/healing/health-check",
            json={
                "check_services": True,
                "check_errors": True,
                "auto_heal": False  # Don't auto-heal in test
            }
        )
        
        if response.status_code == 200:
            health_report = response.json()
            print(f"✅ Health Report:")
            print(f"   - Overall Status: {health_report['overall_status']}")
            print(f"   - Services Checked: {len(health_report['services'])}")
            print(f"   - Errors Detected: {len(health_report['errors_detected'])}")
            
            # Show service status
            for service, status in health_report['services'].items():
                status_icon = "✅" if status.get("status") == "healthy" else "⚠️" if status.get("status") == "unhealthy" else "❌"
                print(f"     {status_icon} {service}: {status.get('status', 'unknown')}")
            
            # Show detected errors
            if health_report['errors_detected']:
                print(f"   - Detected Error Patterns:")
                for error in health_report['errors_detected'][:3]:  # Show first 3
                    print(f"     • {error['pattern']} (severity: {error['severity']})")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print("\n" + "=" * 60)
    print("🔧 Self-Healing System Testing Complete")

def test_self_healing_effectiveness():
    """Test how effective the self-healing system is"""
    
    base_url = "http://localhost:8004"
    
    print("\n📊 Testing Self-Healing Effectiveness")
    print("=" * 60)
    
    # Test before and after healing
    print("\n1. System Status Before Healing...")
    try:
        response = requests.get(f"{base_url}/api/system/health")
        if response.status_code == 200:
            before_health = response.json()
            print(f"   Status: {before_health['status']}")
            for component, details in before_health.get('components', {}).items():
                status = details.get('status', 'unknown')
                status_icon = "✅" if status == "healthy" else "❌"
                print(f"   {status_icon} {component}: {status}")
                if details.get('error'):
                    print(f"      Error: {details['error'][:60]}...")
    except Exception as e:
        print(f"   ❌ Before check error: {e}")
    
    # Trigger emergency healing
    print("\n2. Triggering Emergency Healing...")
    try:
        response = requests.post(f"{base_url}/api/healing/emergency-heal")
        if response.status_code == 200:
            healing_result = response.json()
            print(f"   ✅ Emergency healing completed")
            print(f"   - Success Rate: {healing_result['success_rate']:.1%}")
            print(f"   - Fixed Issues: {healing_result['successful_fixes']}/{healing_result['total_attempts']}")
        else:
            print(f"   ❌ Emergency healing failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Emergency healing error: {e}")
    
    # Wait a moment for fixes to take effect
    print("\n3. Waiting for fixes to take effect...")
    time.sleep(3)
    
    # Test after healing
    print("\n4. System Status After Healing...")
    try:
        response = requests.get(f"{base_url}/api/system/health")
        if response.status_code == 200:
            after_health = response.json()
            print(f"   Status: {after_health['status']}")
            for component, details in after_health.get('components', {}).items():
                status = details.get('status', 'unknown')
                status_icon = "✅" if status == "healthy" else "❌"
                print(f"   {status_icon} {component}: {status}")
                if details.get('error'):
                    print(f"      Error: {details['error'][:60]}...")
        else:
            print(f"   ❌ After check error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ After check error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Self-Healing Effectiveness Testing Complete")

if __name__ == "__main__":
    print("🚀 Self-Healing System Test Suite")
    print("Make sure the API server is running on port 8004")
    
    try:
        # Test self-healing system
        test_self_healing_system()
        
        # Test effectiveness
        test_self_healing_effectiveness()
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
