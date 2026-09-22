import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import ENV_FILE, ARCHIVE_DIR, DATA_WORKFLOWS_DIR
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(ENV_FILE)
url = os.getenv("N8N_URL", "http://localhost:5678").rstrip("/")
key = os.getenv("N8N_API_KEY")

validate_js = r"""
const body = $input.first().json.body || $input.first().json;

// Honeypot check - bots fill this, humans don't
const honeypot = (body.website || "").trim();
if (honeypot) {
  return [{ json: { result: "honeypot", status: "success", message: "Thank you! We received your quote request and will contact you within 24 hours." } }];
}

const name = (body.name || "").trim();
const business = (body.business || "").trim();
const phoneRaw = (body.phone || "").trim();
const vehicleType = (body.vehicleType || "").trim();
const message = (body.message || "").trim();
const submissionId = (body.submissionId || "").trim();
const sourcePage = (body.sourcePage || "").trim();

const errors = [];

if (!name || name.length < 2) {
  errors.push({ field: "name", message: "Name must be at least 2 characters." });
} else if (name.length > 100) {
  errors.push({ field: "name", message: "Name must be under 100 characters." });
}

const phoneAllowed = /^[0-9+\s\-().]+$/;
const phoneDigits = phoneRaw.replace(/\D/g, "");

if (!phoneRaw) {
  errors.push({ field: "phone", message: "A valid phone or WhatsApp number is required." });
} else if (!phoneAllowed.test(phoneRaw)) {
  errors.push({ field: "phone", message: "Phone number contains invalid characters. Use digits, +, spaces, and dashes only." });
} else if (phoneDigits.length < 7) {
  errors.push({ field: "phone", message: "A valid phone number with at least 7 digits is required." });
} else if (phoneDigits.length > 15) {
  errors.push({ field: "phone", message: "Phone number is too long (max 15 digits)." });
}

const allowedVehicles = ["Car", "Truck", "Van", "SUV", "Fleet (Multiple Vehicles)", "Other"];
if (!vehicleType || !allowedVehicles.includes(vehicleType)) {
  errors.push({ field: "vehicleType", message: "Please select a valid vehicle type from the list." });
}

if (business.length > 100) {
  errors.push({ field: "business", message: "Business name must be under 100 characters." });
}

if (message.length > 500) {
  errors.push({ field: "message", message: "Message must be under 500 characters." });
}

if (errors.length > 0) {
  return [{ json: { result: "invalid", status: "error", field: errors[0].field, message: errors[0].message } }];
}

// Formula injection protection
const sanitize = (val) => {
  if (val && /^[=+\-@]/.test(val)) return "'" + val;
  return val;
};

return [{ json: {
  result: "valid",
  submission_id: submissionId || ("sub_" + Date.now() + "_" + Math.random().toString(36).substring(2, 8)),
  submitted_at: new Date().toISOString(),
  name: sanitize(name),
  business: sanitize(business),
  phone: phoneRaw,
  vehicle_type: vehicleType,
  message: sanitize(message),
  source_page: sourcePage,
  status: "NEW"
} }];
"""

logger_js = r"""
const errorInfo = $input.first().json;
let lead = {};
try {
  lead = $('Validate + Sanitize').first().json;
} catch(e) {}

const logEntry = {
  logged_at: new Date().toISOString(),
  lead_payload: lead,
  error: errorInfo,
  recovery_status: "PENDING"
};

console.error("SHEET_WRITE_FAILURE:", JSON.stringify(logEntry));

return [{ json: { logged: true, logEntry } }];
"""

