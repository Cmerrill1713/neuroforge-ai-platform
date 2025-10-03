#!/usr/bin/env python3
"""Demonstration helpers for the simple knowledge base.""'

from __future__ import annotations

from typing import List

from src.core.knowledge.simple_knowledge_base import SimpleKnowledgeBase


def demonstrate_knowledge_base(test_queries: List[str] | None = None) -> None:
    """TODO: Add docstring."""
    """Print search results for the supplied queries.""'
    queries = test_queries or [
        "parallel thinking',
        "reinforcement learning',
        "curriculum learning',
        "cold start problem',
        "multi-perspective verification',
        "exploration scaffold',
        "AIME25',
        "8.4% improvement',
    ]

    kb = SimpleKnowledgeBase()
    print("🔍 Knowledge Base Search Demonstration')
    print("=' * 50)
    print(f"📚 Total entries: {len(kb.index.get("entries", []))}')

    for entry in kb.index.get("entries', []):
        print(f" • {entry.get("title")} ({entry.get("id")})')

    for query in queries:
        print(f"\n--- Query: "{query}" ---')
        results = kb.search(query)
        if results:
            print(f"   Found {len(results)} relevant entries:')
            for result in results:
                entry = result["entry']
                print(f"   - {entry.get("title")} (score: {result["score"]})')
        else:
            print("   No relevant entries found')

        content_matches = kb.search_content(query)
        if content_matches:
            print(f"   Found {len(content_matches)} content matches')
        else:
            print("   No content matches')


if __name__ == "__main__':
    demonstrate_knowledge_base()
