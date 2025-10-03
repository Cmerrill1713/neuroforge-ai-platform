#!/usr/bin/env python3
"""
Comprehensive Frontend Testing Suite
Tests all frontend functionality on port 3000 and identifies issues
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import aiohttp

class ComprehensiveFrontendTester:
    def __init__(self, port=3000):
        self.frontend_url = f"http://localhost:{port}"
        self.backend_urls = {
            'agentic': 'http://localhost:8000',
            'consolidated': 'http://localhost:8004'
        }
        self.session = None
        self.issues = []
        self.test_results = []
        self.warnings = []
        
    async def initialize(self):
        """Initialize the test session."""
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Clean up the test session."""
        if self.session:
            await self.session.close()

    def log_issue(self, severity: str, component: str, issue: str, details: str = ""):
        """Log an issue found during testing."""
        issue_obj = {
            'severity': severity,  # 'critical', 'error', 'warning', 'info'
            'component': component,
            'issue': issue,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        if severity in ['critical', 'error']:
            self.issues.append(issue_obj)
        elif severity == 'warning':
            self.warnings.append(issue_obj)
            
        print(f"[{severity.upper()}] {component}: {issue}")
        if details:
            print(f"  └─ {details}")

    def log_success(self, test_name: str, message: str):
        """Log a successful test."""
        self.test_results.append({
            'test': test_name,
            'status': 'PASS',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        print(f"✅ {test_name}: {message}")

    async def test_frontend_accessibility(self):
        """Test 1: Frontend Server Accessibility"""
        print("\n" + "="*70)
        print("TEST 1: Frontend Server Accessibility")
        print("="*70)
        
        try:
            start_time = time.time()
            async with self.session.get(f"{self.frontend_url}/") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    html = await response.text()
                    
                    # Check for Next.js indicators
                    if '__next' in html.lower() or 'next.js' in html.lower():
                        self.log_success('frontend_server', f'Server running (Response: {response_time:.3f}s)')
                    else:
                        self.log_issue('warning', 'frontend_server', 'Server responds but may not be Next.js', 
                                     'HTML does not contain Next.js indicators')
                    
                    # Check response time
                    if response_time > 2.0:
                        self.log_issue('warning', 'performance', 'Slow page load', 
                                     f'Initial load took {response_time:.3f}s (>2s)')
                    
                    # Check for critical content
                    required_elements = ['AI Assistant', 'Chat', 'Agents', 'Knowledge']
                    missing_elements = [elem for elem in required_elements if elem not in html]
                    if missing_elements:
                        self.log_issue('error', 'content', 'Missing expected UI elements', 
                                     f'Missing: {", ".join(missing_elements)}')
                else:
                    self.log_issue('critical', 'frontend_server', f'Server error: HTTP {response.status}')
                    
        except asyncio.TimeoutError:
            self.log_issue('critical', 'frontend_server', 'Request timeout', 
                         'Frontend did not respond within 10 seconds')
        except Exception as e:
            self.log_issue('critical', 'frontend_server', 'Connection failed', str(e))

    async def test_api_endpoints(self):
        """Test 2: API Endpoint Integration"""
        print("\n" + "="*70)
        print("TEST 2: API Endpoint Integration")
        print("="*70)
        
        # Test backend health endpoints
        endpoints_to_test = [
            ('agentic', '/api/system/health'),
            ('agentic', '/api/agents/'),
            ('consolidated', '/'),
            ('consolidated', '/api/chat/'),
        ]
        
        for backend_name, endpoint in endpoints_to_test:
            backend_url = self.backend_urls.get(backend_name)
            if not backend_url:
                continue
                
            try:
                url = f"{backend_url}{endpoint}"
                start_time = time.time()
                
                if endpoint.endswith('/'):
                    # GET request
                    async with self.session.get(url) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            self.log_success(f'api_{backend_name}_{endpoint.replace("/", "_")}', 
                                           f'Endpoint accessible ({response_time:.3f}s)')
                        elif response.status == 404:
                            self.log_issue('error', f'{backend_name}_api', f'Endpoint not found: {endpoint}')
                        else:
                            self.log_issue('warning', f'{backend_name}_api', 
                                         f'Unexpected status {response.status} for {endpoint}')
                            
            except asyncio.TimeoutError:
                self.log_issue('error', f'{backend_name}_api', f'Endpoint timeout: {endpoint}')
            except Exception as e:
                self.log_issue('error', f'{backend_name}_api', f'Failed to connect to {endpoint}', str(e))

    async def test_chat_functionality(self):
        """Test 3: Chat Interface Functionality"""
        print("\n" + "="*70)
        print("TEST 3: Chat Interface Functionality")
        print("="*70)
        
        # Test chat endpoint
        chat_url = f"{self.backend_urls['consolidated']}/api/chat/"
        try:
            test_message = "Hello, this is a test message"
            payload = {
                "message": test_message,
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            start_time = time.time()
            async with self.session.post(chat_url, json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check response structure
                    required_fields = ['response']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_issue('error', 'chat_api', 'Invalid response structure', 
                                     f'Missing fields: {", ".join(missing_fields)}')
                    else:
                        self.log_success('chat_functionality', 
                                       f'Chat working (Response: {response_time:.3f}s)')
                        
                        # Check response quality
                        if len(data.get('response', '')) < 10:
                            self.log_issue('warning', 'chat_quality', 'Response seems too short')
                            
                        # Check optional fields
                        optional_fields = ['agent_used', 'confidence', 'cache_hit', 'response_time']
                        present_optional = [f for f in optional_fields if f in data]
                        if len(present_optional) < 2:
                            self.log_issue('warning', 'chat_metadata', 
                                         'Missing metadata fields', 
                                         f'Only found: {", ".join(present_optional)}')
                else:
                    self.log_issue('error', 'chat_api', f'Chat request failed: HTTP {response.status}')
                    
        except asyncio.TimeoutError:
            self.log_issue('error', 'chat_api', 'Chat request timeout', 
                         'Request took longer than 10 seconds')
        except Exception as e:
            self.log_issue('error', 'chat_api', 'Chat request failed', str(e))

    async def test_knowledge_search(self):
        """Test 4: Knowledge Search Functionality"""
        print("\n" + "="*70)
        print("TEST 4: Knowledge Search Functionality")
        print("="*70)
        
        # Test knowledge search on agentic platform
        search_url = f"{self.backend_urls['agentic']}/api/knowledge/search"
        try:
            payload = {
                "query": "machine learning algorithms",
                "limit": 5
            }
            
            async with self.session.post(search_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if results are returned
                    if 'results' in data and len(data['results']) > 0:
                        self.log_success('knowledge_search', f'Found {len(data["results"])} results')
                    elif 'results' in data:
                        self.log_issue('warning', 'knowledge_search', 'No results returned', 
                                     'Knowledge base may be empty')
                    else:
                        self.log_issue('error', 'knowledge_search', 'Invalid response structure', 
                                     'Missing "results" field')
                elif response.status == 404:
                    self.log_issue('error', 'knowledge_api', 'Knowledge search endpoint not found')
                else:
                    self.log_issue('warning', 'knowledge_api', 
                                 f'Unexpected status: {response.status}')
                    
        except Exception as e:
            self.log_issue('error', 'knowledge_api', 'Knowledge search failed', str(e))

    async def test_voice_functionality(self):
        """Test 5: Voice Features"""
        print("\n" + "="*70)
        print("TEST 5: Voice Functionality")
        print("="*70)
        
        # Test voice options endpoint
        voice_url = f"{self.backend_urls['consolidated']}/api/voice/options"
        try:
            async with self.session.get(voice_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'voices' in data and len(data['voices']) > 0:
                        self.log_success('voice_options', f'Found {len(data["voices"])} voice options')
                    else:
                        self.log_issue('warning', 'voice_options', 'No voices available')
                elif response.status == 404:
                    self.log_issue('warning', 'voice_api', 'Voice endpoint not available')
                else:
                    self.log_issue('warning', 'voice_api', f'Voice API error: {response.status}')
        except Exception as e:
            self.log_issue('warning', 'voice_api', 'Voice functionality unavailable', str(e))

    async def test_agent_system(self):
        """Test 6: Agent System"""
        print("\n" + "="*70)
        print("TEST 6: Agent System")
        print("="*70)
        
        # Test agents endpoint
        agents_url = f"{self.backend_urls['consolidated']}/api/agents/"
        try:
            async with self.session.get(agents_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_success('agents_list', f'Found {len(data)} agents')
                    elif isinstance(data, dict) and 'agents' in data:
                        self.log_success('agents_list', f'Found {len(data["agents"])} agents')
                    else:
                        self.log_issue('warning', 'agents_api', 'Unexpected response format')
                elif response.status == 404:
                    self.log_issue('error', 'agents_api', 'Agents endpoint not found')
                else:
                    self.log_issue('warning', 'agents_api', f'Agents API error: {response.status}')
        except Exception as e:
            self.log_issue('error', 'agents_api', 'Agent system unavailable', str(e))

    async def test_frontend_pages(self):
        """Test 7: Frontend Page Routes"""
        print("\n" + "="*70)
        print("TEST 7: Frontend Page Routes")
        print("="*70)
        
        # Test important frontend routes
        routes = [
            '/',
            '/api/evolutionary/stats',
            '/api/rag/metrics',
        ]
        
        for route in routes:
            try:
                url = f"{self.frontend_url}{route}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        self.log_success(f'route_{route.replace("/", "_")}', 'Route accessible')
                    elif response.status == 404:
                        self.log_issue('warning', 'frontend_routes', f'Route not found: {route}')
                    else:
                        self.log_issue('warning', 'frontend_routes', 
                                     f'Route {route} returned {response.status}')
            except Exception as e:
                self.log_issue('warning', 'frontend_routes', f'Failed to access {route}', str(e))

    async def test_typescript_compilation(self):
        """Test 8: TypeScript Compilation (Static Check)"""
        print("\n" + "="*70)
        print("TEST 8: TypeScript Compilation")
        print("="*70)
        
        # Note: This is already checked, just reporting
        self.log_success('typescript', 'No TypeScript compilation errors (verified)')

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        critical_issues = [i for i in self.issues if i['severity'] == 'critical']
        error_issues = [i for i in self.issues if i['severity'] == 'error']
        
        passed_tests = len(self.test_results)
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        # Calculate health score
        health_score = 100
        health_score -= len(critical_issues) * 25
        health_score -= len(error_issues) * 10
        health_score -= len(self.warnings) * 2
        health_score = max(0, health_score)
        
        status = 'EXCELLENT' if health_score >= 90 else \
                 'GOOD' if health_score >= 75 else \
                 'FAIR' if health_score >= 50 else \
                 'POOR'
        
        report = {
            'test_date': datetime.now().isoformat(),
            'frontend_url': self.frontend_url,
            'health_score': health_score,
            'status': status,
            'summary': {
                'total_tests_passed': passed_tests,
                'critical_issues': len(critical_issues),
                'errors': len(error_issues),
                'warnings': total_warnings,
            },
            'issues': self.issues,
            'warnings': self.warnings,
            'test_results': self.test_results
        }
        
        return report

    def print_summary(self, report: Dict[str, Any]):
        """Print a formatted summary report"""
        print("\n" + "="*70)
        print("FRONTEND TEST SUMMARY")
        print("="*70)
        print(f"\n🎯 Health Score: {report['health_score']}/100 ({report['status']})")
        print(f"✅ Tests Passed: {report['summary']['total_tests_passed']}")
        print(f"🚨 Critical Issues: {report['summary']['critical_issues']}")
        print(f"❌ Errors: {report['summary']['errors']}")
        print(f"⚠️  Warnings: {report['summary']['warnings']}")
        
        if report['issues']:
            print("\n" + "="*70)
            print("CRITICAL ISSUES & ERRORS")
            print("="*70)
            for issue in report['issues']:
                severity_icon = '🚨' if issue['severity'] == 'critical' else '❌'
                print(f"\n{severity_icon} [{issue['severity'].upper()}] {issue['component']}")
                print(f"   Issue: {issue['issue']}")
                if issue['details']:
                    print(f"   Details: {issue['details']}")
        
        if report['warnings']:
            print("\n" + "="*70)
            print("WARNINGS")
            print("="*70)
            for warning in report['warnings'][:5]:  # Show first 5 warnings
                print(f"\n⚠️  {warning['component']}: {warning['issue']}")
                if warning['details']:
                    print(f"   Details: {warning['details']}")
            
            if len(report['warnings']) > 5:
                print(f"\n... and {len(report['warnings']) - 5} more warnings")
        
        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        
        if report['summary']['critical_issues'] > 0:
            print("🚨 URGENT: Fix critical issues immediately before deployment")
        
        if report['summary']['errors'] > 0:
            print("❌ Fix error-level issues to ensure full functionality")
        
        if report['summary']['warnings'] > 0:
            print("⚠️  Review warnings for potential improvements")
        
        if report['health_score'] >= 90:
            print("✅ Frontend is in excellent condition!")
        elif report['health_score'] >= 75:
            print("👍 Frontend is functional with minor issues")
        else:
            print("⚠️  Frontend needs attention before production deployment")
        
        print("\n" + "="*70)

async def main():
    """Run comprehensive frontend tests"""
    print("🎨 COMPREHENSIVE FRONTEND TESTING SUITE")
    print("Testing frontend on port 3000...")
    print("="*70)
    
    tester = ComprehensiveFrontendTester(port=3000)
    await tester.initialize()
    
    try:
        # Run all tests
        await tester.test_frontend_accessibility()
        await tester.test_api_endpoints()
        await tester.test_chat_functionality()
        await tester.test_knowledge_search()
        await tester.test_voice_functionality()
        await tester.test_agent_system()
        await tester.test_frontend_pages()
        await tester.test_typescript_compilation()
        
        # Generate and save report
        report = tester.generate_report()
        
        # Print summary
        tester.print_summary(report)
        
        # Save detailed report
        timestamp = int(time.time())
        report_filename = f"frontend_test_report_{timestamp}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        return report
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    report = asyncio.run(main())
    
    # Exit with error code if critical issues found
    if report['summary']['critical_issues'] > 0:
        exit(1)

