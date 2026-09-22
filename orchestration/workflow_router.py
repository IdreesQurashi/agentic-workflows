"""
Workflow Router & Task Dispatcher (Layer 2 Orchestrator)
Evaluates incoming user intent and dispatches tasks to specific agentic pipelines.
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger("WorkflowRouter")


class WorkflowRouter:
    """
    Intelligent router mapping natural language intents to directives and execution pipelines.
    """

    ROUTE_MAP: Dict[str, Dict[str, str]] = {
        "outbound": {
            "directive": "autonomous_outbound_pipeline.md",
            "module": "execution.outbound.zero_bounce_dispatcher",
            "description": "B2B lead intelligence and deliverability outbound loop",
        },
        "copilot": {
            "directive": "high_velocity_copilot.md",
            "module": "execution.copilot.mak_session",
            "description": "Live 2 hour client operational shift tracking and proof of work",
        },
        "evaluation": {
            "directive": "runtime_eval_gating.md",
            "module": "execution.evals.runtime_eval_gater",
            "description": "Runtime LLM as a Judge confidence and safety scoring",
        },
        "integration": {
            "directive": "n8n_enterprise_vault.md",
            "module": "execution.integrations.n8n_client",
            "description": "n8n workflow integration and webhook execution",
        },
    }

    def resolve_route(self, intent_text: str) -> Optional[Dict[str, str]]:
        """Resolves task domain from intent keywords."""
        lower_intent = intent_text.lower()
        if any(term in lower_intent for term in ["outbound", "email", "lead", "sniper", "ats"]):
            return self.ROUTE_MAP["outbound"]
        if any(term in lower_intent for term in ["shift", "mak", "copilot", "jargon", "loom"]):
            return self.ROUTE_MAP["copilot"]
        if any(term in lower_intent for term in ["eval", "judge", "score", "grounding", "confidence"]):
            return self.ROUTE_MAP["evaluation"]
        if any(term in lower_intent for term in ["n8n", "webhook", "blueprint", "vault"]):
            return self.ROUTE_MAP["integration"]

        return None

    def list_available_pipelines(self) -> List[Dict[str, str]]:
        """Returns all configured system routing targets."""
        return [
            {"domain": key, "directive": val["directive"], "description": val["description"]}
            for key, val in self.ROUTE_MAP.items()
        ]
