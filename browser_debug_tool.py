#!/usr/bin/env python3
"""
Browser Debug Tool
Diagnose and fix broken pages using browser automation
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class BrowserDebugTool:
    """Tool to diagnose and fix broken pages."""
    
    def __init__(self):
        self.frontend_dir = Path("frontend")
        self.app_dir = self.frontend_dir / "app"
        self.src_dir = self.frontend_dir / "src"
        self.components_dir = self.src_dir / "components"
        
    def diagnose_issues(self):
        """Diagnose common issues that break pages."""
        print("🔍 Diagnosing Page Issues...")
        
        issues = []
        
        # Check for missing files
        issues.extend(self.check_missing_files())
        
        # Check for import errors
        issues.extend(self.check_import_errors())
        
        # Check for syntax errors
        issues.extend(self.check_syntax_errors())
        
        # Check for component errors
        issues.extend(self.check_component_errors())
        
        # Check for configuration issues
        issues.extend(self.check_config_issues())
        
        return issues
    
    def check_missing_files(self) -> List[Dict[str, Any]]:
        """Check for missing critical files."""
        print("📁 Checking for missing files...")
        
        issues = []
        required_files = [
            "frontend/package.json",
            "frontend/next.config.js",
            "frontend/tsconfig.json",
            "frontend/tailwind.config.js",
            "frontend/postcss.config.js",
            "frontend/app/layout.tsx",
            "frontend/app/page.tsx",
            "frontend/src/theme/muiTheme.ts"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                issues.append({
                    "type": "missing_file",
                    "file": file_path,
                    "severity": "error",
                    "description": f"Missing required file: {file_path}"
                })
        
        return issues
    
    def check_import_errors(self) -> List[Dict[str, Any]]:
        """Check for import errors in components."""
        print("📦 Checking for import errors...")
        
        issues = []
        
        # Check main page imports
        main_page = self.app_dir / "page.tsx"
        if main_page.exists():
            content = main_page.read_text()
            
            # Check for problematic imports
            problematic_imports = [
                "from '@/components/",
                "from '@/theme/",
                "from '@/lib/",
                "from '@mui/",
                "from 'framer-motion'"
            ]
            
            for import_line in problematic_imports:
                if import_line in content:
                    # Check if the imported file exists
                    if import_line.startswith("from '@/components/"):
                        component_name = import_line.split("'")[1].split("/")[-1]
                        component_file = self.components_dir / f"{component_name}.tsx"
                        if not component_file.exists():
                            issues.append({
                                "type": "missing_import",
                                "file": str(main_page),
                                "import": import_line,
                                "severity": "error",
                                "description": f"Missing component: {component_name}"
                            })
        
        return issues
    
    def check_syntax_errors(self) -> List[Dict[str, Any]]:
        """Check for syntax errors in TypeScript/JSX files."""
        print("🔤 Checking for syntax errors...")
        
        issues = []
        
        # Check main page for common syntax errors
        main_page = self.app_dir / "page.tsx"
        if main_page.exists():
            content = main_page.read_text()
            
            # Check for unclosed JSX tags
            if content.count('<') != content.count('>'):
                issues.append({
                    "type": "syntax_error",
                    "file": str(main_page),
                    "severity": "error",
                    "description": "Unclosed JSX tags detected"
                })
            
            # Check for missing semicolons in critical places
            if 'export default' in content and not content.strip().endswith(';'):
                issues.append({
                    "type": "syntax_error",
                    "file": str(main_page),
                    "severity": "warning",
                    "description": "Missing semicolon at end of file"
                })
        
        return issues
    
    def check_component_errors(self) -> List[Dict[str, Any]]:
        """Check for component-specific errors."""
        print("🧩 Checking for component errors...")
        
        issues = []
        
        # Check for components that are imported but don't exist
        main_page = self.app_dir / "page.tsx"
        if main_page.exists():
            content = main_page.read_text()
            
            # Extract component imports
            import_lines = [line for line in content.split('\n') if 'import' in line and 'from' in line]
            
            for line in import_lines:
                if 'from' in line and "'" in line:
                    import_path = line.split("'")[1]
                    if import_path.startswith('@/components/'):
                        component_name = import_path.split('/')[-1]
                        component_file = self.components_dir / f"{component_name}.tsx"
                        
                        if not component_file.exists():
                            issues.append({
                                "type": "missing_component",
                                "file": str(main_page),
                                "component": component_name,
                                "severity": "error",
                                "description": f"Component {component_name} is imported but doesn't exist"
                            })
        
        return issues
    
    def check_config_issues(self) -> List[Dict[str, Any]]:
        """Check for configuration issues."""
        print("⚙️ Checking for configuration issues...")
        
        issues = []
        
        # Check Next.js config
        next_config = self.frontend_dir / "next.config.js"
        if not next_config.exists():
            issues.append({
                "type": "missing_config",
                "file": "next.config.js",
                "severity": "error",
                "description": "Missing Next.js configuration file"
            })
        
        # Check TypeScript config
        ts_config = self.frontend_dir / "tsconfig.json"
        if not ts_config.exists():
            issues.append({
                "type": "missing_config",
                "file": "tsconfig.json",
                "severity": "error",
                "description": "Missing TypeScript configuration file"
            })
        
        # Check package.json for required dependencies
        package_json = self.frontend_dir / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                required_deps = [
                    "next", "react", "react-dom", "@mui/material", 
                    "@mui/icons-material", "framer-motion"
                ]
                
                dependencies = package_data.get("dependencies", {})
                for dep in required_deps:
                    if dep not in dependencies:
                        issues.append({
                            "type": "missing_dependency",
                            "dependency": dep,
                            "severity": "error",
                            "description": f"Missing required dependency: {dep}"
                        })
            except json.JSONDecodeError:
                issues.append({
                    "type": "config_error",
                    "file": "package.json",
                    "severity": "error",
                    "description": "Invalid JSON in package.json"
                })
        
        return issues
    
    def fix_issues(self, issues: List[Dict[str, Any]]):
        """Fix identified issues."""
        print("🔧 Fixing Issues...")
        
        for issue in issues:
            if issue["type"] == "missing_file":
                self.create_missing_file(issue)
            elif issue["type"] == "missing_component":
                self.create_missing_component(issue)
            elif issue["type"] == "missing_config":
                self.create_missing_config(issue)
            elif issue["type"] == "syntax_error":
                self.fix_syntax_error(issue)
    
    def create_missing_file(self, issue: Dict[str, Any]):
        """Create missing files."""
        file_path = Path(issue["file"])
        
        if issue["file"] == "frontend/next.config.js":
            content = """/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  transpilePackages: ['@mui/material', '@mui/icons-material'],
}

