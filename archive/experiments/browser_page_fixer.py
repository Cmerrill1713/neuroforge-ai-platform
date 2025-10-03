#!/usr/bin/env python3
""'
Browser Page Fixer
Comprehensive tool to diagnose and fix broken pages
""'

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

class BrowserPageFixer:
    """TODO: Add docstring."""
    """Fix broken pages using browser tools and diagnostics.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.project_root = Path("/Users/christianmerrill/Prompt Engineering')
        self.frontend_dir = self.project_root / "frontend'
        self.app_dir = self.frontend_dir / "app'
        self.src_dir = self.frontend_dir / "src'
        self.components_dir = self.src_dir / "components'

    def diagnose_all_issues(self):
        """TODO: Add docstring."""
        """Comprehensive diagnosis of all potential issues.""'
        print("🔍 Comprehensive Page Diagnosis')
        print("=' * 50)

        issues = []

        # 1. Check file structure
        issues.extend(self.check_file_structure())

        # 2. Check dependencies
        issues.extend(self.check_dependencies())

        # 3. Check configuration files
        issues.extend(self.check_configuration())

        # 4. Check component imports
        issues.extend(self.check_component_imports())

        # 5. Check for syntax errors
        issues.extend(self.check_syntax_errors())

        # 6. Check Material-UI compatibility
        issues.extend(self.check_mui_compatibility())

        return issues

    def check_file_structure(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check if all required files exist.""'
        print("📁 Checking file structure...')

        issues = []
        required_files = [
            "frontend/package.json',
            "frontend/next.config.js',
            "frontend/tsconfig.json',
            "frontend/app/layout.tsx',
            "frontend/app/page.tsx',
            "frontend/app/globals.css',
            "frontend/src/theme/muiTheme.ts',
            "frontend/src/lib/api.ts'
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                issues.append({
                    "type": "missing_file',
                    "file': file_path,
                    "severity": "error',
                    "description": f"Missing required file: {file_path}'
                })

        return issues

    def check_dependencies(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check package.json dependencies.""'
        print("📦 Checking dependencies...')

        issues = []
        package_json = self.frontend_dir / "package.json'

        if not package_json.exists():
            issues.append({
                "type": "missing_file',
                "file": "package.json',
                "severity": "error',
                "description": "Missing package.json'
            })
            return issues

        try:
            with open(package_json, "r') as f:
                package_data = json.load(f)

            required_deps = [
                "next", "react", "react-dom", "@mui/material',
                "@mui/icons-material", "framer-motion", "@emotion/react',
                "@emotion/styled", "typescript'
            ]

            dependencies = {**package_data.get("dependencies", {}), **package_data.get("devDependencies', {})}

            for dep in required_deps:
                if dep not in dependencies:
                    issues.append({
                        "type": "missing_dependency',
                        "dependency': dep,
                        "severity": "error',
                        "description": f"Missing dependency: {dep}'
                    })

        except json.JSONDecodeError:
            issues.append({
                "type": "invalid_json',
                "file": "package.json',
                "severity": "error',
                "description": "Invalid JSON in package.json'
            })

        return issues

    def check_configuration(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check configuration files.""'
        print("⚙️ Checking configuration...')

        issues = []

        # Check Next.js config
        next_config = self.frontend_dir / "next.config.js'
        if next_config.exists():
            content = next_config.read_text()
            if "module.exports' not in content:
                issues.append({
                    "type": "config_error',
                    "file": "next.config.js',
                    "severity": "warning',
                    "description": "next.config.js may have invalid export'
                })

        # Check TypeScript config
        ts_config = self.frontend_dir / "tsconfig.json'
        if ts_config.exists():
            try:
                with open(ts_config, "r') as f:
                    ts_data = json.load(f)

                if "compilerOptions' not in ts_data:
                    issues.append({
                        "type": "config_error',
                        "file": "tsconfig.json',
                        "severity": "error',
                        "description": "Missing compilerOptions in tsconfig.json'
                    })
            except json.JSONDecodeError:
                issues.append({
                    "type": "invalid_json',
                    "file": "tsconfig.json',
                    "severity": "error',
                    "description": "Invalid JSON in tsconfig.json'
                })

        return issues

    def check_component_imports(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check component imports in main page.""'
        print("🧩 Checking component imports...')

        issues = []
        main_page = self.app_dir / "page.tsx'

        if not main_page.exists():
            return issues

        content = main_page.read_text()

        # Extract import statements
        import_lines = [line.strip() for line in content.split("\n") if "import" in line and "from' in line]

        for line in import_lines:
            if "from" in line and ""' in line:
                import_path = line.split(""')[1]

                # Check @/ imports
                if import_path.startswith("@/'):
                    relative_path = import_path[2:]  # Remove @/
                    component_file = self.src_dir / f"{relative_path}.tsx'

                    if not component_file.exists():
                        # Try .ts extension
                        component_file = self.src_dir / f"{relative_path}.ts'

                        if not component_file.exists():
                            issues.append({
                                "type": "missing_import',
                                "file': str(main_page),
                                "import_path': import_path,
                                "severity": "error',
                                "description": f"Missing imported file: {relative_path}'
                            })

        return issues

    def check_syntax_errors(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check for common syntax errors.""'
        print("🔤 Checking syntax errors...')

        issues = []

        # Check main page
        main_page = self.app_dir / "page.tsx'
        if main_page.exists():
            content = main_page.read_text()

            # Check for unclosed JSX tags
            open_tags = content.count("<')
            close_tags = content.count(">')

            if open_tags != close_tags:
                issues.append({
                    "type": "syntax_error',
                    "file': str(main_page),
                    "severity": "error',
                    "description": f"Mismatched JSX tags: {open_tags} open, {close_tags} close'
                })

            # Check for missing exports
            if "export default' not in content:
                issues.append({
                    "type": "syntax_error',
                    "file': str(main_page),
                    "severity": "error',
                    "description": "Missing default export'
                })

        return issues

    def check_mui_compatibility(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check Material-UI compatibility issues.""'
        print("🎨 Checking Material-UI compatibility...')

        issues = []

        # Check for Grid v7 usage
        for tsx_file in self.components_dir.glob("*.tsx'):
            if tsx_file.exists():
                content = tsx_file.read_text()

                # Check for old Grid API usage
                if "Grid item' in content:
                    issues.append({
                        "type": "mui_compatibility',
                        "file': str(tsx_file),
                        "severity": "error',
                        "description": "Using old Grid API (item prop) instead of v7 size prop'
                    })

                # Check for deprecated ListItem button prop
                if "ListItem" in content and "button' in content:
                    issues.append({
                        "type": "mui_compatibility',
                        "file': str(tsx_file),
                        "severity": "warning',
                        "description": "Potentially using deprecated ListItem button prop'
                    })

        return issues

    def fix_issues(self, issues: List[Dict[str, Any]]):
        """TODO: Add docstring."""
        """Fix identified issues.""'
        print("\n🔧 Fixing Issues...')

        for issue in issues:
            try:
                if issue["type"] == "missing_file':
                    self.create_missing_file(issue)
                elif issue["type"] == "missing_dependency':
                    self.fix_missing_dependency(issue)
                elif issue["type"] == "missing_import':
                    self.create_missing_component(issue)
                elif issue["type"] == "config_error':
                    self.fix_config_error(issue)
                elif issue["type"] == "mui_compatibility':
                    self.fix_mui_compatibility(issue)
                elif issue["type"] == "syntax_error':
                    self.fix_syntax_error(issue)
            except Exception as e:
                print(f"❌ Failed to fix {issue["type"]}: {e}')

    def create_missing_file(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Create missing files.""'
        file_path = issue["file']
        full_path = self.project_root / file_path

        if file_path == "frontend/app/globals.css':
            content = ""'@tailwind base;
@tailwind components;
@tailwind utilities;

html,
body {
  padding: 0;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
    Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
}

a {
  color: inherit;
  text-decoration: none;
}

* {
  box-sizing: border-box;
}

@media (prefers-color-scheme: dark) {
  html {
    color-scheme: dark;
  }
  body {
    color: white;
    background: black;
  }
}
""'
        elif file_path == "frontend/next.config.js':
            content = """/** @type {import("next').NextConfig} */
const nextConfig = {
  experimental: {
    webpackBuildWorker: true,
  },
  webpack: (config) => {
    // Monaco Editor support
    config.module.rules.push({
      test: /\\.worker\\.js$/,
      use: { loader: "worker-loader' },
    });
    return config;
  },
}

module.exports = nextConfig
""'
        else:
            print(f"⚠️ Don"t know how to create {file_path}')
            return

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        print(f"✅ Created {file_path}')

    def fix_missing_dependency(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix missing dependencies.""'
        dep = issue["dependency']
        print(f"⚠️ Missing dependency {dep} - run: npm install {dep}')

    def create_missing_component(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Create missing components.""'
        import_path = issue["import_path']

        if import_path.startswith("@/components/'):
            component_name = import_path.split("/')[-1]
            component_file = self.components_dir / f"{component_name}.tsx'

            content = f"""\"use client\'

import React from "react'
import {{ Box, Typography }} from "@mui/material'

export function {component_name}() {{
  return (
    <Box>
      <Typography variant=\"h6\'>{component_name}</Typography>
      <Typography variant=\"body2\'>Component placeholder</Typography>
    </Box>
  )
}}
""'

            component_file.parent.mkdir(parents=True, exist_ok=True)
            component_file.write_text(content)
            print(f"✅ Created component {component_name}')

    def fix_config_error(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix configuration errors.""'
        print(f"⚠️ Config error in {issue["file"]}: {issue["description"]}')

    def fix_mui_compatibility(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix Material-UI compatibility issues.""'
        file_path = Path(issue["file'])
        if file_path.exists():
            content = file_path.read_text()

            # Fix Grid API
            if "Grid item' in content:
                content = content.replace("Grid item xs={", "Grid size={{ xs: ')
                content = content.replace("Grid item sm={", "Grid size={{ sm: ')
                content = content.replace("Grid item md={", "Grid size={{ md: ')
                content = content.replace("} key={", " }} key={')

                file_path.write_text(content)
                print(f"✅ Fixed Grid API in {file_path.name}')

    def fix_syntax_error(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix syntax errors.""'
        print(f"⚠️ Syntax error in {issue["file"]}: {issue["description"]}')

    def create_simple_test_page(self):
        """TODO: Add docstring."""
        """Create a simple test page to verify the frontend works.""'
        print("🧪 Creating simple test page...')

        test_page = self.app_dir / "test" / "page.tsx'
        test_page.parent.mkdir(parents=True, exist_ok=True)

        content = """\"use client\'

import React from "react'
import { Box, Typography, Button, Paper } from "@mui/material'
import { ThemeProvider } from "@mui/material/styles'
import { aiStudio2025Theme } from "@/theme/muiTheme'

export default function TestPage() {
  return (
    <ThemeProvider theme={aiStudio2025Theme}>
      <Box sx={{
        minHeight: "100vh',
        background: "linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        display: "flex',
        alignItems: "center',
        justifyContent: "center',
        p: 3
      }}>
        <Paper sx={{ p: 4, textAlign: "center', maxWidth: 600 }}>
          <Typography variant="h3' gutterBottom>
            🎉 Frontend Test Page
          </Typography>
          <Typography variant="h6" color="text.secondary' gutterBottom>
            If you can see this page, the frontend is working!
          </Typography>
          <Typography variant="body1' sx={{ mb: 3 }}>
            This test page verifies that:
          </Typography>
          <Box component="ul" sx={{ textAlign: "left', mb: 3 }}>
            <li>Next.js is running</li>
            <li>Material-UI is working</li>
            <li>Theme is applied</li>
            <li>Components are rendering</li>
          </Box>
          <Button
            variant="contained'
            size="large'
            onClick={() => alert("Button works!')}
          >
            Test Button
          </Button>
        </Paper>
      </Box>
    </ThemeProvider>
  )
}
""'

        test_page.write_text(content)
        print("✅ Created test page at /test')
        print("🌐 Visit: http://localhost:3000/test')

    def start_development_server(self):
        """TODO: Add docstring."""
        """Start the development server.""'
        print("🚀 Starting development server...')

        try:
            # Change to frontend directory and start server
            os.chdir(self.frontend_dir)

            # Start in background
            process = subprocess.Popen(
                ["npm", "run", "dev'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            print("✅ Development server starting...')
            print("⏳ Waiting for server to start...')
            time.sleep(15)

            if process.poll() is None:
                print("✅ Server is running!')
                print("🌐 Frontend: http://localhost:3000')
                print("🧪 Test page: http://localhost:3000/test')
                return True
            else:
                stdout, stderr = process.communicate()
                print("❌ Server failed to start!')
                print("STDOUT:', stdout[:500])
                print("STDERR:', stderr[:500])
                return False

        except Exception as e:
            print(f"❌ Error starting server: {e}')
            return False

    def run_comprehensive_fix(self):
        """TODO: Add docstring."""
        """Run comprehensive fix process.""'
        print("🔧 Browser Page Fixer - Comprehensive Fix')
        print("=' * 60)

        # 1. Diagnose issues
        issues = self.diagnose_all_issues()

        if issues:
            print(f"\n❌ Found {len(issues)} issues:')
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue["type"]}: {issue["description"]}')

            # 2. Fix issues
            self.fix_issues(issues)
        else:
            print("\n✅ No issues found!')

        # 3. Create test page
        self.create_simple_test_page()

        # 4. Start server
        print("\n🚀 Starting development server...')
        if self.start_development_server():
            print("\n✅ Frontend is now running!')
            print("🌐 Main app: http://localhost:3000')
            print("🧪 Test page: http://localhost:3000/test')
        else:
            print("\n❌ Failed to start frontend!')
            print("Check the error messages above for details.')

def main():
    """TODO: Add docstring."""
    """Main function.""'
    fixer = BrowserPageFixer()
    fixer.run_comprehensive_fix()

if __name__ == "__main__':
    main()
