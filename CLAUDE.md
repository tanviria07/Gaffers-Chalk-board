# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gaffer's Chalkboard is an AI-powered soccer explanation app that helps users understand soccer tactics via interactive video analysis. Users paste YouTube URLs, watch matches, and ask an AI Coach questions about what's happening in the video.

## Commands

```bash
# Frontend only (port 8080)
npm run dev

# Backend only (port 3001)
npm run backend

# Both together
npm run dev:all

# Build for production
npm run build

# Lint
npm run lint
```

## Architecture

### Frontend (React + Vite + TypeScript)

- **Entry**: `src/App.tsx` with React Router, main page at `src/pages/Index.tsx`
- **Video handling**:
  - `src/lib/videoSources.ts` - Extensible provider pattern (YouTube implemented)
  - `src/lib/videoContext.ts` - Video state abstraction passed to AI Coach
  - `src/components/VideoZone.tsx` - Video player with URL input
- **AI Chat**: `src/components/AICoach.tsx` - Chat UI that calls `/api/explain`
- **API Client**: `src/lib/explanationAgent.ts` - Frontend wrapper for backend API with stub fallback
- **UI**: shadcn/ui components in `src/components/ui/`, Tailwind with custom "chalk" theme

### Backend (`backend/`)

- **Server**: `backend/server.js` - Express server on port 3001
- **Endpoint**: `POST /api/explain` - Accepts `{ userMessage, videoContext, style }`
- **AI Provider**: Uses OpenAI API if `OPENAI_API_KEY` env var is set, otherwise returns smart stub responses
- **Health**: `GET /health` - Returns API key availability status

### Data Flow

1. User enters YouTube URL in VideoZone
2. `videoSourceManager.parseUrl()` extracts video ID and provider
3. `createVideoContext()` builds context object with current timestamp
4. User asks question in AICoach panel
5. `generateExplanation()` POSTs to `/api/explain` with message, context, style
6. Backend generates response (AI or stub) and returns explanation with tags

### Vite Proxy

The frontend proxies `/api` requests to `localhost:3001` (configured in `vite.config.ts`).

## Key Types

```typescript
// src/lib/explanationAgent.ts
type ExplanationStyle = 'NFL analogies' | 'Beginner friendly' | 'Tactical';

interface AgentInput {
  userMessage: string;
  videoContext: VideoContext | null;
  style: ExplanationStyle;
}

interface AgentOutput {
  responseText: string;
  timestampUsed: number;
  tags?: string[];
}

// src/lib/videoContext.ts
interface VideoContext {
  currentTime: number;
  videoUrl: string;
  provider: 'youtube' | 'vimeo' | 'upload' | 'unknown';
  videoId: string;
}
```

## Environment Variables

Copy `.env.example` to `backend/.env`:

```bash
OPENAI_API_KEY=sk-...     # Optional: enables real AI responses
PORT=3001                  # Backend port (default 3001)
```

Without an API key, the app uses deterministic stub responses based on user message keywords.

## Design System

Custom Tailwind theme in `tailwind.config.ts`:
- Colors: `chalk-white`, `chalk-yellow`, `chalk-green`, `chalk-wood`
- Fonts: "Caveat" (headers), "Bitter" (body)
- Custom animations: `chalk-draw`, `pulse-glow`, `slide-up`
