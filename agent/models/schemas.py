from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AnalyzeRequest(BaseModel):
    videoId: str = Field(..., description="Video URL (any site) or YouTube video ID (for backward compatibility)")
    timestamp: float = Field(..., description="Current video timestamp in seconds")


class FieldDiagram(BaseModel):
    attackers: list = Field(default_factory=list, description="Attacker positions")
    defenders: list = Field(default_factory=list, description="Defender positions")
    ball: list = Field(default_factory=list, description="Ball position")
    diagramType: str = Field(default="defensive", description="Diagram type")


class AnalyzeResponse(BaseModel):
    originalCommentary: str = Field(..., description="Soccer commentary from frame analysis")
    nflAnalogy: str = Field(..., description="NFL analogy explanation")
    timestamp: float = Field(..., description="Timestamp used for analysis")
    cached: bool = Field(default=False, description="Whether result was from cache")


class ChatRequest(BaseModel):
    videoId: str = Field(..., description="Video URL or YouTube video ID")
    timestamp: float = Field(..., description="Current video timestamp in seconds")
    userMessage: str = Field(..., description="User's question or message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context with commentary and nflAnalogy")
    videoMetadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional video metadata (title, description, etc.)")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    timestamp: float = Field(..., description="Timestamp used for the response")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: Optional[str] = None


class LiveCommentaryRequest(BaseModel):
    videoId: str = Field(..., description="Video URL or YouTube video ID")
    timestamp: float = Field(..., description="Current video timestamp in seconds")
    windowSize: Optional[float] = Field(default=5.0, description="Size of frame window in seconds")


class LiveCommentaryResponse(BaseModel):
    commentary: Optional[str] = Field(None, description="Enhanced commentary text (None if skipped)")
    rawAction: Optional[str] = Field(None, description="Raw action text from Gemini Vision")
    timestamp: float = Field(..., description="Timestamp used for commentary")
    skipped: bool = Field(default=False, description="Whether commentary was skipped due to similarity")
    error: Optional[str] = Field(None, description="Error message if generation failed")
