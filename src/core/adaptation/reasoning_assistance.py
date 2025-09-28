#!/usr/bin/env python3
"""
Reasoning Assistance System for Smaller Models
Provides structured reasoning frameworks to help smaller models think better
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import re

logger = logging.getLogger(__name__)

class ReasoningDomain(str, Enum):
    """Domains where reasoning assistance is needed"""
    PROGRAMMING = "programming"
    MATHEMATICS = "mathematics"
    LOGIC = "logic"
    PROBLEM_SOLVING = "problem_solving"
    ANALYSIS = "analysis"
    DECISION_MAKING = "decision_making"

class ReasoningStep(str, Enum):
    """Steps in the reasoning process"""
    UNDERSTAND = "understand"
    ANALYZE = "analyze"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    REFLECT = "reflect"

@dataclass
class ReasoningFramework:
    """Framework for structured reasoning"""
    domain: ReasoningDomain
    steps: List[ReasoningStep]
    templates: Dict[str, str]
    examples: List[str]
    validation_criteria: List[str]

@dataclass
class ReasoningAssistance:
    """Assistance provided for reasoning"""
    framework: ReasoningFramework
    step_by_step_guide: List[str]
    examples: List[str]
    validation_questions: List[str]
    common_pitfalls: List[str]
    success_indicators: List[str]

@dataclass
class ReasoningResult:
    """Result of reasoning assistance"""
    original_problem: str
    structured_solution: str
    reasoning_steps: List[str]
    validation_passed: bool
    confidence_score: float
    improvement_suggestions: List[str]

class ReasoningAssistanceSystem:
    """
    System that provides reasoning assistance to smaller models
    """
    
    def __init__(self):
        self.reasoning_frameworks = self._initialize_reasoning_frameworks()
        self.domain_templates = self._initialize_domain_templates()
        self.common_pitfalls = self._initialize_common_pitfalls()
        self.validation_patterns = self._initialize_validation_patterns()
        
        logger.info("🧠 Reasoning Assistance System initialized")
    
    def _initialize_reasoning_frameworks(self) -> Dict[ReasoningDomain, ReasoningFramework]:
        """Initialize reasoning frameworks for different domains"""
        return {
            ReasoningDomain.PROGRAMMING: ReasoningFramework(
                domain=ReasoningDomain.PROGRAMMING,
                steps=[
                    ReasoningStep.UNDERSTAND,
                    ReasoningStep.ANALYZE,
                    ReasoningStep.PLAN,
                    ReasoningStep.EXECUTE,
                    ReasoningStep.VERIFY
                ],
                templates={
                    "understand": "What is the problem asking me to do? What are the inputs and expected outputs?",
                    "analyze": "What are the key requirements? What constraints do I need to consider?",
                    "plan": "What approach should I take? What data structures or algorithms are needed?",
                    "execute": "Let me implement the solution step by step.",
                    "verify": "Does my solution work correctly? Have I tested edge cases?"
                },
                examples=[
                    "Example: To sort a list, I need to compare elements and swap them if they're in wrong order",
                    "Example: To find maximum, I keep track of the largest value I've seen so far",
                    "Example: To validate input, I check if it meets the required format and range"
                ],
                validation_criteria=[
                    "Does the code handle edge cases?",
                    "Is the algorithm efficient?",
                    "Are variable names clear?",
                    "Is the logic correct?"
                ]
            ),
            
            ReasoningDomain.MATHEMATICS: ReasoningFramework(
                domain=ReasoningDomain.MATHEMATICS,
                steps=[
                    ReasoningStep.UNDERSTAND,
                    ReasoningStep.ANALYZE,
                    ReasoningStep.PLAN,
                    ReasoningStep.EXECUTE,
                    ReasoningStep.VERIFY
                ],
                templates={
                    "understand": "What mathematical concept is this asking about? What are the given values?",
                    "analyze": "What formula or method should I use? What are the relationships between variables?",
                    "plan": "What steps do I need to take? What calculations are required?",
                    "execute": "Let me work through the calculations step by step.",
                    "verify": "Does my answer make sense? Can I check it another way?"
                },
                examples=[
                    "Example: To solve 2x + 5 = 13, I subtract 5 from both sides, then divide by 2",
                    "Example: To find area of rectangle, I multiply length by width",
                    "Example: To convert units, I multiply by the appropriate conversion factor"
                ],
                validation_criteria=[
                    "Is the formula correct?",
                    "Are the calculations accurate?",
                    "Does the answer have the right units?",
                    "Is the answer reasonable?"
                ]
            ),
            
            ReasoningDomain.LOGIC: ReasoningFramework(
                domain=ReasoningDomain.LOGIC,
                steps=[
                    ReasoningStep.UNDERSTAND,
                    ReasoningStep.ANALYZE,
                    ReasoningStep.PLAN,
                    ReasoningStep.EXECUTE,
                    ReasoningStep.VERIFY,
                    ReasoningStep.REFLECT
                ],
                templates={
                    "understand": "What is the logical statement? What are the premises and conclusion?",
                    "analyze": "What type of logical argument is this? What rules apply?",
                    "plan": "How can I prove or disprove this? What logical steps are needed?",
                    "execute": "Let me work through the logical reasoning step by step.",
                    "verify": "Is each step logically valid? Does the conclusion follow?",
                    "reflect": "Are there any logical fallacies? Is the reasoning sound?"
                },
                examples=[
                    "Example: If A implies B, and B implies C, then A implies C (transitive property)",
                    "Example: If all birds can fly, and penguins are birds, then penguins can fly (but this is false)",
                    "Example: To prove by contradiction, assume the opposite and show it leads to a contradiction"
                ],
                validation_criteria=[
                    "Is each premise true?",
                    "Does the conclusion follow logically?",
                    "Are there any logical fallacies?",
                    "Is the reasoning valid?"
                ]
            ),
            
            ReasoningDomain.PROBLEM_SOLVING: ReasoningFramework(
                domain=ReasoningDomain.PROBLEM_SOLVING,
                steps=[
                    ReasoningStep.UNDERSTAND,
                    ReasoningStep.ANALYZE,
                    ReasoningStep.PLAN,
                    ReasoningStep.EXECUTE,
                    ReasoningStep.VERIFY,
                    ReasoningStep.REFLECT
                ],
                templates={
                    "understand": "What is the core problem? What are the constraints and requirements?",
                    "analyze": "What are the key factors? What information do I have and need?",
                    "plan": "What approach should I take? What are the possible solutions?",
                    "execute": "Let me implement my chosen solution step by step.",
                    "verify": "Does my solution work? Have I considered all requirements?",
                    "reflect": "Could I have solved this better? What did I learn?"
                },
                examples=[
                    "Example: To organize a party, I need to consider venue, food, guests, and budget",
                    "Example: To fix a bug, I need to reproduce it, find the cause, and test the fix",
                    "Example: To learn a new skill, I break it into smaller, manageable steps"
                ],
                validation_criteria=[
                    "Does the solution address all requirements?",
                    "Is the approach efficient?",
                    "Have I considered alternatives?",
                    "Is the solution practical?"
                ]
            )
        }
    
    def _initialize_domain_templates(self) -> Dict[str, str]:
        """Initialize templates for different domains"""
        return {
            "programming": """
