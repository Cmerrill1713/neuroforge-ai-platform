"""Integration with DSPy's MIPROv2 teleprompter for prompt optimization."""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Sequence, Tuple

from pydantic import BaseModel, Field

from ..agents import PromptAgentProfile

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass  # type: ignore

logger = logging.getLogger(__name__)


class PromptExample(BaseModel):
    """Training example used for prompt optimization."""

    input_text: str = Field(..., description="User input supplied to the agent")
    expected_output: str = Field(..., description="Desired agent response")
    context: Optional[str] = Field(None, description="Optional contextual information")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


@dataclass
class PromptOptimizationSettings:
    """Configuration for the MIPRO teleprompter run."""

    auto: Optional[str] = "light"
    num_candidates: Optional[int] = None
    num_trials: Optional[int] = None
    max_bootstrapped_demos: int = 4
    max_labeled_demos: int = 0
    minibatch: bool = False
    minibatch_size: int = 35
    minibatch_full_eval_steps: int = 5
    requires_permission_to_run: bool = False


@dataclass
class PromptOptimizationReport:
    """Summary of a prompt optimization run."""

    profile_name: str
    original_prompt: str
    optimized_prompt: str
    score: float
    train_examples: int
    val_examples: int


class MIPROPromptOptimizer:
    """Wrapper around DSPy's MIPROv2 prompt optimizer."""

    def __init__(
        self,
        *,
        metric: Optional[Callable[[Any, Any], float]] = None,
        settings: Optional[PromptOptimizationSettings] = None,
        dependency_loader: Optional[Callable[[], Tuple[Any, Any, Any, Any]]] = None,
    ) -> None:
        self.metric = metric or self._default_metric
        self.settings = settings or PromptOptimizationSettings()
        self._dependency_loader = dependency_loader or self._load_dependencies

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def optimize_profile(
        self,
        profile: PromptAgentProfile,
        dataset: Sequence[PromptExample],
        *,
        validation_dataset: Optional[Sequence[PromptExample]] = None,
    ) -> Tuple[PromptAgentProfile, PromptOptimizationReport]:
        """Run MIPROv2 on a given profile and dataset."""

        if not dataset:
            raise ValueError("Prompt optimization dataset cannot be empty")

        dspy_module, utils_module, mipro_class, evaluate_class = self._dependency_loader()
        trainset = self._build_dataset(dspy_module, dataset)
        valset = self._build_dataset(dspy_module, validation_dataset or dataset)

        student = self._build_student_program(dspy_module, utils_module, profile)
        teleprompter = self._create_teleprompter(mipro_class)
        optimized_program = self._compile_program(teleprompter, student, trainset, valset)
        optimized_instructions = self._extract_instructions(utils_module, optimized_program)

        score = self._evaluate_program(evaluate_class, optimized_program, valset)
        optimized_profile = self._build_updated_profile(profile, optimized_instructions, score)

        report = PromptOptimizationReport(
            profile_name=profile.name,
            original_prompt=profile.system_prompt,
            optimized_prompt=optimized_instructions,
            score=score,
            train_examples=len(trainset),
            val_examples=len(valset),
        )
        return optimized_profile, report

    # ------------------------------------------------------------------
    # Helpers - structure kept separate for testing
    # ------------------------------------------------------------------
    def _load_dependencies(self) -> Tuple[Any, Any, Any, Any]:
        """Load DSPy modules lazily to avoid import overhead during startup."""

        dspy_module = importlib.import_module("dspy")
        utils_module = importlib.import_module("dspy.teleprompt.utils")
        mipro_module = importlib.import_module("dspy.teleprompt.mipro_optimizer_v2")
        evaluate_module = importlib.import_module("dspy.evaluate.evaluate")
        return dspy_module, utils_module, mipro_module.MIPROv2, evaluate_module.Evaluate

    def _build_dataset(self, dspy_module: Any, dataset: Sequence[PromptExample]) -> List[Any]:
        examples: List[Any] = []
        for record in dataset:
            context = record.context or ""
            example = dspy_module.Example(
                user_input=record.input_text,
                context=context,
                answer=record.expected_output,
            ).with_inputs("user_input", "context")
            examples.append(example)
        return examples

    def _build_student_program(self, dspy_module: Any, utils_module: Any, profile: PromptAgentProfile) -> Any:
        base_prompt = profile.system_prompt

        class PromptProgram(dspy_module.Module):
            def __init__(self, instructions: str) -> None:
                super().__init__()
                self.generate = dspy_module.ChainOfThought("user_input, context -> answer")
                signature = utils_module.get_signature(self.generate)
                signature.instructions = instructions

            def forward(self, user_input: str, context: str = "") -> Any:
                context_value = context or ""
                prediction = self.generate(user_input=user_input, context=context_value)
                return prediction

        return PromptProgram(base_prompt)

    def _create_teleprompter(self, mipro_class: Any) -> Any:
        kwargs: dict[str, Any] = {
            "metric": self.metric,
            "auto": self.settings.auto,
            "max_bootstrapped_demos": self.settings.max_bootstrapped_demos,
            "max_labeled_demos": self.settings.max_labeled_demos,
        }
        if self.settings.auto is None and self.settings.num_candidates is not None:
            kwargs["num_candidates"] = self.settings.num_candidates
        return mipro_class(**kwargs)

    def _compile_program(
        self,
        teleprompter: Any,
        student_program: Any,
        trainset: Sequence[Any],
        valset: Sequence[Any],
    ) -> Any:
        compile_kwargs = {
            "trainset": list(trainset),
            "valset": list(valset),
            "requires_permission_to_run": self.settings.requires_permission_to_run,
            "minibatch": self.settings.minibatch,
            "minibatch_size": self.settings.minibatch_size,
            "minibatch_full_eval_steps": self.settings.minibatch_full_eval_steps,
        }
        if self.settings.auto is None and self.settings.num_trials is not None:
            compile_kwargs["num_trials"] = self.settings.num_trials
        optimized_program = teleprompter.compile(student_program, **compile_kwargs)
        return optimized_program

    def _extract_instructions(self, utils_module: Any, program: Any) -> str:
        predictors = program.predictors()
        if not predictors:
            raise RuntimeError("Optimized program did not expose any predictors")
        signature = utils_module.get_signature(predictors[0])
        return signature.instructions

    def _evaluate_program(self, evaluate_class: Any, program: Any, valset: Sequence[Any]) -> float:
        if not valset:
            return 0.0
        evaluator = evaluate_class(devset=list(valset), metric=self.metric)
        score = evaluator(program)
        try:
            return float(score)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            return 0.0

    def _build_updated_profile(
        self,
        profile: PromptAgentProfile,
        optimized_instructions: str,
        score: float,
    ) -> PromptAgentProfile:
        metadata = dict(profile.metadata)
        metadata.update(
            {
                "optimized_by": "mipro_v2",
                "optimized_at": datetime.utcnow().isoformat(),
                "optimized_score": score,
            }
        )
        return profile.model_copy(update={"system_prompt": optimized_instructions, "metadata": metadata})

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _default_metric(example: Any, prediction: Any) -> float:
        """Exact-match metric used when the caller does not supply one."""

        expected = getattr(example, "answer", "")
        actual = getattr(prediction, "answer", "")
        return 1.0 if str(actual).strip() == str(expected).strip() else 0.0


__all__ = [
    "MIPROPromptOptimizer",
    "PromptExample",
    "PromptOptimizationReport",
    "PromptOptimizationSettings",
]
