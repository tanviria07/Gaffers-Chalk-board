# Gaffer's Chalkboard - Project Status

## Project Overview
**Gaffer's Chalkboard** is an AI-powered soccer explanation app that helps users understand soccer tactics and plays using interactive video analysis with NFL-style analogies. The app provides real-time commentary and tactical explanations as users watch YouTube soccer videos.

## Current Implementation Status


#### 1. **Video Integration System**
- **Video Source Abstraction**: Extensible architecture supporting multiple video providers (currently YouTube, designed for Vimeo/upload extension)
- **URL Input**: Users can paste YouTube video URLs to load videos
- **Video Player**: YouTube iframe integration with time tracking
- **Video Context Tracking**: System tracks current video time, URL, provider type, and video ID

#### 2. **AI Explanation Agent (MVP)**
- **Backend API**: Express.js server (`/api/generate-analogy` endpoint)
- **Multiple AI Providers**: Supports OpenAI, Claude, or stub responses (stub-first by default)
- **YouTube Captions Integration**: Fetches video captions/subtitles for context
- **Caching System**: In-memory cache for captions and generated analogies to reduce API calls
- **Real-time Analysis**: Automatically generates explanations as video plays (debounced every 5 seconds)

#### 3. **Frontend Components**
- **VideoZone**: Video player with URL input, YouTube embed, time tracking
- **Analogy Display**: Shows original commentary and NFL analogies side-by-side
- **Tactics Diagram**: Visual field diagrams showing tactical concepts
- **Audio Button**: Text-to-speech functionality for listening to explanations
- **Event Timeline**: Visual timeline of match events (currently using mock data)

#### 4. **Layout & UX**
- **Broadcast-style Layout**: Video takes ~70% width, explanations panel on right (~30%)
- **Responsive Design**: Works on desktop and mobile
- **No Page Scrolling**: Fixed-height layout with internal scroll areas
- **Real-time Updates**: Live analysis updates as video plays

### 🏗️ Architecture

#### Frontend Structure
```
src/
├── components/
│   ├── VideoZone.tsx          # Video player with URL input
│   ├── TacticsDiagram.tsx     # Field diagrams
│   ├── AudioButton.tsx        # Text-to-speech controls
│   └── EventTimeline.tsx      # Match events timeline
├── lib/
│   ├── videoSources.ts        # Video provider abstraction
│   ├── videoContext.ts        # Video context adapter
│   ├── analogyAgent.ts        # Frontend API client for analogies
│   └── explanationAgent.ts    # Legacy explanation agent (may be unused)
└── pages/
    └── Index.tsx              # Main page with layout
```

#### Backend Structure
```
backend/
├── server.js                  # Express API server
│   ├── /api/generate-analogy # Main endpoint for NFL analogies
│   ├── /api/explain          # Legacy explanation endpoint
│   └── /health               # Health check
└── package.json
```

### 🔧 Technical Stack
- **Frontend**: React 18 + TypeScript + Vite
- **UI**: shadcn/ui components + Tailwind CSS
- **Backend**: Express.js (Node.js)
- **AI**: OpenAI API / Claude API (optional, stub by default)
- **Video**: YouTube IFrame API integration
- **Audio**: Web Speech API (text-to-speech)

### 📋 Current Functionality

**What Works:**
1. ✅ Paste YouTube URL → Video loads and plays
2. ✅ Video time tracking via YouTube IFrame API
3. ✅ Automatic analogy generation as video plays (every 5 seconds)
4. ✅ Displays original commentary + NFL analogy side-by-side
5. ✅ Shows tactical field diagrams
6. ✅ Text-to-speech audio playback
7. ✅ Stub responses work without API keys
8. ✅ Caching system for performance

**What's Using Mock Data:**
- Event Timeline (uses `matchData.ts` mock events)

**What's Not Yet Implemented:**
- ❌ User chat interface (AICoach component exists but not integrated in current layout)
- ❌ Database for storing explanations
- ❌ User authentication
- ❌ Multiple video source support beyond YouTube (architecture ready)

### 🎯 Key Design Decisions

1. **Stub-First Approach**: System works without API keys using intelligent template responses
2. **Extensible Video Sources**: Architecture supports adding Vimeo, uploads, etc. easily
3. **Caching**: Reduces API costs and improves performance
4. **Real-time Updates**: Debounced analysis prevents excessive API calls
5. **Broadcast Layout**: Mimics live sports broadcast with analyst panel

### 📝 Environment Setup

**Required:**
- Node.js 18+
- npm

**Optional (for real AI):**
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `backend/.env`
- Set `AI_PROVIDER=openai` or `AI_PROVIDER=claude` in `backend/.env`

**Default Behavior:**
- Works without API keys using stub responses
- `AI_PROVIDER=stub` by default (zero cost)

### 🚀 Running the App

```bash
# Install dependencies
npm install
cd backend && npm install && cd ..

# Run both servers
npm run dev:all

# Or separately:
npm run backend  # Terminal 1 - port 3001
npm run dev      # Terminal 2 - port 8080
```

Open `http://localhost:8080` in browser.

### 📊 Current State Summary

**MVP Status**: ✅ Functional
- Core video + analogy system works
- Real-time analysis functional
- Stub responses provide good UX without API costs
- Ready for API key integration when needed

**Next Steps (Potential):**
- Integrate AICoach chat interface into layout
- Add database for explanation history
- Support more video sources (Vimeo, uploads)
- Enhanced time tracking accuracy
- User accounts/authentication

---

**Repository**: https://github.com/tanviria07/gaffer-s-chalkboard
**Team**: Tanvir IA (Frontend) + Ashraf Tutul (Backend)
