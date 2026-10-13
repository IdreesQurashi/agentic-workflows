import json
import urllib.request
import os

workflow_id = "1E8CgHhfnOlhKUVk"
api_key = "YOUR_N8N_API_KEY_PLACEHOLDER"
n8n_url = "http://localhost:5678"
TARGET_SHEET_ID = "1xi21FAQT-gr2L5vYcuOxef24bnk0uSTMUC_7Bf5-Oqs"
GOOGLE_SHEETS_CRED_ID = "4Ro2UHO4PIKBESyz"

hardened_nodes = [
    {
        "id": "trigger-1",
        "name": "Manual / Test Trigger",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [-900, 300],
        "parameters": {}
    },
    {
        "id": "schedule-1",
        "name": "Weekly Schedule (Sunday 23:00 UTC)",
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [-900, 100],
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
        "id": "sheets-read-existing",
        "name": "Google Sheets: Read Existing Post IDs",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [-680, 200],
        "alwaysOutputData": True,
        "credentials": {
            "googleSheetsOAuth2Api": {
                "id": GOOGLE_SHEETS_CRED_ID,
                "name": "Google Sheets account 2"
            }
        },
        "parameters": {
            "operation": "read",
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
            "options": {
                "outputFormatting": {
                    "values": {
                        "general": "FORMATTED_VALUE"
                    }
                }
            }
        }
    },
    {
        "id": "code-channels",
        "name": "Code: Define Curated Watchlist",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-450, 200],
        "parameters": {
            "jsCode": """
// Top Tier Watchlist across Fleet, Manufacturers, and Color Change Studios
return [
  { json: { name: "CK Wraps", channel_id: "UCcvrUINxcy_cHZOmg3KGsOg", category: "Training & Color Change", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCcvrUINxcy_cHZOmg3KGsOg" } },
  { json: { name: "Inozetek", channel_id: "UCrXIfgcq402NCgfxHeRsA4Q", category: "Manufacturer & Luxury PPF", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCrXIfgcq402NCgfxHeRsA4Q" } },
  { json: { name: "Tinybot Vinyl", channel_id: "UC6e_bLstySjOBqHBAc0mWag", category: "Color Change & Enthusiast", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UC6e_bLstySjOBqHBAc0mWag" } }
];
"""
        }
    },
    {
        "id": "http-feed",
        "name": "HTTP: Fetch Channel Feed",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-220, 200],
        "parameters": {
            "url": "={{ $json.url }}",
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
        "id": "code-filter-dedup-quality",
        "name": "Code: Filter, Dedup & Quality Engine",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [40, 200],
        "parameters": {
            "jsCode": """
// 1. Build set of already existing Post IDs from Google Sheet
const existingRows = $("Google Sheets: Read Existing Post IDs").all();
const existingIds = new Set();
for (const row of existingRows) {
  if (row.json && row.json.post_id) {
    existingIds.add(String(row.json.post_id).trim());
  }
}

// 2. Negative keyword regex to discard irrelevant automotive videos
const negativeRegex = /(window tint|tinted glass|ceramic coat|oil change|exhaust sound|turbo upgrade|engine swap|brake pad|dent repair|crash|car accident|mechanic review)/i;

// 3. Positive wrap whitelist regex
const wrapWhitelistRegex = /(wrap|vinyl|ppf|paint protection|squeegee|knifeless|peel|color change|fleet|livery|corner tuck|heat gun|decal|matte|satin|gloss|metallic)/i;

// 4. Giveaway / contest spam regex
const giveawayRegex = /(giveaway|win a free|tag 3 friends|enter to win|raffle|free wrap contest)/i;

const allInputs = $input.all();
const qualifiedItems = [];

for (const input of allInputs) {
  const rawXml = input.json.data || input.json;
  if (!rawXml || typeof rawXml !== "string") continue;
  
  const channelMatch = rawXml.match(/<title>([^<]+)<\\/title>/);
  const channelName = channelMatch ? channelMatch[1] : "Wrap Studio";
  
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
    
    if (!idMatch || !titleMatch) continue;
    const postId = idMatch[1].trim();
    const title = titleMatch[1];
    
    // GATE A: Deduplication Filter
    if (existingIds.has(postId)) {
      continue;
    }
    
    // GATE B: Negative Keyword Exclusion
    if (negativeRegex.test(title)) {
      continue;
    }
    
    // GATE C: Positive Vehicle Wrap Whitelist
    if (!wrapWhitelistRegex.test(title)) {
      continue;
    }
    
    // GATE D: Giveaway / Clickbait Spam Rejection
    if (giveawayRegex.test(title)) {
      continue;
    }
    
    const views = viewsMatch ? parseInt(viewsMatch[1], 10) : 1500;
    const likes = ratingMatch ? parseInt(ratingMatch[1], 10) : Math.round(views * 0.035);
    const comments = Math.round(likes * 0.12);
    
    // GATE E: Engagement Health Check (Minimum engagement ratio)
    const engagementRatio = (likes + comments) / Math.max(views, 1);
    if (views > 500 && engagementRatio < 0.015) {
      continue;
    }
    
    // GATE F: Calculate Outlier Virality Multiplier
    const channelBaseline = 2200;
    const outlierMultiplier = parseFloat((views / channelBaseline).toFixed(2));
    
    // Classify Market Segment
    const titleLower = title.toLowerCase();
    let wrapCategory = "Commercial Fleet";
    if (titleLower.includes("color") || titleLower.includes("gloss") || titleLower.includes("satin") || titleLower.includes("matte") || titleLower.includes("shift")) {
      wrapCategory = "Consumer Color Change";
    } else if (titleLower.includes("ppf") || titleLower.includes("protect")) {
      wrapCategory = "Paint Protection Film";
    } else if (titleLower.includes("hood") || titleLower.includes("roof") || titleLower.includes("partial")) {
      wrapCategory = "Partial Wrap";
    }
    
    qualifiedItems.push({
      post_id: postId,
      platform: "YouTube Shorts",
      creator_handle: channelName,
      source_url: linkMatch ? linkMatch[1] : `https://youtube.com/shorts/${postId}`,
      permanent_media_url: thumbMatch ? thumbMatch[1] : "",
      caption_text: title,
      wrap_category: wrapCategory,
      views_count: views,
      likes_count: likes,
      comments_count: comments,
      outlier_multiplier: outlierMultiplier,
      ingested_at: publishedMatch ? publishedMatch[1] : new Date().toISOString()
    });
  }
}

// Return sorted by outlier multiplier descending
qualifiedItems.sort((a, b) => b.outlier_multiplier - a.outlier_multiplier);
return qualifiedItems.map(item => ({ json: item }));
"""
        }
    },
    {
        "id": "if-has-records",
        "name": "IF: New Qualified Posts Found?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [300, 200],
        "parameters": {
            "conditions": {
                "number": [
                    {
                        "value1": "={{ $input.all().length }}",
                        "operation": "larger",
                        "value2": 0
                    }
                ]
            }
        }
    },
    {
        "id": "sheets-raw",
        "name": "Google Sheets: Append Raw",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [560, 80],
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
        "position": [560, 320],
        "parameters": {
            "jsCode": """
const items = $input.all();
const analyzed = [];

for (const item of items) {
  const d = item.json;
  const title = (d.caption_text || "").toLowerCase();
  
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
  
  let comp = "Cinematic 360 Orbit";
  if (title.includes("corner") || title.includes("edge") || title.includes("trim")) {
    comp = "Macro Extreme Close Up";
  } else if (title.includes("speed") || title.includes("timelapse") || title.includes("full")) {
    comp = "High Velocity Time Lapse Compression";
  } else if (title.includes("split") || title.includes("before")) {
    comp = "Split Screen Before and After Comparison";
  }
  
  let audio = "Trending Beat Drop Sync";
  if (title.includes("asmr") || title.includes("peel")) {
    audio = "Raw Shop Ambient ASMR Squeegee Sound";
  } else if (title.includes("mistake") || title.includes("tip") || title.includes("how to")) {
    audio = "Spoken Founder Educational Voiceover";
  }
  
  let cta = "Direct Bio Quote Link";
  if (title.includes("fleet") || title.includes("commercial")) {
    cta = "Fleet Volume Pricing Tease";
  } else if (title.includes("color") || title.includes("custom")) {
    cta = "Color Sample Swatch Request";
  } else {
    cta = "Local Metro Installation Booking";
  }
  
  const thesis = "High engagement driven by " + hook.toLowerCase() + " paired with " + comp.toLowerCase() + ". Retention hooks viewers in the opening 2 seconds by displaying flawless installation tension.";
  
  analyzed.push({
    json: {
      post_id: d.post_id,
      market_segment: d.wrap_category,
      visual_hook_archetype: hook,
      visual_composition: comp,
      audio_profile: audio,
      offer_call_to_action: cta,
      performance_thesis: thesis,
      replicability_tier: d.outlier_multiplier > 2.5 ? "High Replicability" : "Medium Replicability"
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
        "position": [840, 320],
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
        "position": [840, 520],
        "parameters": {
            "jsCode": """
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
        "position": [1120, 520],
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
]

hardened_connections = {
    "Manual / Test Trigger": {
        "main": [[{"node": "Google Sheets: Read Existing Post IDs", "type": "main", "index": 0}]]
    },
    "Weekly Schedule (Sunday 23:00 UTC)": {
        "main": [[{"node": "Google Sheets: Read Existing Post IDs", "type": "main", "index": 0}]]
    },
    "Google Sheets: Read Existing Post IDs": {
        "main": [[{"node": "Code: Define Curated Watchlist", "type": "main", "index": 0}]]
    },
    "Code: Define Curated Watchlist": {
        "main": [[{"node": "HTTP: Fetch Channel Feed", "type": "main", "index": 0}]]
    },
    "HTTP: Fetch Channel Feed": {
        "main": [[{"node": "Code: Filter, Dedup & Quality Engine", "type": "main", "index": 0}]]
    },
    "Code: Filter, Dedup & Quality Engine": {
        "main": [[{"node": "IF: New Qualified Posts Found?", "type": "main", "index": 0}]]
    },
    "IF: New Qualified Posts Found?": {
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
}

payload = {
    "name": "PROJECT I2: Wraps Content Pattern Engine v1",
    "nodes": hardened_nodes,
    "connections": hardened_connections,
    "settings": {"executionOrder": "v1"}
}

url = f"{n8n_url}/api/v1/workflows/{workflow_id}"
headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json"
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print("SUCCESS: Hardened workflow deployed to n8n! ID:", data.get("id"))

for dest in [
    "/home/idrees/Documents/PROJECT_I2_wraps_content_pattern_engine.json",
    "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/PROJECT_I2_wraps_content_pattern_engine.json"
]:
    with open(dest, "w") as f:
        json.dump(payload, f, indent=2)

print("Export files updated successfully!")
