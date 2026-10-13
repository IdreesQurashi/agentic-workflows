"""
Generate and upload production-ready n8n Health Monitor Workflow to local n8n instance.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678").rstrip('/')
N8N_API_KEY = os.getenv("N8N_API_KEY")

HEADERS = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

workflow_payload = {
    "name": "n8n Daily Instance Health Monitor",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "cronExpression",
                            "expression": "0 8 * * *"
                        }
                    ]
                }
            },
            "id": "b3f86e9d-1941-4c6e-8219-c6e7a2b0e111",
            "name": "Schedule Daily 08:00 AM",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [-600, 300]
        },
        {
            "parameters": {
                "jsCode": """const now = new Date();
const past24h = new Date(now.getTime() - (24 * 60 * 60 * 1000));

return [{
  json: {
    startedAfter: past24h.toISOString(),
    startedBefore: now.toISOString(),
    baseUrl: 'http://localhost:5678',
    externalBaseUrl: 'http://localhost:5678',
    recipientEmail: 'idreesqurashi.ai@gmail.com'
  }
}];"""
            },
            "id": "d4c72a81-e872-4b20-80d4-1a35f3d4c222",
            "name": "Set Config & 24h Window",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [-380, 300]
        },
        {
            "parameters": {
                "url": "={{ $json.baseUrl }}/api/v1/workflows",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "X-N8N-API-KEY",
                            "value": N8N_API_KEY
                        }
                    ]
                },
                "options": {}
            },
            "id": "e5b83b92-f983-4c31-91e5-2b46e4e5d333",
            "name": "Fetch Workflows",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-160, 200]
        },
        {
            "parameters": {
                "url": "={{ $('Set Config & 24h Window').first().json.baseUrl }}/api/v1/executions",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {
                            "name": "startedAfter",
                            "value": "={{ $('Set Config & 24h Window').first().json.startedAfter }}"
                        },
                        {
                            "name": "includeData",
                            "value": "false"
                        },
                        {
                            "name": "limit",
                            "value": "250"
                        }
                    ]
                },
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "X-N8N-API-KEY",
                            "value": N8N_API_KEY
                        }
                    ]
                },
                "options": {}
            },
            "id": "f6c94c03-a094-4d42-a2f6-3c57f5f6e444",
            "name": "Fetch 24h Executions",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-160, 400]
        },
        {
            "parameters": {
                "jsCode": """const config = $('Set Config & 24h Window').first().json;
const workflowsData = $('Fetch Workflows').first().json.data || [];
const executionsData = $('Fetch 24h Executions').first().json.data || [];

const totalWorkflows = workflowsData.length;
const activeWorkflows = workflowsData.filter(w => w.active === true);
const inactiveWorkflows = workflowsData.filter(w => !w.active);

const workflowMap = {};
workflowsData.forEach(w => {
  workflowMap[w.id] = w.name;
});

const totalRecordedExecutions = executionsData.length;
const failedExecutions = executionsData.filter(e => e.status === 'error' || e.finished === false);
const successfulExecutions = executionsData.filter(e => e.status === 'success');

const failedCount = failedExecutions.length;
const successCount = successfulExecutions.length;
const successRate = totalRecordedExecutions > 0 
  ? ((successCount / totalRecordedExecutions) * 100).toFixed(1) 
  : '100.0';

const failuresSummary = failedExecutions.slice(0, 10).map(e => {
  const wfName = workflowMap[e.workflowId] || 'Unknown Workflow';
  const execUrl = `${config.externalBaseUrl}/workflow/${e.workflowId}/executions/${e.id}`;
  return {
    id: e.id,
    workflowId: e.workflowId,
    workflowName: wfName,
    startedAt: e.startedAt,
    status: e.status,
    executionUrl: execUrl
  };
});

const isUrgent = failedCount > 0;
const statusBadge = isUrgent ? 'CRITICAL - ACTION REQUIRED' : 'HEALTHY - ALL SYSTEMS GO';
const statusColor = isUrgent ? '#dc2626' : '#16a34a';
const statusBg = isUrgent ? '#fee2e2' : '#dcfce7';

