#!/usr/bin/env python3
"""
MUI Patterns Scraper MCP Server
Scrapes Material-UI documentation and patterns, stores in Supabase
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import httpx
from datetime import datetime
import os
from supabase import create_client, Client

# Supabase configuration for Docker instance
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://localhost:54321")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0")

class MUIPatternsScraper:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.setup_supabase()
        
    def setup_supabase(self):
        """Initialize Supabase client"""
        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase client initialized", file=sys.stderr)
        except Exception as e:
            print(f"❌ Supabase setup failed: {e}", file=sys.stderr)
    
    async def scrape_mui_docs(self, component: str = "all") -> Dict[str, Any]:
        """Scrape Material-UI documentation for patterns"""
        patterns = {
            "component": component,
            "timestamp": datetime.now().isoformat(),
            "patterns": [],
            "examples": [],
            "best_practices": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Scrape main MUI docs
                urls = [
                    "https://mui.com/material-ui/getting-started/",
                    "https://mui.com/material-ui/components/",
                    f"https://mui.com/material-ui/react-{component}/" if component != "all" else None
                ]
                
                for url in urls:
                    if url:
                        response = await client.get(url)
                        if response.status_code == 200:
                            content = response.text
                            patterns["patterns"].extend(self.extract_patterns(content))
                            patterns["examples"].extend(self.extract_examples(content))
                            patterns["best_practices"].extend(self.extract_best_practices(content))
                            
        except Exception as e:
            print(f"❌ Scraping error: {e}", file=sys.stderr)
            
        return patterns
    
    def extract_patterns(self, html_content: str) -> List[Dict]:
        """Extract design patterns from HTML content"""
        patterns = []
        # Simple pattern extraction (in real implementation, use BeautifulSoup)
        if "chat" in html_content.lower():
            patterns.append({
                "type": "chat_interface",
                "description": "Material-UI chat interface pattern",
                "components": ["Card", "TextField", "IconButton", "Avatar"],
                "layout": "vertical_stack"
            })
        return patterns
    
    def extract_examples(self, html_content: str) -> List[Dict]:
        """Extract code examples from HTML content"""
        examples = []
        # Extract code examples (simplified)
        if "TextField" in html_content:
            examples.append({
                "component": "TextField",
                "code": '<TextField label="Outlined" variant="outlined" />',
                "description": "Basic TextField example"
            })
        return examples
    
    def extract_best_practices(self, html_content: str) -> List[Dict]:
        """Extract best practices from HTML content"""
        practices = []
        if "accessibility" in html_content.lower():
            practices.append({
                "category": "accessibility",
                "practice": "Use proper ARIA labels",
                "description": "Ensure all interactive elements have proper accessibility labels"
            })
        return practices
    
    async def store_patterns(self, patterns: Dict[str, Any]) -> bool:
        """Store patterns in Supabase using existing agent_communication_patterns table"""
        if not self.supabase:
            return False
            
        try:
            # Convert MUI patterns to agent communication pattern format
            mui_pattern = {
                "pattern_name": f"mui_{patterns['component']}_pattern",
                "from_agent_type": "ui_designer",
                "to_agent_type": "frontend_developer", 
                "message_type": "design_pattern",
                "pattern_schema": {
                    "type": "object",
                    "properties": {
                        "component": {"type": "string"},
                        "patterns": {"type": "array"},
                        "examples": {"type": "array"},
                        "best_practices": {"type": "array"},
                        "timestamp": {"type": "string"}
                    }
                },
                "description": f"Material-UI patterns for {patterns['component']} component",
                "usage_count": 0
            }
            
            result = self.supabase.table("agent_communication_patterns").insert(mui_pattern).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"❌ Storage error: {e}", file=sys.stderr)
            return False
    
    async def get_stored_patterns(self, component: str = None) -> List[Dict]:
        """Retrieve stored patterns from Supabase"""
        if not self.supabase:
            return []
            
        try:
            query = self.supabase.table("agent_communication_patterns").select("*")
            query = query.eq("from_agent_type", "ui_designer")
            query = query.eq("message_type", "design_pattern")
            
            if component:
                query = query.like("pattern_name", f"mui_{component}_pattern")
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"❌ Retrieval error: {e}", file=sys.stderr)
            return []

async def main():
    """Main MCP server loop"""
    scraper = MUIPatternsScraper()
    
    while True:
        try:
            # Read MCP request
            request = json.loads(sys.stdin.readline())
            
            if request.get("method") == "scrape_mui_patterns":
                component = request.get("params", {}).get("component", "all")
                patterns = await scraper.scrape_mui_docs(component)
                stored = await scraper.store_patterns(patterns)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "patterns": patterns,
                        "stored": stored
                    }
                }
                
            elif request.get("method") == "get_mui_patterns":
                component = request.get("params", {}).get("component")
                patterns = await scraper.get_stored_patterns(component)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"patterns": patterns}
                }
                
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
