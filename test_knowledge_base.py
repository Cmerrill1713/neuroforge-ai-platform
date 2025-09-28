#!/usr/bin/env python3
"""
Simple knowledge base retrieval system for Parallel-R1 paper
Demonstrates search and retrieval capabilities
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

class SimpleKnowledgeBase:
    """Simple knowledge base with text search capabilities."""
    
    def __init__(self, kb_dir: str = "knowledge_base"):
        self.kb_dir = Path(kb_dir)
        self.index_path = self.kb_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the knowledge base index."""
        if self.index_path.exists():
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": []}
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant entries."""
        results = []
        query_lower = query.lower()
        
        for entry in self.index["entries"]:
            score = 0
            
            # Score based on title match
            if query_lower in entry["title"].lower():
                score += 10
            
            # Score based on keyword match
            for keyword in entry["keywords"]:
                if query_lower in keyword.lower():
                    score += 5
            
            # Score based on retrieval tags
            for tag in entry["retrieval_tags"]:
                if query_lower in tag.lower():
                    score += 3
            
            # Score based on domain/subdomain
            if query_lower in entry.get("domain", "").lower():
                score += 2
            if query_lower in entry.get("subdomain", "").lower():
                score += 2
            
            if score > 0:
                results.append({
                    "entry": entry,
                    "score": score
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def get_entry(self, entry_id: str) -> Dict[str, Any]:
        """Get a specific entry by ID."""
        # Try different naming patterns
        possible_paths = [
            self.kb_dir / f"{entry_id}_entry.json",
            self.kb_dir / f"{entry_id}.json",
            self.kb_dir / f"{entry_id}_paper.json",
            self.kb_dir / "parallel_r1_entry.json"  # Direct path for our specific case
        ]
        
        for entry_path in possible_paths:
            if entry_path.exists():
                with open(entry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Verify this is the right entry
                    if data.get("id") == entry_id:
                        return data
        return None
    
    def search_content(self, query: str, entry_id: str = None) -> List[Dict[str, Any]]:
        """Search within entry content."""
        results = []
        query_lower = query.lower()
        
        # If specific entry requested, search only that entry
        if entry_id:
            entry = self.get_entry(entry_id)
            if entry:
                content = entry.get("content", "")
                if query_lower in content.lower():
                    # Find context around matches
                    matches = self._find_context_matches(content, query_lower)
                    results.extend(matches)
        else:
            # Search all entries
            for index_entry in self.index["entries"]:
                entry = self.get_entry(index_entry["id"])
                if entry:
                    content = entry.get("content", "")
                    if query_lower in content.lower():
                        matches = self._find_context_matches(content, query_lower)
                        for match in matches:
                            match["entry_id"] = index_entry["id"]
                            match["entry_title"] = index_entry["title"]
                        results.extend(matches)
                
                # Also search the searchable text file
                searchable_path = self.kb_dir / f"{index_entry['id']}_searchable.txt"
                if searchable_path.exists():
                    with open(searchable_path, 'r', encoding='utf-8') as f:
                        searchable_content = f.read()
                    if query_lower in searchable_content.lower():
                        matches = self._find_context_matches(searchable_content, query_lower)
                        for match in matches:
                            match["entry_id"] = index_entry["id"]
                            match["entry_title"] = index_entry["title"]
                            match["source"] = "searchable_text"
                        results.extend(matches)
        
        return results
    
    def _find_context_matches(self, content: str, query: str, context_size: int = 200) -> List[Dict[str, Any]]:
        """Find matches with surrounding context."""
        matches = []
        content_lower = content.lower()
        
        start = 0
        while True:
            pos = content_lower.find(query, start)
            if pos == -1:
                break
            
            # Extract context around match
            context_start = max(0, pos - context_size)
            context_end = min(len(content), pos + len(query) + context_size)
            context = content[context_start:context_end]
            
            # Highlight the match
            highlighted_context = context.replace(
                content[pos:pos + len(query)],
                f"**{content[pos:pos + len(query)]}**"
            )
            
            matches.append({
                "context": highlighted_context,
                "position": pos,
                "query": query
            })
            
            start = pos + 1
        
        return matches

def demonstrate_knowledge_base():
    """Demonstrate knowledge base search capabilities."""
    
    print("🔍 Knowledge Base Search Demonstration")
    print("=" * 50)
    
    # Initialize knowledge base
    kb = SimpleKnowledgeBase()
    
    # Test queries
    test_queries = [
        "parallel thinking",
        "reinforcement learning",
        "curriculum learning",
        "cold start problem",
        "multi-perspective verification",
        "exploration scaffold",
        "AIME25",
        "8.4% improvement"
    ]
    
    print(f"📚 Knowledge Base Status:")
    print(f"   Total entries: {len(kb.index['entries'])}")
    
    for entry in kb.index["entries"]:
        print(f"   - {entry['title']} ({entry['id']})")
    
    print(f"\n🔍 Testing search queries:")
    
    for query in test_queries:
        print(f"\n--- Query: '{query}' ---")
        
        # Search entries
        results = kb.search(query)
        if results:
            print(f"   Found {len(results)} relevant entries:")
            for result in results:
                entry = result["entry"]
                print(f"   - {entry['title']} (score: {result['score']})")
        else:
            print(f"   No relevant entries found")
        
        # Search content
        content_results = kb.search_content(query)
        if content_results:
            print(f"   Found {len(content_results)} content matches:")
            for i, match in enumerate(content_results[:2], 1):  # Show first 2 matches
                print(f"   {i}. {match['context'][:100]}...")
        else:
            print(f"   No content matches found")
    
    # Test specific entry retrieval
    print(f"\n📖 Testing specific entry retrieval:")
    entry = kb.get_entry("parallel_r1_paper")
    if entry:
        print(f"   ✅ Retrieved entry: {entry['title']}")
        print(f"   Authors: {', '.join(entry['authors'][:3])}...")
        print(f"   Keywords: {', '.join(entry['keywords'][:5])}...")
        print(f"   Content length: {len(entry['content'])} characters")
    else:
        print(f"   ❌ Failed to retrieve entry")

if __name__ == "__main__":
    demonstrate_knowledge_base()
    
    print(f"\n🎉 Knowledge base demonstration completed!")
    print(f"   The Parallel-R1 paper is now searchable and retrievable.")
    print(f"   You can use this system to find relevant information.")
