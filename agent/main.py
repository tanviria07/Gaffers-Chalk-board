from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import os
import asyncio
import logging
from dotenv import load_dotenv
from pathlib import Path
from models.schemas import (
    AnalyzeRequest, AnalyzeResponse, HealthResponse, ChatRequest, ChatResponse,
    LiveCommentaryRequest, LiveCommentaryResponse, NFLAnalogyRequest, NFLAnalogyResponse,
    TTSRequest
)
from services.caption_extractor import YouTubeCaptionExtractor
from services.analogy_generator import AnalogyGenerator
from services.cache_manager import CacheManager
from services.vision_analyzer import VisionAnalyzer
from services.youtube_extractor import YouTubeFrameExtractor
from services.chat_service import ChatService
from services.video_metadata import VideoMetadataExtractor
from services.commentary_orchestrator import CommentaryOrchestrator
from services.nfl_analogy_service import NFLAnalogyService
from services.tts_service import TTSService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load .env file from the same directory as this script
env_path = Path(__file__).parent / '.env'
loaded = load_dotenv(env_path)  # <-- add this


def _mask(key: str, show: int = 6):
    v = os.getenv(key)
    if not v:
        return "NOT SET"
    if len(v) <= show * 2:
        return v
    return f"{v[:show]}...{v[-show:]}"

print("[ENV CHECK]")
print("AI_PROVIDER        =", os.getenv("AI_PROVIDER"))
print("GEMINI_API_KEY     =", _mask("GEMINI_API_KEY"))
print("ELEVENLABS_API_KEY =", _mask("ELEVENLABS_API_KEY"))
print("PORT               =", os.getenv("PORT"))
print("HOST               =", os.getenv("HOST"))
print("-" * 40)


