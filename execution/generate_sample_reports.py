"""
Compile sample reports for both Urgent Alert (Failures Present) and Healthy Status (Clean).
Generates standalone HTML previews and Markdown summaries.
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
    "Accept": "application/json"
}

# 1. Fetch real active workflows
wf_res = requests.get(f"{N8N_URL}/api/v1/workflows", headers=HEADERS).json()
workflows = wf_res.get("data", [])
total_wf = len(workflows)
active_wf = [w for w in workflows if w.get("active") is True]

# Sample failure dataset matching real n8n execution data
sample_failures = [
    {
        "id": "397",
        "workflowId": "HvspWeKfuloGBNVW",
        "workflowName": "[Finance] AI-driven inventory management with OpenAI forecasting & ERP integration",
        "startedAt": "2026-09-19T18:45:37.278Z",
        "errorNode": "Fetch Current Inventory",
        "errorMessage": "NodeApiError: The connection cannot be established, this usually occurs due to an incorrect host (domain) value (ENOTFOUND your-warehouse-api.com)",
        "executionUrl": f"{N8N_URL}/workflow/HvspWeKfuloGBNVW/executions/397"
    },
    {
        "id": "396",
        "workflowId": "WVmMNj5AXW6QoJPF",
        "workflowName": "[Content] Automated LinkedIn content creation with GPT-4 and DALL-E for scheduled posts",
        "startedAt": "2026-09-19T18:44:02.729Z",
        "errorNode": "Generate Visual Graphic",
        "errorMessage": "NodeApiError: Invalid API Key provided for OpenAI DALL-E endpoint (401 Unauthorized)",
        "executionUrl": f"{N8N_URL}/workflow/WVmMNj5AXW6QoJPF/executions/396"
    }
]

def generate_report_html(is_urgent, failed_count, success_count, failures, active_list, total_count):
    status_color = "#dc2626" if is_urgent else "#16a34a"
    status_bg = "#fee2e2" if is_urgent else "#dcfce7"
    status_badge = "CRITICAL - ACTION REQUIRED" if is_urgent else "HEALTHY - ALL SYSTEMS GO"
    total_runs = failed_count + success_count
    success_rate = f"{(success_count / total_runs * 100):.1f}" if total_runs > 0 else "100.0"

    failure_rows = ""
    if failures:
        for f in failures:
            failure_rows += f"""
            <tr style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 12px 10px; font-weight: 600; color: #111827;">
                {f['workflowName']}<br>
                <span style="font-size: 12px; color: #dc2626; font-weight: 500;">Failed Node: {f['errorNode']}</span><br>
                <span style="font-size: 11px; color: #6b7280; font-family: monospace;">{f['errorMessage'][:130]}...</span>
              </td>
              <td style="padding: 12px 10px; color: #4b5563; font-weight: 500;">#{f['id']}</td>
              <td style="padding: 12px 10px; color: #6b7280; font-size: 12px;">{f['startedAt']}</td>
              <td style="padding: 12px 10px; text-align: right;">
                <a href="{f['executionUrl']}" style="background-color: #dc2626; color: #ffffff; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: 600; display: inline-block;" target="_blank">Triage Failure</a>
              </td>
            </tr>
            """
    else:
        failure_rows = '<tr><td colspan="4" style="padding: 20px; text-align: center; color: #16a34a; font-weight: 600;">Zero execution failures recorded in the past 24 hours.</td></tr>'

    active_items = "".join([f"<li style='padding: 3px 0; color: #374151;'><strong>{w['name']}</strong> <span style='color: #9ca3af;'>({w['id']})</span></li>" for w in active_list[:10]])

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>n8n Instance Health Report</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 24px; color: #1f2937;">
  <div style="max-width: 720px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
    
    <div style="background-color: {status_color}; padding: 20px 24px; color: #ffffff;">
      <h1 style="margin: 0; font-size: 20px; font-weight: 700; letter-spacing: -0.025em;">
        { '🚨 URGENT: n8n Instance Health Alert' if is_urgent else '✅ n8n Instance Daily Health Report' }
      </h1>
      <p style="margin: 6px 0 0 0; font-size: 13px; opacity: 0.9;">
        Audited Reporting Window: Last 24 Hours &bull; Monitored Instance: {N8N_URL}
      </p>
    </div>

    <div style="padding: 24px;">
      <div style="display: inline-block; padding: 6px 14px; border-radius: 9999px; background-color: {status_bg}; color: {status_color}; font-weight: 700; font-size: 12px; text-transform: uppercase; margin-bottom: 24px;">
        {status_badge}
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Active Flows</div>
          <div style="font-size: 22px; font-weight: 700; color: #111827; margin-top: 4px;">{len(active_list)}</div>
          <div style="font-size: 11px; color: #9ca3af;">of {total_count} total</div>
        </div>
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Recorded Runs</div>
          <div style="font-size: 22px; font-weight: 700; color: #111827; margin-top: 4px;">{total_runs}</div>
          <div style="font-size: 11px; color: #9ca3af;">past 24h</div>
        </div>
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Success Rate</div>
          <div style="font-size: 22px; font-weight: 700; color: #16a34a; margin-top: 4px;">{success_rate}%</div>
          <div style="font-size: 11px; color: #9ca3af;">{success_count} passed</div>
        </div>
        <div style="background: { '#fee2e2' if is_urgent else '#f9fafb' }; border: 1px solid { '#fca5a5' if is_urgent else '#e5e7eb' }; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: { '#991b1b' if is_urgent else '#6b7280' }; font-weight: 600;">Failed Runs</div>
          <div style="font-size: 22px; font-weight: 700; color: { '#dc2626' if is_urgent else '#111827' }; margin-top: 4px;">{failed_count}</div>
          <div style="font-size: 11px; color: { '#b91c1c' if is_urgent else '#9ca3af' };">urgent action</div>
        </div>
      </div>

      <h2 style="font-size: 15px; font-weight: 700; margin: 24px 0 12px 0; border-bottom: 2px solid #f3f4f6; padding-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; color: #374151;">
        { '⚠️ Incident Breakdown (Failed Executions)' if is_urgent else 'Operational Status' }
      </h2>
      <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 24px;">
        <thead>
          <tr style="background-color: #f9fafb; text-align: left; color: #6b7280; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #e5e7eb;">
            <th style="padding: 10px;">Workflow & Root Cause</th>
            <th style="padding: 10px;">Exec ID</th>
            <th style="padding: 10px;">Timestamp</th>
            <th style="padding: 10px; text-align: right;">Action</th>
          </tr>
        </thead>
        <tbody>
          {failure_rows}
        </tbody>
      </table>

      <h2 style="font-size: 15px; font-weight: 700; margin: 24px 0 12px 0; border-bottom: 2px solid #f3f4f6; padding-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; color: #374151;">
        Active Workflows Monitored ({len(active_list)})
      </h2>
      <ul style="margin: 0; padding-left: 20px; font-size: 13px; line-height: 1.7;">
        {active_items if active_list else '<li style=\"color: #6b7280;\">No workflows currently active.</li>'}
      </ul>
    </div>

    <div style="background: #f9fafb; border-top: 1px solid #e5e7eb; padding: 14px 24px; font-size: 12px; color: #6b7280; text-align: center;">
      Autonomous Daily Audit via n8n Engine &bull; Recipient: idreesqurashi.ai@gmail.com
    </div>
  </div>
</body>
</html>
"""

# Generate Urgent HTML
urgent_html = generate_report_html(
    is_urgent=True,
    failed_count=2,
    success_count=48,
    failures=sample_failures,
    active_list=active_wf,
    total_count=total_wf
)

with open("directives/sample_urgent_report.html", "w") as f:
    f.write(urgent_html)

# Generate Clean HTML
clean_html = generate_report_html(
    is_urgent=False,
    failed_count=0,
    success_count=52,
    failures=[],
    active_list=active_wf,
    total_count=total_wf
)

with open("directives/sample_clean_report.html", "w") as f:
    f.write(clean_html)

print("Generated sample_urgent_report.html and sample_clean_report.html")
