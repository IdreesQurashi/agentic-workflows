"""
Runtime Evaluation Gating Engine (Layer 3 Execution Tool)
Evaluates generated candidate outputs against rigid criteria and confidence thresholds.
"""

from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger("RuntimeEvalGater")


class EvalCandidate(BaseModel):
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    factual_grounding_score: float = Field(..., ge=0.0, le=1.0)
    spam_trigger_score: float = Field(..., ge=0.0, le=1.0)
    decision: Literal["APPROVE", "REJECT", "REWRITE"]
    reasoning: str


class RuntimeEvalGater:
    """
    Deterministic pre flight gating engine before triggering any external action.
    """

    def __init__(self, pass_threshold: float = 0.85, grounding_threshold: float = 0.90):
        self.pass_threshold = pass_threshold
        self.grounding_threshold = grounding_threshold

    def evaluate_payload(
        self,
        relevance: float,
        factual_grounding: float,
        spam_score: float,
        reasoning: str = "",
    ) -> EvalCandidate:
        """Evaluates payload scores and issues structured Pydantic decision."""
        composite = (relevance * 0.40) + (factual_grounding * 0.40) + ((1.0 - spam_score) * 0.20)

        if composite < self.pass_threshold or factual_grounding < self.grounding_threshold:
            decision = "REJECT"
            reason = f"Composite score {composite:.2f} or grounding {factual_grounding:.2f} failed threshold."
        else:
            decision = "APPROVE"
            reason = f"Payload verified with composite score {composite:.2f}."

        if reasoning:
            reason = f"{reason} Notes: {reasoning}"

        logger.info(f"Gate Decision: {decision} (Composite: {composite:.3f})")
        return EvalCandidate(
            relevance_score=relevance,
            factual_grounding_score=factual_grounding,
            spam_trigger_score=spam_score,
            decision=decision,
            reasoning=reason,
        )