PROGRAMMING REASONING FRAMEWORK:

1. UNDERSTAND THE PROBLEM:
   - What is the task asking me to do?
   - What are the inputs and expected outputs?
   - What are the constraints and requirements?

2. ANALYZE THE REQUIREMENTS:
   - What data structures do I need?
   - What algorithms are appropriate?
   - What edge cases should I consider?

3. PLAN THE SOLUTION:
   - What approach will I take?
   - What steps are involved?
   - How will I handle errors?

4. IMPLEMENT STEP BY STEP:
   - Write the code incrementally
   - Test each part as I go
   - Use clear variable names

5. VERIFY THE SOLUTION:
   - Does it work for normal cases?
   - Does it handle edge cases?
   - Is the code readable and efficient?
""",
            "mathematics": """
MATHEMATICAL REASONING FRAMEWORK:

1. UNDERSTAND THE PROBLEM:
   - What is the question asking?
   - What information is given?
   - What do I need to find?

2. ANALYZE THE CONCEPT:
   - What mathematical concept applies?
   - What formula or method should I use?
   - What are the relationships between variables?

3. PLAN THE SOLUTION:
   - What steps do I need to take?
   - What calculations are required?
   - What order should I do them in?

4. EXECUTE THE CALCULATIONS:
   - Work through each step carefully
   - Show all your work
   - Check calculations as you go

