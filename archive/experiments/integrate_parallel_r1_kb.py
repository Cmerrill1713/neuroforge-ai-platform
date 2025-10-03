#!/usr/bin/env python3
""'
Simple knowledge base integration for Parallel-R1 paper
Creates a local knowledge base entry with metadata for retrieval
""'

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def create_knowledge_base_entry():
    """TODO: Add docstring."""
    """Create a knowledge base entry for the Parallel-R1 paper.""'

    print("📚 Creating knowledge base entry for Parallel-R1 paper')
    print("=' * 60)

    # Read the paper content
    paper_path = Path("knowledge_base/parallel_r1_paper.md')
    if not paper_path.exists():
        print(f"❌ Paper file not found: {paper_path}')
        return False

    with open(paper_path, "r", encoding="utf-8') as f:
        paper_content = f.read()

    # Create knowledge base entry
    entry = {
        "id": "parallel_r1_paper',
        "title": "Parallel-R1: Towards Parallel Thinking via Reinforcement Learning',
        "authors': [
            "Tong Zheng", "Hongming Zhang", "Wenhao Yu", "Xiaoyang Wang',
            "Runpeng Dai", "Rui Liu", "Huiwen Bao", "Chengsong Huang',
            "Heng Huang", "Dong Yu'
        ],
        "institutions': [
            "Tencent AI Lab Seattle',
            "University of Maryland, College Park',
            "University of North Carolina at Chapel Hill',
            "City University of Hong Kong',
            "Washington University in St. Louis'
        ],
        "source_url": "https://arxiv.org/pdf/2509.07980',
        "github_url": "https://github.com/zhengkid/Parallel-R1',
        "content': paper_content,
        "content_hash': hashlib.md5(paper_content.encode()).hexdigest(),
        "document_type": "research_paper',
        "domain": "artificial_intelligence',
        "subdomain": "reinforcement_learning',
        "keywords': [
            "parallel_thinking", "reinforcement_learning", "llm", "reasoning',
            "curriculum_learning", "progressive_training", "cold_start_problem',
            "multi_perspective_verification", "exploration_scaffold'
        ],
        "abstract": "Parallel thinking has emerged as a novel approach for enhancing the reasoning capabilities of large language models (LLMs) by exploring multiple reasoning paths concurrently. Parallel-R1 proposes the first reinforcement learning (RL) framework that enables parallel thinking behaviors for complex real-world reasoning tasks.',
        "key_findings': [
            "8.4% accuracy improvement over sequential thinking models',
            "42.9% improvement over baseline on AIME25',
            "Progressive curriculum addresses cold-start problem',
            "Behavioral shift from exploration to verification',
            "Parallel thinking as mid-training exploration scaffold'
        ],
        "technical_contributions': [
            "First RL framework for parallel thinking',
            "Progressive curriculum approach',
            "Cold-start problem solution',
            "Multi-perspective verification system',
            "Exploration scaffold methodology'
        ],
        "created_at': datetime.now(timezone.utc).isoformat(),
        "updated_at': datetime.now(timezone.utc).isoformat(),
        "status": "active',
        "retrieval_tags': [
            "parallel_thinking", "reinforcement_learning", "llm_training',
            "reasoning_enhancement", "curriculum_learning", "multi_agent',
            "exploration_strategy", "verification_system'
        ]
    }

    # Create knowledge base directory structure
    kb_dir = Path("knowledge_base')
    kb_dir.mkdir(exist_ok=True)

    # Save the entry
    entry_path = kb_dir / "parallel_r1_entry.json'
    with open(entry_path, "w", encoding="utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)

    print(f"✅ Knowledge base entry created: {entry_path}')

    # Create index entry
    index_entry = {
        "id": entry["id'],
        "title": entry["title'],
        "document_type": entry["document_type'],
        "domain": entry["domain'],
        "subdomain": entry["subdomain'],
        "keywords": entry["keywords'],
        "retrieval_tags": entry["retrieval_tags'],
        "created_at": entry["created_at'],
        "file_path': str(entry_path),
        "content_hash": entry["content_hash']
    }

    # Update or create index
    index_path = kb_dir / "index.json'
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8') as f:
            index = json.load(f)
    else:
        index = {"entries': []}

    # Add or update entry in index
    existing_entry = None
    for i, existing in enumerate(index["entries']):
        if existing["id"] == entry["id']:
            existing_entry = i
            break

    if existing_entry is not None:
        index["entries'][existing_entry] = index_entry
        print("📝 Updated existing entry in index')
    else:
        index["entries'].append(index_entry)
        print("📝 Added new entry to index')

    # Save index
    with open(index_path, "w", encoding="utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"✅ Index updated: {index_path}')

    # Create searchable text file for simple text search
    searchable_path = kb_dir / "parallel_r1_searchable.txt'
    searchable_content = f""'
TITLE: {entry["title']}
AUTHORS: {", ".join(entry["authors'])}
ABSTRACT: {entry["abstract']}
KEYWORDS: {", ".join(entry["keywords'])}
KEY FINDINGS: {"; ".join(entry["key_findings'])}
TECHNICAL CONTRIBUTIONS: {"; ".join(entry["technical_contributions'])}

CONTENT:
{paper_content}
""'

    with open(searchable_path, "w", encoding="utf-8') as f:
        f.write(searchable_content)

    print(f"✅ Searchable text file created: {searchable_path}')

    # Summary
    print(f"\n📊 Knowledge Base Integration Summary:')
    print(f"   Entry ID: {entry["id"]}')
    print(f"   Title: {entry["title"]}')
    print(f"   Keywords: {len(entry["keywords"])}')
    print(f"   Content Length: {len(paper_content)} characters')
    print(f"   Content Hash: {entry["content_hash"]}')
    print(f"   Created: {entry["created_at"]}')

    print(f"\n🎉 Parallel-R1 paper successfully added to knowledge base!')
    print(f"   The paper is now available for retrieval and search.')
    print(f"   Files created:')
    print(f"   - {entry_path}')
    print(f"   - {index_path}')
    print(f"   - {searchable_path}')

    return True

def verify_knowledge_base():
    """TODO: Add docstring."""
    """Verify the knowledge base entry was created correctly.""'

    print(f"\n🔍 Verifying knowledge base entry...')

    kb_dir = Path("knowledge_base')

    # Check if files exist
    entry_path = kb_dir / "parallel_r1_entry.json'
    index_path = kb_dir / "index.json'
    searchable_path = kb_dir / "parallel_r1_searchable.txt'

    files_exist = all(path.exists() for path in [entry_path, index_path, searchable_path])

    if files_exist:
        print("✅ All knowledge base files created successfully')

        # Load and verify entry
        with open(entry_path, "r", encoding="utf-8') as f:
            entry = json.load(f)

        print(f"   Entry ID: {entry["id"]}')
        print(f"   Title: {entry["title"]}')
        print(f"   Keywords: {len(entry["keywords"])}')
        print(f"   Content Hash: {entry["content_hash"]}')

        # Load and verify index
        with open(index_path, "r", encoding="utf-8') as f:
            index = json.load(f)

        print(f"   Index entries: {len(index["entries"])}')

        # Check searchable content
        with open(searchable_path, "r", encoding="utf-8') as f:
            searchable_content = f.read()

        print(f"   Searchable content length: {len(searchable_content)} characters')

        return True
    else:
        print("❌ Some knowledge base files are missing')
        return False

if __name__ == "__main__':
    success = create_knowledge_base_entry()

    if success:
        verify_knowledge_base()
        print(f"\n🎉 Parallel-R1 paper successfully integrated into knowledge base!')
    else:
        print(f"\n❌ Failed to integrate Parallel-R1 paper into knowledge base')