# --- ADD ONLY THIS BLOCK (env check) ---
print(f"[ENV] Looking for .env at: {env_path}")
print(f"[ENV] .env exists? {env_path.exists()}")
print(f"[ENV] load_dotenv success? {loaded}")
print(f"[ENV] AI_PROVIDER set? {bool(os.getenv('AI_PROVIDER'))}")
print(f"[ENV] GEMINI_API_KEY set? {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"[ENV] ELEVENLABS_API_KEY set? {bool(os.getenv('ELEVENLABS_API_KEY'))}")
# --- END BLOCK ---

app = FastAPI(
    title="Gaffer's Chalkboard Agent",
    description="AI-powered video frame analysis and NFL analogy generation",
    version="1.0.0"
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:5173,http://localhost:8083").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_provider = (os.getenv("AI_PROVIDER", "stub")).lower()
api_key = os.getenv("GEMINI_API_KEY")

caption_extractor = YouTubeCaptionExtractor()
analogy_generator = AnalogyGenerator(api_key=api_key)
vision_analyzer = VisionAnalyzer(api_key=api_key, use_enhanced=True)
frame_extractor = YouTubeFrameExtractor()
cache = CacheManager()
chat_service = ChatService()
metadata_extractor = VideoMetadataExtractor()
commentary_orchestrator = CommentaryOrchestrator()
nfl_analogy_service = NFLAnalogyService(api_key=api_key)
tts_service = TTSService()


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_video(request: AnalyzeRequest):
    try:
        base_timestamp = int(request.timestamp)
        cache_keys = [
            f"{request.videoId}:{base_timestamp}",
            f"{request.videoId}:{base_timestamp - 1}",
            f"{request.videoId}:{base_timestamp + 1}",
            f"{request.videoId}:{base_timestamp - 2}",
            f"{request.videoId}:{base_timestamp + 2}",
        ]
        
        for cache_key in cache_keys:
            cached = cache.get(cache_key)
            if cached:
                print(f"Cache hit for {cache_key}")
                cached['timestamp'] = request.timestamp
                cached_dict = {k: v for k, v in cached.items() if k != 'cached'}
                cached_dict['cached'] = True
                return AnalyzeResponse(**cached_dict)
        
        print(f"Analyzing {request.videoId} at {request.timestamp}s")
        
        print(f"[STEP 1] Extracting frame from video at {request.timestamp}s...")
        frame_base64 = None
        frame_extraction_error = None
        try:
            frame_base64 = await asyncio.wait_for(
                frame_extractor.extract_frame(request.videoId, request.timestamp),
                timeout=10.0
            )
            if frame_base64:
                print(f"[STEP 1] ✓ Frame extracted successfully (size: {len(frame_base64)} chars)")
            else:
                print("[STEP 1] ✗ Frame extraction returned None")
        except asyncio.TimeoutError:
            frame_extraction_error = "Timeout after 5 seconds"
            print(f"[STEP 1] ✗ Frame extraction timed out: {frame_extraction_error}")
        except Exception as e:
            frame_extraction_error = str(e)
            print(f"[STEP 1] ✗ Frame extraction error: {frame_extraction_error}")
            import traceback
            traceback.print_exc()
        
        commentary = None
        vision_analysis_error = None
        if frame_base64:
            if not vision_analyzer.model:
                print("[STEP 2] ✗ Vision analyzer not initialized (no API key)")
                vision_analysis_error = "Vision analyzer not initialized - GEMINI_API_KEY not set"
            else:
                print("[STEP 2] Analyzing frame with vision AI...")
                try:
                    commentary = await asyncio.wait_for(
                        vision_analyzer.analyze_frame(frame_base64),
                        timeout=15.0
                    )
                    if commentary:
                        print(f"[STEP 2] ✓ Generated commentary from vision: {commentary[:50]}...")
                    else:
                        print("[STEP 2] ✗ Vision analysis returned empty commentary")
                except asyncio.TimeoutError:
                    vision_analysis_error = "Timeout after 5 seconds"
                    print(f"[STEP 2] ✗ Vision analysis timed out: {vision_analysis_error}")
                except Exception as e:
                    vision_analysis_error = str(e)
                    print(f"[STEP 2] ✗ Vision analysis error: {vision_analysis_error}")
                    import traceback
                    traceback.print_exc()
        else:
            print("[STEP 2] ⏭ Skipping vision analysis - no frame available")
            vision_analysis_error = frame_extraction_error or "Frame extraction failed"
        
        if not commentary:
            print(f"[STEP 3] Vision analysis failed ({vision_analysis_error}), trying caption extraction...")
            try:
                commentary = await asyncio.wait_for(
                    caption_extractor.get_caption_at_timestamp(
                        request.videoId,
                        request.timestamp
                    ),
                    timeout=10.0
                )
                if commentary:
                    print(f"[STEP 3] ✓ Found caption: {commentary[:50]}...")
                else:
                    print("[STEP 3] ✗ No captions available")
            except asyncio.TimeoutError:
                print("[STEP 3] ✗ Caption extraction timed out")
            except Exception as e:
                print(f"[STEP 3] ✗ Caption extraction error: {e}")
                import traceback
                traceback.print_exc()
        
        if not commentary:
            print("[STEP 4] Using stub commentary as final fallback")
            import random
            stubs = [
                "Players are moving into position, creating space for a potential attack.",
                "The team is building up play from the back, looking for passing options.",
                "A counter-attack is developing with players sprinting forward.",
                "Defensive shape is compact, denying space in the central areas.",
                "The ball is in the final third, with attackers looking for an opening."
            ]
            commentary = random.choice(stubs)
            print(f"[STEP 4] ✓ Using stub commentary: {commentary}")
        
        print("[STEP 5] Generating NFL analogy...")
        if not api_key:
            print("[STEP 5] Using stub analogy (no API key)")
            analogy = analogy_generator._generate_stub_analogy(commentary)
        else:
            print("[STEP 5] Using AI to generate analogy...")
            try:
                analogy = await analogy_generator.generate(commentary)
                print(f"[STEP 5] ✓ Generated analogy: {analogy[:50]}...")
            except Exception as e:
                print(f"[STEP 5] ✗ Analogy generation error: {e}, using stub")
                analogy = analogy_generator._generate_stub_analogy(commentary)
        
        response_data = {
            "originalCommentary": commentary,
            "nflAnalogy": analogy,
            "timestamp": request.timestamp,
            "cached": False
        }
        
        primary_cache_key = f"{request.videoId}:{base_timestamp}"
        cache.set(primary_cache_key, response_data, expire=600)
        
        print(f"[COMPLETE] Analysis complete: {commentary[:50]}...")
        print(f"[SUMMARY] Commentary source: {'Vision AI' if frame_base64 and vision_analyzer.model else 'Captions' if commentary and not any(phrase in commentary for phrase in ['Players are moving', 'The team is building']) else 'Stub'}")
        return AnalyzeResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/captions/{video_id:path}")
async def get_captions(video_id: str, timestamp: float = Query(None), audio_fallback: bool = Query(False)):
    try:
        if timestamp is not None and audio_fallback:
            caption_text = await caption_extractor.get_caption_at_timestamp(video_id, timestamp, use_speech_fallback=True)
            if caption_text:
                return {"text": caption_text, "videoId": video_id, "timestamp": timestamp}
            return {"text": None, "videoId": video_id, "timestamp": timestamp}
        
        captions = await caption_extractor.fetch_captions(video_id)
        return {"captions": captions, "videoId": video_id}
    except Exception as e:
        print(f"[CAPTIONS] Error fetching captions: {e}")
        import traceback
        traceback.print_exc()
        return {"captions": [], "videoId": video_id, "error": str(e)}


@app.get("/api/video-metadata/{video_id:path}")
async def get_video_metadata(video_id: str):
    try:
        metadata = await metadata_extractor.get_metadata(video_id)
        if metadata:
            return metadata
        else:
            raise HTTPException(status_code=404, detail="Video metadata not found")
    except Exception as e:
        print(f"Metadata extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract metadata: {str(e)}")


@app.post("/api/generate-analogy-from-text")
async def generate_analogy_from_text(request: dict):
    try:
        commentary = request.get('commentary', '')
        if not commentary:
            return {"nflAnalogy": "This is like a well-designed offensive scheme — every player has a role, creating space and options."}
        
        if not api_key:
            analogy = analogy_generator._generate_stub_analogy(commentary)
        else:
            try:
                analogy = await analogy_generator.generate(commentary)
            except Exception as e:
                print(f"[ANALOGY] Error generating analogy: {e}, using stub")
                analogy = analogy_generator._generate_stub_analogy(commentary)
        
        return {"nflAnalogy": analogy}
    except Exception as e:
        print(f"[ANALOGY] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"nflAnalogy": "This is like a well-designed offensive scheme — every player has a role, creating space and options."}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print(f"Chat request for {request.videoId} at {request.timestamp}s: {request.userMessage[:50]}...")
        if request.context:
            print(f"[CHAT] Context provided - commentary: {request.context.get('commentary', 'N/A')[:60]}...")
            print(f"[CHAT] Context provided - nflAnalogy: {request.context.get('nflAnalogy', 'N/A')[:60]}...")
        
        video_metadata = request.videoMetadata
        if not video_metadata:
            print(f"[CHAT] Fetching video metadata...")
            video_metadata = await metadata_extractor.get_metadata(request.videoId)
            if video_metadata:
                print(f"[CHAT] Got metadata: {video_metadata.get('title', 'N/A')[:50]}...")
        
        caption_text = None
        try:
            caption_text = await caption_extractor.get_caption_at_timestamp(request.videoId, request.timestamp)
            if caption_text:
                print(f"[CHAT] Got caption at {request.timestamp}s: {caption_text[:60]}...")
        except Exception as e:
            print(f"[CHAT] Could not get caption: {e}")
        
        enhanced_context = request.context.copy() if request.context else {}
        if caption_text:
            enhanced_context['caption'] = caption_text
        
        response_text = await chat_service.chat(
            user_message=request.userMessage,
            video_id=request.videoId,
            current_time=request.timestamp,
            context=enhanced_context,
            video_metadata=video_metadata,
            caption_extractor=caption_extractor,
            frame_extractor=frame_extractor,
            vision_analyzer=vision_analyzer
        )
        
        return ChatResponse(
            response=response_text,
            timestamp=request.timestamp
        )
    
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/api/live-commentary", response_model=LiveCommentaryResponse)
async def generate_live_commentary(request: LiveCommentaryRequest):
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"[LIVE COMMENTARY] Generating commentary for {request.videoId} at {request.timestamp}s")

        # Hard timeout so UI stays responsive even if YouTube blocks some frames
        timeout_seconds = float(os.getenv("LIVE_COMMENTARY_TIMEOUT", "8.0"))

        result = await asyncio.wait_for(
            commentary_orchestrator.generate_live_commentary(
                video_url=request.videoId,
                current_time=request.timestamp,
                window_size=request.windowSize
            ),
            timeout=timeout_seconds
        )

        logger.info(f"[LIVE COMMENTARY] Result: commentary={result.get('commentary') is not None}, skipped={result.get('skipped', False)}")
        return LiveCommentaryResponse(**result)

    except asyncio.TimeoutError:
        logger = logging.getLogger(__name__)
        logger.warning("[LIVE COMMENTARY] Timed out — returning skipped to keep UI smooth")
        return LiveCommentaryResponse(commentary=None, skipped=True, timestamp=request.timestamp)


    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"[LIVE COMMENTARY] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Commentary generation failed: {str(e)}")


@app.post("/api/nfl-analogy", response_model=NFLAnalogyResponse)
async def generate_nfl_analogy(request: NFLAnalogyRequest):
    """
    Convert soccer commentary to NFL analogy and broadcast-style commentary.

    - Stays faithful to the soccer commentary (no invented events)
    - Uses generic NFL terms (no real team/player/stadium names)
    - Returns tactical analogy (2-4 sentences) and broadcast commentary (15-35 words)
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"[NFL-ANALOGY] Request: {request.soccer_commentary[:50]}...")

        if not request.soccer_commentary or not request.soccer_commentary.strip():
            return NFLAnalogyResponse(nfl_analogy="", nfl_commentary="")

        nfl_analogy, nfl_commentary = await nfl_analogy_service.generate_nfl_analogy(
            request.soccer_commentary
        )

        logger.info(f"[NFL-ANALOGY] Generated analogy: {nfl_analogy[:50]}...")
        return NFLAnalogyResponse(nfl_analogy=nfl_analogy, nfl_commentary=nfl_commentary)

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"[NFL-ANALOGY] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"NFL analogy generation failed: {str(e)}")


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using ElevenLabs API.

    Returns audio/mpeg content that can be played directly in the browser.
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"[TTS] Request: {len(request.text)} characters")

        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if not tts_service.is_available():
            raise HTTPException(status_code=503, detail="TTS service not available - ELEVENLABS_API_KEY not set")

        audio_bytes = await tts_service.synthesize(request.text)

        if audio_bytes is None:
            raise HTTPException(status_code=500, detail="Failed to generate audio")

        logger.info(f"[TTS] Generated {len(audio_bytes)} bytes of audio")
        return Response(content=audio_bytes, media_type="audio/mpeg")

    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"[TTS] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.get("/health")
async def health_check():
    api_key_set = bool(os.getenv("GEMINI_API_KEY"))
    vision_enabled = vision_analyzer.model is not None
    gemini_enabled = bool(os.getenv("GEMINI_API_KEY"))
    tts_enabled = tts_service.is_available()

    return {
        "status": "healthy",
        "service": "gaffer-agent",
        "version": "1.1.0",
        "has_api_key": api_key_set,
        "has_vision": vision_enabled,
        "has_gemini": gemini_enabled,
        "has_tts": tts_enabled,
        "port": int(os.getenv("PORT", 8000)),
        "message": "Vision analysis enabled" if vision_enabled else "Vision analysis disabled - set GEMINI_API_KEY in .env to enable"
    }


@app.get("/")
async def root():
    return {
        "service": "Gaffer's Chalkboard Agent",
        "version": "1.1.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "chat": "/api/chat",
            "live-commentary": "/api/live-commentary",
            "nfl-analogy": "/api/nfl-analogy",
            "tts": "/api/tts",
            "health": "/health",
            "docs": "/docs"
        },
        "ai_provider": ai_provider,
        "vision_enabled": vision_analyzer.model is not None,
        "gemini_enabled": bool(os.getenv("GEMINI_API_KEY")),
        "tts_enabled": tts_service.is_available()
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Gaffer's Chalkboard Agent on {host}:{port}")
    print(f"AI Provider: {ai_provider}")
    vision_provider = vision_analyzer.provider if vision_analyzer.model else None
    print(f"Vision Analysis: {'Enabled (' + vision_provider + ')' if vision_provider else 'Disabled (no API key)'}")
    
    print(f"API Docs available at: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)
