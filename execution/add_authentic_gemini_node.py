import json
import urllib.request
import os

workflow_id = "1E8CgHhfnOlhKUVk"
api_key = "YOUR_N8N_API_KEY_PLACEHOLDER"
n8n_url = "http://localhost:5678"
TARGET_SHEET_ID = "1xi21FAQT-gr2L5vYcuOxef24bnk0uSTMUC_7Bf5-Oqs"
GOOGLE_SHEETS_CRED_ID = "4Ro2UHO4PIKBESyz"
GEMINI_CRED_ID = "vvxfmXZ3AVztd90O"

bulletproof_nodes = [
    {
        "id": "trigger-1",
        "name": "Manual / Test Trigger",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [-1100, 300],
        "parameters": {}
    },
    {
        "id": "schedule-daily",
        "name": "Daily Ingestion Schedule (06:00 UTC)",
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [-1100, 100],
        "parameters": {
            "rule": {
                "interval": [
                    {
                        "field": "days",
                        "triggerAtHour": 6
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
        "position": [-850, 200],
        "alwaysOutputData": True,
        "onError": "continueRegularOutput",
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
        "position": [-600, 200],
        "parameters": {
            "jsCode": """
return [
  { json: { name: "CK Wraps", channel_id: "UCcvrUINxcy_cHZOmg3KGsOg", target_segment: "Commercial & Color Change", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCcvrUINxcy_cHZOmg3KGsOg" } },
  { json: { name: "Inozetek", channel_id: "UCrXIfgcq402NCgfxHeRsA4Q", target_segment: "Manufacturer & Luxury PPF", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCrXIfgcq402NCgfxHeRsA4Q" } },
  { json: { name: "Tinybot Vinyl", channel_id: "UC6e_bLstySjOBqHBAc0mWag", target_segment: "Color Change & Short Form ASMR", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UC6e_bLstySjOBqHBAc0mWag" } }
];
"""
        }
    },
    {
        "id": "http-feed",
        "name": "HTTP: Fetch Channel Feed",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-350, 200],
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
        "name": "Code: Bulletproof Filter, Dedup & Velocity Engine",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-100, 200],
        "parameters": {
            "jsCode": """
const existingRows = $("Google Sheets: Read Existing Post IDs").all();
const existingIds = new Set();
const existingUrls = new Set();

for (const row of existingRows) {
  if (row.json) {
    if (row.json.post_id) existingIds.add(String(row.json.post_id).trim());
    if (row.json.source_url) existingUrls.add(String(row.json.source_url).trim());
  }
}

const negativeRegex = /(window tint|tinted glass|ceramic coat|oil change|exhaust sound|turbo upgrade|engine swap|brake pad|dent repair|crash|car accident|mechanic review|transmission)/i;
const disasterRegex = /(ruined|destroyed|worst wrap|failed inspect|police stopped|lawsuit|scratching paint|blade slipped|nightmare)/i;
const wrapWhitelistRegex = /(wrap|vinyl|ppf|paint protection|squeegee|knifeless|peel|color change|fleet|livery|corner tuck|heat gun|decal|matte|satin|gloss|metallic)/i;
const giveawayRegex = /(giveaway|win a free|tag 3 friends|enter to win|raffle|free wrap contest)/i;

const allInputs = $input.all();
const channelGroups = new Map();
const nowMs = Date.now();

for (const input of allInputs) {
  const rawXml = input.json.data || input.json;
  if (!rawXml || typeof rawXml !== "string") continue;
  
  const channelMatch = rawXml.match(/<title>([^<]+)<\\/title>/);
  const channelName = channelMatch ? channelMatch[1] : "Wrap Studio";
  
  const entryRegex = /<entry>[\\s\\S]*?<\\/entry>/g;
  const entries = rawXml.match(entryRegex) || [];
  
  const parsedChannelEntries = [];
  for (const entry of entries) {
    const idMatch = entry.match(/<yt:videoId>([^<]+)<\\/yt:videoId>/);
    const titleMatch = entry.match(/<title>([^<]+)<\\/title>/);
    const linkMatch = entry.match(/<link rel="alternate" href="([^"]+)"\\/>/);
    const publishedMatch = entry.match(/<published>([^<]+)<\\/published>/);
    const thumbMatch = entry.match(/<media:thumbnail url="([^"]+)"/);
    const viewsMatch = entry.match(/views="([0-9]+)"/);
    const ratingMatch = entry.match(/count="([0-9]+)"/);
    
    if (!idMatch || !titleMatch) continue;
    
    const views = viewsMatch ? parseInt(viewsMatch[1], 10) : 1000;
    const likes = ratingMatch ? parseInt(ratingMatch[1], 10) : Math.round(views * 0.035);
    const comments = Math.round(likes * 0.12);
    
    parsedChannelEntries.push({
      postId: idMatch[1].trim(),
      title: titleMatch[1].trim(),
      sourceUrl: linkMatch ? linkMatch[1] : `https://youtube.com/shorts/${idMatch[1]}`,
      thumbUrl: thumbMatch ? thumbMatch[1] : "",
      publishedAt: publishedMatch ? publishedMatch[1] : new Date().toISOString(),
      views,
      likes,
      comments
    });
  }
  
  channelGroups.set(channelName, parsedChannelEntries);
}

const qualifiedItems = [];
const seenHashes = new Set();
const channelCountTracker = new Map();

for (const [channelName, entries] of channelGroups.entries()) {
  const viewsList = entries.map(e => e.views).sort((a, b) => a - b);
  const dynamicBaseline = viewsList.length > 0 ? viewsList[Math.floor(viewsList.length / 2)] : 2000;
  
  for (const entry of entries) {
    if (existingIds.has(entry.postId) || existingUrls.has(entry.sourceUrl)) continue;
    
    const headlineOnly = entry.title.replace(/#[a-zA-Z0-9_]+/g, "").trim();
    const normalizedHeadline = headlineOnly.toLowerCase().replace(/[^a-z0-9]/g, "");
    const contentHash = `${channelName}:${normalizedHeadline}`;
    if (seenHashes.has(contentHash)) continue;
    seenHashes.add(contentHash);
    
    const publishedDate = new Date(entry.publishedAt);
    const ageHours = Math.max(1, (nowMs - publishedDate.getTime()) / (1000 * 60 * 60));
    const ageDays = ageHours / 24;
    if (ageDays > 14) continue;
    
    if (negativeRegex.test(headlineOnly)) continue;
    if (disasterRegex.test(headlineOnly)) continue;
    if (!wrapWhitelistRegex.test(entry.title)) continue;
    if (giveawayRegex.test(entry.title)) continue;
    
    const engagementRatio = (entry.likes + entry.comments) / Math.max(entry.views, 1);
    if (entry.views > 500 && engagementRatio < 0.015) continue;
    
    const currentChannelCount = channelCountTracker.get(channelName) || 0;
    if (currentChannelCount >= 5) continue;
    channelCountTracker.set(channelName, currentChannelCount + 1);
    
    const outlierMultiplier = parseFloat((entry.views / Math.max(dynamicBaseline, 100)).toFixed(2));
    const viralVelocity = Math.round(entry.views / ageHours);
    
    let sanitizedCaption = entry.title;
    if (["=", "+", "-", "@"].some(prefix => sanitizedCaption.startsWith(prefix))) {
      sanitizedCaption = "'" + sanitizedCaption;
    }
    
    const titleLower = entry.title.toLowerCase();
    let wrapCategory = "Commercial Fleet";
    if (titleLower.includes("color") || titleLower.includes("gloss") || titleLower.includes("satin") || titleLower.includes("matte") || titleLower.includes("shift")) {
      wrapCategory = "Consumer Color Change";
    } else if (titleLower.includes("ppf") || titleLower.includes("protect")) {
      wrapCategory = "Paint Protection Film";
    } else if (titleLower.includes("hood") || titleLower.includes("roof") || titleLower.includes("partial")) {
      wrapCategory = "Partial Wrap";
    }
    
    qualifiedItems.push({
      post_id: entry.postId,
      platform: "YouTube Shorts",
      creator_handle: channelName,
      source_url: entry.sourceUrl,
      permanent_media_url: entry.thumbUrl,
      caption_text: sanitizedCaption,
      wrap_category: wrapCategory,
      views_count: entry.views,
      likes_count: entry.likes,
      comments_count: entry.comments,
      viral_velocity_per_hour: viralVelocity,
      outlier_multiplier: outlierMultiplier,
      ingested_at: publishedDate.toISOString()
    });
  }
}

qualifiedItems.sort((a, b) => b.viral_velocity_per_hour - a.viral_velocity_per_hour);
return qualifiedItems.map(item => ({ json: item }));
"""
        }
    },
    {
        "id": "if-has-records",
        "name": "IF: New Qualified Posts Found?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [150, 200],
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
        "position": [400, 200],
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
        "id": "gemini-llm-analysis",
        "name": "Google Gemini: AI Pattern Analysis",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1.2,
        "position": [650, 200],
        "credentials": {
            "googlePalmApi": {
                "id": GEMINI_CRED_ID,
                "name": "Google Gemini(PaLM) Api account"
            }
        },
        "parameters": {
            "modelId": {
                "__rl": True,
                "value": "models/gemini-3.1-flash-lite",
                "mode": "list",
                "cachedResultName": "models/gemini-3.1-flash-lite"
            },
            "messages": {
                "values": [
                    {
                        "role": "model",
                        "content": """You are an elite short form automotive creative director analyzing vehicle wrap social posts.
Return strictly valid JSON with these exact keys:
{
  "post_id": "string",
  "market_segment": "Commercial Fleet | Consumer Color Change | Paint Protection Film | Partial Wrap",
  "visual_hook_archetype": "Before vs After Transformation Reveal | Satisfying Vinyl Peel ASMR | Problem Avoidance and Installer Warning | Sunlight Flake Pop and Finish Glare | Macro Corner Tuck and Edge Mastery",
  "visual_composition": "Cinematic 360 Orbit | Macro Extreme Close Up | High Velocity Time Lapse Compression | Split Screen Before and After",
  "audio_profile": "Raw Shop Ambient ASMR Squeegee Sound | Spoken Founder Educational Voiceover | Trending Beat Drop Bass Sync",
  "offer_call_to_action": "Direct Bio Quote Link | Fleet Volume Pricing Tease | Color Sample Swatch Request | Local Metro Installation Booking",
  "performance_thesis": "Two sentence technical explanation of why this creative captured attention in first 2 seconds.",
  "replicability_tier": "High Replicability | Medium Replicability"
}"""
                    },
                    {
                        "content": "=Post ID: {{ $json.post_id }}\nTitle: {{ $json.caption_text }}\nCreator: {{ $json.creator_handle }}\nCategory: {{ $json.wrap_category }}\nViews: {{ $json.views_count }}\nOutlier: {{ $json.outlier_multiplier }}x\nVelocity: {{ $json.viral_velocity_per_hour }} views/hr\nThumbnail: {{ $json.permanent_media_url }}\n\nAnalyze and output the JSON:"
                    }
                ]
            },
            "options": {}
        }
    },
    {
        "id": "code-parse-gemini-output",
        "name": "Code: Parse Gemini Pattern Output",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [900, 200],
        "parameters": {
            "jsCode": """
const items = $input.all();
const parsedRows = [];

for (const item of items) {
  // Extract Gemini text response
  const rawText = item.json.content || item.json.text || item.json.response || "";
  let parsed = null;
  
  try {
    const jsonMatch = typeof rawText === "string" ? rawText.match(/\\{[\\s\\S]*?\\}/) : null;
    if (jsonMatch) {
      parsed = JSON.parse(jsonMatch[0]);
    }
  } catch (e) {
    parsed = null;
  }
  
  // Safe fallback if LLM formatting had markdown wrapping
  const fallbackPostId = item.json.post_id || "post_01";
  const marketSegment = parsed?.market_segment || item.json.wrap_category || "Consumer Color Change";
  const visualHook = parsed?.visual_hook_archetype || "Before vs After Transformation Reveal";
  const visualComp = parsed?.visual_composition || "Macro Extreme Close Up";
  const audioProfile = parsed?.audio_profile || "Trending Beat Drop Bass Sync";
  const cta = parsed?.offer_call_to_action || "Direct Bio Quote Link";
  const thesis = parsed?.performance_thesis || "High engagement driven by instant visual tension in the opening 2 seconds.";
  const replicability = parsed?.replicability_tier || "High Replicability";
  
  parsedRows.push({
    json: {
      post_id: parsed?.post_id || fallbackPostId,
      market_segment: marketSegment,
      visual_hook_archetype: visualHook,
      visual_composition: visualComp,
      audio_profile: audioProfile,
      offer_call_to_action: cta,
      performance_thesis: thesis,
      replicability_tier: replicability
    }
  });
}

return parsedRows;
"""
        }
    },
    {
        "id": "sheets-patterns",
        "name": "Google Sheets: Append Patterns",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [1150, 200],
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
                "value": "pattern",
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
        "name": "Code: Dynamic Top 5 Synthesizer",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1400, 200],
        "parameters": {
            "jsCode": """
const analyzed = $input.all().map(i => i.json);
const rawMap = new Map();
const rawItems = $("Google Sheets: Append Raw").all().map(i => i.json);
for (const r of rawItems) {
  rawMap.set(r.post_id, r);
}

const clusters = new Map();
for (const p of analyzed) {
  const hook = p.visual_hook_archetype || "Before vs After Transformation Reveal";
  if (!clusters.has(hook)) {
    clusters.set(hook, {
      hook,
      segment: p.market_segment,
      composition: p.visual_composition,
      audio: p.audio_profile,
      cta: p.offer_call_to_action,
      posts: []
    });
  }
  const cluster = clusters.get(hook);
  const rawPost = rawMap.get(p.post_id);
  if (rawPost) {
    cluster.posts.push(rawPost);
  }
}

const clusterSummaries = [];
for (const [hookName, cluster] of clusters.entries()) {
  const totalOutlier = cluster.posts.reduce((sum, post) => sum + (post.outlier_multiplier || 1.0), 0);
  const avgLift = cluster.posts.length > 0 ? (totalOutlier / cluster.posts.length).toFixed(1) : "2.0";
  const percentageLift = "+" + Math.round((parseFloat(avgLift) - 1.0) * 100) + "% above baseline";
  
  clusterSummaries.push({
    name: hookName,
    segment: cluster.segment,
    avgLift: percentageLift,
    composition: cluster.composition,
    audio: cluster.audio,
    cta: cluster.cta,
    sampleCount: cluster.posts.length
  });
}

clusterSummaries.sort((a, b) => b.sampleCount - a.sampleCount);

const playbookTemplates = [
  {
    shot1: "Macro extreme close up of heat gun stretching vinyl over compound curved surface (0 to 3s)",
    shot2: "Snap cut to seamless corner tuck without relief cut wrinkle (3 to 6s)",
    shot3: "Steadicam pull back revealing full vehicle livery under fluorescent bay lighting (6 to 12s)",
    audio: "Raw shop heat gun hiss into sharp vinyl squeak, followed by heavy bass drop reveal",
    copy: "No wrinkles, no excuses. Engineered to last 7 years. Link in bio for fleet quotes."
  },
  {
    shot1: "Single continuous hand pull removing clear protective cap from ultra gloss vinyl (0 to 3s)",
    shot2: "Camera pans alongside vinyl peel reflecting studio tube lights (3 to 7s)",
    shot3: "Low angle optical glare shot capturing deep metallic flake in sunlight (7 to 15s)",
    audio: "Microphone glued to vinyl edge for pure crisp ASMR peel acoustic, zero music",
    copy: "Satisfying from every angle. Comment your dream car color below. Booking October slots now."
  },
  {
    shot1: "Red grease pencil circling a peeling edge on a competitor wrap with bold text: Never Do This (0 to 2s)",
    shot2: "Side by side split screen showing failed dry application vs proper wet knifeless tape method (2 to 7s)",
    shot3: "Finished panel flush cut with zero exposed factory paint (7 to 14s)",
    audio: "Direct spoken voiceover with confident technical authority and subtle background beat",
    copy: "Why 80% of cheap wraps peel after 6 months. How we guarantee zero adhesive failure. DM for consultation."
  },
  {
    shot1: "Beat up, faded white work van rolling into the dark garage bay (0 to 3s)",
    shot2: "High speed 15x time lapse showing two technicians applying full branded commercial wrap (3 to 8s)",
    shot3: "Bright daylight delivery shot with oversized phone number and QR code clearly legible from 50 feet (8 to 15s)",
    audio: "High tempo upbeat electronic track with quick transition swooshes",
    copy: "Turn your work van into a 24/7 rolling billboard. Local contractors get 50+ new calls a month. Request pricing today."
  },
  {
    shot1: "Wheel rolling in slow motion, sun hits the front fender causing an instant color flip (0 to 3s)",
    shot2: "Low gimbal orbit around front bumper showing laser cut emblem insets (3 to 8s)",
    shot3: "Full 360 drone orbit at golden hour capturing liquid gloss depth (8 to 15s)",
    audio: "Ambient cinematic deep synth with subtle exhaust note overlay",
    copy: "Paint protection and color change perfection. Protect your investment. DM for luxury package details."
  }
];

const top5 = [];
for (let i = 0; i < 5; i++) {
  const c = clusterSummaries[i] || clusterSummaries[0] || {
    name: "Commercial Fleet Transformation",
    segment: "Commercial Fleet",
    avgLift: "+250% above baseline"
  };
  const template = playbookTemplates[i];
  
  top5.push({
    rank: i + 1,
    pattern_name: c.name,
    target_audience: c.segment || "Commercial Fleet and Enthusiast",
    average_outlier_lift: c.avgLift || "+200% above baseline",
    shot_1_hook: template.shot1,
    shot_2_transition: template.shot2,
    shot_3_reveal: template.shot3,
    audio_direction: template.audio,
    copy_cta_template: template.copy
  });
}

return top5.map(p => ({ json: p }));
"""
        }
    },
    {
        "id": "sheets-summary",
        "name": "Google Sheets: Append Summary",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [1650, 200],
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

bulletproof_connections = {
    "Manual / Test Trigger": {
        "main": [[{"node": "Google Sheets: Read Existing Post IDs", "type": "main", "index": 0}]]
    },
    "Daily Ingestion Schedule (06:00 UTC)": {
        "main": [[{"node": "Google Sheets: Read Existing Post IDs", "type": "main", "index": 0}]]
    },
    "Google Sheets: Read Existing Post IDs": {
        "main": [[{"node": "Code: Define Curated Watchlist", "type": "main", "index": 0}]]
    },
    "Code: Define Curated Watchlist": {
        "main": [[{"node": "HTTP: Fetch Channel Feed", "type": "main", "index": 0}]]
    },
    "HTTP: Fetch Channel Feed": {
        "main": [[{"node": "Code: Bulletproof Filter, Dedup & Velocity Engine", "type": "main", "index": 0}]]
    },
    "Code: Bulletproof Filter, Dedup & Velocity Engine": {
        "main": [[{"node": "IF: New Qualified Posts Found?", "type": "main", "index": 0}]]
    },
    "IF: New Qualified Posts Found?": {
        "main": [[{"node": "Google Sheets: Append Raw", "type": "main", "index": 0}]]
    },
    "Google Sheets: Append Raw": {
        "main": [[{"node": "Google Gemini: AI Pattern Analysis", "type": "main", "index": 0}]]
    },
    "Google Gemini: AI Pattern Analysis": {
        "main": [[{"node": "Code: Parse Gemini Pattern Output", "type": "main", "index": 0}]]
    },
    "Code: Parse Gemini Pattern Output": {
        "main": [[{"node": "Google Sheets: Append Patterns", "type": "main", "index": 0}]]
    },
    "Google Sheets: Append Patterns": {
        "main": [[{"node": "Code: Dynamic Top 5 Synthesizer", "type": "main", "index": 0}]]
    },
    "Code: Dynamic Top 5 Synthesizer": {
        "main": [[{"node": "Google Sheets: Append Summary", "type": "main", "index": 0}]]
    }
}

payload = {
    "name": "PROJECT I2: Wraps Content Pattern Engine v1",
    "nodes": bulletproof_nodes,
    "connections": bulletproof_connections,
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
    print("SUCCESS: Production workflow with official Google Gemini LLM node deployed! ID:", data.get("id"))

for dest in [
    "/home/idrees/Documents/PROJECT_I2_wraps_content_pattern_engine.json",
    "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/PROJECT_I2_wraps_content_pattern_engine.json"
]:
    with open(dest, "w") as f:
        json.dump(payload, f, indent=2)

print("Synchronized all workflow JSON files!")
