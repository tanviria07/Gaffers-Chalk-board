# Overshoot + Gemini Pipeline Implementation Roadmap

## 🎯 Goal
Implement a live soccer commentary system using:
1. **Overshoot** - Video stream handling (frames + timestamps)
2. **Gemini Vision** - Generate raw soccer action text from frames
3. **Gemini Text** - Convert raw action to broadcast-style commentary
4. **Deduplication** - Prevent repetitive commentary
5. **Live Commentary Bar** - Real-time text updates in frontend

---

## 📊 Current Architecture Analysis

### Backend (Python FastAPI)
- **Location**: `agent/main.py`
- **Current Vision**: Azure OpenAI GPT-4 Vision / Claude Vision
- **Frame Extraction**: `agent/services/youtube_extractor.py` (yt-dlp + OpenCV)
- **Vision Analysis**: `agent/services/vision_analyzer.py`
- **Current Flow**: Single frame → Vision API → Commentary → NFL Analogy

### Frontend (React + TypeScript)
- **Location**: `src/pages/Index.tsx`
- **Current Updates**: Every 1 second (caption-based or vision API fallback)
- **Display**: Commentary + NFL Analogy side-by-side
- **No Live Commentary Bar**: Currently shows "What's Happening" panel

### Key Services
- `YouTubeFrameExtractor` - Extracts single frames at timestamps
- `VisionAnalyzer` - Analyzes frames with Azure/Claude
- `CaptionExtractor` - Falls back to YouTube captions
- `ChatService` - Handles Q&A about video

---

## 🚀 Implementation Roadmap

### Phase 1: Overshoot Integration (Video Stream Handler)

#### 1.1 Install Overshoot
**File**: `agent/requirements.txt`
```python
# Add Overshoot dependency
overshoot>=0.1.0  # Check actual package name/version
```

**Action Items**:
- [ ] Research Overshoot Python package/API
- [ ] Add to requirements.txt
- [ ] Install: `pip install overshoot`

#### 1.2 Create Overshoot Service
**New File**: `agent/services/overshoot_streamer.py`

**Responsibilities**:
- Connect to YouTube video stream
- Sample frames every 1-2 seconds
- Group frames into windows (3-5 seconds)
- Output: `[(timestamp, [frame1, frame2, ...]), ...]`

**Key Methods**:
```python
class OvershootStreamer:
    async def connect_stream(video_url: str) -> StreamConnection
    async def sample_frames(interval: float = 1.5) -> AsyncIterator[FrameWindow]
    async def get_window(start_time: float, end_time: float) -> FrameWindow
```

**Implementation Notes**:
- Use Overshoot's video stream API
- Handle frame grouping (last 3-5 seconds)
- Maintain frame buffer for windowing
- Return base64-encoded frames (compatible with existing system)

#### 1.3 Integration Point
**File**: `agent/main.py`
- Add new endpoint: `/api/stream-commentary`
- Or modify existing `/api/analyze` to support window-based analysis

---

### Phase 2: Gemini Vision Integration (Raw Soccer Action)

#### 2.1 Install Gemini SDK
**File**: `agent/requirements.txt`
```python
google-generativeai>=0.3.0  # Gemini API client
```

**Action Items**:
- [ ] Add Google Generative AI SDK
- [ ] Get Gemini API key from Google AI Studio
- [ ] Add `GEMINI_API_KEY` to `.env`

#### 2.2 Create Gemini Vision Service
**New File**: `agent/services/gemini_vision.py`

**Responsibilities**:
- Accept window of frames (3-5 frames)
- Send to Gemini Vision with soccer commentary prompt
- Return raw soccer action text (15 words max)

**Key Methods**:
```python
class GeminiVisionAnalyzer:
    async def analyze_frame_window(frames: List[str], timestamps: List[float]) -> str
    # Returns: "Winger drives inside and slips a pass to the overlapping fullback."
```

**Prompt Template**:
```
You are a soccer commentator. From these frames, write ONE short line describing 
the key action happening right now. Use soccer vocabulary. Do not explain rules. 
Do not mention NFL. Keep it under 15 words.
```

**Implementation Notes**:
- Use `gemini-pro-vision` or `gemini-1.5-pro` model
- Handle multiple frames in single request (if supported)
- Fallback to single frame if multi-frame not supported
- Return concise, action-focused text

#### 2.3 Update Vision Analyzer
**File**: `agent/services/vision_analyzer.py`
- Add Gemini Vision as new provider option
- Keep Azure/Claude as fallback
- Add method: `_analyze_with_gemini_vision()`

