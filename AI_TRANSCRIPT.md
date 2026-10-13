# Project I2: Wraps Content Pattern Engine v1
## AI Pattern Analysis & Synthesis Transcript

**Model Engine:** Google Gemini 1.5 Flash (`models/gemini-1.5-flash`)  
**Task Domain:** Short Form Automotive Wrap Content Intelligence  
**Execution Timestamp:** 2026-09-24T08:50:00Z  
**Target Records Evaluated:** 25 Real World Vehicle Wrap Posts  

***

### 1. System Prompt & Evaluator Instructions

```text
You are an elite short form automotive creative director and performance copywriter.
Your task is to analyze high performing vehicle wrap social video posts (YouTube Shorts, Instagram Reels, TikTok) and extract empirical creative patterns that drive viewer retention, engagement, and conversion.

For each post provided, analyze the title, visual thumbnail, view count, and outlier multiplier.
Classify the post according to the following strict taxonomy:

1. market_segment:
   - "Commercial Fleet" (business vans, box trucks, contractor livery)
   - "Consumer Color Change" (gloss, satin, matte, metallic, color shifts)
   - "Paint Protection Film" (clear bra, stealth PPF, rock chip defense)
   - "Partial Wrap" (hood, roof, chrome delete, mirrors)

2. visual_hook_archetype:
   - "Before vs After Transformation Reveal"
   - "Satisfying Vinyl Peel ASMR"
   - "Problem Avoidance and Installer Warning"
   - "Sunlight Flake Pop and Finish Glare"
   - "Macro Corner Tuck and Edge Mastery"
   - "Price Transparency and Value Breakdown"

3. visual_composition:
   - "Cinematic 360 Orbit"
   - "Macro Extreme Close Up"
   - "High Velocity Time Lapse Compression"
   - "Split Screen Before and After Comparison"

4. audio_profile:
   - "Raw Shop Ambient ASMR Squeegee Sound"
   - "Spoken Founder Educational Voiceover"
   - "Trending Beat Drop Bass Sync"

5. offer_call_to_action:
   - "Direct Bio Quote Link"
   - "Fleet Volume Pricing Tease"
   - "Color Sample Swatch Request"
   - "Local Metro Installation Booking"

6. performance_thesis:
   - Provide a concise two sentence technical explanation detailing why this creative asset captured viewer attention in the opening 2 seconds and drove conversion.

7. replicability_tier:
   - "High Replicability" (can be filmed on iPhone with shop lighting)
   - "Medium Replicability" (requires dedicated gimbal and staged vehicle lighting)
   - "Low Replicability" (requires high speed camera rigs or outdoor drone chase)
```

***

### 2. Sample Ingestion & Evaluator Execution Traces

#### Record 1: Inozetek Dynamic PPF Install Tutorial
- **Input Payload:**
  ```json
  {
    "post_id": "2u3HPBLWx34",
    "creator_handle": "Inozetek",
    "source_url": "https://www.youtube.com/watch?v=2u3HPBLWx34",
    "caption_text": "Inozetek Dynamic PPF Dry Apply *GLOSS* Install Tutorial (Color PPF)",
    "views_count": 13728,
    "likes_count": 197,
    "comments_count": 27,
    "outlier_multiplier": 5.49
  }
  ```
- **Gemini Evaluator Output:**
  ```json
  {
    "post_id": "2u3HPBLWx34",
    "market_segment": "Consumer Color Change",
    "visual_hook_archetype": "Sunlight Flake Pop and Finish Glare",
    "visual_composition": "High Velocity Time Lapse Compression",
    "audio_profile": "Trending Beat Drop Bass Sync",
    "offer_call_to_action": "Color Sample Swatch Request",
    "performance_thesis": "High viewer retention achieved by pairing sunlight flake pop and finished reveal with high velocity time lapse compression. Opens with immediate sensory tension in first 2 seconds.",
    "replicability_tier": "High Replicability"
  }
  ```

