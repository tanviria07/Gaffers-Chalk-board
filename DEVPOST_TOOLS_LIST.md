# Tools & Technologies Used - Devpost Submission

## 🛠️ Core Technologies

### Backend
- **Python 3.11+** - Main backend language
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - Frontend framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **shadcn/ui** - UI component library

---

## 🤖 AI & Machine Learning APIs

### Primary (Current Implementation)
- **Google Gemini 1.5 Flash** - Vision analysis and text generation
  - Gemini Vision API - Analyzes video frames for soccer action
  - Gemini Text API - Enhances commentary to broadcast style

### Secondary (Existing Features)
- **Anthropic Claude** - Vision analysis (fallback)
- **Azure OpenAI GPT-4** - Vision analysis and chat (fallback)
- **YOLOv8** - Object detection (players, ball)
- **MediaPipe** - Pose estimation (player actions)

---

## 🎥 Video Processing

### Video Extraction
- **yt-dlp** - YouTube video stream extraction
- **OpenCV** - Frame extraction and image processing
- **Pillow (PIL)** - Image manipulation

### Video Playback
- **YouTube IFrame API** - Video player integration

---

## 🔧 Development Tools

### Backend
- **python-dotenv** - Environment variable management
- **httpx** - Async HTTP client
- **aiohttp** - Async HTTP framework
- **pydantic** - Data validation

### Frontend
- **React Router** - Navigation
- **TanStack Query** - Data fetching and caching
- **Lucide React** - Icons

---

## 📦 Data & Storage

- **In-memory caching** - Fast response caching
- **YouTube Captions API** - Subtitle extraction

---

## 🚀 Deployment & Infrastructure

- **Node.js** - Frontend build runtime
- **npm** - Package management

---

## 🎯 Hackathon-Specific

### Overshoot (Planned Integration)
- **Overshoot API** - Real-time video stream processing
  - Status: Placeholder implemented, SDK integration pending

---

## 📋 Complete Tech Stack Summary

**Languages:**
- Python, TypeScript, JavaScript

**Frameworks:**
- FastAPI, React, Vite

**AI/ML:**
- Google Gemini 1.5 Flash, Anthropic Claude, Azure OpenAI GPT-4, YOLOv8, MediaPipe

**Video:**
- yt-dlp, OpenCV, YouTube IFrame API

**UI:**
- Tailwind CSS, shadcn/ui, React Router

**Tools:**
- python-dotenv, httpx, pydantic, TanStack Query

---

## 🏷️ Devpost Tags (Suggested)

- `python`
- `react`
- `typescript`
- `fastapi`
- `google-gemini`
- `computer-vision`
- `youtube-api`
- `sports-analytics`
- `ai-commentary`
- `real-time-analysis`
- `overshoot` (when integrated)

---

## 📝 Short Description for Devpost

**Tech Stack:**
Built with Python (FastAPI) backend and React/TypeScript frontend. Uses Google Gemini 1.5 Flash for vision analysis and commentary generation, yt-dlp for video extraction, OpenCV for frame processing, and integrates with YouTube API for video playback. Planned integration with Overshoot API for real-time video stream processing.

---

**Last Updated:** 2024-12-19
