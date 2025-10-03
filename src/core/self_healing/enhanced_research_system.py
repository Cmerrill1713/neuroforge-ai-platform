#!/usr/bin/env python3
"""
Enhanced Research System with Parallel Crawling and Knowledge Base Integration
"""

import asyncio
import aiohttp
import logging
import json
import re
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import weaviate
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

class EnhancedResearchSystem:
    """Enhanced research system with parallel crawling and knowledge base integration"""
    
    def __init__(self):
        self.session = None
        self.weaviate_client = None
        self.research_cache = {}
        self.knowledge_base_path = Path("knowledge_base")
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize connections to external services"""
        try:
            # Initialize Weaviate client
            self.weaviate_client = weaviate.Client("http://localhost:8090")
            logger.info("✅ Weaviate client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Weaviate client initialization failed: {e}")
        
        # Initialize session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
    
    async def research_error_solution(self, error_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Research error solution using parallel crawling and knowledge base integration"""
        start_time = datetime.now()
        logger.info(f"🔬 Starting enhanced research for: {error_message[:100]}...")
        
        # Check cache first
        cache_key = self._generate_cache_key(error_message)
        if cache_key in self.research_cache:
            cached_result = self.research_cache[cache_key]
            logger.info(f"📚 Found cached research result")
            return {
                **cached_result,
                "cached": True,
                "execution_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
        
        # Generate research queries
        research_queries = self._generate_research_queries(error_message, context)
        logger.info(f"🎯 Generated {len(research_queries)} research queries")
        
        # Execute parallel research
        research_tasks = []
        for query in research_queries:
            task = self._execute_research_query(query, error_message)
            research_tasks.append(task)
        
        # Wait for all research tasks to complete
        research_results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [r for r in research_results if isinstance(r, dict) and r.get("success")]
        logger.info(f"✅ Completed {len(successful_results)}/{len(research_tasks)} research tasks")
        
        # Aggregate and analyze results
        aggregated_result = self._aggregate_research_results(successful_results, error_message)
        
        # Deposit to knowledge base
        if aggregated_result.get("solution_found"):
            await self._deposit_to_knowledge_base(aggregated_result, error_message)
        
        # Cache result
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        aggregated_result.update({
            "cached": False,
            "execution_time_ms": execution_time,
            "research_tasks_completed": len(successful_results),
            "total_research_tasks": len(research_tasks)
        })
        
        self.research_cache[cache_key] = aggregated_result
        
        logger.info(f"🎉 Enhanced research completed in {execution_time:.2f}ms")
        return aggregated_result
    
    def _generate_research_queries(self, error_message: str, context: Dict[str, Any] = None) -> List[str]:
        """Generate diverse research queries for the error"""
        queries = []
        
        # Extract key terms from error
        error_terms = self._extract_error_terms(error_message)
        
        # Base queries
        base_queries = [
            f"{error_message} solution fix",
            f"python {error_terms.get('main_term', 'error')} troubleshooting",
            f"{error_terms.get('main_term', 'error')} stack overflow",
            f"{error_terms.get('main_term', 'error')} github issues",
            f"{error_terms.get('main_term', 'error')} documentation"
        ]
        
        # Add specific queries based on error type
        if "import" in error_message.lower():
            queries.extend([
                f"python import error {error_terms.get('main_term', '')}",
                f"module not found {error_terms.get('main_term', '')}",
                f"cannot import name {error_terms.get('main_term', '')}"
            ])
        
        if "attribute" in error_message.lower():
            queries.extend([
                f"python attribute error {error_terms.get('main_term', '')}",
                f"object has no attribute {error_terms.get('main_term', '')}"
            ])
        
        if "dimension" in error_message.lower():
            queries.extend([
                f"numpy dimension mismatch fix",
                f"matrix dimension error solution",
                f"embedding dimension mismatch"
            ])
        
        # Combine all queries
        all_queries = base_queries + queries
        
        # Remove duplicates and limit to top queries
        unique_queries = list(dict.fromkeys(all_queries))
        return unique_queries[:8]  # Limit to 8 parallel queries
    
    def _extract_error_terms(self, error_message: str) -> Dict[str, str]:
        """Extract key terms from error message"""
        terms = {}
        
        # Extract main term (usually after "cannot import name" or "object has no attribute")
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
        
        # Extract module/class names
        if "from" in error_message:
            match = re.search(r"from '([^']+)'", error_message)
            if match:
                terms["module"] = match.group(1)
        
        return terms
    
    async def _execute_research_query(self, query: str, original_error: str) -> Dict[str, Any]:
        """Execute a single research query using multiple sources"""
        try:
            # Execute parallel searches
            search_tasks = [
                self._web_search(query),
                self._github_search(query),
                self._stackoverflow_search(query),
                self._documentation_search(query)
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
                for result in all_results[:5]:  # Top 5 results
                    if result.get("url"):
                        crawl_tasks.append(self._crawl_url(result["url"], query))
                
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
            logger.error(f"Research query failed for '{query}': {e}")
            return {"success": False, "query": query, "error": str(e)}
    
    async def _web_search(self, query: str) -> Dict[str, Any]:
        """Perform web search using DuckDuckGo"""
        try:
            # Use DuckDuckGo search
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    for result in soup.find_all('a', class_='result__a')[:5]:
                        title = result.get_text(strip=True)
                        url = result.get('href', '')
                        if url and title:
                            results.append({
                                "title": title,
                                "url": url,
                                "source": "duckduckgo"
                            })
                    
                    return {"success": True, "results": results}
            
            return {"success": False, "error": f"HTTP {response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _github_search(self, query: str) -> Dict[str, Any]:
        """Search GitHub for issues and code"""
        try:
            # Search GitHub API for issues
            search_url = f"https://api.github.com/search/issues?q={query}+is:issue"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for issue in data.get("items", [])[:3]:
                        results.append({
                            "title": issue.get("title", ""),
                            "url": issue.get("html_url", ""),
                            "source": "github",
                            "body": issue.get("body", "")[:500] + "..." if len(issue.get("body", "")) > 500 else issue.get("body", "")
                        })
                    
                    return {"success": True, "results": results}
            
            return {"success": False, "error": f"HTTP {response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stackoverflow_search(self, query: str) -> Dict[str, Any]:
        """Search Stack Overflow"""
        try:
            # Use Stack Overflow search API
            search_url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={query}&site=stackoverflow"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get("items", [])[:3]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": f"https://stackoverflow.com/questions/{item.get('question_id')}",
                            "source": "stackoverflow",
                            "body": item.get("body", "")[:500] + "..." if len(item.get("body", "")) > 500 else item.get("body", "")
                        })
                    
                    return {"success": True, "results": results}
            
            return {"success": False, "error": f"HTTP {response.status}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _documentation_search(self, query: str) -> Dict[str, Any]:
        """Search official documentation"""
        try:
            # Search Python documentation and other official docs
            doc_urls = [
                f"https://docs.python.org/3/search.html?q={query}",
                f"https://numpy.org/doc/stable/search.html?q={query}",
                f"https://pandas.pydata.org/docs/search.html?q={query}"
            ]
            
            results = []
            for url in doc_urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract documentation links
                            for link in soup.find_all('a', href=True)[:2]:
                                href = link.get('href', '')
                                title = link.get_text(strip=True)
                                if href and title and ('search' not in href):
                                    results.append({
                                        "title": title,
                                        "url": href if href.startswith('http') else f"https://docs.python.org/3/{href}",
                                        "source": "documentation"
                                    })
                except Exception:
                    continue
            
            return {"success": True, "results": results[:3]}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _crawl_url(self, url: str, query: str) -> Dict[str, Any]:
        """Crawl a URL and extract relevant content"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Extract text content
                    text = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Find relevant sections
                    relevant_content = self._extract_relevant_content(clean_text, query)
                    
                    return {
                        "success": True,
                        "url": url,
                        "title": soup.title.string if soup.title else "No title",
                        "content": relevant_content[:2000] + "..." if len(relevant_content) > 2000 else relevant_content,
                        "full_content_length": len(clean_text),
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
        relevant_sentences = [sentence for _, sentence in scored_sentences[:10]]
        
        return " ".join(relevant_sentences)
    
    def _aggregate_research_results(self, research_results: List[Dict[str, Any]], original_error: str) -> Dict[str, Any]:
        """Aggregate research results into a comprehensive solution"""
        if not research_results:
            return {
                "solution_found": False,
                "confidence": 0.0,
                "solution_type": "none",
                "research_method": "enhanced_parallel",
                "details": "No research results found"
            }
        
        # Collect all crawled content
        all_content = []
        all_sources = []
        
        for result in research_results:
            all_sources.extend(result.get("search_results", []))
            all_content.extend(result.get("crawled_content", []))
        
        # Analyze content for solutions
        solution_analysis = self._analyze_content_for_solutions(all_content, original_error)
        
        # Generate solution
        solution = self._generate_solution_from_analysis(solution_analysis, original_error)
        
        return {
            "solution_found": solution["solution_found"],
            "confidence": solution["confidence"],
            "solution_type": solution["solution_type"],
            "research_method": "enhanced_parallel_crawling",
            "details": solution["details"],
            "fix_instructions": solution["fix_instructions"],
            "sources_analyzed": len(all_sources),
            "content_analyzed": len(all_content),
            "research_queries": len(research_results),
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_content_for_solutions(self, content_list: List[Dict[str, Any]], original_error: str) -> Dict[str, Any]:
        """Analyze crawled content for potential solutions"""
        solutions = []
        common_patterns = []
        
        for content in content_list:
            if not content.get("success"):
                continue
            
            text = content.get("content", "").lower()
            url = content.get("url", "")
            
            # Look for solution patterns
            if "solution" in text or "fix" in text or "resolve" in text:
                # Extract solution text
                solution_text = self._extract_solution_text(content.get("content", ""))
                if solution_text:
                    solutions.append({
                        "text": solution_text,
                        "source": url,
                        "relevance": self._calculate_relevance(text, original_error)
                    })
        
        # Find common patterns
        if solutions:
            common_patterns = self._find_common_patterns(solutions)
        
        return {
            "solutions": solutions,
            "common_patterns": common_patterns,
            "total_solutions": len(solutions)
        }
    
    def _extract_solution_text(self, content: str) -> str:
        """Extract solution text from content"""
        # Look for solution indicators
        solution_indicators = [
            "solution:", "fix:", "resolve:", "answer:", "workaround:",
            "try this:", "do this:", "here's how:", "the solution is:"
        ]
        
        for indicator in solution_indicators:
            if indicator in content.lower():
                # Extract text after indicator
                parts = content.lower().split(indicator)
                if len(parts) > 1:
                    solution_text = parts[1].strip()
                    # Take first few sentences
                    sentences = re.split(r'[.!?]+', solution_text)
                    return ". ".join(sentences[:3]).strip()
        
        return ""
    
    def _calculate_relevance(self, text: str, original_error: str) -> float:
        """Calculate relevance score between text and original error"""
        error_terms = original_error.lower().split()
        text_terms = text.split()
        
        # Count term matches
        matches = sum(1 for term in error_terms if term in text)
        total_terms = len(error_terms)
        
        return matches / total_terms if total_terms > 0 else 0.0
    
    def _find_common_patterns(self, solutions: List[Dict[str, Any]]) -> List[str]:
        """Find common patterns across solutions"""
        patterns = []
        
        # Look for common code patterns
        code_patterns = [
            r"pip install \w+",
            r"import \w+",
            r"from \w+ import \w+",
            r"\.\w+\(\)",
            r"try:.*?except:",
        ]
        
        for pattern in code_patterns:
            matches = 0
            for solution in solutions:
                if re.search(pattern, solution["text"], re.IGNORECASE):
                    matches += 1
            
            if matches >= 2:  # Pattern appears in at least 2 solutions
                patterns.append(pattern)
        
        return patterns
    
    def _generate_solution_from_analysis(self, analysis: Dict[str, Any], original_error: str) -> Dict[str, Any]:
        """Generate solution from analysis results"""
        solutions = analysis.get("solutions", [])
        common_patterns = analysis.get("common_patterns", [])
        
        if not solutions:
            return {
                "solution_found": False,
                "confidence": 0.0,
                "solution_type": "none",
                "details": "No solutions found in analyzed content",
                "fix_instructions": []
            }
        
        # Determine solution type based on error and solutions
        solution_type = self._determine_solution_type(original_error, solutions)
        
        # Generate fix instructions
        fix_instructions = self._generate_fix_instructions(solution_type, solutions, common_patterns)
        
        # Calculate confidence based on solution quality and consensus
        confidence = self._calculate_confidence(solutions, common_patterns)
        
        return {
            "solution_found": True,
            "confidence": confidence,
            "solution_type": solution_type,
            "details": f"Found {len(solutions)} potential solutions with {len(common_patterns)} common patterns",
            "fix_instructions": fix_instructions
        }
    
    def _determine_solution_type(self, original_error: str, solutions: List[Dict[str, Any]]) -> str:
        """Determine the type of solution needed"""
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
    
    def _generate_fix_instructions(self, solution_type: str, solutions: List[Dict[str, Any]], common_patterns: List[str]) -> List[str]:
        """Generate fix instructions based on solution type and patterns"""
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
                "Check the documentation for correct attribute names",
                "Ensure the object is properly initialized"
            ])
        elif solution_type == "dimension_fix":
            instructions.extend([
                "Check matrix/array dimensions before operations",
                "Use numpy reshape or transpose if needed",
                "Verify input data shapes match expected dimensions",
                "Clear cache if using cached embeddings with different models"
            ])
        
        # Add common patterns as instructions
        for pattern in common_patterns:
            if "pip install" in pattern:
                instructions.append("Install required packages using pip")
            elif "import" in pattern:
                instructions.append("Add necessary import statements")
            elif "try:" in pattern:
                instructions.append("Use try-except blocks for error handling")
        
        return list(dict.fromkeys(instructions))  # Remove duplicates
    
    def _calculate_confidence(self, solutions: List[Dict[str, Any]], common_patterns: List[str]) -> float:
        """Calculate confidence score based on solution quality and consensus"""
        if not solutions:
            return 0.0
        
        # Base confidence from number of solutions
        base_confidence = min(len(solutions) * 0.2, 0.6)
        
        # Bonus for common patterns
        pattern_bonus = len(common_patterns) * 0.1
        
        # Bonus for high relevance solutions
        relevance_bonus = sum(s.get("relevance", 0) for s in solutions) / len(solutions) * 0.2
        
        total_confidence = base_confidence + pattern_bonus + relevance_bonus
        return min(total_confidence, 0.95)  # Cap at 95%
    
    async def _deposit_to_knowledge_base(self, research_result: Dict[str, Any], original_error: str):
        """Deposit research results to the knowledge base"""
        try:
            if not self.weaviate_client:
                logger.warning("⚠️ Weaviate client not available, skipping knowledge base deposit")
                return
            
            # Prepare document for knowledge base
            document = {
                "content": f"Error: {original_error}\n\nSolution: {research_result.get('details', '')}\n\nFix Instructions: {'; '.join(research_result.get('fix_instructions', []))}",
                "title": f"Solution for: {original_error[:100]}",
                "url": "internal://research-system",
                "source_type": "research_solution",
                "domain": "error_resolution",
                "keywords": ["error", "solution", "fix", "troubleshooting"],
                "research_confidence": research_result.get("confidence", 0.0),
                "solution_type": research_result.get("solution_type", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to Weaviate
            collection = self.weaviate_client.collections.get("KnowledgeDocument")
            collection.data.insert(document)
            
            logger.info(f"✅ Research result deposited to knowledge base")
            
        except Exception as e:
            logger.error(f"❌ Failed to deposit to knowledge base: {e}")
    
    def _generate_cache_key(self, error_message: str) -> str:
        """Generate cache key for error message"""
        # Normalize error message for caching
        normalized = re.sub(r'\s+', ' ', error_message.lower().strip())
        # Take first 50 characters as key
        return normalized[:50]
    
    async def close(self):
        """Close connections"""
        if self.session:
            await self.session.close()
        if self.weaviate_client:
            self.weaviate_client.close()

# Global instance
enhanced_research_system = EnhancedResearchSystem()
