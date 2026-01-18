# Migration to Python FastAPI Agent

## Overview

The backend has been migrated from Node.js/Express to Python FastAPI for better AI/ML capabilities and video frame analysis.


### Backend
- **Old**: Node.js Express server (`backend/server.js`) on port 3001
- **New**: Python FastAPI agent (`agent/main.py`) on port 8000
- **New Endpoint**: `/api/analyze` (replaces `/api/generate-analogy`)

### Frontend
- Updated `vite.config.ts` to proxy `/api` requests to Python FastAPI (port 8000)
- Created `src/lib/frameCapture.ts` for capturing video frames
- Updated `src/lib/analogyAgent.ts` to use new `/api/analyze` endpoint
- Updated `src/pages/Index.tsx` to capture frames before analysis

## Architecture

```
Frontend (React) → Vite Proxy → Python FastAPI (port 8000) → Claude/OpenAI APIs
```

## New Features

1. **Vision AI Analysis**: Analyzes actual video frames using Claude Vision API
2. **Frame Capture**: Captures frames from YouTube videos (using thumbnail API for MVP)
3. **Image Compression**: Automatically compresses images before sending to AI
4. **Better Caching**: In-memory cache with expiration support

## Setup Instructions

### 1. Python Agent Setup

```bash
cd agent
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Create `agent/.env`:
```env
AI_PROVIDER=stub  # or "anthropic" for real AI
ANTHROPIC_API_KEY=your_key_here  # optional
PORT=8000
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```

### 3. Run Services

**Terminal 1 - Python Agent:**
```bash
cd agent
python main.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### 4. Access Application

Open `http://localhost:8080` in your browser.

## API Changes

### Old Endpoint (Node.js)
```
POST /api/generate-analogy
Body: { videoId, timestamp, caption? }
```

### New Endpoint (Python)
```
POST /api/analyze
Body: { frameImage: base64, timestamp, videoId }
Response: { originalCommentary, nflAnalogy, fieldDiagram, timestamp, cached }
```

## Frame Extraction Strategy

**Current Implementation:**
- ✅ Backend extracts frames directly from YouTube videos using `yt-dlp` and OpenCV
- ✅ No frontend frame capture needed - backend handles everything
- ✅ Real frame analysis with Claude Vision API
- ✅ Automatic image compression and optimization

**How It Works:**
1. Frontend sends `videoId` and `timestamp` to `/api/analyze`
2. Backend uses `yt-dlp` to get video stream URL
3. OpenCV extracts frame at specified timestamp
4. Frame is compressed and sent to Claude Vision
5. Analysis and NFL analogy are generated
6. Results are cached for 5 minutes

## Testing

### Test Python Agent
```bash
curl http://localhost:8000/health
```

### Test Analysis Endpoint
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "frameImage": "base64_image_data",
    "timestamp": 123.45,
    "videoId": "test123"
  }'
```

### View API Docs
Visit `http://localhost:8000/docs` for interactive API documentation.

## Migration Notes

- **Node.js backend is still present** but not used by frontend
- **Can be removed** if you want to fully migrate
- **Stub mode works** without API keys (zero cost)
- **CORS configured** for localhost development

## Troubleshooting

### Import Errors
Make sure you're running from the `agent` directory:
```bash
cd agent
python main.py
```

### Port Conflicts
Change port in `agent/.env`:
```env
PORT=8001
```

### CORS Errors
Add your frontend URL to `CORS_ORIGINS` in `agent/.env`.

### Frame Capture Issues
The system will fall back to placeholder frames if YouTube thumbnail capture fails. This is expected for MVP.

## Next Steps

1. ✅ Python FastAPI agent created
2. ✅ Frontend updated to use new API
3. ⏳ Test with real YouTube videos
4. ⏳ Add YouTube Data API for better frame capture
5. ⏳ Remove Node.js backend (optional)