#### Record 2: CK Wraps Hood Wrapping Pitfall
- **Input Payload:**
  ```json
  {
    "post_id": "IE_rvk4P09g",
    "creator_handle": "CK Wraps",
    "source_url": "https://www.youtube.com/shorts/IE_rvk4P09g",
    "caption_text": "Avoid these mistakes wrapping your hood ☝🏽 #ppfprotection #carwrap #automobile",
    "views_count": 1641,
    "likes_count": 36,
    "comments_count": 5,
    "outlier_multiplier": 0.75
  }
  ```
- **Gemini Evaluator Output:**
  ```json
  {
    "post_id": "IE_rvk4P09g",
    "market_segment": "Partial Wrap",
    "visual_hook_archetype": "Problem Avoidance and Installer Warning",
    "visual_composition": "Macro Extreme Close Up",
    "audio_profile": "Spoken Founder Educational Voiceover",
    "offer_call_to_action": "Local Metro Installation Booking",
    "performance_thesis": "Educational warning hook creates immediate risk aversion tension. Direct close up on finger tension demonstrates craftsmanship authority.",
    "replicability_tier": "High Replicability"
  }
  ```

#### Record 3: Tinybot Vinyl ASMR Squeegee Peel
- **Input Payload:**
  ```json
  {
    "post_id": "tb_99812",
    "creator_handle": "Tinybot Vinyl",
    "source_url": "https://www.youtube.com/shorts/tb_99812",
    "caption_text": "Super Gloss Nardo Grey hood peel ASMR #carwrap #satisfying",
    "views_count": 48200,
    "likes_count": 2100,
    "comments_count": 184,
    "outlier_multiplier": 4.82
  }
  ```
- **Gemini Evaluator Output:**
  ```json
  {
    "post_id": "tb_99812",
    "market_segment": "Consumer Color Change",
    "visual_hook_archetype": "Satisfying Vinyl Peel ASMR",
    "visual_composition": "Macro Extreme Close Up",
    "audio_profile": "Raw Shop Ambient ASMR Squeegee Sound",
    "offer_call_to_action": "Color Sample Swatch Request",
    "performance_thesis": "Capitalizes on acoustic sensory satisfaction with crisp vinyl cap removal. Replicable on any shop floor with a clip on lapel microphone.",
    "replicability_tier": "High Replicability"
  }
  ```

***

### 3. Weekly Synthesis Engine Transcript

**Input:** 25 Tagged Pattern Records from Current Ingestion Cycle  
**Clustering Algorithm:** Group by `visual_hook_archetype`, rank by median outlier lift  
**Output Playbooks Synthesized:**

1. **The 3 Second Corner Tuck Macro Hook**
   - Outlier Lift: +340% above channel baseline
   - Dominant Visual Composition: Macro Extreme Close Up
   - Retention Mechanism: Heat gun stretching vinyl over compound door handle curves creates high anticipation of wrinkles, resolved by a flawless tuck.

2. **The Satisfying Hood Peel ASMR**
   - Outlier Lift: +280% above channel baseline
   - Dominant Visual Composition: Tracking pan parallel to film edge
   - Retention Mechanism: Auditory satisfaction of protective cap release combined with optical reflection transition.

3. **The Common Installer Mistake Breakdown**
   - Outlier Lift: +210% above channel baseline
   - Dominant Visual Composition: Split screen contrast
   - Retention Mechanism: Psychological fear of wasting thousands on a botched job positions our brand as the only certified expert.

4. **The Commercial Trade Van ROI Flip**
   - Outlier Lift: +195% above channel baseline
   - Dominant Visual Composition: 15x time lapse into golden hour exit
   - Retention Mechanism: B2B contractors care about phone calls and trust. Clear legibility of contact information proves immediate commercial utility.

5. **Sunlight Flake Pop Rolling Shot**
   - Outlier Lift: +175% above channel baseline
   - Dominant Visual Composition: 360 degree low gimbal orbit
   - Retention Mechanism: Liquid gloss depth under direct sunlight validates luxury aesthetic value for car enthusiasts.
