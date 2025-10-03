#!/usr/bin/env python3
"""
Parallel Research Crawler - Simplified parallel crawling for research system
"""

import asyncio
import aiohttp
import logging
import json
import re
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ParallelResearchCrawler:
    """Parallel research crawler for gathering real-time information"""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
        return self.session
    
    async def research_error_parallel(self, error_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Research error solution using parallel crawling"""
        start_time = datetime.now()
        logger.info(f"🔬 Starting parallel research for: {error_message[:100]}...")
        
        # Generate research queries
        research_queries = self._generate_research_queries(error_message)
        logger.info(f"🎯 Generated {len(research_queries)} research queries")
        
        # Execute parallel research tasks
        research_tasks = []
        for query in research_queries:
            task = self._execute_parallel_research(query, error_message)
            research_tasks.append(task)
        
        # Wait for all tasks to complete
        research_results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [r for r in research_results if isinstance(r, dict) and r.get("success")]
        logger.info(f"✅ Completed {len(successful_results)}/{len(research_tasks)} parallel research tasks")
        
        # Aggregate results
        aggregated_result = self._aggregate_parallel_results(successful_results, error_message)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        aggregated_result.update({
            "execution_time_ms": execution_time,
            "parallel_tasks_completed": len(successful_results),
            "total_parallel_tasks": len(research_tasks)
        })
        
        logger.info(f"🎉 Parallel research completed in {execution_time:.2f}ms")
        return aggregated_result
    
    def _generate_research_queries(self, error_message: str) -> List[str]:
        """Generate diverse research queries"""
        queries = []
        
        # Extract key terms
        error_terms = self._extract_error_terms(error_message)
        
        # Base queries
        base_queries = [
            f"{error_message} solution",
            f"{error_message} fix",
            f"python {error_terms.get('main_term', 'error')} troubleshooting"
        ]
        
        # Add specific queries based on error type
        if "import" in error_message.lower():
            queries.extend([
                f"python import error {error_terms.get('main_term', '')}",
                f"cannot import name {error_terms.get('main_term', '')}",
                f"module not found {error_terms.get('main_term', '')}"
            ])
        
        if "attribute" in error_message.lower():
            queries.extend([
                f"python attribute error {error_terms.get('main_term', '')}",
                f"object has no attribute {error_terms.get('main_term', '')}"
            ])
        
        if "dimension" in error_message.lower():
            queries.extend([
                f"numpy dimension mismatch fix",
                f"matrix dimension error solution"
            ])
        
        # Combine and deduplicate
        all_queries = base_queries + queries
        unique_queries = list(dict.fromkeys(all_queries))
        return unique_queries[:6]  # Limit to 6 parallel queries
    
    def _extract_error_terms(self, error_message: str) -> Dict[str, str]:
        """Extract key terms from error message"""
        terms = {}
        
        if "cannot import name" in error_message:
            match = re.search(r"cannot import name '([^']+)'", error_message)
            if match:
                terms["main_term"] = match.group(1)
        
        elif "object has no attribute" in error_message:
            match = re.search(r"object has no attribute '([^']+)'", error_message)
            if match:
                terms["main_term"] = match.group(1)
        
        elif "dimension" in error_message.lower():
            terms["main_term"] = "dimension_mismatch"
        
        return terms
    
    async def _execute_parallel_research(self, query: str, original_error: str) -> Dict[str, Any]:
        """Execute parallel research using multiple sources"""
        try:
            # Execute parallel searches
            search_tasks = [
                self._web_search_parallel(query),
                self._github_search_parallel(query),
                self._stackoverflow_search_parallel(query)
            ]
            
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Aggregate results
            all_results = []
            for result in search_results:
                if isinstance(result, dict) and result.get("success"):
                    all_results.extend(result.get("results", []))
            
            # Crawl top results in parallel
            if all_results:
                crawl_tasks = []
                for result in all_results[:3]:  # Top 3 results
                    if result.get("url"):
                        crawl_tasks.append(self._crawl_url_parallel(result["url"], query))
                
                if crawl_tasks:
                    crawl_results = await asyncio.gather(*crawl_tasks, return_exceptions=True)
                    crawled_content = [r for r in crawl_results if isinstance(r, dict) and r.get("success")]
                    
                    return {
                        "success": True,
                        "query": query,
                        "search_results": all_results,
                        "crawled_content": crawled_content,
                        "total_sources": len(all_results),
                        "crawled_sources": len(crawled_content)
                    }
            
            return {
                "success": True,
                "query": query,
                "search_results": all_results,
                "crawled_content": [],
                "total_sources": len(all_results),
                "crawled_sources": 0
            }
            
        except Exception as e:
            logger.error(f"Parallel research failed for '{query}': {e}")
            return {"success": False, "query": query, "error": str(e)}
    
    async def _web_search_parallel(self, query: str) -> Dict[str, Any]:
        """Perform web search using curl and grep"""
        try:
            # Use curl to search DuckDuckGo
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            
            session = await self._get_session()
            async with session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Simple parsing for results
                    results = []
                    # Look for result links (basic parsing)
                    import re
                    link_pattern = r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
                    matches = re.findall(link_pattern, html)
                    
                    for url, title in matches[:5]:
                        if url and title and not url.startswith('#') and 'duckduckgo.com' not in url:
                            results.append({
                                "title": title.strip(),
                                "url": url,
                                "source": "duckduckgo"
                            })
                    
                    return {"success": True, "results": results}
            
            return {"success": False, "error": f"HTTP {response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _github_search_parallel(self, query: str) -> Dict[str, Any]:
        """Search GitHub for issues"""
        try:
            # Search GitHub API
            search_url = f"https://api.github.com/search/issues?q={query}+is:issue"
            
            session = await self._get_session()
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for issue in data.get("items", [])[:3]:
                        results.append({
                            "title": issue.get("title", ""),
                            "url": issue.get("html_url", ""),
                            "source": "github",
                            "body": issue.get("body", "")[:300] + "..." if len(issue.get("body", "")) > 300 else issue.get("body", "")
                        })
                    
                    return {"success": True, "results": results}
            
            return {"success": False, "error": f"HTTP {response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stackoverflow_search_parallel(self, query: str) -> Dict[str, Any]:
        """Search Stack Overflow"""
        try:
            # Use Stack Overflow search
            search_url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={query}&site=stackoverflow"
            
            session = await self._get_session()
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get("items", [])[:3]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": f"https://stackoverflow.com/questions/{item.get('question_id')}",
                            "source": "stackoverflow",
                            "body": item.get("body", "")[:300] + "..." if len(item.get("body", "")) > 300 else item.get("body", "")
                        })
                    
                    return {"success": True, "results": results}
            
            return {"success": False, "error": f"HTTP {response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _crawl_url_parallel(self, url: str, query: str) -> Dict[str, Any]:
        """Crawl a URL and extract relevant content"""
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Simple text extraction
                    import re
                    # Remove HTML tags
                    text = re.sub(r'<[^>]+>', ' ', html)
                    # Clean up whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    # Find relevant sections
                    relevant_content = self._extract_relevant_content(text, query)
                    
                    return {
                        "success": True,
                        "url": url,
                        "title": "Crawled Content",
                        "content": relevant_content[:1500] + "..." if len(relevant_content) > 1500 else relevant_content,
                        "full_content_length": len(text),
                        "relevant_content_length": len(relevant_content)
                    }
                
                return {"success": False, "error": f"HTTP {response.status}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_relevant_content(self, text: str, query: str) -> str:
        """Extract content relevant to the query"""
        query_terms = query.lower().split()
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Score sentences based on query term matches
        scored_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = sum(1 for term in query_terms if term in sentence_lower)
            if score > 0:
                scored_sentences.append((score, sentence.strip()))
        
        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        relevant_sentences = [sentence for _, sentence in scored_sentences[:8]]
        
        return " ".join(relevant_sentences)
    
    def _aggregate_parallel_results(self, research_results: List[Dict[str, Any]], original_error: str) -> Dict[str, Any]:
        """Aggregate parallel research results"""
        if not research_results:
            return {
                "solution_found": False,
                "confidence": 0.0,
                "solution_type": "none",
                "research_method": "parallel_crawling",
                "details": "No research results found"
            }
        
        # Collect all content
        all_content = []
        all_sources = []
        
        for result in research_results:
            all_sources.extend(result.get("search_results", []))
            all_content.extend(result.get("crawled_content", []))
        
        # Analyze for solutions
        solution_analysis = self._analyze_content_for_solutions(all_content, original_error)
        
        # Generate solution
        solution = self._generate_solution_from_analysis(solution_analysis, original_error)
        
        return {
            "solution_found": solution["solution_found"],
            "confidence": solution["confidence"],
            "solution_type": solution["solution_type"],
            "research_method": "parallel_crawling",
            "details": solution["details"],
            "fix_instructions": solution["fix_instructions"],
            "sources_analyzed": len(all_sources),
            "content_analyzed": len(all_content),
            "research_queries": len(research_results)
        }
    
    def _analyze_content_for_solutions(self, content_list: List[Dict[str, Any]], original_error: str) -> Dict[str, Any]:
        """Analyze crawled content for solutions"""
        solutions = []
        
        for content in content_list:
            if not content.get("success"):
                continue
            
            text = content.get("content", "").lower()
            url = content.get("url", "")
            
            # Look for solution patterns
            if any(word in text for word in ["solution", "fix", "resolve", "answer"]):
                solution_text = self._extract_solution_text(content.get("content", ""))
                if solution_text:
                    solutions.append({
                        "text": solution_text,
                        "source": url,
                        "relevance": self._calculate_relevance(text, original_error)
                    })
        
        return {
            "solutions": solutions,
            "total_solutions": len(solutions)
        }
    
    def _extract_solution_text(self, content: str) -> str:
        """Extract solution text from content"""
        solution_indicators = ["solution:", "fix:", "resolve:", "answer:", "try this:"]
        
        for indicator in solution_indicators:
            if indicator in content.lower():
                parts = content.lower().split(indicator)
                if len(parts) > 1:
                    solution_text = parts[1].strip()
                    sentences = re.split(r'[.!?]+', solution_text)
                    return ". ".join(sentences[:3]).strip()
        
        return ""
    
    def _calculate_relevance(self, text: str, original_error: str) -> float:
        """Calculate relevance score"""
        error_terms = original_error.lower().split()
        text_terms = text.split()
        
        matches = sum(1 for term in error_terms if term in text)
        total_terms = len(error_terms)
        
        return matches / total_terms if total_terms > 0 else 0.0
    
    def _generate_solution_from_analysis(self, analysis: Dict[str, Any], original_error: str) -> Dict[str, Any]:
        """Generate solution from analysis"""
        solutions = analysis.get("solutions", [])
        
        if not solutions:
            return {
                "solution_found": False,
                "confidence": 0.0,
                "solution_type": "none",
                "details": "No solutions found",
                "fix_instructions": []
            }
        
        # Determine solution type
        solution_type = self._determine_solution_type(original_error, solutions)
        
        # Generate fix instructions
        fix_instructions = self._generate_fix_instructions(solution_type, solutions)
        
        # Calculate confidence
        confidence = self._calculate_confidence(solutions)
        
        return {
            "solution_found": True,
            "confidence": confidence,
            "solution_type": solution_type,
            "details": f"Found {len(solutions)} potential solutions through parallel crawling",
            "fix_instructions": fix_instructions
        }
    
    def _determine_solution_type(self, original_error: str, solutions: List[Dict[str, Any]]) -> str:
        """Determine solution type"""
        error_lower = original_error.lower()
        
        if "import" in error_lower:
            return "import_fix"
        elif "attribute" in error_lower:
            return "attribute_fix"
        elif "dimension" in error_lower:
            return "dimension_fix"
        elif "module" in error_lower:
            return "module_fix"
        else:
            return "general_fix"
    
    def _generate_fix_instructions(self, solution_type: str, solutions: List[Dict[str, Any]]) -> List[str]:
        """Generate fix instructions"""
        instructions = []
        
        if solution_type == "import_fix":
            instructions.extend([
                "Check if the module/class exists in the target package",
                "Verify the import path is correct",
                "Ensure the package is installed (pip install <package>)",
                "Check for typos in the import statement"
            ])
        elif solution_type == "attribute_fix":
            instructions.extend([
                "Check if the attribute exists on the object",
                "Verify the object type and available methods",
                "Check the documentation for correct attribute names"
            ])
        elif solution_type == "dimension_fix":
            instructions.extend([
                "Check matrix/array dimensions before operations",
                "Use numpy reshape or transpose if needed",
                "Verify input data shapes match expected dimensions"
            ])
        
        return instructions
    
    def _calculate_confidence(self, solutions: List[Dict[str, Any]]) -> float:
        """Calculate confidence score"""
        if not solutions:
            return 0.0
        
        # Base confidence from number of solutions
        base_confidence = min(len(solutions) * 0.2, 0.6)
        
        # Bonus for high relevance solutions
        relevance_bonus = sum(s.get("relevance", 0) for s in solutions) / len(solutions) * 0.3
        
        total_confidence = base_confidence + relevance_bonus
        return min(total_confidence, 0.9)  # Cap at 90%
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global instance
parallel_research_crawler = ParallelResearchCrawler()
