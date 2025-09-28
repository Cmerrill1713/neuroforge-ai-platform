"""Prompt-driven agent profiles and factories."""

from __future__ import annotations

import logging
import textwrap
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - defensive import
    yaml = None  # type: ignore

from pydantic import BaseModel, Field, field_validator

from ..engines.ollama_adapter import OllamaAdapter, ModelResponse

logger = logging.getLogger(__name__)

_DEFAULT_PROMPT_TEMPLATE = textwrap.dedent(
    """
    {system_prompt}

    ## Task
    {user_input}
    {context_block}
    """
).strip()


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
    default_parameters: Dict[str, object] = Field(default_factory=dict, description="Default generation parameters")
    tools: List[str] = Field(default_factory=list, description="Tools this agent is authorised to call")
    priority: int = Field(default=100, ge=0, description="Lower numbers indicate higher routing priority")
    metadata: Dict[str, object] = Field(default_factory=dict, description="Additional metadata for the agent")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Agent profile name cannot be empty")
        return value

    def matches_task_type(self, task_type: Optional[str]) -> bool:
        if not task_type:
            return False
        if not self.task_types:
            return False
        lowered = task_type.lower()
        return lowered in {item.lower() for item in self.task_types}

    def matches_tags(self, tags: Optional[Iterable[str]]) -> bool:
        if not tags:
            return False
        if not self.tags:
            return False
        lowered_tags = {tag.lower() for tag in tags}
        return any(tag.lower() in lowered_tags for tag in self.tags)

    def render_prompt(self, user_input: str, context: Optional[Dict[str, object]] = None) -> str:
        """Render a complete prompt for this profile."""
        clean_input = textwrap.dedent(user_input).strip()
        context_block = ""
        if context:
            formatted = _format_context(context)
            if formatted:
                context_block = "\n\n## Context\n" + formatted
        data = {
            "system_prompt": textwrap.dedent(self.system_prompt).strip(),
            "user_input": clean_input,
            "context_block": context_block,
        }
        try:
            prompt = self.prompt_template.format(**data)
        except KeyError as exc:  # pragma: no cover - defensive
            raise PromptBuildError(
                f"Missing placeholder '{exc.args[0]}' in prompt template for agent '{self.name}'"
            ) from exc
        return textwrap.dedent(prompt).strip()