5. VERIFY THE ANSWER:
   - Does the answer make sense?
   - Can I check it another way?
   - Are the units correct?
""",
            "logic": """
LOGICAL REASONING FRAMEWORK:

1. UNDERSTAND THE ARGUMENT:
   - What are the premises?
   - What is the conclusion?
   - What type of argument is this?

2. ANALYZE THE LOGIC:
   - What logical rules apply?
   - Is this deductive or inductive?
   - What are the logical relationships?

3. PLAN THE REASONING:
   - How can I prove or disprove this?
   - What logical steps are needed?
   - What evidence supports this?

4. EXECUTE THE REASONING:
   - Work through each logical step
   - Ensure each step follows logically
   - Check for logical validity

5. VERIFY THE CONCLUSION:
   - Does the conclusion follow?
   - Are there any logical fallacies?
   - Is the reasoning sound?

6. REFLECT ON THE PROCESS:
   - Are there alternative approaches?
   - What assumptions did I make?
   - Is the conclusion reliable?
"""
        }
    
    def _initialize_common_pitfalls(self) -> Dict[ReasoningDomain, List[str]]:
        """Initialize common pitfalls for each domain"""
        return {
            ReasoningDomain.PROGRAMMING: [
                "Not considering edge cases (empty input, null values)",
                "Using inefficient algorithms when better ones exist",
                "Not handling errors or exceptions properly",
                "Writing code without understanding the problem first",
                "Not testing the solution thoroughly"
            ],
            ReasoningDomain.MATHEMATICS: [
                "Using the wrong formula or method",
                "Making calculation errors",
                "Not checking if the answer makes sense",
                "Forgetting to include units in the answer",
                "Not showing work clearly"
            ],
            ReasoningDomain.LOGIC: [
                "Making logical fallacies (circular reasoning, false premises)",
                "Not considering alternative explanations",
                "Confusing correlation with causation",
                "Making assumptions without stating them",
                "Not verifying each logical step"
            ],
            ReasoningDomain.PROBLEM_SOLVING: [
                "Jumping to solutions without understanding the problem",
                "Not considering multiple approaches",
                "Not breaking complex problems into smaller parts",
                "Not verifying the solution works",
                "Not learning from mistakes"
            ]
        }
    
    def _initialize_validation_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for validating reasoning"""
        return {
            "completeness": [
                "Have I addressed all parts of the problem?",
                "Have I considered all requirements?",
                "Have I checked all edge cases?"
            ],
            "accuracy": [
                "Is my solution correct?",
                "Are my calculations accurate?",
                "Is my logic sound?"
            ],
            "efficiency": [
                "Is this the best approach?",
                "Can I solve this more efficiently?",
                "Are there unnecessary steps?"
            ],
            "clarity": [
                "Is my reasoning clear?",
                "Can someone else follow my steps?",
                "Are my explanations understandable?"
            ]
        }
    
    def provide_reasoning_assistance(self, 
                                   problem: str, 
                                   domain: ReasoningDomain,
                                   model_capability: str = "small") -> ReasoningAssistance:
        """Provide reasoning assistance for a specific problem and domain"""
        
        logger.info(f"🧠 Providing reasoning assistance for {domain.value} problem")
        
        framework = self.reasoning_frameworks[domain]
        
        # Generate step-by-step guide
        step_by_step_guide = []
        for step in framework.steps:
            template = framework.templates.get(step.value, "")
            if template:
                step_by_step_guide.append(f"{step.value.upper()}: {template}")
        
        # Get domain-specific examples
        examples = framework.examples
        
        # Generate validation questions
        validation_questions = framework.validation_criteria
        
        # Get common pitfalls
        common_pitfalls = self.common_pitfalls.get(domain, [])
        
        # Generate success indicators
        success_indicators = self._generate_success_indicators(domain)
        
        return ReasoningAssistance(
            framework=framework,
            step_by_step_guide=step_by_step_guide,
            examples=examples,
            validation_questions=validation_questions,
            common_pitfalls=common_pitfalls,
            success_indicators=success_indicators
        )
    
    def _generate_success_indicators(self, domain: ReasoningDomain) -> List[str]:
        """Generate success indicators for a domain"""
        
        indicators = {
            ReasoningDomain.PROGRAMMING: [
                "Code compiles and runs without errors",
                "Handles edge cases correctly",
                "Uses appropriate data structures",
                "Has clear variable names and comments",
                "Passes all test cases"
            ],
            ReasoningDomain.MATHEMATICS: [
                "Uses correct formulas and methods",
                "Shows all work clearly",
                "Gets the right answer",
                "Includes correct units",
                "Answer makes logical sense"
            ],
            ReasoningDomain.LOGIC: [
                "Premises are clearly stated",
                "Each step follows logically",
                "No logical fallacies",
                "Conclusion follows from premises",
                "Reasoning is sound and valid"
            ],
            ReasoningDomain.PROBLEM_SOLVING: [
                "Problem is clearly understood",
                "Solution addresses all requirements",
                "Approach is systematic",
                "Solution is practical and efficient",
                "Results are verified"
            ]
        }
        
        return indicators.get(domain, [])
    
    def structure_reasoning_process(self, 
                                  problem: str, 
                                  domain: ReasoningDomain,
                                  current_response: str = "") -> ReasoningResult:
        """Structure the reasoning process for a problem"""
        
        logger.info(f"🔧 Structuring reasoning process for {domain.value}")
        
        # Get reasoning assistance
        assistance = self.provide_reasoning_assistance(problem, domain)
        
        # Build structured solution
        structured_solution = self._build_structured_solution(problem, assistance, domain)
        
        # Extract reasoning steps
        reasoning_steps = assistance.step_by_step_guide
        
        # Validate the reasoning
        validation_passed = self._validate_reasoning(structured_solution, domain)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(structured_solution, domain)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(
            structured_solution, domain, validation_passed
        )
        
        return ReasoningResult(
            original_problem=problem,
            structured_solution=structured_solution,
            reasoning_steps=reasoning_steps,
            validation_passed=validation_passed,
            confidence_score=confidence_score,
            improvement_suggestions=improvement_suggestions
        )
    
    def _build_structured_solution(self, 
                                 problem: str, 
                                 assistance: ReasoningAssistance,
                                 domain: ReasoningDomain) -> str:
        """Build a structured solution using the reasoning framework"""
        
        solution_parts = []
        
        # Add domain template
        domain_template = self.domain_templates.get(domain.value, "")
        if domain_template:
            solution_parts.append(domain_template)
        
        # Add step-by-step guide
        solution_parts.append("\nAPPLYING THE FRAMEWORK TO YOUR PROBLEM:")
        solution_parts.append(f"Problem: {problem}")
        solution_parts.append("")
        
        for i, step in enumerate(assistance.step_by_step_guide, 1):
            solution_parts.append(f"{i}. {step}")
        
        # Add examples
        if assistance.examples:
            solution_parts.append("\nRELEVANT EXAMPLES:")
            for example in assistance.examples[:3]:
                solution_parts.append(f"• {example}")
        
        # Add common pitfalls to avoid
        if assistance.common_pitfalls:
            solution_parts.append("\nCOMMON PITFALLS TO AVOID:")
            for pitfall in assistance.common_pitfalls[:3]:
                solution_parts.append(f"• {pitfall}")
        
        # Add validation questions
        if assistance.validation_questions:
            solution_parts.append("\nVALIDATION QUESTIONS:")
            for question in assistance.validation_questions:
                solution_parts.append(f"• {question}")
        
        return "\n".join(solution_parts)
    
    def _validate_reasoning(self, solution: str, domain: ReasoningDomain) -> bool:
        """Validate the reasoning in a solution"""
        
        # Check for completeness
        completeness_patterns = [
            r"understand|analyze|plan|execute|verify",
            r"step\s*\d+|first|second|third|next|then",
            r"problem|solution|answer|result"
        ]
        
        completeness_score = 0
        for pattern in completeness_patterns:
            if re.search(pattern, solution, re.IGNORECASE):
                completeness_score += 1
        
        # Check for domain-specific elements
        domain_patterns = {
            ReasoningDomain.PROGRAMMING: [r"function|algorithm|code|variable|loop"],
            ReasoningDomain.MATHEMATICS: [r"formula|calculate|equation|solve|answer"],
            ReasoningDomain.LOGIC: [r"premise|conclusion|logical|reasoning|valid"],
            ReasoningDomain.PROBLEM_SOLVING: [r"approach|solution|requirement|constraint"]
        }
        
        domain_score = 0
        patterns = domain_patterns.get(domain, [])
        for pattern in patterns:
            if re.search(pattern, solution, re.IGNORECASE):
                domain_score += 1
        
        # Validation passes if both completeness and domain scores are adequate
        return completeness_score >= 2 and domain_score >= 1
    
    def _calculate_confidence_score(self, solution: str, domain: ReasoningDomain) -> float:
        """Calculate confidence score for a solution"""
        
        # Base score
        score = 0.5
        
        # Increase score for structured reasoning
        if re.search(r"step\s*\d+|first|second|third", solution, re.IGNORECASE):
            score += 0.2
        
        # Increase score for domain-specific content
        domain_keywords = {
            ReasoningDomain.PROGRAMMING: ["function", "algorithm", "code", "test"],
            ReasoningDomain.MATHEMATICS: ["formula", "calculate", "equation", "verify"],
            ReasoningDomain.LOGIC: ["premise", "conclusion", "logical", "valid"],
            ReasoningDomain.PROBLEM_SOLVING: ["approach", "solution", "requirement"]
        }
        
        keywords = domain_keywords.get(domain, [])
        keyword_count = sum(1 for keyword in keywords if keyword in solution.lower())
        score += min(0.3, keyword_count * 0.1)
        
        return min(1.0, score)
    
    def _generate_improvement_suggestions(self, 
                                        solution: str, 
                                        domain: ReasoningDomain,
                                        validation_passed: bool) -> List[str]:
        """Generate improvement suggestions for a solution"""
        
        suggestions = []
        
        if not validation_passed:
            suggestions.append("Add more structured reasoning steps")
            suggestions.append("Include domain-specific considerations")
        
        # Check for common issues
        if not re.search(r"step\s*\d+|first|second", solution, re.IGNORECASE):
            suggestions.append("Break down the solution into clear steps")
        
        if not re.search(r"verify|check|test", solution, re.IGNORECASE):
            suggestions.append("Add verification or testing steps")
        
        if domain == ReasoningDomain.PROGRAMMING and not re.search(r"edge\s*case|error|exception", solution, re.IGNORECASE):
            suggestions.append("Consider edge cases and error handling")
        
        if domain == ReasoningDomain.MATHEMATICS and not re.search(r"unit|formula|calculation", solution, re.IGNORECASE):
            suggestions.append("Include formula references and unit considerations")
        
        return suggestions

