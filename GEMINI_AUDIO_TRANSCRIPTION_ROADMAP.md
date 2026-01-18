# Gemini Audio Transcription Roadmap

## Current Situation

### What We Have Now ✅
- **YouTube Captions** (Primary): Extracts subtitles directly from YouTube API
- **Azure Speech-to-Text** (Fallback): When YouTube captions are restricted/blocked
  - Uses `AudioExtractor` to download audio segments
  - Transcribes via Azure Speech-to-Text API
  - Located in: `agent/services/audio_extractor.py`

### Problem
- Sometimes YouTube videos **restrict or block** caption extraction
- Azure Speech-to-Text requires separate API key and service setup
- Want unified solution using **Gemini** (already using it for vision/commentary)

---

## Gemini Audio Capabilities

### Can Gemini Listen to Audio? ✅ YES

**Gemini 1.5 Pro & Flash support:**
- ✅ Audio file input (MP3, WAV, M4A, etc.)
- ✅ Video file with audio track
- ✅ Direct audio transcription
- ✅ Multi-language support
- ✅ Real-time or batch processing

**Example Gemini Audio API:**
```python
# Gemini can process audio files
model.generate_content([
    audio_file_path,  # Direct audio file
    "Transcribe this audio in English, with timestamps"
])
```

---

## Option Comparison

### Option 1: Keep Azure Speech-to-Text (Current)
**Pros:**
- ✅ Already implemented and working
- ✅ Specialized for speech-to-text
- ✅ Low latency, optimized for transcription

**Cons:**
- ❌ Requires separate API key (`AZURE_SPEECH_KEY`)
- ❌ Another service to manage
- ❌ Not unified with Gemini ecosystem

---

### Option 2: Switch to Gemini Audio Transcription ⭐ RECOMMENDED
**Pros:**
- ✅ **Unified**: Same API key as Gemini Vision/Commentary
- ✅ **One service**: All AI features use Gemini
- ✅ **Context-aware**: Gemini understands soccer commentary context
- ✅ **Multi-modal**: Can analyze audio + video together
- ✅ **Simple**: No extra API keys needed

**Cons:**
- ⚠️ May be slightly slower than Azure (but acceptable)
- ⚠️ Need to test audio format compatibility

---

### Option 3: Hybrid Approach
**Pros:**
- ✅ Fallback chain: YouTube → Gemini → Azure
- ✅ Maximum reliability

**Cons:**
- ❌ More complex code
- ❌ Need to manage both API keys

---

## Recommended Roadmap: Switch to Gemini Audio ⭐

### Phase 1: Research & Planning ✅
- [x] Check Gemini audio capabilities (DONE - Gemini supports audio)
- [x] Compare with current Azure solution
- [ ] Test Gemini audio transcription quality on soccer videos
- [ ] Check API costs comparison

### Phase 2: Implementation
**Steps:**
1. **Create `GeminiAudioTranscriber` service**
   - File: `agent/services/gemini_audio_transcriber.py`
   - Methods:
     - `transcribe_audio_segment(audio_file_path)` → Returns transcript text
     - `transcribe_with_timestamps(audio_file_path)` → Returns captions with timestamps

2. **Update `AudioExtractor`**
   - Add option to use Gemini instead of Azure
   - Keep Azure as optional fallback
   - File: `agent/services/audio_extractor.py`

3. **Update `CaptionExtractor`**
   - Priority chain: YouTube → Gemini Audio → Azure (optional)
   - File: `agent/services/caption_extractor.py`

4. **Add Configuration**
   - Environment variable: `USE_GEMINI_AUDIO=true` (default: true)
   - Keep `AZURE_SPEECH_KEY` optional (fallback only)

### Phase 3: Integration Points

**Where Gemini Audio Will Be Used:**
1. **Live Commentary Pipeline** (`commentary_orchestrator.py`)
   - If no YouTube captions → Extract audio → Gemini transcribes
   