let failureRowsHtml = '';
if (failuresSummary.length > 0) {
  failureRowsHtml = failuresSummary.map(f => `
    <tr style="border-bottom: 1px solid #e5e7eb;">
      <td style="padding: 10px; font-weight: 600; color: #1f2937;">${f.workflowName}</td>
      <td style="padding: 10px; color: #4b5563;">#${f.id}</td>
      <td style="padding: 10px; color: #6b7280; font-size: 13px;">${new Date(f.startedAt).toLocaleString()}</td>
      <td style="padding: 10px; text-align: right;">
        <a href="${f.executionUrl}" style="background-color: #dc2626; color: #ffffff; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: 500;" target="_blank">Inspect Failure</a>
      </td>
    </tr>
  `).join('');
} else {
  failureRowsHtml = '<tr><td colspan="4" style="padding: 16px; text-align: center; color: #16a34a; font-weight: 500;">Zero failures recorded in the past 24 hours.</td></tr>';
}

const activeWfListHtml = activeWorkflows.slice(0, 15).map(w => `
  <li style="padding: 4px 0; color: #374151; font-size: 14px;">
    <strong>${w.name}</strong> <span style="color: #9ca3af; font-size: 12px;">(${w.id})</span>
  </li>
`).join('');

const htmlEmail = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>n8n Instance Health Report</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px; color: #1f2937;">
  <div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    
    <div style="background-color: ${statusColor}; padding: 20px 24px; color: #ffffff;">
      <h1 style="margin: 0; font-size: 20px; font-weight: 700; letter-spacing: -0.025em;">
        ${isUrgent ? '🚨 URGENT: n8n Instance Health Alert' : '✅ n8n Instance Daily Health Report'}
      </h1>
      <p style="margin: 6px 0 0 0; font-size: 14px; opacity: 0.9;">
        Reporting Window: Last 24 Hours &bull; Audited on ${new Date().toUTCString()}
      </p>
    </div>

    <div style="padding: 24px;">
      <div style="display: inline-block; padding: 6px 12px; border-radius: 9999px; background-color: ${statusBg}; color: ${statusColor}; font-weight: 700; font-size: 13px; text-transform: uppercase; margin-bottom: 20px;">
        ${statusBadge}
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Active Flows</div>
          <div style="font-size: 22px; font-weight: 700; color: #111827; margin-top: 4px;">${activeWorkflows.length}</div>
          <div style="font-size: 11px; color: #9ca3af;">of ${totalWorkflows} total</div>
        </div>
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Recorded Runs</div>
          <div style="font-size: 22px; font-weight: 700; color: #111827; margin-top: 4px;">${totalRecordedExecutions}</div>
          <div style="font-size: 11px; color: #9ca3af;">past 24h</div>
        </div>
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Success Rate</div>
          <div style="font-size: 22px; font-weight: 700; color: #16a34a; margin-top: 4px;">${successRate}%</div>
          <div style="font-size: 11px; color: #9ca3af;">${successCount} passed</div>
        </div>
        <div style="background: ${isUrgent ? '#fee2e2' : '#f9fafb'}; border: 1px solid ${isUrgent ? '#fca5a5' : '#e5e7eb'}; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: ${isUrgent ? '#991b1b' : '#6b7280'}; font-weight: 600;">Failed Runs</div>
          <div style="font-size: 22px; font-weight: 700; color: ${isUrgent ? '#dc2626' : '#111827'}; margin-top: 4px;">${failedCount}</div>
          <div style="font-size: 11px; color: ${isUrgent ? '#b91c1c' : '#9ca3af'};">urgent review</div>
        </div>
      </div>

      <h2 style="font-size: 16px; font-weight: 700; margin: 24px 0 12px 0; border-bottom: 2px solid #f3f4f6; padding-bottom: 6px;">
        ${isUrgent ? '⚠️ Recent Failed Executions (Top ' + failuresSummary.length + ')' : 'Execution Health Status'}
      </h2>
      <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 24px;">
        <thead>
          <tr style="background-color: #f9fafb; text-align: left; color: #6b7280; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e5e7eb;">
            <th style="padding: 10px;">Workflow</th>
            <th style="padding: 10px;">Exec ID</th>
            <th style="padding: 10px;">Timestamp</th>
            <th style="padding: 10px; text-align: right;">Action</th>
          </tr>
        </thead>
        <tbody>
          ${failureRowsHtml}
        </tbody>
      </table>

      <h2 style="font-size: 16px; font-weight: 700; margin: 24px 0 12px 0; border-bottom: 2px solid #f3f4f6; padding-bottom: 6px;">
        Active Production Workflows (${activeWorkflows.length})
      </h2>
      <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
        ${activeWorkflows.length > 0 ? activeWfListHtml : '<li style="color: #6b7280;">No workflows currently active.</li>'}
      </ul>
    </div>

    <div style="background: #f9fafb; border-top: 1px solid #e5e7eb; padding: 14px 24px; font-size: 12px; color: #6b7280; text-align: center;">
      Generated autonomously by n8n Health Monitor &bull; Instance: ${config.baseUrl}
    </div>
  </div>
