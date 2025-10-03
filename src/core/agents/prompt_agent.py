import logging
import textwrap
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

_DEFAULT_PROMPT_TEMPLATE = textwrap.dedent("""
{system_prompt}

## Task
{user_input}
{context_block}
""").strip()

class PromptBuildError(RuntimeError):
    """Raised when a prompt or agent profile cannot be resolved."""

class PromptAgentProfile(BaseModel):
    """Definition for a prompt-driven agent."""
    
    name: str = Field(..., description="Unique agent profile name")
    description: str = Field(..., description="Short description for the agent")
    system_prompt: str = Field(..., description="System instructions for the agent")
    prompt_template: str = Field(default=_DEFAULT_PROMPT_TEMPLATE, description="Template used to build prompts")
    task_types: List[str] = Field(default_factory=list, description="Task types this agent specialises in")
    tags: List[str] = Field(default_factory=list, description="Additional identifiers for routing")
    model_preferences: List[str] = Field(default_factory=list, description="Preferred model keys in order")
    default_parameters: Dict[str, Any] = Field(default_factory=dict, description="Default generation parameters")
    tools: List[str] = Field(default_factory=list, description="Tools this agent is authorised to call")
    priority: int = Field(default=100, ge=0, description="Lower numbers indicate higher routing priority")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the agent")

class PromptAgent:
    """Prompt-driven agent implementation"""
    
    def __init__(self, profile: PromptAgentProfile):
        self.profile = profile
        self.logger = logging.getLogger(__name__)
    
    def build_prompt(self, user_input: str, context: str = "") -> str:
        """Build a prompt using the agent's template"""
        context_block = f"\n\n## Context\n{context}" if context else ""
        
        return self.profile.prompt_template.format(
            system_prompt=self.profile.system_prompt,
            user_input=user_input,
            context_block=context_block
        )

class PromptAgentRegistry:
    """Registry for managing prompt-driven agents"""
    
    def __init__(self):
        self.agents: Dict[str, PromptAgent] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, profile: PromptAgentProfile) -> PromptAgent:
        """Register a new agent profile"""
        agent = PromptAgent(profile)
        self.agents[profile.name] = agent
        self.logger.info(f"Registered agent: {profile.name}")
        return agent
    
    def get_agent(self, name: str) -> Optional[PromptAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self.agents.keys())
    
    def find_agents_for_task(self, task_type: str) -> List[PromptAgent]:
        """Find agents suitable for a specific task type"""
        suitable_agents = []
        for agent in self.agents.values():
            if task_type in agent.profile.task_types:
                suitable_agents.append(agent)
        
        # Sort by priority (lower number = higher priority)
        return sorted(suitable_agents, key=lambda a: a.profile.priority)