class PromptAgentRegistry:
    """Registry that keeps track of prompt-driven agent profiles."""

    def __init__(self, profiles: Optional[Sequence[PromptAgentProfile]] = None, default_name: Optional[str] = None):
        self._profiles: Dict[str, PromptAgentProfile] = {}
        self._default: Optional[str] = None
        if profiles:
            for profile in profiles:
                self.register(profile)
        if default_name:
            self.set_default(default_name)

    def register(self, profile: PromptAgentProfile, *, overwrite: bool = False) -> None:
        key = profile.name.lower()
        if key in self._profiles and not overwrite:
            raise ValueError(f"Agent profile '{profile.name}' already registered")
        self._profiles[key] = profile
        if self._default is None:
            self._default = key
        if profile.metadata.get("is_default"):
            self._default = key
        logger.debug("Registered agent profile '%s'", profile.name)

    def set_default(self, profile_name: str) -> None:
        key = profile_name.lower()
        if key not in self._profiles:
            raise ValueError(f"Unknown agent profile '{profile_name}'")
        self._default = key

    def get(self, profile_name: str) -> Optional[PromptAgentProfile]:
        return self._profiles.get(profile_name.lower())

    def list_profiles(self) -> List[PromptAgentProfile]:
        return list(self._profiles.values())

    def resolve(
        self,
        *,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> Optional[PromptAgentProfile]:
        """Resolve an agent profile using explicit name, task type, or tags."""
        if agent_name:
            profile = self.get(agent_name)
            if profile:
                return profile
        candidates: List[PromptAgentProfile] = []
        if task_type:
            for profile in self._profiles.values():
                if profile.matches_task_type(task_type):
                    candidates.append(profile)
        if not candidates and tags:
            for profile in self._profiles.values():
                if profile.matches_tags(tags):
                    candidates.append(profile)
        if candidates:
            return sorted(candidates, key=lambda p: p.priority)[0]
        if self._default:
            return self._profiles[self._default]
        return None

    @classmethod
    def from_config(cls, path: str) -> "PromptAgentRegistry":
        if yaml is None:
            raise RuntimeError("PyYAML is required to load agent profiles from configuration")
        try:
            with open(path, "r", encoding="utf-8") as handle:
                config = yaml.safe_load(handle) or {}
        except FileNotFoundError:
            logger.debug("Agent configuration file '%s' not found", path)
            return cls()
        agents_block = config.get("agents", [])
        profiles = [PromptAgentProfile(**entry) for entry in agents_block]
        default_name = config.get("default_agent")
        registry = cls(profiles, default_name=default_name)
        logger.info("Loaded %d agent profile(s) from %s", len(profiles), path)
        return registry

    def is_empty(self) -> bool:
        return not self._profiles


@dataclass
class PromptDrivenAgent:
    """Runtime wrapper that executes prompts against the Ollama adapter."""

    profile: PromptAgentProfile
    adapter: OllamaAdapter
    default_parameters: Dict[str, object]

    async def run(
        self,
        user_input: str,
        *,
        context: Optional[Dict[str, object]] = None,
        overrides: Optional[Dict[str, object]] = None,
    ) -> ModelResponse:
        overrides = overrides or {}
        prompt = self.profile.render_prompt(user_input, context)
        generation_params = self._resolve_generation_params(overrides)
        model_key = self._resolve_model_key(context=context, overrides=overrides)
        options = generation_params.pop("options", {})
        response = await self.adapter.generate_response(
            model_key=model_key,
            prompt=prompt,
            **generation_params,
            **options,
        )
        return response

    def _resolve_generation_params(self, overrides: Dict[str, object]) -> Dict[str, object]:
        params: Dict[str, object] = {}
        params.update(self.default_parameters)
        params.update(self.profile.default_parameters)
        for key in ("max_tokens", "temperature"):
            if key in overrides:
                params[key] = overrides[key]

        options: Dict[str, object] = {}
        default_opts = self.default_parameters.get("options")
        if isinstance(default_opts, dict):
            options.update(default_opts)
        profile_opts = self.profile.default_parameters.get("options")
        if isinstance(profile_opts, dict):
            options.update(profile_opts)
        override_opts = overrides.get("options")
        if isinstance(override_opts, dict):
            options.update(override_opts)
        if options:
            params["options"] = options

        if "max_tokens" in params:
            try:
                params["max_tokens"] = int(params["max_tokens"])  # type: ignore[assignment]
            except (TypeError, ValueError) as exc:
                raise PromptBuildError("max_tokens must be an integer") from exc
        if "temperature" in params:
            try:
                params["temperature"] = float(params["temperature"])  # type: ignore[assignment]
            except (TypeError, ValueError) as exc:
                raise PromptBuildError("temperature must be a number") from exc
        if "max_tokens" not in params:
            params["max_tokens"] = 1024
        if "temperature" not in params:
            params["temperature"] = 0.7
        return params

    def _resolve_model_key(
        self,
        *,
        context: Optional[Dict[str, object]],
        overrides: Dict[str, object],
    ) -> str:
        if "model_key" in overrides:
            return str(overrides["model_key"])
        if context:
            preferred = context.get("preferred_model")
            if preferred:
                return str(preferred)
        for candidate in self.profile.model_preferences:
            if candidate in self.adapter.models:
                return candidate
        if "primary" in self.adapter.models:
            return "primary"
        if self.profile.model_preferences:
            return self.profile.model_preferences[0]
        if self.adapter.models:
            return next(iter(self.adapter.models.keys()))
        return "primary"


class PromptAgentManager:
    """Convenience wrapper that caches prompt-driven agents."""

    def __init__(self, adapter: OllamaAdapter, registry: PromptAgentRegistry, default_parameters: Optional[Dict[str, object]] = None):
        self.adapter = adapter
        self.registry = registry
        self.default_parameters = default_parameters or {}
        self._agents: Dict[str, PromptDrivenAgent] = {}

    def resolve_agent(
        self,
        *,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> PromptDrivenAgent:
        profile = self.registry.resolve(agent_name=agent_name, task_type=task_type, tags=tags)
        if profile is None:
            raise PromptBuildError("Unable to resolve an agent profile for the given request")
        key = profile.name.lower()
        if key not in self._agents:
            self._agents[key] = PromptDrivenAgent(profile, self.adapter, self.default_parameters)
        return self._agents[key]

    def list_profiles(self) -> List[PromptAgentProfile]:
        return self.registry.list_profiles()


def _format_context(context: Dict[str, object]) -> str:
    lines: List[str] = []
    for key, value in context.items():
        formatted_value = _stringify_context_value(value)
        if formatted_value:
            for idx, segment in enumerate(formatted_value.splitlines() or [""]):
                if idx == 0:
                    lines.append(f"- {key}: {segment}")
                else:
                    lines.append(f"  {segment}")
    return "\n".join(lines)


def _stringify_context_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_stringify_context_value(item) for item in value if item is not None)
    if isinstance(value, dict):
        parts = [f"{k}={_stringify_context_value(v)}" for k, v in value.items()]
        return "{" + ", ".join(parts) + "}"
    return str(value)
