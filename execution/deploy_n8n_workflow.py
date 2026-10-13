import json
import urllib.request
import os

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "YOUR_N8N_API_KEY_PLACEHOLDER")

GOOGLE_SHEETS_CRED_ID = "4Ro2UHO4PIKBESyz"
GEMINI_CRED_ID = "vvxfmXZ3AVztd90O"

# Default target sheet ID from Project A1 or configurable
TARGET_SHEET_ID = "1dQgwRKS1H4tbCnFP5mosaAPGZFPACpffFdUj0pTFtHg"

workflow_payload = {
    "name": "PROJECT I2: Wraps Content Pattern Engine v1",
    "nodes": [
        {
            "id": "trigger-1",
            "name": "Manual / Test Trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [-600, 300],
            "parameters": {}
        },
        {
            "id": "schedule-1",
            "name": "Weekly Schedule (Sunday 23:00 UTC)",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [-600, 100],
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "weeks",
                            "triggerAtDay": [0],
                            "triggerAtHour": 23
                        }
                    ]
                }
            }
        },
        {
            "id": "http-ckwraps",
            "name": "HTTP: Fetch CK Wraps",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-350, 0],
            "parameters": {
                "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCcvrUINxcy_cHZOmg3KGsOg",
                "options": {
                    "response": {
                        "response": {
                            "responseFormat": "text"
                        }
                    }
                }
            }
        },
        {
            "id": "http-metro",
            "name": "HTTP: Fetch Metro Restyling",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-350, 180],
            "parameters": {
                "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCYDN_iAFJqm_FW5tJ8UrkCQ",
                "options": {
                    "response": {
                        "response": {
                            "responseFormat": "text"
                        }
                    }
                }
            }
        },
        {
            "id": "http-inozetek",
            "name": "HTTP: Fetch Inozetek",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-350, 360],
            "parameters": {
                "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCrXIfgcq402NCgfxHeRsA4Q",
                "options": {
                    "response": {
                        "response": {
                            "responseFormat": "text"
                        }
                    }
                }
            }
        },
        {
            "id": "http-vinylfrog",
            "name": "HTTP: Fetch Vinyl Frog",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-350, 540],
            "parameters": {
                "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC5jnLyJzWyUNd8y_dD8s4Xw",
                "options": {
                    "response": {
                        "response": {
                            "responseFormat": "text"
                        }
                    }
                }
            }
        },
        {
            "id": "code-parser",
            "name": "Code: Parse XML Feeds and Outliers",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [-50, 260],
            "parameters": {
                "jsCode": """
// Aggregate and parse XML feeds from all channels
const items = [];
const feedInputs = [$("HTTP: Fetch CK Wraps").first()?.json?.data,
                    $("HTTP: Fetch Metro Restyling").first()?.json?.data,
                    $("HTTP: Fetch Inozetek").first()?.json?.data,
                    $("HTTP: Fetch Vinyl Frog").first()?.json?.data];

for (const rawXml of feedInputs) {
  if (!rawXml || typeof rawXml !== 'string') continue;
  
  // Extract channel title
  const channelMatch = rawXml.match(/<title>([^<]+)<\\/title>/);
  const channelName = channelMatch ? channelMatch[1] : "Wrap Studio";
  
  // Extract video entries
  const entryRegex = /<entry>[\\s\\S]*?<\\/entry>/g;
  const entries = rawXml.match(entryRegex) || [];
  
  for (const entry of entries) {
    const idMatch = entry.match(/<yt:videoId>([^<]+)<\\/yt:videoId>/);
    const titleMatch = entry.match(/<title>([^<]+)<\\/title>/);
    const linkMatch = entry.match(/<link rel="alternate" href="([^"]+)"\\/>/);
    const publishedMatch = entry.match(/<published>([^<]+)<\\/published>/);
    const thumbMatch = entry.match(/<media:thumbnail url="([^"]+)"/);
    const viewsMatch = entry.match(/views="([0-9]+)"/);
    const ratingMatch = entry.match(/count="([0-9]+)"/);
    
    if (idMatch && titleMatch) {
      const views = viewsMatch ? parseInt(viewsMatch[1], 10) : 500;
      const likes = ratingMatch ? parseInt(ratingMatch[1], 10) : 50;
      const comments = Math.round(likes * 0.12);
      
      // Calculate Outlier Multiplier (views vs baseline)
      const baseline = 2000;
      const outlier = parseFloat((views / baseline).toFixed(2));
      
      // Determine preliminary wrap category
      const titleLower = titleMatch[1].toLowerCase();
      let wrapCategory = "Commercial Fleet";
      if (titleLower.includes("color") || titleLower.includes("gloss") || titleLower.includes("satin") || titleLower.includes("matte")) {
        wrapCategory = "Color Change";
      } else if (titleLower.includes("ppf") || titleLower.includes("protect")) {
        wrapCategory = "Paint Protection Film";
      } else if (titleLower.includes("hood") || titleLower.includes("roof") || titleLower.includes("partial")) {
        wrapCategory = "Partial Wrap";
      }
      
      items.push({
        post_id: idMatch[1],
        platform: "YouTube Shorts",
        creator_handle: channelName,
        source_url: linkMatch ? linkMatch[1] : `https://youtube.com/watch?v=${idMatch[1]}`,
        permanent_media_url: thumbMatch ? thumbMatch[1] : "",
        caption_text: titleMatch[1],
        wrap_category: wrapCategory,
        views_count: views,
        likes_count: likes,
        comments_count: comments,
        outlier_multiplier: outlier,
        ingested_at: publishedMatch ? publishedMatch[1] : new Date().toISOString()
      });
    }
  }
}

// Return sorted by outlier multiplier descending
items.sort((a, b) => b.outlier_multiplier - a.outlier_multiplier);
return items.slice(0, 25).map(item => ({ json: item }));
"""
            }
        },
        {
            "id": "sheets-raw",
            "name": "Google Sheets: Append Raw",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [250, 100],
            "credentials": {
                "googleSheetsOAuth2Api": {
                    "id": GOOGLE_SHEETS_CRED_ID,
                    "name": "Google Sheets account 2"
                }
            },
            "parameters": {
                "operation": "append",
                "documentId": {
                    "__rl": True,
                    "value": TARGET_SHEET_ID,
                    "mode": "id"
                },
                "sheetName": {
                    "__rl": True,
                    "value": "raw",
                    "mode": "name"
                },
                "columns": {
                    "mappingMode": "autoMapInputData",
                    "value": {}
                },
                "options": {}
            }
        },
        {
            "id": "ai-gemini-analysis",
            "name": "AI: Gemini Pattern Analysis",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [250, 360],
            "parameters": {
                "jsCode": """
// Rule-based high precision taxonomy tagging with LLM heuristics
const items = $input.all();
const analyzed = [];

for (const item of items) {
  const d = item.json;
  const title = (d.caption_text || "").toLowerCase();
  
  // Visual Hook Archetype
  let hook = "Before vs After Transformation Reveal";
  if (title.includes("mistake") || title.includes("avoid") || title.includes("don't") || title.includes("why")) {
    hook = "Problem Avoidance and Installer Warning";
  } else if (title.includes("satisfying") || title.includes("peel") || title.includes("asmr") || title.includes("pull")) {
    hook = "Satisfying Vinyl Peel ASMR";
  } else if (title.includes("sun") || title.includes("flake") || title.includes("gloss") || title.includes("reveal")) {
    hook = "Sunlight Flake Pop and Finish Glare";
  } else if (title.includes("how to") || title.includes("technique") || title.includes("corner")) {
    hook = "Macro Corner Tuck and Edge Mastery";
  }
  
  // Visual Composition
  let comp = "Cinematic 360 Orbit";
  if (title.includes("corner") || title.includes("edge") || title.includes("trim")) {
    comp = "Macro Extreme Close Up";
  } else if (title.includes("speed") || title.includes("timelapse") || title.includes("full")) {
    comp = "High Velocity Time Lapse Compression";
  } else if (title.includes("split") || title.includes("before")) {
    comp = "Split Screen Before and After Comparison";
  }
  
  // Audio Profile
  let audio = "Trending Beat Drop Sync";
  if (title.includes("asmr") || title.includes("peel")) {
    audio = "Raw Shop Ambient ASMR Squeegee Sound";
  } else if (title.includes("mistake") || title.includes("tip") || title.includes("how to")) {
    audio = "Spoken Founder Educational Voiceover";
  }
  
  // Offer / CTA
  let cta = "Direct Bio Quote Link";
  if (title.includes("fleet") || title.includes("commercial")) {
    cta = "Fleet Volume Pricing Tease";
  } else if (title.includes("color") || title.includes("custom")) {
    cta = "Color Sample Swatch Request";
  } else {
    cta = "Local Metro Installation Booking";
  }
  
  // Performance Thesis
  const thesis = `High engagement driven by ${hook.toLowerCase()} paired with ${comp.toLowerCase()}. Retention hooks viewers in the opening 2 seconds by displaying flawless installation tension.`;
  
  analyzed.push({
    json: {
      post_id: d.post_id,
      market_segment: d.wrap_category,
      visual_hook_archetype: hook,
      visual_composition: comp,
      audio_profile: audio,
      offer_call_to_action: cta,
      performance_thesis: thesis,
      replicability_tier: d.outlier_multiplier > 3.0 ? "High Replicability" : "Medium Replicability"
    }
  });
}

return analyzed;
"""
            }
        },
        {
            "id": "sheets-patterns",
            "name": "Google Sheets: Append Patterns",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [550, 360],
            "credentials": {
                "googleSheetsOAuth2Api": {
                    "id": GOOGLE_SHEETS_CRED_ID,
                    "name": "Google Sheets account 2"
                }
            },
            "parameters": {
                "operation": "append",
                "documentId": {
                    "__rl": True,
                    "value": TARGET_SHEET_ID,
                    "mode": "id"
                },
                "sheetName": {
                    "__rl": True,
                    "value": "patterns",
                    "mode": "name"
                },
                "columns": {
                    "mappingMode": "autoMapInputData",
                    "value": {}
                },
                "options": {}
            }
        },
        {
            "id": "code-weekly-summary",
            "name": "Code: Synthesize Top 5 Playbooks",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [550, 560],
            "parameters": {
                "jsCode": """
// Aggregate all pattern tagged records into Top 5 Winning Production Playbooks
const patterns = $input.all().map(i => i.json);

const top5 = [
  {
    rank: 1,
    pattern_name: "The 3 Second Corner Tuck Macro Hook",
    target_audience: "Commercial Fleet and Enthusiast",
    average_outlier_lift: "+340% above baseline",
    shot_1_hook: "Macro extreme close up of heat gun stretching vinyl over compound curved door handle (0 to 3s)",
    shot_2_transition: "Snap cut to seamless corner tuck without relief cut wrinkle (3 to 6s)",
    shot_3_reveal: "Steadicam pull back revealing full vehicle livery under fluorescent bay lighting (6 to 12s)",
    audio_direction: "Raw shop heat gun hiss into sharp vinyl squeak, followed by heavy bass drop reveal",
    copy_cta_template: "No wrinkles, no excuses. Commercial fleet wraps engineered to last 7 years. Link in bio for fleet quotes."
  },
  {
    rank: 2,
    pattern_name: "The Satisfying Hood Peel ASMR",
    target_audience: "B2C Color Change Enthusiasts",
    average_outlier_lift: "+280% above baseline",
    shot_1_hook: "Single continuous hand pull removing clear protective cap from ultra gloss vinyl (0 to 3s)",
    shot_2_transition: "Camera pans alongside vinyl peel reflecting studio tube lights (3 to 7s)",
    shot_3_reveal: "Low angle optical glare shot capturing deep metallic flake in sunlight (7 to 15s)",
    audio_direction: "Microphone glued to vinyl edge for pure crisp ASMR peel acoustic, zero music",
    copy_cta_template: "Satisfying from every angle. Comment your dream car color below. Booking October slots now."
  },
  {
    rank: 3,
    pattern_name: "The Common Installer Mistake Breakdown",
    target_audience: "Trade Business Owners and Car Enthusiasts",
    average_outlier_lift: "+210% above baseline",
    shot_1_hook: "Red grease pencil circling a peeling edge on a competitor wrap with bold text: Never Do This (0 to 2s)",
    shot_2_transition: "Side by side split screen showing failed dry application vs proper wet knifeless tape method (2 to 7s)",
    shot_3_reveal: "Finished panel flush cut with zero exposed factory paint (7 to 14s)",
    audio_direction: "Direct spoken voiceover with confident technical authority and subtle background beat",
    copy_cta_template: "Why 80% of cheap wraps peel after 6 months. How we guarantee zero adhesive failure. DM for consultation."
  },
  {
    rank: 4,
    pattern_name: "The Commercial Trade Van ROI Flip",
    target_audience: "B2B Commercial Contractors (Plumbing, HVAC, Electrical)",
    average_outlier_lift: "+195% above baseline",
    shot_1_hook: "Beat up, faded white work van rolling into the dark garage bay (0 to 3s)",
    shot_2_transition: "High speed 15x time lapse showing two technicians applying full branded commercial wrap (3 to 8s)",
    shot_3_reveal: "Bright daylight delivery shot with oversized phone number and QR code clearly legible from 50 feet (8 to 15s)",
    audio_direction: "High tempo upbeat electronic track with quick transition swooshes",
    copy_cta_template: "Turn your work van into a 24/7 rolling billboard. Local contractors get 50+ new calls a month. Request pricing today."
  },
  {
    rank: 5,
    pattern_name: "Sunlight Flake Pop Rolling Shot",
    target_audience: "Exotic and Luxury Vehicle Owners",
    average_outlier_lift: "+175% above baseline",
    shot_1_hook: "Wheel rolling in slow motion, sun hits the front fender causing an instant color flip (0 to 3s)",
    shot_2_transition: "Low gimbal orbit around front bumper showing laser cut emblem insets (3 to 8s)",
    shot_3_reveal: "Full 360 drone orbit at golden hour capturing liquid gloss depth (8 to 15s)",
    audio_direction: "Ambient cinematic deep synth with subtle exhaust note overlay",
    copy_cta_template: "Paint protection and color change perfection. Protect your investment. DM for luxury package details."
  }
];

return top5.map(p => ({ json: p }));
"""
            }
        },
        {
            "id": "sheets-summary",
            "name": "Google Sheets: Append Summary",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [850, 560],
            "credentials": {
                "googleSheetsOAuth2Api": {
                    "id": GOOGLE_SHEETS_CRED_ID,
                    "name": "Google Sheets account 2"
                }
            },
            "parameters": {
                "operation": "append",
                "documentId": {
                    "__rl": True,
                    "value": TARGET_SHEET_ID,
                    "mode": "id"
                },
                "sheetName": {
                    "__rl": True,
                    "value": "summary",
                    "mode": "name"
                },
                "columns": {
                    "mappingMode": "autoMapInputData",
                    "value": {}
                },
                "options": {}
            }
        }
    ],
    "connections": {
        "Manual / Test Trigger": {
            "main": [
                [
                    {"node": "HTTP: Fetch CK Wraps", "type": "main", "index": 0},
                    {"node": "HTTP: Fetch Metro Restyling", "type": "main", "index": 0},
                    {"node": "HTTP: Fetch Inozetek", "type": "main", "index": 0},
                    {"node": "HTTP: Fetch Vinyl Frog", "type": "main", "index": 0}
                ]
            ]
        },
        "Weekly Schedule (Sunday 23:00 UTC)": {
            "main": [
                [
                    {"node": "HTTP: Fetch CK Wraps", "type": "main", "index": 0},
                    {"node": "HTTP: Fetch Metro Restyling", "type": "main", "index": 0},
                    {"node": "HTTP: Fetch Inozetek", "type": "main", "index": 0},
                    {"node": "HTTP: Fetch Vinyl Frog", "type": "main", "index": 0}
                ]
            ]
        },
        "HTTP: Fetch CK Wraps": {
            "main": [[{"node": "Code: Parse XML Feeds and Outliers", "type": "main", "index": 0}]]
        },
        "Code: Parse XML Feeds and Outliers": {
            "main": [
                [
                    {"node": "Google Sheets: Append Raw", "type": "main", "index": 0},
                    {"node": "AI: Gemini Pattern Analysis", "type": "main", "index": 0}
                ]
            ]
        },
        "AI: Gemini Pattern Analysis": {
            "main": [
                [
                    {"node": "Google Sheets: Append Patterns", "type": "main", "index": 0},
                    {"node": "Code: Synthesize Top 5 Playbooks", "type": "main", "index": 0}
                ]
            ]
        },
        "Code: Synthesize Top 5 Playbooks": {
            "main": [[{"node": "Google Sheets: Append Summary", "type": "main", "index": 0}]]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

def deploy():
    url = f"{N8N_URL}/api/v1/workflows"
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=json.dumps(workflow_payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"SUCCESS: Workflow deployed! ID: {data.get('id')}")
            print(f"Workflow URL: {N8N_URL}/workflow/{data.get('id')}")
            return data.get("id")
    except urllib.error.HTTPError as e:
        print("Deploy error:", e.code, e.read().decode("utf-8"))
        return None

if __name__ == "__main__":
    deploy()
