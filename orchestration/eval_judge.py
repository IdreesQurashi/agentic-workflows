"""
Runtime Evaluation Judge (Layer 2 Orchestrator)
Evaluates outputs against ground truth constraints and enforces confidence floors.
"""

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional
import logging

logger = logging.getLogger("RuntimeEvalJudge")


@dataclass
class EvalReport:
    relevance_score: float
    factual_grounding_score: float
    spam_trigger_score: float
    composite_score: float
    decision: Literal["APPROVE", "REJECT", "ESCALATE"]
    reasoning: str


class RuntimeEvalJudge:
    """
    LLM as a Judge runtime gating system.
    Enforces the 85% composite confidence floor and 90% grounding strictness.
    """

    def __init__(self, confidence_floor: float = 0.85, grounding_floor: float = 0.90):
        self.confidence_floor = confidence_floor
        self.grounding_floor = grounding_floor

    def evaluate(
        self,
        relevance: float,
        grounding: float,
        spam_risk: float,
        reasoning: str = "",
    ) -> EvalReport:
        """
        Calculates composite confidence score and issues deterministic decision.
        Composite Formula: 40% Relevance + 40% Grounding + 20% Non Spam Reliability.
        """
        relevance = max(0.0, min(1.0, float(relevance)))
        grounding = max(0.0, min(1.0, float(grounding)))
        spam_risk = max(0.0, min(1.0, float(spam_risk)))

        composite = (relevance * 0.40) + (grounding * 0.40) + ((1.0 - spam_risk) * 0.20)

        if grounding < self.grounding_floor:
            decision = "REJECT"
            reason = f"Grounding score {grounding:.2f} failed strict floor of {self.grounding_floor:.2f}."
        elif composite < self.confidence_floor:
            decision = "REJECT"
            reason = f"Composite score {composite:.2f} failed confidence floor of {self.confidence_floor:.2f}."
        else:
            decision = "APPROVE"
            reason = f"Composite score {composite:.2f} passed all gating thresholds."

        if reasoning:
            reason = f"{reason} Context: {reasoning}"

        logger.info(f"Evaluation Decision: {decision} (Composite: {composite:.3f})")
        return EvalReport(
            relevance_score=relevance,
            factual_grounding_score=grounding,
            spam_trigger_score=spam_risk,
            composite_score=round(composite, 4),
            decision=decision,
            reasoning=reason,
        )
