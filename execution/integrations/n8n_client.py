"""
n8n API Client & Workflow Integrator (Layer 3 Execution Tool)
Provides deterministic programmatic control over self hosted n8n workflow instances.
"""

import os
import requests
import json
import argparse
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678").rstrip('/')
N8N_API_KEY = os.getenv("N8N_API_KEY")

HEADERS = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}


class N8nClient:
    """
    Deterministic client for interacting with n8n instance APIs and webhooks.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or N8N_URL).rstrip('/')
        self.api_key = api_key or N8N_API_KEY
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def list_workflows(self) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/v1/workflows/{workflow_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/api/v1/workflows", headers=self.headers, json=workflow_data)
        response.raise_for_status()
        return response.json()

    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/api/v1/workflows/{workflow_id}/activate", headers=self.headers)
        response.raise_for_status()
        return response.json()


def get_workflows():
    return N8nClient().list_workflows()

def get_workflow(workflow_id):
    return N8nClient().get_workflow(workflow_id)

def create_workflow(workflow_data):
    return N8nClient().create_workflow(workflow_data)

def activate_workflow(workflow_id):
    return N8nClient().activate_workflow(workflow_id)
