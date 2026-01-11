# YouTube Frame Extraction Setup

## Overview

The Python FastAPI agent now extracts real frames from YouTube videos using `yt-dlp` and `opencv-python-headless`, then analyzes them with Claude Vision API.

## Dependencies

The following packages are required:
- `yt-dlp`: Extracts video stream URLs from YouTube
- `opencv-python-headless`: Processes video frames (headless version, no GUI dependencies)
- `anthropic`: Claude Vision API for frame analysis

## Installation

### 1. Install System Dependencies (if needed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
FFmpeg should be installed automatically with yt-dlp, but you may need to install it separately:
- Download from: https://ffmpeg.org/download.html
- Add to PATH

### 2. Install Python Dependencies

```bash
cd agent
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create `agent/.env` file:

```env
# Required for real AI analysis
ANTHROPIC_API_KEY=your_anthropic_key_here

# Server settings
PORT=8000
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```

### API Key Setup

1. Get your Anthropic API key from: https://console.anthropic.com/
2. Add it to `agent/.env`
3. The service will use stub responses if no key is provided

## How It Works

1. **Frontend Request**: Sends `videoId` and `timestamp` to `/api/analyze`
2. **Frame Extraction**: Backend uses `yt-dlp` to get video stream URL
3. **Frame Capture**: OpenCV seeks to timestamp and extracts frame
4. **Image Processing**: Frame is resized to 512px and compressed to JPEG (60% quality)
5. **Vision Analysis**: Claude Vision API analyzes the frame
6. **Analogy Generation**: Claude generates NFL analogy from commentary
7. **Caching**: Results are cached for 5 minutes

## Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Test Frame Extraction

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "videoId": "YsWzugAns8w",
    "timestamp": 495.0
  }'
```

**Expected Response:**
```json
{
  "originalCommentary": "Players are positioned in a compact defensive shape...",
  "nflAnalogy": "This is like a prevent defense...",
  "timestamp": 495.0,
  "cached": false
}
```

## Performance

- **Frame Extraction**: 1-3 seconds (depends on video quality and network)
- **Vision Analysis**: 1-2 seconds (Claude API)
- **Total Response Time**: 3-5 seconds per analysis
- **Caching**: Reduces repeat requests to < 100ms

## Troubleshooting

### Error: "Failed to extract video frame"

**Possible causes:**
1. Video is unavailable or private
2. Invalid video ID
3. Timestamp is beyond video length
4. Network issues accessing YouTube

**Solutions:**
- Verify video ID is correct
- Check video is publicly accessible
- Ensure timestamp is within video duration
- Check internet connection

### Error: "yt-dlp extraction error"

**Possible causes:**
1. yt-dlp needs update
2. YouTube changed their API
3. Video format not supported

**Solutions:**
```bash
pip install --upgrade yt-dlp
```

### Error: "Failed to open video stream"

**Possible causes:**
1. FFmpeg not installed
2. Network timeout
3. Video codec not supported

**Solutions:**
- Install FFmpeg: `sudo apt-get install ffmpeg` (Linux) or `brew install ffmpeg` (Mac)
- Check network connectivity
- Try a different video

### Slow Performance

**Optimizations:**
- Videos are limited to 720p for faster processing
- Frames are resized to 512px before analysis
- Results are cached for 5 minutes
- Consider using lower quality videos for testing

## Limitations

1. **Video Quality**: Limited to 720p for performance
2. **Rate Limiting**: YouTube may throttle requests
3. **Private Videos**: Cannot extract frames from private/unlisted videos
4. **Live Streams**: May not work with live YouTube streams
5. **Copyright**: Ensure you have rights to analyze the video content

## Production Considerations

1. **Rate Limiting**: Add rate limiting to prevent abuse
2. **Queue System**: Use a task queue (Celery, RQ) for async processing
3. **Caching**: Use Redis for distributed caching
4. **Error Handling**: Add retry logic for transient failures
5. **Monitoring**: Add logging and metrics
6. **Cost Management**: Monitor Claude API usage and costs

## Next Steps

- [ ] Add support for other video platforms (Vimeo, etc.)
- [ ] Implement batch frame extraction
- [ ] Add video thumbnail preview
- [ ] Support for custom video uploads
- [ ] Add position detection for field diagrams
