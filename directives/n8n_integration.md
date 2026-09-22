# n8n Integration Directive

This directive outlines how to interact with the local n8n instance.

## Execution Script
- **Tool**: `execution/n8n_client.py`
- **Purpose**: Authenticate and execute commands against the local n8n API.

## Configuration
- Credentials (`N8N_URL` and `N8N_API_KEY`) must reside in the `.env` file.
- All API interactions must use the `X-N8N-API-KEY` header.

## Guidelines
- Never hardcode API keys in the scripts.
- Only run scripts via the dedicated backend Playwright virtual environment (`/home/idrees/job_agent/.venv/bin/python3`).
