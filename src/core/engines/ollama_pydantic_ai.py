#!/usr/bin/env python3
"""Prompt-driven Ollama integration for the agentic core."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from ..agents import (
    PromptAgentManager,
    PromptAgentProfile,
    PromptAgentRegistry,
    PromptBuildError,
)
from .ollama_adapter import OllamaAdapter, ModelResponse

logger = logging.getLogger(__name__)


class OllamaAgentConfig(BaseModel):
    """Configuration for prompt-driven Ollama agents."""

    primary_model: str = Field(default="primary", description="Primary model key")
    coding_model: str = Field(default="coding", description="Model to use for coding tasks")
    multimodal_model: str = Field(default="multimodal", description="Model for multimodal tasks")
    lightweight_model: str = Field(default="lightweight", description="Latency optimised model")
    hrm_model: str = Field(default="hrm", description="Heiretical reasoning model key")
    max_tokens: int = Field(default=2048, ge=128, description="Default maximum tokens per response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Default generation temperature")
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    prefer_fast_responses: bool = Field(default=False, description="Prefer low-latency models when possible")
    enable_model_switching: bool = Field(default=True, description="Allow automatic model switching based on context")
    policies_path: str = Field(default="configs/policies.yaml", description="Path to Ollama model policy file")
    agents_config_path: str = Field(default="configs/agents.yaml", description="Path to prompt agent configuration file")

    @field_validator("temperature")
    @classmethod
    def _validate_temperature(cls, value: float) -> float:
        if not 0.0 <= value <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return value


class OllamaToolContext(BaseModel):
    """Execution context passed to prompt agents."""

    task_type: str = Field(..., description="Type of task being executed")
    complexity: str = Field(default="medium", description="Task complexity (low, medium, high)")
    requires_reasoning: bool = Field(default=False, description="Whether deep reasoning is required")
    requires_creativity: bool = Field(default=False, description="Whether creative output is desired")
    latency_requirement: int = Field(default=1000, description="Maximum acceptable latency in milliseconds")
    preferred_model: Optional[str] = Field(default=None, description="Explicit model preference")
    avoid_model: Optional[str] = Field(default=None, description="Model to avoid for this task")


class OllamaAgentResult(BaseModel):
    """Result returned from an Ollama-backed agent."""

    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="Underlying model identifier")
    processing_time: float = Field(..., description="Processing time in seconds")
    tokens_generated: int = Field(..., description="Approximate tokens generated")
    confidence: float = Field(default=0.8, description="Heuristic confidence score")
    tools_executed: List[str] = Field(default_factory=list, description="List of tools executed")
    tool_results: List[Dict[str, Any]] = Field(default_factory=list, description="Results from executed tools")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the result")
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Session identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the run")


def _builtin_profiles(config: OllamaAgentConfig) -> List[PromptAgentProfile]:
    """Define the built-in prompt agent profiles."""
    return [
        PromptAgentProfile(
            name="generalist",
            description="Balanced reasoning agent for explanations, synthesis, and planning.",
            system_prompt=(
                "You are Generalist, a reliable and structured assistant."
                " Provide clear reasoning, highlight assumptions, and organise answers with headings"
                " or lists when it improves readability. Cite supporting evidence when available."
            ),
            task_types=["text_generation", "analysis", "planning", "reasoning"],
            tags=["default", "general"],
            model_preferences=[config.primary_model, config.lightweight_model],
            default_parameters={"temperature": config.temperature, "max_tokens": config.max_tokens},
            priority=10,
            metadata={"is_default": True},
        ),
        PromptAgentProfile(
            name="codesmith",
            description="Specialised software engineering agent for coding tasks.",
            system_prompt=(
                "You are CodeSmith, a precise and methodical coding assistant."
                " When producing code, follow best practices, add inline comments when clarity is needed,"
                " and include quick validation steps or tests when useful."
            ),
            task_types=["code_generation", "debugging", "refactoring"],
            tags=["code", "developer"],
            model_preferences=[config.coding_model, config.primary_model],
            default_parameters={"temperature": 0.2, "max_tokens": min(config.max_tokens, 1536)},
            priority=5,
        ),
        PromptAgentProfile(
            name="analyst",
            description="Deep analysis agent that emphasises structured insights and risks.",
            system_prompt=(
                "You are Insight Analyst. Provide thorough analysis with sections for key findings,"
                " supporting evidence, risks, and recommended actions. Keep tone professional and concise."
            ),
            task_types=["analysis", "assessment", "review"],
            tags=["analysis", "review"],
            model_preferences=[config.primary_model, config.multimodal_model],
            default_parameters={"temperature": 0.5, "max_tokens": config.max_tokens},
            priority=8,
        ),
        PromptAgentProfile(
            name="quicktake",
            description="Rapid-response agent optimised for short answers and FAQ-style prompts.",
            system_prompt=(
                "You are QuickTake. Deliver concise answers (<=5 sentences) focusing on direct conclusions."
                " Avoid unnecessary elaboration."
            ),
            task_types=["simple_reasoning", "faq", "quick"],
            tags=["fast", "low_latency"],
            model_preferences=[config.lightweight_model, config.primary_model],
            default_parameters={"temperature": 0.4, "max_tokens": min(config.max_tokens, 512)},
            priority=6,
        ),
        PromptAgentProfile(
            name="heretical_reasoner",
            description="Specialist for puzzles, lateral thinking, and complex reasoning tasks.",
            system_prompt=(
                "You are the Heiretical Reasoning Model (HRM). Emphasise creative deduction,"
                " explore multiple solution paths, and validate conclusions with concise proofs."
            ),
            task_types=["puzzle", "logic", "riddle", "reasoning_deep"],
            tags=["hrm", "reasoning", "puzzle"],
            model_preferences=[config.hrm_model, config.primary_model],
            default_parameters={"temperature": 0.6, "max_tokens": min(config.max_tokens, 2048)},
            priority=4,
        ),
    ]


class OllamaPydanticAIAgent:
    """Prompt-driven wrapper around Ollama models."""

    def __init__(
        self,
        config: OllamaAgentConfig,
        *,
        agent_registry: Optional[PromptAgentRegistry] = None,
        adapter: Optional[OllamaAdapter] = None,
    ) -> None:
        self.config = config
        self.adapter = adapter or OllamaAdapter(config.policies_path)
        self.registry = agent_registry or PromptAgentRegistry.from_config(config.agents_config_path)
        self.agent_manager = PromptAgentManager(
            self.adapter,
            self.registry,
            default_parameters={"max_tokens": config.max_tokens, "temperature": config.temperature},
        )
        self.logger = logging.getLogger(__name__)
        self.performance_stats: Dict[str, Any] = {
            "total_requests": 0,
            "total_time": 0.0,
            "model_usage": {},
            "agent_usage": {},
        }
        if self.registry.is_empty():
            self._register_builtin_profiles()

    async def initialize(self) -> bool:
        """Initialise the adapter and verify connectivity."""
        try:
            ready = await self.adapter.check_ollama_status()
            if not ready:
                self.logger.warning("Ollama service not reachable; continuing in degraded mode")
            return ready
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("Failed to initialise Ollama adapter: %s", exc)
            return False

    def register_profile(self, profile: PromptAgentProfile, *, overwrite: bool = False) -> None:
        self.registry.register(profile, overwrite=overwrite)

    async def run_agent(
        self,
        user_input: str,
        context: Optional[OllamaToolContext] = None,
        *,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> OllamaAgentResult:
        metadata = metadata or {}
        context = context or OllamaToolContext(task_type="text_generation")
        overrides = overrides or {}
        tags_value = metadata.get("tags")
        if isinstance(tags_value, str):
            tags_iter = [tags_value]
        else:
            tags_iter = tags_value
        try:
            agent = self.agent_manager.resolve_agent(
                agent_name=agent_name,
                task_type=context.task_type,
                tags=tags_iter,
            )
        except PromptBuildError as exc:
            self.logger.error("%s", exc)
            return self._build_error_result(str(exc))

        prompt_context = _build_prompt_context(context, metadata)
        combined_overrides = _collect_overrides(
            context,
            overrides,
            metadata,
            self.config,
            available_models=self.agent_manager.adapter.models.keys(),
        )

        try:
            response = await agent.run(user_input, context=prompt_context, overrides=combined_overrides)
        except Exception as exc:  # pragma: no cover - runtime safety
            self.logger.error("Agent execution failed: %s", exc, exc_info=True)
            return self._build_error_result(str(exc))

        response.metadata.setdefault("agent_profile", agent.profile.name)
        result = self._to_result(response, agent.profile.name, metadata)
        self._update_stats(result)
        return result

    def get_performance_stats(self) -> Dict[str, Any]:
        stats = dict(self.performance_stats)
        if stats["total_requests"] > 0:
            stats["average_time"] = stats["total_time"] / stats["total_requests"]
        else:
            stats["average_time"] = 0.0
        return stats

    def _register_builtin_profiles(self) -> None:
        for profile in _builtin_profiles(self.config):
            if not self.registry.get(profile.name):
                self.registry.register(profile)

    def _to_result(self, response: ModelResponse, agent_name: str, metadata: Dict[str, Any]) -> OllamaAgentResult:
        tokens_generated = response.tokens_generated or _estimate_tokens(response.content)
        return OllamaAgentResult(
            content=response.content,
            model_used=response.model,
            processing_time=response.processing_time,
            tokens_generated=tokens_generated,
            confidence=metadata.get("confidence", 0.8),
            tools_executed=metadata.get("tools_executed", []),
            tool_results=metadata.get("tool_results", []),
            metadata={"agent_profile": agent_name, **metadata},
        )

    def _update_stats(self, result: OllamaAgentResult) -> None:
        self.performance_stats["total_requests"] += 1
        self.performance_stats["total_time"] += result.processing_time
        self.performance_stats["model_usage"][result.model_used] = (
            self.performance_stats["model_usage"].get(result.model_used, 0) + 1
        )
        agent_name = result.metadata.get("agent_profile", "unknown")
        self.performance_stats["agent_usage"][agent_name] = (
            self.performance_stats["agent_usage"].get(agent_name, 0) + 1
        )

    def _build_error_result(self, message: str) -> OllamaAgentResult:
        return OllamaAgentResult(
            content=f"Error: {message}",
            model_used="error",
            processing_time=0.0,
            tokens_generated=0,
            confidence=0.0,
            metadata={"error": True},
        )


_TOOL_CONTEXT_FIELDS = {
    "complexity",
    "requires_reasoning",
    "requires_creativity",
    "latency_requirement",
    "preferred_model",
    "avoid_model",
}
_OVERRIDE_FIELDS = {"max_tokens", "temperature", "options", "model_key"}


class OllamaAgenticLLMCore:
    """High-level facade mirroring the original core interface."""

    def __init__(self, config: Optional[OllamaAgentConfig] = None) -> None:
        self.config = config or OllamaAgentConfig()
        self.agent = OllamaPydanticAIAgent(self.config)
        self.logger = logging.getLogger(__name__)

    async def initialize(self) -> bool:
        return await self.agent.initialize()

    async def process_request(
        self,
        user_input: str,
        task_type: str = "text_generation",
        *,
        agent_name: Optional[str] = None,
        context: Optional[Any] = None,
        **kwargs: Any,
    ) -> OllamaAgentResult:
        if isinstance(context, OllamaToolContext):
            context_dict = context.model_dump()
        elif context is None:
            context_dict = {}
        elif isinstance(context, dict):
            context_dict = dict(context)
        else:
            raise TypeError("context must be a dict or OllamaToolContext")

        merged = {**context_dict, **kwargs}
        tool_kwargs = {key: value for key, value in merged.items() if key in _TOOL_CONTEXT_FIELDS}
        tool_context = OllamaToolContext(task_type=task_type, **tool_kwargs)
        metadata = {
            key: value
            for key, value in merged.items()
            if key not in _TOOL_CONTEXT_FIELDS and key not in _OVERRIDE_FIELDS
        }
        overrides = {key: value for key, value in merged.items() if key in _OVERRIDE_FIELDS}
        return await self.agent.run_agent(
            user_input,
            context=tool_context,
            agent_name=agent_name,
            metadata=metadata,
            overrides=overrides,
        )

    async def analyze_context(self, context_text: str, **kwargs: Any) -> Dict[str, Any]:
        result = await self.process_request(
            context_text,
            task_type="analysis",
            **kwargs,
        )
        return {
            "analysis": result.content,
            "confidence": result.confidence,
            "model_used": result.model_used,
            "processing_time": result.processing_time,
        }

    async def generate_answer(self, question: str, **kwargs: Any) -> Dict[str, Any]:
        result = await self.process_request(
            question,
            task_type="text_generation",
            **kwargs,
        )
        return {
            "answer": result.content,
            "confidence": result.confidence,
            "model_used": result.model_used,
            "processing_time": result.processing_time,
        }


def _build_prompt_context(context: OllamaToolContext, metadata: Dict[str, Any]) -> Dict[str, Any]:
    prompt_context: Dict[str, Any] = {
        "task_type": context.task_type,
        "complexity": context.complexity,
        "requires_reasoning": context.requires_reasoning,
        "requires_creativity": context.requires_creativity,
        "latency_requirement": context.latency_requirement,
    }
    if context.preferred_model:
        prompt_context["preferred_model"] = context.preferred_model
    if context.avoid_model:
        prompt_context["avoid_model"] = context.avoid_model
    if metadata:
        prompt_context["metadata"] = metadata
    return prompt_context


def _collect_overrides(
    context: OllamaToolContext,
    overrides: Dict[str, Any],
    metadata: Dict[str, Any],
    config: OllamaAgentConfig,
    *,
    available_models: Iterable[str],
) -> Dict[str, Any]:
    combined = dict(overrides)
    if context.preferred_model and "model_key" not in combined:
        combined["model_key"] = context.preferred_model
    if context.avoid_model and combined.get("model_key") == context.avoid_model:
        combined.pop("model_key")
    if (
        config.prefer_fast_responses
        and "model_key" not in combined
        and context.latency_requirement < 600
    ):
        combined["model_key"] = config.lightweight_model
    hrm_task_types = {"puzzle", "logic", "riddle", "reasoning_deep"}
    if (
        "model_key" not in combined
        and config.hrm_model
        and config.hrm_model in available_models
        and (
            context.requires_reasoning
            or context.task_type.lower() in hrm_task_types
            or metadata.get("reasoning_mode") == "hrm"
        )
    ):
        combined["model_key"] = config.hrm_model
    for key in ("max_tokens", "temperature"):
        if key not in combined and key in metadata:
            combined[key] = metadata[key]
    if "model_key" not in combined and "model_key" in metadata:
        combined["model_key"] = metadata["model_key"]
    options_value = metadata.get("options")
    if "options" not in combined and isinstance(options_value, dict):
        combined["options"] = options_value
    return combined


def _estimate_tokens(content: str) -> int:
    if not content:
        return 0
    return max(1, len(content.split()))


async def main() -> None:  # pragma: no cover - example usage
    logging.basicConfig(level=logging.INFO)
    core = OllamaAgenticLLMCore()
    await core.initialize()
    result = await core.generate_answer("Summarise the vision for the Agentic LLM Core project")
    logger.info("\n" + result["answer"])


if __name__ == "__main__":  # pragma: no cover - manual execution
    asyncio.run(main())
