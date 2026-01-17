# Chatbot Issues & How It's Working Now

## Current Problems

### 1. **Timestamp Parsing Not Working**
- **Problem**: "25 second" or "what happened in 25 second" not being parsed
- **Current Code**: Regex pattern `r'(?:at\s+)?(\d+)\s*(?:second|sec|s)'` should work but might be failing
- **Why**: The pattern requires "second" or "sec" or "s" - but user might say "25 second" (singular) or just "25"

### 2. **Too Slow (2-3 minutes)**
- **Problem**: Analyzing 20 frames (1 per second) is too slow
- **Why**: 
  - 20 frames × (YOLOv8 + MediaPipe + GPT-4 Vision API) = very slow
  - Each GPT-4 Vision API call takes ~1-2 seconds
  - 20 frames × 2 seconds = 40+ seconds minimum
  - With network delays, rate limits = 2-3 minutes

### 3. **Generic Responses**
- **Problem**: Responses look generic, not from actual frame analysis
- **Why**: 
  - Frames might not be extracting properly
  - Vision analysis might be failing silently
  - System falling back to video metadata/description instead of frame analysis

## How It's Currently Working

### Step 1: User Asks Question
```
User: "What happened in 25 second"
```

### Step 2: Parse Timestamp
- Code tries to find timestamp in message
- Pattern: `(\d+):(\d{1,2})` for "0:25" format
- Pattern: `(\d+)\s*(?:second|sec|s)` for "25 second" format
- **Issue**: Might not match "25 second" correctly

### Step 3: Calculate 20-Second Window
- If timestamp found: analyze 10 seconds before + 10 seconds after
- Example: 25 seconds → analyze 15-35 seconds

### Step 4: Extract Frames
- Extract 20 frames (1 per second) in parallel
- 15s, 16s, 17s, ..., 35s
- **Problem**: Too many frames = too slow

### Step 5: Analyze Each Frame
For each of 20 frames:
1. **YOLOv8** (Object Detection) - ~50-100ms
2. **MediaPipe** (Pose Estimation) - ~30-50ms  
3. **GPT-4 Vision** (API call) - ~1-2 seconds
4. **Total per frame**: ~2 seconds
5. **Total for 20 frames**: ~40 seconds (but with delays = 2-3 minutes)

### Step 6: Combine Results
- All frame analyses combined
- Sent to GPT-4 for final answer
- **Problem**: If frames fail, falls back to generic metadata

## What Needs to Be Fixed

1. **Better Timestamp Parsing**
   - Handle "25 second", "25 seconds", "at 25", "25s", etc.
   - More flexible patterns

2. **Reduce Frame Count**
   - Instead of 20 frames, use 5-7 frames (every 3-4 seconds)
   - Still good coverage, much faster

3. **Better Error Handling**
   - Log when frames fail to extract
   - Log when vision analysis fails
   - Don't silently fall back to generic responses

4. **Prioritize Frame Analysis**
   - If frames are available, USE THEM
   - Don't fall back to metadata unless frames truly fail

## Next Steps

I'll fix these issues:
1. Improve timestamp parsing
2. Reduce frame sampling (5-7 frames instead of 20)
3. Add better logging
4. Ensure frame analysis is actually used
