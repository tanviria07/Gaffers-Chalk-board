# Gaffer's Chalkboard - Python FastAPI Agent

Python FastAPI service for YouTube video frame extraction, analysis, and NFL analogy generation.

## Features

- **YouTube Frame Extraction**: Extracts real frames from YouTube videos using yt-dlp and OpenCV
- **Vision AI Analysis**: Analyzes video frames using Claude Vision API
- **NFL Analogy Generation**: Converts soccer commentary to NFL analogies
- **Caching**: In-memory caching to reduce API costs
- **Image Compression**: Automatically compresses frames before sending to AI APIs
- **Stub Mode**: Works without API keys using intelligent stub responses

## Setup

### 1. Create Virtual Environment

```bash
cd agent
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys (optional)
# ANTHROPIC_API_KEY=your_key_here
# AI_PROVIDER=anthropic  # or "stub" for no API calls
```

## Running

### Development Mode

```bash
python main.py
```

The server will start on `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST `/api/analyze`

Extract frame from YouTube video and generate analysis.

**Request:**
```json
{
  "videoId": "youtube_video_id",
  "timestamp": 123.45
}
```

**Note:** The backend automatically extracts the frame from YouTube - no need to send frame images from the frontend.

**Response:**
```json
{
  "originalCommentary": "Players are moving into position...",
  "nflAnalogy": "This is like an all-out blitz...",
  "fieldDiagram": {
    "attackers": [[0.7, 0.5]],
    "defenders": [[0.3, 0.5]],
    "ball": [0.65, 0.45],
    "diagramType": "defensive"
  },
  "timestamp": 123.45,
  "cached": false
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "gaffer-agent",
  "version": "1.0.0"
}
```

### GET `/docs`

Interactive API documentation (Swagger UI).

## Configuration

### Environment Variables

- `AI_PROVIDER`: `"anthropic"`, `"openai"`, or `"stub"` (default: `"stub"`)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required if `AI_PROVIDER=anthropic`)
- `OPENAI_API_KEY`: Your OpenAI API key (required if `AI_PROVIDER=openai`)
- `PORT`: Server port (default: `8000`)
- `HOST`: Server host (default: `0.0.0.0`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Architecture

```
agent/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── services/
│   ├── vision_analyzer.py  # Vision AI service
│   ├── analogy_generator.py # NFL analogy generator
│   └── cache_manager.py    # Caching logic
├── models/
│   └── schemas.py          # Pydantic models
└── utils/
    └── image_processor.py  # Image compression utilities
```

## Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Test Analysis Endpoint

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "frameImage": "base64_image_data_here",
    "timestamp": 123.45,
    "videoId": "test123"
  }'
```

## Notes

- **YouTube Frame Extraction**: Backend extracts frames directly from YouTube videos - no frontend frame capture needed
- **Stub Mode**: Works without API keys using intelligent stub responses (zero cost)
- **Caching**: Results are cached for 5 minutes to reduce API costs
- **Image Compression**: Frames are automatically resized to 512px and compressed to 60% JPEG quality
- **Error Handling**: Falls back to stub responses if API calls fail
- **Performance**: Typical response time is 3-5 seconds (1-3s frame extraction + 1-2s AI analysis)

## YouTube Frame Extraction

The agent uses `yt-dlp` and `opencv-python-headless` to extract frames from YouTube videos:

1. Gets video stream URL using yt-dlp
2. Opens stream with OpenCV
3. Seeks to specified timestamp
4. Extracts and compresses frame
5. Sends to Claude Vision for analysis

See [YOUTUBE_EXTRACTION_SETUP.md](./YOUTUBE_EXTRACTION_SETUP.md) for detailed setup instructions.

## Production Considerations

- Replace in-memory cache with Redis for distributed systems
- Add rate limiting
- Add authentication/authorization
- Add logging and monitoring
- Use environment-specific configurations