2. **Chat Service** (`chat_service.py`)
   - When user asks about specific timestamp
   - No captions available → Use Gemini audio transcription

3. **"What's Happening" Box** (frontend)
   - Already uses `fetchCaptions()` → Will automatically get Gemini transcripts

### Phase 4: Testing & Optimization
- [ ] Test audio extraction quality (10s segments, 30s segments)
- [ ] Test transcription accuracy on soccer commentary
- [ ] Benchmark speed vs Azure Speech-to-Text
- [ ] Test with different languages/accents
- [ ] Handle edge cases (silent segments, background noise)

---

## Implementation Details

### File Structure
```
agent/services/
├── audio_extractor.py           # Audio download (unchanged)
├── gemini_audio_transcriber.py  # NEW: Gemini audio transcription
└── caption_extractor.py         # Updated: Uses Gemini audio as fallback
```

### Code Flow (When YouTube Captions Restricted)

```
1. Try YouTube Captions API
   ↓ (Fails - Restricted)
   
2. Extract Audio Segment (10-30 seconds)
   - Use existing AudioExtractor
   - Download audio: video_url, start_time, end_time
   ↓
   
3. Send to Gemini Audio API
   - Upload audio file to Gemini
   - Prompt: "Transcribe this soccer commentary audio. Include key moments like goals, saves, and player actions."
   ↓
   
4. Get Transcript
   - Return as caption format: {text, start, dur}
   ↓
   
5. Use in "What's Happening" Box
   - Same format as YouTube captions
   - Works with existing frontend code
```

### Gemini Audio API Usage (Expected)

```python
# Example (to be implemented)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Upload audio file
with open(audio_file_path, 'rb') as f:
    audio_data = f.read()

response = model.generate_content([
    {
        "mime_type": "audio/wav",
        "data": audio_data
    },
    "Transcribe this soccer commentary. Keep it natural and include timestamps."
])
```

---

## Configuration

### Environment Variables
```env
# Required (already have)
GEMINI_API_KEY=your_gemini_key

# Optional (only if you want Azure fallback)
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastus

# New (optional - defaults to true)
USE_GEMINI_AUDIO=true
```

---

## Benefits After Implementation

### Before (Current)
```
YouTube Captions (if available)
    ↓ (Restricted)
Azure Speech-to-Text (requires separate API key)
    ↓ (Fail - no API key set)
"No captions available" ❌
```

### After (With Gemini)
```
YouTube Captions (if available)
    ↓ (Restricted)
Gemini Audio Transcription (same API key!)
    ↓
Captions appear in "What's Happening" box ✅
```

---

## Migration Plan

1. **Phase 1**: Keep Azure as primary, add Gemini as alternative
   - Test Gemini alongside Azure
   - Compare quality/speed

2. **Phase 2**: Switch Gemini to primary, Azure as fallback
   - One API key (Gemini) for everything
   - Azure only if Gemini fails

3. **Phase 3**: Remove Azure (optional)
   - If Gemini works well, simplify to one service

---

## Next Steps

1. **Research**: Test Gemini audio transcription on sample soccer video
2. **Plan**: Finalize implementation details
3. **Code**: Implement `GeminiAudioTranscriber` service
4. **Test**: Verify quality and performance
5. **Deploy**: Update production code

---

## Questions to Answer Before Coding

1. **Audio Format**: What format should we send to Gemini? (WAV, MP3, M4A?)
2. **Chunk Size**: How long should audio segments be? (10s? 30s? 60s?)
3. **Timestamps**: Can Gemini return word-level timestamps or just sentence-level?
4. **Cost**: What's the cost per minute of audio transcription with Gemini?
5. **Speed**: How fast is Gemini audio transcription vs Azure?

---

## Timeline Estimate

- **Research & Testing**: 1-2 days
- **Implementation**: 1-2 days  
- **Testing & Bug Fixes**: 1 day
- **Total**: 3-5 days

---

**Status**: 📋 Roadmap Complete - Ready for Implementation