import os
import requests
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678").rstrip('/')
N8N_API_KEY = os.getenv("N8N_API_KEY")

HEADERS = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_workflows():
    response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_workflow(workflow_id):
    response = requests.get(f"{N8N_URL}/api/v1/workflows/{workflow_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def create_workflow(workflow_data):
    response = requests.post(f"{N8N_URL}/api/v1/workflows", headers=HEADERS, json=workflow_data)
    response.raise_for_status()
    return response.json()

def update_workflow(workflow_id, workflow_data):
    response = requests.put(f"{N8N_URL}/api/v1/workflows/{workflow_id}", headers=HEADERS, json=workflow_data)
    response.raise_for_status()
    return response.json()

def delete_workflow(workflow_id):
    response = requests.delete(f"{N8N_URL}/api/v1/workflows/{workflow_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def activate_workflow(workflow_id):
    response = requests.post(f"{N8N_URL}/api/v1/workflows/{workflow_id}/activate", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def deactivate_workflow(workflow_id):
    response = requests.post(f"{N8N_URL}/api/v1/workflows/{workflow_id}/deactivate", headers=HEADERS)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="n8n API Client")
    parser.add_argument("action", choices=["list", "get", "create", "update", "delete", "activate", "deactivate"], help="Action to perform")
    parser.add_argument("--id", type=str, help="Workflow ID (required for get, update, delete, activate, deactivate)")
    parser.add_argument("--file", type=str, help="Path to JSON file containing workflow data (required for create, update)")
    
    args = parser.parse_args()
    
    try:
        if args.action == "list":
            print(json.dumps(get_workflows(), indent=2))
        elif args.action == "get":
            if not args.id: raise ValueError("--id is required for get")
            print(json.dumps(get_workflow(args.id), indent=2))
        elif args.action == "create":
            if not args.file: raise ValueError("--file is required for create")
            with open(args.file, 'r') as f:
                data = json.load(f)
            print(json.dumps(create_workflow(data), indent=2))
        elif args.action == "update":
            if not args.id or not args.file: raise ValueError("--id and --file are required for update")
            with open(args.file, 'r') as f:
                data = json.load(f)
            print(json.dumps(update_workflow(args.id, data), indent=2))
        elif args.action == "delete":
            if not args.id: raise ValueError("--id is required for delete")
            print(json.dumps(delete_workflow(args.id), indent=2))
        elif args.action == "activate":
            if not args.id: raise ValueError("--id is required for activate")
            print(json.dumps(activate_workflow(args.id), indent=2))
        elif args.action == "deactivate":
            if not args.id: raise ValueError("--id is required for deactivate")
            print(json.dumps(deactivate_workflow(args.id), indent=2))
    except Exception as e:
        print(f"Error: {e}")
