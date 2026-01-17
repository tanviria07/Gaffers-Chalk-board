# Chatbot Accuracy Improvement Roadmap

## Current Problem
When user asks "what happened at 12 minutes", the chatbot gives generic responses instead of specific events (like Ronaldo's bicycle kick goal).

## Root Causes

1. **Caption Matching Issues**
   - Only looks within 3-5 second window
   - May miss captions if timing is slightly off
   - Captions might not exist for that exact moment

2. **Video Title Not Prioritized**
   - Title says "Greatest Goal" and "bicycle kick" but AI doesn't prioritize it
   - Generic responses override specific video information

3. **No Visual Analysis at Timestamp**
   - Not extracting frame at asked timestamp
   - Missing visual context that would show the bicycle kick

4. **Limited Context Window**
   - Only gets single caption at timestamp
   - Doesn't get surrounding context (captions before/after)

## Solutions & Technologies

### 🎯 **Solution 1: Extract Frame at Asked Timestamp + Vision AI** (RECOMMENDED)

**What it does:**
- When user asks about specific timestamp, extract video frame at that time
- Use Vision AI (Claude/GPT-4 Vision) to analyze the frame
- Combine visual analysis + captions + metadata

**Technologies:**
- `yt-dlp` + `OpenCV` (already have)
- Vision AI: Claude Vision API or GPT-4 Vision
- Multi-modal prompt combining image + text

**Implementation:**
```python
# In chat_service.py
if asked_timestamp:
    # Extract frame at that timestamp
    frame = await frame_extractor.extract_frame(video_id, asked_timestamp)
    if frame:
        # Analyze with Vision AI
        visual_analysis = await vision_analyzer.analyze_frame(frame)
        # Add to prompt
```

**Pros:**
- Most accurate - sees what's actually happening
- Works even if captions are wrong/missing
- Can identify specific actions (bicycle kick, goal, etc.)

**Cons:**
- Slower (needs frame extraction + vision API call)
- Costs more (vision API calls)

---

### 🎯 **Solution 2: Better Caption Context Window**

**What it does:**
- Get multiple captions around the timestamp (±10-15 seconds)
- Provide context before/after the moment
- Better understanding of what's happening

**Technologies:**
- Enhanced `caption_extractor.py`
- Caption aggregation logic

**Implementation:**
```python
# Get captions in wider window
captions_context = await caption_extractor.get_captions_in_range(
    video_id, 
    timestamp - 10, 
    timestamp + 10
)
# Combine multiple captions for context
```

**Pros:**
- Fast (no API calls)
- Free
- Better context understanding

**Cons:**
- Still depends on caption quality
- May not work if captions don't exist

---

### 🎯 **Solution 3: Video Scene Segmentation**

**What it does:**
- Detect key moments in video (goals, saves, etc.)
- Create timeline of events
- Match user's timestamp to nearest event

**Technologies:**
- **Video understanding models:**
  - Video-LLaMA
  - Video-ChatGPT
  - CLIP + scene detection
- **Event detection:**
  - Action recognition models
  - Goal detection algorithms

**Implementation:**
```python
# Pre-process video to detect key events
events = detect_key_events(video_id)
# events = [
#   {"timestamp": 720, "type": "goal", "description": "Ronaldo bicycle kick"},
#   ...
# ]
# Match user's timestamp to nearest event
```

**Pros:**
- Very accurate for major events
- Can pre-process once, use many times
- Knows exact moments of goals/saves

**Cons:**
- Complex to implement
- Requires video processing
- May need specialized models

---

### 🎯 **Solution 4: Enhanced Prompt Engineering**

**What it does:**
- Prioritize video title/description more heavily
- Explicitly instruct AI to use title information
- Better parsing of video metadata

**Technologies:**
- Better prompt templates
- Structured prompting with priority levels

**Implementation:**
```python
# Enhanced prompt
user_prompt = f"""
CRITICAL: Video title says "{video_title}"
If title mentions specific event (goal, kick, save), that's what happened!

USER ASKED ABOUT: {asked_timestamp}
CAPTION AT THAT TIME: {caption}
VIDEO TITLE: {video_title}  # PRIORITIZE THIS!

Answer based on title first, then caption, then general knowledge.
"""
```

**Pros:**
- Easy to implement
- No new dependencies
- Immediate improvement

**Cons:**
- Still depends on title accuracy
- May not work if title is vague

---

### 🎯 **Solution 5: Multi-Modal Video Understanding**

**What it does:**
- Combine ALL sources: frame + captions + metadata + title
- Use video-language models
- Better understanding of video content

**Technologies:**
- **Video-Language Models:**
  - Video-LLaMA
  - Video-ChatGPT
  - GPT-4 Vision (for video frames)
  - Gemini Pro Vision
- **Multi-modal embeddings:**
  - CLIP for video understanding
  - VideoBERT

**Implementation:**
```python
# Combine all sources
context = {
    "frame": extract_frame(timestamp),
    "caption": get_caption(timestamp),
    "title": video_metadata["title"],
    "description": video_metadata["description"],
    "nearby_captions": get_captions_range(timestamp - 10, timestamp + 10)
}
# Use multi-modal model
response = video_llm.understand(context, user_question)
```

**Pros:**
- Most comprehensive
- Best accuracy
- Handles complex queries

**Cons:**
- Most complex
- May require new infrastructure
- Higher costs

---

## Recommended Implementation Order

### Phase 1: Quick Wins (Do First)
1. ✅ **Enhanced Prompt Engineering** - Prioritize video title
2. ✅ **Better Caption Context** - Get ±10-15 seconds of captions

### Phase 2: Core Improvement
3. ✅ **Frame Extraction at Timestamp** - Extract frame when user asks about specific time
4. ✅ **Vision AI Analysis** - Analyze frame with Claude/GPT-4 Vision

### Phase 3: Advanced (Optional)
5. ⚠️ **Video Scene Segmentation** - Pre-process videos for key events
6. ⚠️ **Multi-Modal Models** - Full video understanding

---

## Immediate Fix (Quick Implementation)

**Priority 1: Better Title Usage**
- Make video title the PRIMARY source when it mentions specific events
- Parse title for keywords: "bicycle kick", "goal", "save", etc.

**Priority 2: Frame Analysis for Timestamp Queries**
- When user asks about specific timestamp, extract frame
- Use Vision AI to see what's actually happening
- This will catch the bicycle kick even if captions are wrong

**Priority 3: Wider Caption Window**
- Get captions from ±10 seconds around timestamp
- Better context for understanding the moment

---

## Expected Results

**Before:**
- "At 12 minutes, Ronaldo demonstrates footwork..." (generic)

**After:**
- "At 12 minutes, Ronaldo scores an incredible bicycle kick goal against Juventus! The video frame shows him mid-air executing the overhead kick, and the commentators are going wild. This is the moment described in the video title as 'the Greatest Goal in Champions League History'."

---

## Cost Considerations

- **Frame Extraction**: Free (yt-dlp + OpenCV)
- **Vision AI**: ~$0.01-0.03 per frame analysis (Claude/GPT-4)
- **Caption Extraction**: Free
- **Video Processing**: One-time cost for scene detection

**Recommendation**: Use frame extraction + Vision AI for timestamp-specific queries (worth the cost for accuracy).
