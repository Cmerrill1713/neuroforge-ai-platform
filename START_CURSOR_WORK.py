#!/usr/bin/env python3
"""
START CURSOR WORK - MANDATORY ENTRY POINT
This is the ONLY way to start Cursor work. It enforces all requirements.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """MANDATORY entry point for all Cursor work."""
    print("🚨 CURSOR WORK ENTRY POINT")
    print("=" * 40)
    print("⚠️ This script enforces ALL requirements")
    print("⚠️ Work cannot proceed without meeting requirements")
    print("=" * 40)
    
    project_root = Path(__file__).parent
    
    # Step 1: Check if required documentation exists
    print("\n📋 Step 1: Checking required documentation...")
    required_docs = [
        "SYSTEM_OVERVIEW_MASTER.md",
        "SYSTEM_ARCHITECTURE_MAP.md", 
        "FEATURE_DEPENDENCY_MAP.md",
        "CURSOR_WORK_REQUIREMENTS.md"
    ]
    
    missing_docs = []
    for doc in required_docs:
        if not (project_root / doc).exists():
            missing_docs.append(doc)
            
    if missing_docs:
        print(f"❌ BLOCKING: Missing required documentation: {missing_docs}")
        print("🔧 REQUIRED: Ensure all documentation exists")
        sys.exit(1)
        
    print("✅ All required documentation exists")
    
    # Step 2: Run system validation
    print("\n🔍 Step 2: Running system validation...")
    validator_script = project_root / "MANDATORY_SYSTEM_VALIDATOR.py"
    
    if not validator_script.exists():
        print("❌ BLOCKING: System validator not found")
        sys.exit(1)
        
    try:
        result = subprocess.run(
            [sys.executable, str(validator_script)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print("❌ BLOCKING: System validation failed")
            print(f"Error: {result.stderr}")
            print("🔧 REQUIRED: Fix system issues before proceeding")
            sys.exit(1)
            
        print("✅ System validation passed")
        
    except subprocess.TimeoutExpired:
        print("❌ BLOCKING: System validation timed out")
        sys.exit(1)
    except Exception as e:
        print(f"❌ BLOCKING: System validation error: {e}")
        sys.exit(1)
        
    # Step 3: Run preflight check
    print("\n✈️ Step 3: Running preflight check...")
    preflight_script = project_root / "CURSOR_MANDATORY_PREFLIGHT.py"
    
    if not preflight_script.exists():
        print("❌ BLOCKING: Preflight script not found")
        sys.exit(1)
        
    try:
        result = subprocess.run(
            [sys.executable, str(preflight_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print("❌ BLOCKING: Preflight check failed")
            print(f"Error: {result.stderr}")
            print("🔧 REQUIRED: Fix preflight issues before proceeding")
            sys.exit(1)
            
        print("✅ Preflight check passed")
        
    except subprocess.TimeoutExpired:
        print("❌ BLOCKING: Preflight check timed out")
        sys.exit(1)
    except Exception as e:
        print(f"❌ BLOCKING: Preflight check error: {e}")
        sys.exit(1)
        
    # Step 4: Run rule enforcement
    print("\n🚨 Step 4: Running rule enforcement...")
    enforcer_script = project_root / "ENFORCE_CURSOR_RULES.py"
    
    if not enforcer_script.exists():
        print("❌ BLOCKING: Rule enforcer not found")
        sys.exit(1)
        
    try:
        result = subprocess.run(
            [sys.executable, str(enforcer_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print("❌ BLOCKING: Rule enforcement failed")
            print(f"Error: {result.stderr}")
            print("🔧 REQUIRED: Fix rule violations before proceeding")
            sys.exit(1)
            
        print("✅ Rule enforcement passed")
        
    except subprocess.TimeoutExpired:
        print("❌ BLOCKING: Rule enforcement timed out")
        sys.exit(1)
    except Exception as e:
        print(f"❌ BLOCKING: Rule enforcement error: {e}")
        sys.exit(1)
        
    # All checks passed
    print("\n" + "=" * 40)
    print("✅ ALL REQUIREMENTS MET")
    print("🎯 CURSOR WORK IS AUTHORIZED")
    print("=" * 40)
    
    print("\n📋 NEXT STEPS:")
    print("1. Read all required documentation")
    print("2. Understand system architecture")
    print("3. Follow development workflow")
    print("4. Test changes incrementally")
    print("5. Update documentation after changes")
    
    print("\n🔧 USEFUL COMMANDS:")
    print("• Check system state: python3 system_cli.py")
    print("• Check health: curl http://localhost:8004/api/system/health")
    print("• Check ports: lsof -i :8004 :3000 :11434")
    
    print("\n📚 REQUIRED DOCUMENTATION:")
    for doc in required_docs:
        print(f"• {doc}")
        
    print("\n🎯 WORK CAN NOW PROCEED")
    print("⚠️ Remember to follow all requirements during development")

if __name__ == "__main__":
    main()