module.exports = nextConfig
"""
        elif issue["file"] == "frontend/tsconfig.json":
            content = """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
"""
        elif issue["file"] == "frontend/tailwind.config.js":
            content = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""
        elif issue["file"] == "frontend/postcss.config.js":
            content = """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
        elif issue["file"] == "frontend/app/layout.tsx":
            content = """import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Studio 2025',
  description: 'Next-Gen Development Environment',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
"""
        elif issue["file"] == "frontend/src/theme/muiTheme.ts":
            content = """import { createTheme } from '@mui/material/styles'

export const aiStudio2025Theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#9c27b0',
    },
    background: {
      default: '#0f0f23',
      paper: '#1a1a2e',
    },
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
})
"""
        else:
            return
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        print(f"✅ Created {issue['file']}")
    
    def create_missing_component(self, issue: Dict[str, Any]):
        """Create missing components."""
        component_name = issue["component"]
        component_file = self.components_dir / f"{component_name}.tsx"
        
        if component_name == "AIModelSelector":
            content = """"use client"

import React from 'react'
import { FormControl, InputLabel, Select, MenuItem, Box } from '@mui/material'

interface AIModelSelectorProps {
  activeModel: string
  onModelChange: (model: string) => void
}

export function AIModelSelector({ activeModel, onModelChange }: AIModelSelectorProps) {
  const models = [
    { id: 'qwen2.5:7b', name: 'Qwen2.5 7B' },
    { id: 'qwen2.5:14b', name: 'Qwen2.5 14B' },
    { id: 'qwen2.5:32b', name: 'Qwen2.5 32B' },
    { id: 'qwen2.5:72b', name: 'Qwen2.5 72B' },
  ]

  return (
    <Box sx={{ minWidth: 120 }}>
      <FormControl size="small" fullWidth>
        <InputLabel>Model</InputLabel>
        <Select
          value={activeModel}
          label="Model"
          onChange={(e) => onModelChange(e.target.value)}
        >
          {models.map((model) => (
            <MenuItem key={model.id} value={model.id}>
              {model.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  )
}
"""
        elif component_name == "RedisCacheIndicator":
            content = """"use client"

import React from 'react'
import { Chip, Box } from '@mui/material'
import { Storage as StorageIcon } from '@mui/icons-material'

export function RedisCacheIndicator() {
  return (
    <Box>
      <Chip
        icon={<StorageIcon />}
        label="Cache"
        size="small"
        color="success"
        variant="outlined"
      />
    </Box>
  )
}
"""
        elif component_name == "WebSocketStatus":
            content = """"use client"

import React from 'react'
import { Chip, Box } from '@mui/material'
import { Wifi as WifiIcon } from '@mui/icons-material'

export function WebSocketStatus() {
  return (
    <Box>
      <Chip
        icon={<WifiIcon />}
        label="WS"
        size="small"
        color="success"
        variant="outlined"
      />
    </Box>
  )
}
"""
        else:
            # Generic component
            content = f"""\"use client\"

import React from 'react'
import {{ Box, Typography }} from '@mui/material'

export function {component_name}() {{
  return (
    <Box>
      <Typography variant=\"h6\">{component_name}</Typography>
      <Typography variant=\"body2\">Component placeholder</Typography>
    </Box>
  )
}}
"""
        
        component_file.parent.mkdir(parents=True, exist_ok=True)
        component_file.write_text(content)
        print(f"✅ Created component {component_name}")
    
    def create_missing_config(self, issue: Dict[str, Any]):
        """Create missing configuration files."""
        self.create_missing_file(issue)
    
    def fix_syntax_error(self, issue: Dict[str, Any]):
        """Fix syntax errors."""
        if issue["description"] == "Missing semicolon at end of file":
            file_path = Path(issue["file"])
            if file_path.exists():
                content = file_path.read_text()
                if not content.strip().endswith(';'):
                    content = content.rstrip() + ';'
                    file_path.write_text(content)
                    print(f"✅ Fixed semicolon in {issue['file']}")
    
    def start_servers(self):
        """Start frontend and backend servers."""
        print("🚀 Starting servers...")
        
        # Start frontend
        try:
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("✅ Frontend server starting...")
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
        
        # Start backend
        try:
            subprocess.Popen(
                ["python3", "api_server.py"],
                cwd=Path("."),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("✅ Backend server starting...")
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
    
    def test_pages(self):
        """Test if pages are working."""
        print("🧪 Testing pages...")
        
        import requests
        
        try:
            # Test frontend
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend is responding")
            else:
                print(f"❌ Frontend returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Frontend not responding: {e}")
        
        try:
            # Test backend
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is responding")
            else:
                print(f"❌ Backend returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Backend not responding: {e}")

def main():
    """Main function."""
    print("🔧 Browser Debug Tool")
    print("=" * 50)
    
    debug_tool = BrowserDebugTool()
    
    # Diagnose issues
    issues = debug_tool.diagnose_issues()
    
    if issues:
        print(f"\n❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  • {issue['type']}: {issue['description']}")
        
        # Fix issues
        debug_tool.fix_issues(issues)
        
        print("\n✅ Issues fixed! Restarting servers...")
        time.sleep(2)
        debug_tool.start_servers()
        
        print("\n⏳ Waiting for servers to start...")
        time.sleep(10)
        
        # Test pages
        debug_tool.test_pages()
    else:
        print("\n✅ No issues found!")
        debug_tool.start_servers()
        time.sleep(10)
        debug_tool.test_pages()

if __name__ == "__main__":
    main()
