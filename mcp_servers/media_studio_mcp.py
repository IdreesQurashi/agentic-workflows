import subprocess
import os
import json
import time
import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MediaStudio")

OUTPUT_DIR = "/home/idrees/Antigravity/storage/media_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_PLACEHOLDER")

def format_srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms >= 1000:
        ms = 999
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"

@mcp.tool()
def download_youtube_media(youtube_url: str, extract_audio_only: bool = False, filename_prefix: str = "yt_media") -> str:
    """Download audio (MP3) or full video (MP4) from YouTube using yt-dlp."""
    try:
        out_template = os.path.join(OUTPUT_DIR, f"{filename_prefix}_%(id)s.%(ext)s")
        if extract_audio_only:
            cmd = ["/home/idrees/.local/bin/yt-dlp", "-x", "--audio-format", "mp3", "-o", out_template, youtube_url]
        else:
            cmd = ["/home/idrees/.local/bin/yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "-o", out_template, youtube_url]
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            return f"Media downloaded successfully into: {OUTPUT_DIR}"
        return f"Download failed: {result.stderr[:300]}"
    except Exception as e:
        return f"Error downloading media: {e}"

@mcp.tool()
def inspect_media_metadata(file_path: str) -> str:
    """Get exact duration, resolution, codecs, frame rate, and bitrates of any video/audio file."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File does not exist at {file_path}"
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,size,bit_rate",
            "-show_entries", "stream=width,height,codec_name,r_frame_rate,channels,sample_rate",
            "-of", "json", file_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout
        return f"ffprobe error: {res.stderr}"
    except Exception as e:
        return f"Media inspection error: {e}"

@mcp.tool()
def inspect_audio_loudness(file_path: str) -> str:
    """Measure EBU R128 integrated loudness (LUFS), Loudness Range (LRA), and True Peak (dBTP)."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File does not exist at {file_path}"
        cmd = ["ffmpeg", "-i", file_path, "-af", "loudnorm=I=-14:LRA=7:tp=-1.5:print_format=json", "-f", "null", "-"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        # Parse JSON block from stderr
        lines = res.stderr.splitlines()
        json_lines = []
        capture = False
        for l in lines:
            if "{" in l:
                capture = True
            if capture:
                json_lines.append(l)
            if "}" in l and capture:
                break
        return "\n".join(json_lines) if json_lines else res.stderr[-400:]
    except Exception as e:
        return f"Loudness inspection error: {e}"

@mcp.tool()
def analyze_video_virality(file_path: str, target_platform: str = "YouTube Shorts / TikTok") -> str:
    """
    Multimodal AI analysis using Gemini 3.6 Flash:
    Extracts 0-3s Hook, Engagement Arc, Payoff Climax, Exact Optimal 25-45s Timestamps, and Curiosity Banner.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
        
        uploaded_file = client.files.upload(file=file_path)
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(3)
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
            return "File processing failed on Gemini server."

        prompt = f"""
You are an elite viral video editor and algorithmic retention strategist for {target_platform}.
Analyze this media file thoroughly and extract the single highest-converting viral short clip (duration strictly between 24 and 45 seconds).

Return valid JSON with:
{{
  "hook_analysis": {{
    "hook_text": "Exact first words or action in the first 0-3 seconds",
    "hook_score": 95,
    "why_it_hooks": "Psychological trigger explaining why viewers stop scrolling"
  }},
  "engagement_arc": {{
    "core_conflict_or_insight": "What keeps retention high between 3s and 30s",
    "pacing_rating": "Fast"
  }},
  "payoff": {{
    "climax_quote": "The peak punchline, debate climax, or insight delivery",
    "payoff_score": 95
  }},
  "best_clip_window": {{
    "start_seconds": 0.0,
    "end_seconds": 30.0,
    "duration_seconds": 30.0,
    "start_timestamp": "MM:SS",
    "end_timestamp": "MM:SS"
  }},
  "recommended_hook_banner": "PUNCHY 3-5 WORD UPPERCASE BANNER WITH EMOJI",
  "overall_virality_score": 95
}}
"""
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[uploaded_file, prompt]
        )
        return response.text
    except Exception as e:
        return f"Error analyzing video virality: {e}"

@mcp.tool()
def score_transcript_virality(transcript_text: str) -> str:
    """Local algorithmic scoring of transcript text for hook strength, keyword density, pacing, and virality index."""
    try:
        hook_keywords = [
            "why", "how", "what", "secret", "truth", "money", "billion", "million",
            "dollar", "scam", "racist", "hate", "women", "men", "girls", "cheat",
            "crazy", "insane", "never", "police", "jail", "fight", "banned", "danger",
            "trans", "trump", "israel", "muslim", "jewish", "oppressor", "exposed", "fake", "matrix"
        ]
        words = transcript_text.split()
        total_words = len(words)
        first_10_words = " ".join(words[:10]).lower()
        
        hook_score = 40.0
        for kw in hook_keywords:
            if kw in first_10_words:
                hook_score += 20.0
        if any(p in first_10_words for p in ["?", "!"]):
            hook_score += 15.0
        hook_score = min(100.0, hook_score)
        
        keyword_hits = [w for w in words if w.lower().strip(".,!?") in hook_keywords]
        keyword_density_score = min(100.0, (len(keyword_hits) / max(1, total_words)) * 500.0)
        
        composite_score = round((hook_score * 0.5) + (keyword_density_score * 0.5), 1)
        
        result = {
            "total_words": total_words,
            "hook_score": hook_score,
            "keyword_density_score": keyword_density_score,
            "virality_score": composite_score,
            "detected_power_keywords": list(set(keyword_hits))
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error scoring transcript: {e}"

@mcp.tool()
def generate_kinetic_captions(video_path: str, start_seconds: float, end_seconds: float, output_srt_path: str, output_ass_path: str, banner_text: str = "", layout_preset: str = "split") -> str:
    """Generate kinetic ASS and SRT subtitles with word-level timestamps, yellow keyword pop, and safe-zone margins."""
    try:
        import whisper
        dur = end_seconds - start_seconds
        temp_wav = f"/tmp/mcp_slice_{int(start_seconds)}_{int(end_seconds)}.wav"
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(start_seconds), "-t", str(dur), "-i", video_path,
            "-vn", "-ar", "16000", "-ac", "1", temp_wav
        ], capture_output=True, check=True)
        
        model = whisper.load_model("base")
        res = model.transcribe(temp_wav, word_timestamps=True)
        
        srt_lines = []
        srt_idx = 1
        ass_events = []
        
        if banner_text:
            ass_events.append(f"Dialogue: 0,0:00:00.00,{format_ass_time(dur)},HeaderBanner,,0,0,0,, {banner_text} ")
            
        for seg in res["segments"]:
            words = seg.get("words", [])
            if words:
                chunk_size = 3
                for c_i in range(0, len(words), chunk_size):
                    chunk = words[c_i:c_i+chunk_size]
                    c_st = chunk[0]["start"]
                    c_en = chunk[-1]["end"]
                    text = " ".join([w["word"].strip() for w in chunk])
                    srt_lines.append(f"{srt_idx}\n{format_srt_time(c_st)} --> {format_srt_time(c_en)}\n{text}\n")
                    srt_idx += 1
                    
                    styled_words = []
                    for w_obj in chunk:
                        w = w_obj["word"].strip()
                        clean_w = re.sub(r'[^\w]', '', w)
                        if clean_w.isupper() and len(clean_w) > 1:
                            styled_words.append(f"{{\\c&H0000FFFF&}}{w}{{\\c&HFFFFFF&}}")
                        elif any(kw in clean_w.lower() for kw in [
                            "money", "billion", "million", "scam", "racist", "hate", "women", "men",
                            "fight", "cop", "police", "jail", "trump", "muslim", "jewish", "trans",
                            "cheat", "truth", "secret", "never", "files", "exposed", "matrix"
                        ]):
                            styled_words.append(f"{{\\c&H0000FFFF&}}{w}{{\\c&HFFFFFF&}}")
                        else:
                            styled_words.append(w)
                    styled_text = " ".join(styled_words)
                    ass_events.append(f"Dialogue: 1,{format_ass_time(c_st)},{format_ass_time(c_en)},MainCaption,,0,0,0,,{styled_text}")
            else:
                srt_lines.append(f"{srt_idx}\n{format_srt_time(seg['start'])} --> {format_srt_time(seg['end'])}\n{seg['text'].strip()}\n")
                srt_idx += 1
                ass_events.append(f"Dialogue: 1,{format_ass_time(seg['start'])},{format_ass_time(seg['end'])},MainCaption,,0,0,0,,{seg['text'].strip()}")
                
        margin_v = 860 if layout_preset == "split" else 420
        ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HeaderBanner,DejaVu Sans,44,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,1,0,3,14,0,8,40,40,240,1
Style: MainCaption,DejaVu Sans,64,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,6,4,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        os.makedirs(os.path.dirname(os.path.abspath(output_srt_path)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(output_ass_path)), exist_ok=True)
        
        with open(output_srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines) + "\n")
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header + "\n".join(ass_events) + "\n")
            
        return f"Subtitles generated successfully:\nSRT: {output_srt_path}\nASS: {output_ass_path}"
    except Exception as e:
        return f"Subtitle generation error: {e}"

@mcp.tool()
def compose_vertical_short(video_path: str, start_seconds: float, end_seconds: float, ass_subtitle_path: str, output_video_path: str, layout_preset: str = "split", center_watermark: str = "kick.com/sneako") -> str:
    """
    Render 1080x1920 60FPS vertical short using FFmpeg with -14 LUFS loudness mastering.
    Presets:
    - 'split': Zero-stretch 9:8 vertical stack (1215x1080 -> 1080x960 top/bottom).
    - 'native': 100% original 1080x1920 passthrough with subtitles burned.
    - 'blur': 16:9 box over Gaussian blurred 9:16 background.
    """
    try:
        dur = end_seconds - start_seconds
        os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)
        
        if layout_preset == "auto":
            import sys
            if "/home/idrees/Antigravity/.agents/skills/viral_video_clipper/scripts" not in sys.path:
                sys.path.append("/home/idrees/Antigravity/.agents/skills/viral_video_clipper/scripts")
            from cv_auto_reframer import detect_faces_and_compute_crops
            cv_res = detect_faces_and_compute_crops(video_path, start_seconds, end_seconds)
            base_filter = cv_res.get("ffmpeg_filter")
            filter_complex = (
                f"{base_filter};"
                f"[composed]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{center_watermark}':fontsize=28:fontcolor=white@0.9:shadowcolor=black@0.8:shadowx=2:shadowy=2:x=(w-text_w)/2:y=970[watermarked];"
                f"[watermarked]subtitles='{ass_subtitle_path}':fontsdir='/usr/share/fonts/truetype/dejavu'[v];"
                f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=7[a]"
            )
        elif layout_preset == "split":
            filter_complex = (
                f"[0:v]crop=1215:1080:0:0,scale=1080:960[top];"
                f"[0:v]crop=1215:1080:705:0,scale=1080:960[bottom];"
                f"[top][bottom]vstack=inputs=2[composed];"
                f"[composed]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{center_watermark}':fontsize=28:fontcolor=white@0.9:shadowcolor=black@0.8:shadowx=2:shadowy=2:x=(w-text_w)/2:y=970[watermarked];"
                f"[watermarked]subtitles='{ass_subtitle_path}':fontsdir='/usr/share/fonts/truetype/dejavu'[v];"
                f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=7[a]"
            )
        elif layout_preset == "native":
            filter_complex = (
                f"[0:v]subtitles='{ass_subtitle_path}':fontsdir='/usr/share/fonts/truetype/dejavu'[v];"
                f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=7[a]"
            )
        elif layout_preset == "blur":
            filter_complex = (
                f"[0:v]split=2[bg_in][fg_in];"
                f"[bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:3,eq=brightness=-0.14:saturation=1.2[bg];"
                f"[fg_in]scale=1080:-2:flags=lanczos[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2[composed];"
                f"[composed]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{center_watermark}':fontsize=28:fontcolor=white@0.9:shadowcolor=black@0.8:shadowx=2:shadowy=2:x=(w-text_w)/2:y=615[watermarked];"
                f"[watermarked]subtitles='{ass_subtitle_path}':fontsdir='/usr/share/fonts/truetype/dejavu'[v];"
                f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=7[a]"
            )
        else:
            return f"Error: Invalid layout preset '{layout_preset}'"

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_seconds),
            "-t", str(dur),
            "-i", video_path,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", "60",
            output_video_path
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return f"Render successful: {output_video_path}"
        return f"Render failed: {res.stderr[-400:]}"
    except Exception as e:
        return f"Composition error: {e}"

@mcp.tool()
def direct_multi_shot_timeline(video_path: str, start_seconds: float, end_seconds: float) -> str:
    """
    20-Year Editorial Director & Computer Vision Analysis:
    Detects scene cuts, classifies shots (0 faces, 1 solo speaker, 2 dual split, 3+ panel),
    computes golden-ratio headroom and focal-anchored zooms for every segment.
    """
    try:
        import sys
        if "/home/idrees/Antigravity/.agents/skills/viral_video_clipper/scripts" not in sys.path:
            sys.path.append("/home/idrees/Antigravity/.agents/skills/viral_video_clipper/scripts")
        from director_engine import analyze_and_direct_timeline
        res = analyze_and_direct_timeline(video_path, start_seconds, end_seconds)
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Director analysis error: {e}"

if __name__ == "__main__":
    mcp.run()
