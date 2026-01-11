"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AnalyzeRequest(BaseModel):
    """Request model for video analysis"""
    videoId: str = Field(..., description="YouTube video ID")
    timestamp: float = Field(..., description="Current video timestamp in seconds")


class FieldDiagram(BaseModel):
    """Field diagram data structure"""
    attackers: list = Field(default_factory=list, description="Attacker positions")
    defenders: list = Field(default_factory=list, description="Defender positions")
    ball: list = Field(default_factory=list, description="Ball position")
    diagramType: str = Field(default="defensive", description="Diagram type")


class AnalyzeResponse(BaseModel):
    """Response model for video analysis"""
    originalCommentary: str = Field(..., description="Soccer commentary from frame analysis")
    nflAnalogy: str = Field(..., description="NFL analogy explanation")
    timestamp: float = Field(..., description="Timestamp used for analysis")
    cached: bool = Field(default=False, description="Whether result was from cache")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: Optional[str] = None