</body>
</html>
`;

const subject = isUrgent
  ? `🚨 URGENT: [n8n Alert] ${failedCount} Failed Executions Detected in Last 24h`
  : `✅ [n8n Report] All Systems Healthy (${activeWorkflows.length} Active Workflows)`;

return [{
  json: {
    isUrgent,
    failedCount,
    successCount,
    totalRecordedExecutions,
    activeWorkflowsCount: activeWorkflows.length,
    totalWorkflowsCount: totalWorkflows,
    subject,
    htmlEmail,
    recipientEmail: config.recipientEmail
  }
}];"""
            },
            "id": "a7d05d14-b105-4e53-b3a7-4d68a6a7f555",
            "name": "Aggregate Metrics & Format HTML",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [80, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict",
                        "version": 2
                    },
                    "conditions": [
                        {
                            "id": "c609c951-87dc-4be4-a828-d102e3b2b918",
                            "leftValue": "={{ $json.failedCount }}",
                            "rightValue": 0,
                            "operator": {
                                "type": "number",
                                "operation": "gt"
                            }
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "18e16e25-c216-4f64-94b8-5e79b7b8a666",
            "name": "Check If Failures Exist",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [320, 300]
        },
        {
            "parameters": {
                "sendTo": "={{ $json.recipientEmail }}",
                "subject": "={{ $json.subject }}",
                "emailType": "html",
                "message": "={{ $json.htmlEmail }}",
                "options": {}
            },
            "id": "29f27f36-d327-4a75-a5c9-6f8ac8c9b777",
            "name": "Send Urgent Failure Alert",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [560, 200],
            "credentials": {
                "gmailOAuth2": {
                    "id": "cmK3BbZGxXjQkleW",
                    "name": "Gmail account"
                }
            }
        },
        {
            "parameters": {
                "sendTo": "={{ $json.recipientEmail }}",
                "subject": "={{ $json.subject }}",
                "emailType": "html",
                "message": "={{ $json.htmlEmail }}",
                "options": {}
            },
            "id": "3a038a47-e438-4b86-b6da-7a9bd9dac888",
            "name": "Send Clean Health Digest",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [560, 400],
            "credentials": {
                "gmailOAuth2": {
                    "id": "cmK3BbZGxXjQkleW",
                    "name": "Gmail account"
                }
            }
        }
    ],
    "connections": {
        "Schedule Daily 08:00 AM": {
            "main": [
                [
                    {
                        "node": "Set Config & 24h Window",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Set Config & 24h Window": {
            "main": [
                [
                    {
                        "node": "Fetch Workflows",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Fetch 24h Executions",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Fetch Workflows": {
            "main": [
                [
                    {
                        "node": "Aggregate Metrics & Format HTML",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Fetch 24h Executions": {
            "main": [
                [
                    {
                        "node": "Aggregate Metrics & Format HTML",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Aggregate Metrics & Format HTML": {
            "main": [
                [
                    {
                        "node": "Check If Failures Exist",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Check If Failures Exist": {
            "main": [
                [
                    {
                        "node": "Send Urgent Failure Alert",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Send Clean Health Digest",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

# 1. Save to workflow JSON file
output_path = "execution/workflows/n8n_health_monitor_workflow.json"
with open(output_path, "w") as f:
    json.dump(workflow_payload, f, indent=2)
print(f"Saved workflow to {output_path}")

# 2. Deploy directly to local n8n instance via API
res = requests.post(f"{N8N_URL}/api/v1/workflows", headers=HEADERS, json=workflow_payload)
print(f"Deploy to n8n HTTP status: {res.status_code}")
if res.status_code in [200, 201]:
    created_wf = res.json()
    wf_id = created_wf.get("id")
    print(f"Successfully created workflow on n8n! ID: {wf_id}")
    print(f"Direct UI URL: {N8N_URL}/workflow/{wf_id}")
else:
    print(f"Failed to create workflow: {res.text}")
