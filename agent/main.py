"""
FastAPI Agent for Gaffer's Chalkboard
Main entry point for video frame analysis and NFL analogy generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv
from models.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse
from services.caption_extractor import YouTubeCaptionExtractor
from services.analogy_generator import AnalogyGenerator
from services.cache_manager import CacheManager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Gaffer's Chalkboard Agent",
    description="AI-powered video frame analysis and NFL analogy generation",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:5173,http://localhost:8083").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_provider = (os.getenv("AI_PROVIDER", "stub")).lower()
api_key = os.getenv("ANTHROPIC_API_KEY") if ai_provider == "anthropic" else os.getenv("ANTHROPIC_API_KEY")

caption_extractor = YouTubeCaptionExtractor()
analogy_generator = AnalogyGenerator(api_key=api_key)
cache = CacheManager()


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_video(request: AnalyzeRequest):
    """
    Main endpoint: Extract frame from YouTube and generate analysis
    
    Request body:
    - videoId: YouTube video ID
    - timestamp: Current video timestamp in seconds
    
    Returns:
    - originalCommentary: Soccer commentary from frame analysis
    - nflAnalogy: NFL analogy explanation
    - timestamp: Timestamp used for analysis
    - cached: Whether result was from cache
    """
    try:
        # Check cache first - try exact timestamp and nearby timestamps (±2 seconds)
        base_timestamp = int(request.timestamp)
        cache_keys = [
            f"{request.videoId}:{base_timestamp}",  # Exact match
            f"{request.videoId}:{base_timestamp - 1}",  # 1 second before
            f"{request.videoId}:{base_timestamp + 1}",  # 1 second after
            f"{request.videoId}:{base_timestamp - 2}",  # 2 seconds before
            f"{request.videoId}:{base_timestamp + 2}",  # 2 seconds after
        ]
        
        for cache_key in cache_keys:
            cached = cache.get(cache_key)
            if cached:
                print(f"Cache hit for {cache_key}")
                # Update timestamp to match request
                cached['timestamp'] = request.timestamp
                return AnalyzeResponse(**cached, cached=True)
        
        print(f"Analyzing {request.videoId} at {request.timestamp}s")
        
        # Step 1: Get caption from YouTube with timeout (fast path)
        print("Extracting caption from YouTube...")
        commentary = None
        
        try:
            # Try to get caption with 2 second timeout
            commentary = await asyncio.wait_for(
                caption_extractor.get_caption_at_timestamp(
                    request.videoId,
                    request.timestamp
                ),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            print("Caption extraction timed out, using stub")
        except Exception as e:
            print(f"Caption extraction error: {e}, using stub")
        
        # Fallback if no caption available or timeout
        if not commentary:
            # Use stub commentary
            import random
            stubs = [
                "Players are moving into position, creating space for a potential attack.",
                "The team is building up play from the back, looking for passing options.",
                "A counter-attack is developing with players sprinting forward.",
                "Defensive shape is compact, denying space in the central areas.",
                "The ball is in the final third, with attackers looking for an opening."
            ]
            commentary = random.choice(stubs)
            print(f"Using stub commentary: {commentary}")
        else:
            print(f"Found caption: {commentary[:50]}...")
        
        # Step 2: Generate NFL analogy (FAST - no API call in stub mode!)
        # For maximum speed, stub analogies are used. Set ANTHROPIC_API_KEY for real AI
        print("Generating NFL analogy...")
        if not api_key:
            # Instant stub - no API call!
            analogy = analogy_generator._generate_stub_analogy(commentary)
        else:
            # Real AI - slower but better
            analogy = await analogy_generator.generate(commentary)
        
        # Prepare response
        response_data = {
            "originalCommentary": commentary,
            "nflAnalogy": analogy,
            "timestamp": request.timestamp,
            "cached": False
        }
        
        # Cache for 10 minutes (longer cache for better performance)
        cache.set(cache_key, response_data, expire=600)
        
        print(f"Analysis complete: {commentary[:50]}...")
        return AnalyzeResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gaffer-agent",
        "version": "1.0.0",
        "has_api_key": bool(os.getenv("ANTHROPIC_API_KEY"))
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Gaffer's Chalkboard Agent",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "health": "/health",
            "docs": "/docs"
        },
        "ai_provider": ai_provider
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Gaffer's Chalkboard Agent on {host}:{port}")
    print(f"AI Provider: {ai_provider}")
    print(f"API Docs available at: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)
