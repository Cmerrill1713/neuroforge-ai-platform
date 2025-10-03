#!/usr/bin/env python3
"""
CURSOR MANDATORY PREFLIGHT CHECK
This script MUST be imported and run before any Cursor work.
It enforces documentation reading and system validation.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

class CursorMandatoryPreflight:
    """MANDATORY preflight checks for Cursor work."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.required_docs = [
            "SYSTEM_OVERVIEW_MASTER.md",
            "SYSTEM_ARCHITECTURE_MAP.md",
            "FEATURE_DEPENDENCY_MAP.md", 
            "CURSOR_WORK_REQUIREMENTS.md"
        ]
        
    def check_documentation_read(self) -> Dict[str, Any]:
        """Check if documentation has been read recently."""
        result = {
            "all_docs_exist": True,
            "recent_readings": {},
            "missing_docs": [],
            "can_proceed": False
        }
        
        for doc in self.required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                result["missing_docs"].append(doc)
                result["all_docs_exist"] = False
            else:
                # Check if doc was modified recently (within last 24 hours)
                import time
                mod_time = doc_path.stat().st_mtime
                current_time = time.time()
                hours_ago = (current_time - mod_time) / 3600
                
                result["recent_readings"][doc] = {
                    "exists": True,
                    "hours_since_modification": round(hours_ago, 2),
                    "recently_read": hours_ago < 24
                }
                
        # Can only proceed if all docs exist and at least one was read recently
        result["can_proceed"] = (
            result["all_docs_exist"] and 
            any(info["recently_read"] for info in result["recent_readings"].values())
        )
        
        return result
        
    def enforce_documentation_reading(self):
        """Enforce that documentation must be read."""
        print("🚨 MANDATORY CURSOR PREFLIGHT CHECK")
        print("=" * 50)
        
        doc_check = self.check_documentation_read()
        
        if not doc_check["all_docs_exist"]:
            print("❌ BLOCKING: Required documentation missing!")
            for doc in doc_check["missing_docs"]:
                print(f"   • {doc}")
            print("\n🔧 REQUIRED ACTIONS:")
            print("1. Ensure all required documents exist")
            print("2. Re-run this preflight check")
            sys.exit(1)
            
        if not doc_check["can_proceed"]:
            print("❌ BLOCKING: Documentation not recently read!")
            print("\n📋 REQUIRED DOCUMENTATION:")
            for doc, info in doc_check["recent_readings"].items():
                status = "✅ RECENT" if info["recently_read"] else "❌ OLD"
                print(f"   • {doc}: {status} ({info['hours_since_modification']}h ago)")
                
            print("\n🔧 REQUIRED ACTIONS:")
            print("1. READ the following documents:")
            for doc in self.required_docs:
                print(f"   • {doc}")
            print("2. UNDERSTAND the system architecture and requirements")
            print("3. Re-run this preflight check")
            sys.exit(1)
            
        print("✅ Documentation validation passed")
        print("✅ Cursor work is authorized")
        print("=" * 50)

def mandatory_cursor_preflight():
    """MANDATORY function that must be called before any Cursor work."""
    preflight = CursorMandatoryPreflight()
    preflight.enforce_documentation_reading()
    
    # Also run system validator
    try:
        from MANDATORY_SYSTEM_VALIDATOR import MandatorySystemValidator
        validator = MandatorySystemValidator()
        if not validator.run_full_validation():
            print("🚫 System validation failed - work is blocked")
            sys.exit(1)
    except ImportError:
        print("⚠️ WARNING: MANDATORY_SYSTEM_VALIDATOR not found")
        print("   System validation skipped")
    except Exception as e:
        print(f"🚫 System validation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    mandatory_cursor_preflight()