---

### Phase 3: Gemini Text Integration (Commentary Enhancement)

#### 3.1 Create Gemini Text Service
**New File**: `agent/services/gemini_commentary.py`

**Responsibilities**:
- Accept raw soccer action text
- Enhance with broadcast-style commentary
- Return natural, engaging commentary line

**Key Methods**:
```python
class GeminiCommentaryEnhancer:
    async def enhance_commentary(
        raw_action: str,
        style: str = "Broadcast",
        detail_level: str = "Normal"
    ) -> str
    # Returns: "Relentless pressure there — they force the clearance and win territory."
```

**Prompt Template**:
```
You are a professional soccer commentator. Transform this raw action description 
into engaging broadcast commentary.

Raw Action: "{raw_action}"
Style: {style}
Detail Level: {detail_level}

Requirements:
- Natural, flowing commentary
- Broadcast-style phrasing
- Engaging and dynamic
- 1-2 sentences max
- No NFL references
- Soccer terminology only
```

**Implementation Notes**:
- Use `gemini-pro` or `gemini-1.5-pro` (text-only model)
- Temperature: 0.7-0.8 (creative but consistent)
- Max tokens: 50-100 (keep it concise)

#### 3.2 Integration
**File**: `agent/services/vision_analyzer.py` or new service
- Chain: Gemini Vision → Gemini Text
- Or create orchestrator service

---

### Phase 4: Deduplication System

#### 4.1 Create Deduplication Service
**New File**: `agent/services/commentary_deduplicator.py`

**Responsibilities**:
- Compare new commentary with last N lines
- Use similarity checking (embedding cosine or Gemini)
- Skip if too similar

**Key Methods**:
```python
class CommentaryDeduplicator:
    def __init__(self, similarity_threshold: float = 0.85):
        self.last_commentaries = []  # Keep last 5-10
        self.threshold = similarity_threshold
    
    async def should_skip(self, new_commentary: str) -> bool
    def add_commentary(self, commentary: str, timestamp: float)
```

**Similarity Options**:
1. **Simple String Similarity** (fast, basic):
   - Use Levenshtein distance or Jaccard similarity
   - Fast but less accurate

2. **Gemini Embedding** (accurate, slower):
   - Use Gemini embedding API
   - Cosine similarity between embeddings
   - More accurate semantic comparison

3. **Gemini Classification** (most accurate):
   - Ask Gemini: "Is this basically the same as: {last_commentary}?"
   - Boolean response

**Recommendation**: Start with Option 1, upgrade to Option 2 if needed.

#### 4.2 Integration
**File**: `agent/main.py` or commentary orchestrator
- Check deduplication before returning commentary
- Maintain state (last commentary + timestamp)

---

### Phase 5: Commentary Orchestrator

#### 5.1 Create Orchestrator Service
**New File**: `agent/services/commentary_orchestrator.py`

**Responsibilities**:
- Coordinate Overshoot → Gemini Vision → Gemini Text → Deduplication
- Handle errors and fallbacks
- Manage timing and windowing

**Key Methods**:
```python
class CommentaryOrchestrator:
    async def generate_live_commentary(
        video_url: str,
        current_time: float,
        window_size: float = 5.0
    ) -> CommentaryResult
```

**Flow**:
1. Get frame window from Overshoot (last 3-5 seconds)
2. Send to Gemini Vision → raw action
3. Send to Gemini Text → enhanced commentary
4. Check deduplication → skip if too similar
5. Return commentary + timestamp

**Error Handling**:
- Fallback to single frame if window fails
- Fallback to captions if Gemini fails
- Fallback to stub if all fails

---

### Phase 6: Backend API Endpoints

#### 6.1 New Endpoint: Live Commentary Stream
**File**: `agent/main.py`

**Endpoint**: `POST /api/live-commentary`

**Request**:
```json
{
  "videoId": "youtube_url_or_id",
  "timestamp": 123.5,
  "windowSize": 5.0
}
```

**Response**:
```json
{
  "commentary": "Relentless pressure there — they force the clearance.",
  "timestamp": 123.5,
  "rawAction": "High press wins the ball and forces a rushed clearance.",
  "skipped": false
}
```

#### 6.2 WebSocket Endpoint (Optional - for real-time streaming)
**File**: `agent/main.py`

**Endpoint**: `WS /api/commentary-stream`

**Purpose**: Stream commentary updates in real-time as video plays
- Frontend connects when video starts
- Backend sends commentary every 2-3 seconds
- Frontend displays in live commentary bar

