# Chatbot Context Fix - Roadmap

## Problem Summary
Chatbot gives generic responses because:
- Video analysis failing (no vision AI, captions timing out)
- Only receiving stub context ("Soccer action at 0:22")
- Doesn't know video title/metadata (e.g., "Roberto Carlos Free Kick")
- Can't describe specific moments (goals, free kicks, etc.)

---

## Solution Roadmap

### Phase 1: Extract Video Metadata (HIGH PRIORITY) ⭐
**Goal:** Get video title/description so chatbot knows what video it's watching

**Steps:**
1. Create video metadata extractor service
   - Use yt-dlp to get video title, description, uploader
   - Cache metadata per video ID
   - File: `agent/services/video_metadata.py`

2. Add metadata endpoint
   - `GET /api/video-metadata/:videoId`
   - Returns: `{ title, description, uploader, duration }`
   - File: `agent/main.py`

3. Fetch metadata in frontend
   - Call metadata endpoint when video loads
   - Store in state
   - File: `src/pages/Index.tsx`

4. Pass metadata to chatbot
   - Include video title in chat context
   - File: `src/components/ChatBot.tsx`, `src/lib/chatAgent.ts`

**Expected Result:** Chatbot knows "Roberto Carlos Free Kick" instead of just "some soccer video"

---

### Phase 2: Improve Chat Prompt (HIGH PRIORITY) ⭐
**Goal:** Make chatbot smarter when context is generic

**Steps:**
1. Enhance system prompt
   - Add instructions to use video title/metadata
   - Tell it to recognize famous moments
   - File: `agent/services/chat_service.py`

2. Better context handling
   - When context is generic, emphasize video metadata
   - Add famous moment detection (Roberto Carlos, Messi, etc.)
   - File: `agent/services/chat_service.py`

3. Add video knowledge
   - Include common soccer knowledge in prompt
   - Reference famous goals/moments when video title matches

**Expected Result:** Chatbot uses video title to give specific answers

---

### Phase 3: Fix Caption Extraction (MEDIUM PRIORITY)
**Goal:** Get real commentary from video captions

**Steps:**
1. Fix caption timeout issues
   - Increase timeout or retry logic
   - Better error handling
   - File: `agent/services/caption_extractor.py`

2. Improve caption parsing
   - Better timestamp matching
   - Handle multiple languages
   - File: `agent/services/caption_extractor.py`

**Expected Result:** Real commentary instead of stub responses

---

### Phase 4: Add Video Context to Chat (MEDIUM PRIORITY)
**Goal:** Pass more video information to chatbot

**Steps:**
1. Update chat request schema
   - Add `videoMetadata` field
   - File: `agent/models/schemas.py`

2. Include metadata in chat prompt
   - Video title, description, uploader
   - Current timestamp context
   - File: `agent/services/chat_service.py`

**Expected Result:** Chatbot has full video context

---

### Phase 5: Famous Moment Detection (LOW PRIORITY)
**Goal:** Automatically recognize famous soccer moments

**Steps:**
1. Create famous moments database
   - Map video IDs/titles to famous moments
   - E.g., "Roberto Carlos Free Kick" → "1997 France match, incredible curved free kick"

2. Add to chat context
   - When video matches, add famous moment info
   - File: `agent/services/chat_service.py`

**Expected Result:** Chatbot knows famous moments automatically

---

## Implementation Order

### Quick Wins (Do First):
1. ✅ Phase 1: Extract video metadata
2. ✅ Phase 2: Improve chat prompt

### Next Steps:
3. Phase 3: Fix caption extraction
4. Phase 4: Add video context to chat

### Nice to Have:
5. Phase 5: Famous moment detection

---

## Success Criteria

✅ Chatbot knows video title (e.g., "Roberto Carlos Free Kick")
✅ Chatbot describes specific moments (goals, free kicks, etc.)
✅ Chatbot uses video metadata when analysis fails
✅ Responses are specific, not generic

---

## Files to Modify

### Backend:
- `agent/services/video_metadata.py` (NEW)
- `agent/services/chat_service.py` (UPDATE)
- `agent/main.py` (UPDATE - add metadata endpoint)
- `agent/models/schemas.py` (UPDATE - add metadata field)

### Frontend:
- `src/pages/Index.tsx` (UPDATE - fetch metadata)
- `src/components/ChatBot.tsx` (UPDATE - pass metadata)
- `src/lib/chatAgent.ts` (UPDATE - include metadata)

---

## Estimated Time
- Phase 1: 30-45 minutes
- Phase 2: 20-30 minutes
- Phase 3: 30-60 minutes (if needed)
- Phase 4: 15-20 minutes
- Phase 5: 30-45 minutes (optional)

**Total: ~2-3 hours for core fixes (Phase 1-2)**
