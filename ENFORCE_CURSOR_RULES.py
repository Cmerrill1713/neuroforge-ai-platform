#!/usr/bin/env python3
"""
ENFORCE CURSOR RULES
This script enforces all Cursor work requirements and blocks work if not met.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

class CursorRuleEnforcer:
    """Enforces Cursor work rules and requirements."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.blocking = True  # Set to False to allow warnings instead of blocking
        
    def log(self, message: str, level: str = "INFO"):
        """Log enforcement messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def enforce_documentation_reading(self) -> bool:
        """Enforce that required documentation has been read."""
        self.log("📋 Enforcing documentation reading requirements...")
        
        required_docs = [
            "SYSTEM_OVERVIEW_MASTER.md",
            "SYSTEM_ARCHITECTURE_MAP.md", 
            "FEATURE_DEPENDENCY_MAP.md",
            "CURSOR_WORK_REQUIREMENTS.md"
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not (self.project_root / doc).exists():
                missing_docs.append(doc)
                
        if missing_docs:
            self.log(f"🚫 BLOCKING: Missing required documentation: {missing_docs}", "ERROR")
            if self.blocking:
                return False
                
        # Check if docs were read recently (modified within last 24 hours)
        recently_read = False
        for doc in required_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                mod_time = doc_path.stat().st_mtime
                hours_ago = (time.time() - mod_time) / 3600
                if hours_ago < 24:
                    recently_read = True
                    break
                    
        if not recently_read:
            self.log("🚫 BLOCKING: Required documentation not read recently", "ERROR")
            self.log("📖 REQUIRED: Read all documentation before proceeding", "ERROR")
            if self.blocking:
                return False
                
        self.log("✅ Documentation requirements met")
        return True
        
    def enforce_system_validation(self) -> bool:
        """Enforce that system validation has been run."""
        self.log("🔍 Enforcing system validation requirements...")
        
        # Check if validation report exists and is recent
        validation_report = self.project_root / "VALIDATION_REPORT.json"
        
        if not validation_report.exists():
            self.log("🚫 BLOCKING: No system validation report found", "ERROR")
            self.log("🔧 REQUIRED: Run python3 MANDATORY_SYSTEM_VALIDATOR.py", "ERROR")
            if self.blocking:
                return False
                
        # Check if validation is recent (within last hour)
        if validation_report.exists():
            mod_time = validation_report.stat().st_mtime
            minutes_ago = (time.time() - mod_time) / 60
            
            if minutes_ago > 60:  # 1 hour
                self.log("🚫 BLOCKING: System validation is stale", "ERROR")
                self.log(f"⏰ Last validation: {minutes_ago:.1f} minutes ago", "ERROR")
                self.log("🔧 REQUIRED: Re-run system validation", "ERROR")
                if self.blocking:
                    return False
                    
        self.log("✅ System validation requirements met")
        return True
        
    def enforce_preflight_check(self) -> bool:
        """Enforce that preflight check has been run."""
        self.log("✈️ Enforcing preflight check requirements...")
        
        # Check if preflight was run recently
        preflight_script = self.project_root / "CURSOR_MANDATORY_PREFLIGHT.py"
        
        if not preflight_script.exists():
            self.log("🚫 BLOCKING: Preflight check script not found", "ERROR")
            if self.blocking:
                return False
                
        # Try to run preflight check
        try:
            result = subprocess.run(
                [sys.executable, str(preflight_script)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.log("🚫 BLOCKING: Preflight check failed", "ERROR")
                self.log(f"Error: {result.stderr}", "ERROR")
                if self.blocking:
                    return False
                    
            self.log("✅ Preflight check passed")
            return True
            
        except subprocess.TimeoutExpired:
            self.log("🚫 BLOCKING: Preflight check timed out", "ERROR")
            if self.blocking:
                return False
        except Exception as e:
            self.log(f"🚫 BLOCKING: Preflight check error: {e}", "ERROR")
            if self.blocking:
                return False
                
        return True
        
    def enforce_system_state_check(self) -> bool:
        """Enforce that system state has been checked."""
        self.log("🔍 Enforcing system state check requirements...")
        
        # Check if system_cli.py exists
        system_cli = self.project_root / "system_cli.py"
        if not system_cli.exists():
            self.log("🚫 BLOCKING: system_cli.py not found", "ERROR")
            if self.blocking:
                return False
                
        # Try to run system CLI
        try:
            result = subprocess.run(
                [sys.executable, str(system_cli)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.log("🚫 BLOCKING: System state check failed", "ERROR")
                self.log(f"Error: {result.stderr}", "ERROR")
                if self.blocking:
                    return False
                    
            self.log("✅ System state check passed")
            return True
            
        except subprocess.TimeoutExpired:
            self.log("🚫 BLOCKING: System state check timed out", "ERROR")
            if self.blocking:
                return False
        except Exception as e:
            self.log(f"🚫 BLOCKING: System state check error: {e}", "ERROR")
            if self.blocking:
                return False
                
        return True
        
    def run_all_enforcement_checks(self) -> bool:
        """Run all enforcement checks."""
        self.log("🚨 STARTING CURSOR RULE ENFORCEMENT")
        self.log("=" * 50)
        
        checks = [
            ("Documentation Reading", self.enforce_documentation_reading),
            ("System Validation", self.enforce_system_validation),
            ("Preflight Check", self.enforce_preflight_check),
            ("System State Check", self.enforce_system_state_check)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            self.log(f"\n🔍 Running: {check_name}")
            try:
                if not check_func():
                    all_passed = False
                    self.log(f"❌ {check_name} FAILED", "ERROR")
                else:
                    self.log(f"✅ {check_name} PASSED")
            except Exception as e:
                all_passed = False
                self.log(f"❌ {check_name} ERROR: {e}", "ERROR")
                
        self.log("\n" + "=" * 50)
        
        if all_passed:
            self.log("✅ ALL ENFORCEMENT CHECKS PASSED")
            self.log("🎯 Cursor work is AUTHORIZED")
            return True
        else:
            self.log("🚫 ENFORCEMENT CHECKS FAILED")
            self.log("❌ Cursor work is BLOCKED")
            self.log("\n🔧 REQUIRED ACTIONS:")
            self.log("1. Read all required documentation")
            self.log("2. Run: python3 MANDATORY_SYSTEM_VALIDATOR.py")
            self.log("3. Run: python3 CURSOR_MANDATORY_PREFLIGHT.py")
            self.log("4. Check system state with: python3 system_cli.py")
            self.log("5. Only then can work proceed")
            return False

def main():
    """Main enforcement entry point."""
    enforcer = CursorRuleEnforcer()
    
    # Run all enforcement checks
    can_proceed = enforcer.run_all_enforcement_checks()
    
    # Exit with appropriate code
    if can_proceed:
        sys.exit(0)  # Success - work can proceed
    else:
        sys.exit(1)  # Failure - work is blocked

if __name__ == "__main__":
    main()
