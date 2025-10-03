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

# Minimal implementation to make it compile
class PromptAgent:
    def __init__(self):
        pass
