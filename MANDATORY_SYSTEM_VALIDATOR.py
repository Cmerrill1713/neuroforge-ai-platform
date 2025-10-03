#!/usr/bin/env python3
"""
MANDATORY SYSTEM VALIDATOR
This script MUST be run before any Cursor work can be performed.
It validates system state, documentation, and enforces requirements.
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

class MandatorySystemValidator:
    """MANDATORY system validation that blocks work if requirements not met."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.validation_log = []
        self.blocking_errors = []
        self.warnings = []
        self.required_docs = [
            "SYSTEM_OVERVIEW_MASTER.md",
            "SYSTEM_ARCHITECTURE_MAP.md", 
            "FEATURE_DEPENDENCY_MAP.md",
            "CURSOR_WORK_REQUIREMENTS.md"
        ]
        
    def log(self, message: str, level: str = "INFO"):
        """Log validation messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.validation_log.append(log_entry)
        print(log_entry)
        
    def add_blocking_error(self, error: str):
        """Add a blocking error that prevents work."""
        self.blocking_errors.append(error)
        self.log(f"🚫 BLOCKING ERROR: {error}", "ERROR")
        
    def add_warning(self, warning: str):
        """Add a warning that should be addressed."""
        self.warnings.append(warning)
        self.log(f"⚠️ WARNING: {warning}", "WARNING")
        
    def validate_documentation_exists(self) -> bool:
        """Validate that all required documentation exists."""
        self.log("📋 Validating required documentation...")
        
        missing_docs = []
        for doc in self.required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                missing_docs.append(doc)
                self.add_blocking_error(f"Required document missing: {doc}")
            else:
                self.log(f"✅ Found: {doc}")
                
        if missing_docs:
            self.add_blocking_error(f"Missing {len(missing_docs)} required documents")
            return False
            
        return True
        
    def validate_documentation_content(self) -> bool:
        """Validate that documentation has required content."""
        self.log("📖 Validating documentation content...")
        
        # Check SYSTEM_OVERVIEW_MASTER.md for critical sections
        master_doc = self.project_root / "SYSTEM_OVERVIEW_MASTER.md"
        if master_doc.exists():
            content = master_doc.read_text()
            required_sections = [
                "CRITICAL: READ THIS FIRST",
                "SYSTEM ARCHITECTURE OVERVIEW", 
                "QUICK REFERENCE",
                "DEVELOPMENT WORKFLOW",
                "COMMON MISTAKES TO AVOID"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
                    
            if missing_sections:
                self.add_blocking_error(f"SYSTEM_OVERVIEW_MASTER.md missing sections: {missing_sections}")
                return False
                
        return True
        
    def validate_system_state(self) -> bool:
        """Validate current system state."""
        self.log("🔍 Validating system state...")
        
        # Check if system_cli.py exists and is executable
        system_cli = self.project_root / "system_cli.py"
        if not system_cli.exists():
            self.add_blocking_error("system_cli.py not found - cannot validate system state")
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
                self.add_blocking_error(f"System CLI failed: {result.stderr}")
                return False
                
            self.log("✅ System CLI executed successfully")
            
        except subprocess.TimeoutExpired:
            self.add_blocking_error("System CLI timed out - system may be unresponsive")
            return False
        except Exception as e:
            self.add_blocking_error(f"System CLI error: {str(e)}")
            return False
            
        return True
        
    def validate_port_availability(self) -> bool:
        """Validate that required ports are available or services are healthy."""
        self.log("🔌 Validating port availability and service health...")
        
        required_ports = [8004, 3000, 11434]  # Backend, Frontend, Ollama
        optional_ports = [8000, 8005, 8086, 8087, 8090]  # Optional services
        
        port_conflicts = []
        
        for port in required_ports:
            if self._is_port_in_use(port):
                # Check if the service is healthy
                if port == 8004:
                    # Check if main API is healthy
                    try:
                        response = requests.get("http://localhost:8004/api/system/health", timeout=5)
                        if response.status_code == 200:
                            self.log(f"✅ Port {port} in use but service is healthy")
                            continue
                        else:
                            self.add_blocking_error(f"Port {port} in use but service unhealthy (status {response.status_code})")
                            port_conflicts.append(port)
                    except requests.exceptions.RequestException:
                        self.add_blocking_error(f"Port {port} in use but service not responding")
                        port_conflicts.append(port)
                elif port == 11434:
                    # Check if Ollama is healthy
                    try:
                        response = requests.get("http://localhost:11434/api/tags", timeout=5)
                        if response.status_code == 200:
                            self.log(f"✅ Port {port} in use but Ollama is healthy")
                            continue
                        else:
                            self.add_blocking_error(f"Port {port} in use but Ollama unhealthy (status {response.status_code})")
                            port_conflicts.append(port)
                    except requests.exceptions.RequestException:
                        self.add_blocking_error(f"Port {port} in use but Ollama not responding")
                        port_conflicts.append(port)
                elif port == 3000:
                    # Check if frontend is accessible
                    try:
                        response = requests.get("http://localhost:3000", timeout=5)
                        if response.status_code == 200:
                            self.log(f"✅ Port {port} in use but frontend is accessible")
                            continue
                        else:
                            self.add_warning(f"Port {port} in use but frontend may not be fully ready (status {response.status_code})")
                            # Don't block for frontend issues
                    except requests.exceptions.RequestException:
                        self.log(f"ℹ️ Port {port} in use but frontend not yet accessible")
                        # Don't block for frontend issues
                else:
                    self.add_blocking_error(f"Required port {port} is in use - must be available")
                    port_conflicts.append(port)
            else:
                self.log(f"✅ Port {port} available")
                
        for port in optional_ports:
            if self._is_port_in_use(port):
                self.add_warning(f"Optional port {port} is in use")
            else:
                self.log(f"✅ Optional port {port} available")
                
        return len(port_conflicts) == 0
        
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return False
        except OSError:
            return True
            
    def validate_dependencies(self) -> bool:
        """Validate that required dependencies are available."""
        self.log("📦 Validating dependencies...")
        
        # Check Python requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            self.log("✅ requirements.txt found")
        else:
            self.add_warning("requirements.txt not found")
            
        # Check frontend dependencies
        frontend_package = self.project_root / "frontend" / "package.json"
        if frontend_package.exists():
            self.log("✅ frontend/package.json found")
        else:
            self.add_warning("frontend/package.json not found")
            
        # Check main entry points
        main_files = ["main.py", "consolidated_api_optimized.py"]
        found_main = False
        for main_file in main_files:
            if (self.project_root / main_file).exists():
                self.log(f"✅ Found main entry point: {main_file}")
                found_main = True
                
        if not found_main:
            self.add_blocking_error("No main entry point found (main.py or consolidated_api_optimized.py)")
            return False
            
        return True
        
    def validate_service_health(self) -> bool:
        """Validate that services are healthy if running."""
        self.log("🏥 Validating service health...")
        
        # Check if main API is running and healthy
        try:
            response = requests.get("http://localhost:8004/api/system/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Main API (8004) is healthy")
                return True
            else:
                self.add_warning(f"Main API (8004) returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            self.log("ℹ️ Main API (8004) not running - this is OK for initial setup")
            return True
            
    def create_validation_report(self) -> Dict[str, Any]:
        """Create a comprehensive validation report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "validation_log": self.validation_log,
            "blocking_errors": self.blocking_errors,
            "warnings": self.warnings,
            "can_proceed": len(self.blocking_errors) == 0,
            "required_docs_status": {},
            "system_state": "unknown",
            "port_status": {},
            "dependencies_status": "unknown"
        }
        
        # Check each required document
        for doc in self.required_docs:
            doc_path = self.project_root / doc
            report["required_docs_status"][doc] = {
                "exists": doc_path.exists(),
                "size": doc_path.stat().st_size if doc_path.exists() else 0,
                "modified": doc_path.stat().st_mtime if doc_path.exists() else 0
            }
            
        return report
        
    def save_validation_report(self, report: Dict[str, Any]):
        """Save validation report to file."""
        report_file = self.project_root / "VALIDATION_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        self.log(f"📄 Validation report saved to: {report_file}")
        
    def run_full_validation(self) -> bool:
        """Run complete validation suite."""
        self.log("🚀 Starting MANDATORY system validation...")
        self.log("=" * 60)
        
        # Run all validation checks
        checks = [
            ("Documentation Exists", self.validate_documentation_exists),
            ("Documentation Content", self.validate_documentation_content),
            ("System State", self.validate_system_state),
            ("Port Availability", self.validate_port_availability),
            ("Dependencies", self.validate_dependencies),
            ("Service Health", self.validate_service_health)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            self.log(f"\n🔍 Running: {check_name}")
            try:
                if not check_func():
                    all_passed = False
                    self.add_blocking_error(f"Validation failed: {check_name}")
            except Exception as e:
                all_passed = False
                self.add_blocking_error(f"Validation error in {check_name}: {str(e)}")
                
        # Create and save report
        report = self.create_validation_report()
        self.save_validation_report(report)
        
        # Final status
        self.log("\n" + "=" * 60)
        if all_passed and len(self.blocking_errors) == 0:
            self.log("✅ MANDATORY VALIDATION PASSED - Work can proceed")
            self.log("📋 All requirements met. Cursor work is authorized.")
            return True
        else:
            self.log("🚫 MANDATORY VALIDATION FAILED - Work is BLOCKED")
            self.log(f"❌ {len(self.blocking_errors)} blocking errors found")
            for error in self.blocking_errors:
                self.log(f"   • {error}")
                
            if self.warnings:
                self.log(f"⚠️ {len(self.warnings)} warnings found")
                for warning in self.warnings:
                    self.log(f"   • {warning}")
                    
            self.log("\n🔧 REQUIRED ACTIONS:")
            self.log("1. Fix all blocking errors")
            self.log("2. Address warnings")
            self.log("3. Re-run validation")
            self.log("4. Only then can Cursor work proceed")
            
            return False

def main():
    """Main validation entry point."""
    validator = MandatorySystemValidator()
    
    # Run validation
    can_proceed = validator.run_full_validation()
    
    # Exit with appropriate code
    if can_proceed:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure - blocks work

if __name__ == "__main__":
    main()
