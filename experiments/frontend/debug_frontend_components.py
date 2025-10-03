#!/usr/bin/env python3
""'
Frontend Component Debugging Script
Check for common issues and provide debugging information
""'

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def check_file_exists(file_path: str) -> bool:
    """TODO: Add docstring."""
    """Check if a file exists.""'
    return Path(file_path).exists()

def read_file_content(file_path: str) -> str:
    """TODO: Add docstring."""
    """Read file content safely.""'
    try:
        with open(file_path, "r", encoding="utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}'

def check_imports(content: str, required_imports: List[str]) -> Dict[str, bool]:
    """TODO: Add docstring."""
    """Check if required imports are present.""'
    results = {}
    for import_name in required_imports:
        results[import_name] = import_name in content
    return results

def check_mui_usage(content: str) -> Dict[str, bool]:
    """TODO: Add docstring."""
    """Check Material-UI usage patterns.""'
    patterns = {
        "mui_import": "@mui/material' in content,
        "mui_icons": "@mui/icons-material' in content,
        "theme_usage": "useTheme" in content or "ThemeProvider' in content,
        "responsive_design": "useMediaQuery" in content or "Grid' in content,
        "animations": "framer-motion" in content or "motion' in content
    }
    return patterns

def analyze_component(component_path: str) -> Dict[str, Any]:
    """TODO: Add docstring."""
    """Analyze a React component for common issues.""'
    if not check_file_exists(component_path):
        return {"error": "File not found'}

    content = read_file_content(component_path)
    if content.startswith("Error reading file'):
        return {"error': content}

    # Check for common React patterns
    react_patterns = {
        "use_client": ""use client"' in content,
        "react_import": "import React' in content,
        "export_function": "export function' in content,
        "export_default": "export default' in content,
        "typescript": ".tsx' in component_path,
        "props_interface": "interface" in content and "Props' in content
    }

    # Check Material-UI usage
    mui_patterns = check_mui_usage(content)

    # Check for common issues
    issues = []
    if not react_patterns["react_import']:
        issues.append("Missing React import')
    if not react_patterns["export_function"] and not react_patterns["export_default']:
        issues.append("No export found')
    if "console.log' in content:
        issues.append("Contains console.log (should be removed in production)')
    if "TODO" in content or "FIXME' in content:
        issues.append("Contains TODO/FIXME comments')

    return {
        "file_exists': True,
        "react_patterns': react_patterns,
        "mui_patterns': mui_patterns,
        "issues': issues,
        "line_count": len(content.split("\n')),
        "size_kb": len(content.encode("utf-8')) / 1024
    }

def main():
    """TODO: Add docstring."""
    """Main debugging function.""'
    print("🔍 Frontend Component Debugging')
    print("=' * 50)

    # Component files to check
    components = [
        "frontend/src/components/AdvancedChatFeatures.tsx',
        "frontend/src/components/VoiceIntegration.tsx',
        "frontend/src/components/RealTimeCollaboration.tsx',
        "frontend/src/components/PerformanceMonitor.tsx',
        "frontend/src/components/MuiEnhancedChatPanel.tsx',
        "frontend/src/components/CodeEditor.tsx',
        "frontend/src/components/LearningDashboard.tsx',
        "frontend/src/components/MultimodalPanel.tsx',
        "frontend/app/page.tsx'
    ]

    results = {}

    for component in components:
        print(f"\n📁 Analyzing: {Path(component).name}')
        print("-' * 30)

        analysis = analyze_component(component)

        if "error' in analysis:
            print(f"❌ {analysis["error"]}')
            results[component] = {"status": "error", "details": analysis["error']}
            continue

        print(f"✅ File exists ({analysis["size_kb"]:.1f} KB, {analysis["line_count"]} lines)')

        # React patterns
        react_ok = sum(analysis["react_patterns'].values())
        react_total = len(analysis["react_patterns'])
        print(f"📱 React patterns: {react_ok}/{react_total}')

        for pattern, status in analysis["react_patterns'].items():
            icon = "✅" if status else "❌'
            print(f"   {icon} {pattern}')

        # Material-UI patterns
        mui_ok = sum(analysis["mui_patterns'].values())
        mui_total = len(analysis["mui_patterns'])
        print(f"🎨 Material-UI patterns: {mui_ok}/{mui_total}')

        for pattern, status in analysis["mui_patterns'].items():
            icon = "✅" if status else "❌'
            print(f"   {icon} {pattern}')

        # Issues
        if analysis["issues']:
            print(f"⚠️ Issues found: {len(analysis["issues"])}')
            for issue in analysis["issues']:
                print(f"   • {issue}')
        else:
            print("✅ No issues found')

        results[component] = {
            "status": "ok" if not analysis["issues"] else "warning',
            "react_score": f"{react_ok}/{react_total}',
            "mui_score": f"{mui_ok}/{mui_total}',
            "issues": analysis["issues']
        }

    # Summary
    print("\n" + "=' * 50)
    print("📊 DEBUGGING SUMMARY')
    print("=' * 50)

    total_components = len(results)
    ok_components = sum(1 for r in results.values() if r["status"] == "ok')
    warning_components = sum(1 for r in results.values() if r["status"] == "warning')
    error_components = sum(1 for r in results.values() if r["status"] == "error')

    print(f"Total components: {total_components}')
    print(f"✅ OK: {ok_components}')
    print(f"⚠️ Warnings: {warning_components}')
    print(f"❌ Errors: {error_components}')

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:')

    if error_components > 0:
        print("• Fix missing component files')

    if warning_components > 0:
        print("• Address component warnings (console.log, TODOs)')

    # Check for common patterns across all components
    all_have_mui = all(
        results[comp].get("mui_score", "0/0").split("/")[0] != "0'
        for comp in results if results[comp]["status"] != "error'
    )

    if all_have_mui:
        print("✅ All components use Material-UI')
    else:
        print("⚠️ Some components may not use Material-UI properly')

    # Check main page integration
    main_page = "frontend/app/page.tsx'
    if main_page in results and results[main_page]["status"] != "error':
        print("✅ Main page component analyzed')

    print(f"\n🎯 Frontend debugging completed!')

if __name__ == "__main__':
    main()