**Alternative**: Polling endpoint (simpler, less efficient)

---

### Phase 7: Frontend Integration

#### 7.1 Create Live Commentary Component
**New File**: `src/components/LiveCommentary.tsx`

**Features**:
- Display current commentary line
- Show timestamp (e.g., "12:35")
- Auto-update every 2-3 seconds
- Smooth transitions between lines
- Scrollable history (optional)

**UI Design**:
```
┌─────────────────────────────────────────┐
│ Live Commentary: "Relentless pressure   │
│ there — they force the clearance."     │
│                          12:35          │
└─────────────────────────────────────────┘
```

#### 7.2 Update Main Page
**File**: `src/pages/Index.tsx`

**Changes**:
- Add LiveCommentary component
- Call `/api/live-commentary` every 2-3 seconds when video playing
- Update state with new commentary
- Handle skipped commentary (don't update UI)

**Integration Points**:
- Use `currentTime` from VideoZone
- Poll backend when video is playing
- Stop polling when video paused/stopped

#### 7.3 Create Commentary Agent
**New File**: `src/lib/commentaryAgent.ts`

**Responsibilities**:
- API client for `/api/live-commentary`
- Handle polling/WebSocket connection
- Manage commentary state

**Key Functions**:
```typescript
export async function getLiveCommentary(
  videoId: string,
  timestamp: number
): Promise<CommentaryResponse>

export interface CommentaryResponse {
  commentary: string;
  timestamp: number;
  rawAction?: string;
  skipped: boolean;
}
```

---

### Phase 8: Configuration & Environment

#### 8.1 Environment Variables
**File**: `.env` (or `agent/.env`)

**Add**:
```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Overshoot (if needed)
OVERSHOOT_API_KEY=your_overshoot_key_here  # If required

# Commentary Settings
COMMENTARY_WINDOW_SIZE=5.0  # seconds
COMMENTARY_UPDATE_INTERVAL=2.0  # seconds
COMMENTARY_SIMILARITY_THRESHOLD=0.85
```

#### 8.2 Configuration Service
**New File**: `agent/services/config.py` (or update existing)

**Settings**:
- Window size (default: 5 seconds)
- Frame sampling interval (default: 1.5 seconds)
- Commentary update interval (default: 2 seconds)
- Similarity threshold (default: 0.85)
- Gemini model selection

---

### Phase 9: Testing & Validation

#### 9.1 Unit Tests
**New Files**:
- `agent/tests/test_overshoot_streamer.py`
- `agent/tests/test_gemini_vision.py`
- `agent/tests/test_gemini_commentary.py`
- `agent/tests/test_deduplicator.py`
- `agent/tests/test_orchestrator.py`

#### 9.2 Integration Tests
**File**: `agent/tests/test_live_commentary_integration.py`

**Test Scenarios**:
1. Full pipeline: Overshoot → Gemini Vision → Gemini Text → Deduplication
2. Error handling: Fallback to captions if Gemini fails
3. Deduplication: Skip similar commentary
4. Timing: Commentary updates every 2-3 seconds

#### 9.3 Manual Testing Checklist
- [ ] Load YouTube video
- [ ] Verify Overshoot connects to stream
- [ ] Verify frames are sampled correctly
- [ ] Verify Gemini Vision generates raw action
- [ ] Verify Gemini Text enhances commentary
- [ ] Verify deduplication skips similar lines
- [ ] Verify frontend updates every 2-3 seconds
- [ ] Verify commentary is soccer-focused (no NFL)
- [ ] Test with different video types
- [ ] Test error handling (no API key, network errors)

---

### Phase 10: Performance Optimization

#### 10.1 Caching
**File**: `agent/services/cache_manager.py` (existing)

**Enhancements**:
- Cache Gemini Vision responses (same frame window)
- Cache Gemini Text responses (same raw action)
- Cache windowed frames (avoid re-extraction)

#### 10.2 Parallel Processing
- Extract frames in parallel (already done in `youtube_extractor.py`)
- Process multiple windows concurrently (if needed)
- Batch Gemini API calls (if supported)

#### 10.3 Rate Limiting
- Respect Gemini API rate limits
- Implement exponential backoff
- Queue requests if needed

---

## 📁 File Structure Summary

### New Files to Create
```
agent/
├── services/
│   ├── overshoot_streamer.py      # Phase 1
│   ├── gemini_vision.py           # Phase 2
│   ├── gemini_commentary.py       # Phase 3
│   ├── commentary_deduplicator.py # Phase 4
│   └── commentary_orchestrator.py # Phase 5
├── tests/
│   ├── test_overshoot_streamer.py
│   ├── test_gemini_vision.py
│   ├── test_gemini_commentary.py
│   ├── test_deduplicator.py
│   └── test_orchestrator.py

src/
├── components/
│   └── LiveCommentary.tsx         # Phase 7
└── lib/
    └── commentaryAgent.ts        # Phase 7
```

### Files to Modify
```
agent/
├── main.py                        # Add /api/live-commentary endpoint
├── requirements.txt               # Add Overshoot, Gemini SDK
├── services/
│   └── vision_analyzer.py        # Add Gemini Vision option

src/
├── pages/
│   └── Index.tsx                 # Add LiveCommentary component
└── lib/
    └── analogyAgent.ts           # May need updates
```

---

## 🔧 Implementation Order (Recommended)

### Week 1: Foundation
1. ✅ Research Overshoot Python package/API
2. ✅ Install dependencies (Overshoot, Gemini SDK)
3. ✅ Create Overshoot service (basic frame extraction)
4. ✅ Create Gemini Vision service (test with single frame)

### Week 2: Core Pipeline
5. ✅ Implement frame windowing (Overshoot)
6. ✅ Integrate Gemini Vision with windowed frames
7. ✅ Create Gemini Text service
8. ✅ Chain Vision → Text (orchestrator)

### Week 3: Polish & Frontend
9. ✅ Implement deduplication
10. ✅ Create backend API endpoint
11. ✅ Create frontend LiveCommentary component
12. ✅ Integrate with main page

### Week 4: Testing & Optimization
13. ✅ Write unit tests
14. ✅ Integration testing
15. ✅ Performance optimization
16. ✅ Error handling improvements

---

## 🚨 Critical Considerations

### 1. Overshoot Research Needed
- **Action**: Research if Overshoot has Python SDK or API
- **Alternative**: If no Python SDK, may need to:
  - Use Overshoot's REST API
  - Or build custom frame windowing with existing `youtube_extractor.py`

### 2. Gemini API Limits
- **Free Tier**: 15 RPM (requests per minute)
- **Paid Tier**: Higher limits
- **Solution**: Implement rate limiting and caching

### 3. Cost Management
- Gemini Vision: ~$0.001-0.002 per image
- Gemini Text: ~$0.0001-0.0005 per request
- **Estimate**: ~$0.01-0.02 per minute of video (with caching)
- **Optimization**: Cache aggressively, use lower-cost models when possible

### 4. Fallback Strategy
- If Overshoot unavailable → Use existing `youtube_extractor.py`
- If Gemini Vision fails → Fall back to Azure/Claude Vision
- If Gemini Text fails → Use raw action text directly
- If all fails → Use captions (existing fallback)

### 5. Terminology
- **Don't call it "exact captions"** (implies SRT files)
- **Call it**: "Vision-grounded soccer commentary generated from video"
- This is honest and judge-safe

---

## 📝 Next Steps

1. **Research Phase** (Do First):
   - [ ] Find Overshoot Python package/API documentation
   - [ ] Get Gemini API key from Google AI Studio
   - [ ] Test Gemini Vision API with sample frames
   - [ ] Test Gemini Text API with sample prompts

2. **Proof of Concept** (Week 1):
   - [ ] Extract frame window using Overshoot (or existing extractor)
   - [ ] Send to Gemini Vision → get raw action
   - [ ] Send to Gemini Text → get enhanced commentary
   - [ ] Display in console/log (no frontend yet)

3. **Full Implementation** (Weeks 2-4):
   - Follow roadmap phases above

---

## 🎯 Success Criteria

- ✅ Commentary updates every 2-3 seconds as video plays
- ✅ Commentary is soccer-focused (no NFL references)
- ✅ Commentary is natural and engaging (broadcast-style)
- ✅ No repetitive commentary (deduplication works)
- ✅ Frontend displays live commentary bar
- ✅ System handles errors gracefully (fallbacks work)
- ✅ Performance: < 3 seconds per commentary update (with caching)

---

## 📚 Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Overshoot Documentation](https://overshoot.ai/docs) (to be researched)
- [FastAPI WebSocket Guide](https://fastapi.tiangolo.com/advanced/websockets/)
- [React Polling Patterns](https://react.dev/learn/synchronizing-with-effects)

---

**Last Updated**: 2024-12-19
**Status**: Planning Phase - Ready for Implementation