workflow_data = {
  "name": "Project A1 — Vehicle Wraps Quote Pipeline",
  "settings": {
    "executionOrder": "v1"
  },
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "vehicle-wrap-quote",
        "responseMode": "responseNode",
        "options": {
          "allowedOrigins": "*"
        }
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [-400, 300],
      "webhookId": "vehicle-wrap-quote"
    },
    {
      "parameters": {
        "jsCode": validate_js
      },
      "name": "Validate + Sanitize",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [-160, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": True,
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "leftValue": "={{ $json.result }}",
              "rightValue": "valid",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }
          ],
          "combinator": "and"
        }
      },
      "name": "IF: Is Valid?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2.2,
      "position": [80, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": True,
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "leftValue": "={{ $json.result }}",
              "rightValue": "invalid",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }
          ],
          "combinator": "and"
        }
      },
      "name": "IF: Is Invalid?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2.2,
      "position": [320, 500]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({ status: \"error\", field: $json.field, message: $json.message }) }}",
        "options": {
          "responseCode": 400
        }
      },
      "name": "Respond: Validation Error (400)",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [580, 440]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({ status: \"success\", message: $json.message }) }}",
        "options": {
          "responseCode": 200
        }
      },
      "name": "Respond: Honeypot Fake Success (200)",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [580, 600]
    },
    {
      "parameters": {
        "operation": "append",
        "documentId": {
          "__rl": True,
          "value": "REPLACE_WITH_YOUR_SHEET_ID",
          "mode": "id"
        },
        "sheetName": {
          "__rl": True,
          "value": "Submissions",
          "mode": "name"
        },
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "submission_id": "={{ $json.submission_id }}",
            "submitted_at": "={{ $json.submitted_at }}",
            "name": "={{ $json.name }}",
            "business": "={{ $json.business }}",
            "phone": "={{ $json.phone }}",
            "vehicle_type": "={{ $json.vehicle_type }}",
            "message": "={{ $json.message }}",
            "source_page": "={{ $json.source_page }}",
            "status": "={{ $json.status }}"
          },
          "matchingColumns": [],
          "schema": []
        },
        "options": {
          "cellFormat": "RAW"
        }
      },
      "name": "Google Sheets: Append Row",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [360, 220],
      "onError": "continueErrorOutput",
      "credentials": {
        "googleSheetsOAuth2Api": {
          "id": "DlW6CGRkA6cPkjYs",
          "name": "Google Sheets account"
        }
      }
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "{\"status\":\"success\",\"message\":\"Thank you! We received your quote request and will contact you within 24 hours.\"}",
        "options": {
          "responseCode": 200
        }
      },
      "name": "Respond: Success (200)",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [660, 140]
    },
    {
      "parameters": {
        "jsCode": logger_js
      },
      "name": "Log Error Fallback",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [660, 300],
      "onError": "continueRegularOutput"
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "{\"status\":\"success\",\"message\":\"Your request has been received. We will be in touch shortly.\"}",
        "options": {
          "responseCode": 200
        }
      },
      "name": "Respond: Graceful Failure (200)",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [900, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [{"node": "Validate + Sanitize", "type": "main", "index": 0}]
      ]
    },
    "Validate + Sanitize": {
      "main": [
        [{"node": "IF: Is Valid?", "type": "main", "index": 0}]
      ]
    },
    "IF: Is Valid?": {
      "main": [
        [{"node": "Google Sheets: Append Row", "type": "main", "index": 0}],
        [{"node": "IF: Is Invalid?", "type": "main", "index": 0}]
      ]
    },
    "IF: Is Invalid?": {
      "main": [
        [{"node": "Respond: Validation Error (400)", "type": "main", "index": 0}],
        [{"node": "Respond: Honeypot Fake Success (200)", "type": "main", "index": 0}]
      ]
    },
    "Google Sheets: Append Row": {
      "main": [
        [{"node": "Respond: Success (200)", "type": "main", "index": 0}],
        [{"node": "Log Error Fallback", "type": "main", "index": 0}]
      ]
    },
    "Log Error Fallback": {
      "main": [
        [{"node": "Respond: Graceful Failure (200)", "type": "main", "index": 0}]
      ]
    }
  }
}

os.makedirs(str(DATA_WORKFLOWS_DIR), exist_ok=True)
with open(str(DATA_WORKFLOWS_DIR / "n8n-workflow-export.json"), "w") as f:
    json.dump(workflow_data, f, indent=2)

print("Saved workflow to project-a1-vehicle-wraps/n8n-workflow-export.json")

res = requests.post(f"{url}/api/v1/workflows", headers={"X-N8N-API-KEY": key}, json=workflow_data)
print("Creation status code:", res.status_code)
if res.status_code in (200, 201):
    wf = res.json()
    wf_id = wf.get("id")
    print(f"SUCCESS: Created workflow '{wf.get('name')}' with ID: {wf_id}")
    act_res = requests.post(f"{url}/api/v1/workflows/{wf_id}/activate", headers={"X-N8N-API-KEY": key})
    print(f"Activation response: {act_res.status_code}")
else:
    print("Creation error:", res.text)
