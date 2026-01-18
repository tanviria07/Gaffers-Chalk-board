# Speech-to-Text Fallback Setup

## Overview

When YouTube captions are restricted or unavailable, the system now automatically falls back to **Speech-to-Text** to generate live captions from the video's audio.

## How It Works

1. **Primary**: Try to extract YouTube captions (as before)
2. **Fallback**: If no captions found → Extract audio segment → Transcribe with Speech-to-Text → Use transcript as caption

## Setup Options

### Option 1: Azure Speech-to-Text (Recommended if you have Azure)

**Pros:**
- High accuracy
- Supports multiple languages
- Real-time transcription

**Setup:**
1. Get Azure Speech key from: https://portal.azure.com/
2. Create Speech Service resource (F0 free tier available)
3. Add to `agent/.env`:
```env
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=your_region (e.g., eastus, westus)
```

**Cost:** ~$1 per 1000 minutes of audio transcribed

---

### Option 2: OpenAI Whisper API

If you prefer OpenAI Whisper (very accurate), we can add it as an alternative.

**Setup:**
1. Get OpenAI API key (if not already)
2. Add to `agent/.env`:
```env
OPENAI_API_KEY=your_key_here
WHISPER_ENABLED=true
```

**Cost:** ~$0.006 per minute ($6 per 1000 minutes)

---

### Option 3: Browser Web Speech API (Free, Client-Side)

For a free option, we can use browser's built-in Speech Recognition API (Chrome/Edge only).

**Pros:** 
- Free
- No backend needed
- Works client-side

**Cons:**
- Requires microphone permission (for live audio)
- Less accurate than cloud APIs
- Chrome/Edge only

Would require frontend implementation.

---

## Current Implementation

Right now, the system uses **Azure Speech-to-Text** as fallback.

### When It Activates:

- ✅ YouTube captions not available (restricted/disabled)
- ✅ `AZURE_SPEECH_KEY` is set in `.env`
- ✅ When calling `get_caption_at_timestamp()` and no caption found

### How to Test:

1. Find a video with restricted/disabled captions
2. Play the video
3. Check backend logs - you should see:
   ```
   [CAPTION EXTRACTOR] No YouTube captions found, trying speech-to-text at Xs...
   [CAPTION EXTRACTOR] ✓ Speech-to-text transcript: ...
   ```

### To Enable:

Add to `agent/.env`:
```env
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=eastus
```

### To Disable:

Simply don't set `AZURE_SPEECH_KEY` - the system will skip speech-to-text fallback gracefully.

---

## Performance Notes

- **Audio extraction**: ~2-3 seconds per 5-second segment
- **Transcription**: ~1-2 seconds with Azure Speech
- **Total latency**: ~3-5 seconds (acceptable for fallback)

The system caches captions, so repeated requests are fast.

---

## Alternative: Use Live Commentary Instead

If you don't want to set up Speech-to-Text, the live commentary from the backend (vision-based) will still work as a fallback when captions aren't available.