# Example usage and testing
def test_reasoning_assistance():
    """Test the reasoning assistance system"""
    logger.info("🧪 Testing Reasoning Assistance System")
    
    system = ReasoningAssistanceSystem()
    
    # Test different domains
    test_problems = [
        ("Write a function to sort a list of numbers", ReasoningDomain.PROGRAMMING),
        ("Solve the equation 2x + 5 = 13", ReasoningDomain.MATHEMATICS),
        ("Prove that if A implies B and B implies C, then A implies C", ReasoningDomain.LOGIC),
        ("How would you organize a team project?", ReasoningDomain.PROBLEM_SOLVING)
    ]
    
    for problem, domain in test_problems:
        logger.info(f"\n🎯 Testing {domain.value}: {problem}")
        
        # Get reasoning assistance
        assistance = system.provide_reasoning_assistance(problem, domain)
        
        logger.info(f"   Framework Steps: {len(assistance.framework.steps)}")
        logger.info(f"   Examples Provided: {len(assistance.examples)}")
        logger.info(f"   Validation Questions: {len(assistance.validation_questions)}")
        logger.info(f"   Common Pitfalls: {len(assistance.common_pitfalls)}")
        
        # Structure the reasoning process
        result = system.structure_reasoning_process(problem, domain)
        
        logger.info(f"   Validation Passed: {result.validation_passed}")
        logger.info(f"   Confidence Score: {result.confidence_score:.2f}")
        logger.info(f"   Improvement Suggestions: {len(result.improvement_suggestions)}")
    
    return system

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    system = test_reasoning_assistance()
