# Gaffer's Chalkboard

An AI-powered soccer explanation app that helps users understand soccer tactics and plays using interactive video analysis and intelligent explanations.

## Features

- **Video URL Input**: Paste YouTube video URLs to load and watch soccer matches
- **AI Coach**: Interactive chat interface that explains what's happening in the video
- **Multiple Explanation Styles**: 
  - NFL Analogies (for American football fans)
  - Beginner Friendly (simple explanations)
  - Tactical (technical soccer terminology)
- **Video Context Tracking**: Automatically tracks current video time and context
- **Event Timeline**: Visual timeline of match events
- **Tactics Diagrams**: Interactive diagrams explaining tactical concepts

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **UI Components**: shadcn/ui + Tailwind CSS
- **Backend**: Python FastAPI
- **AI Integration**: Google Gemini API
- **Text-to-Speech**: ElevenLabs API

## Environment Variables

Create a `.env` file in the `agent/` directory:

```bash
# Required for AI features
GEMINI_API_KEY=your-gemini-api-key

# Required for voice playback (TTS)
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Optional
GEMINI_MODEL=gemini-1.5-flash
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```

## API Endpoints

### POST `/api/nfl-analogy`

Convert soccer commentary to NFL analogy and broadcast-style commentary.

**Request:**
```json
{
  "soccer_commentary": "The midfielder plays a through ball to the striker..."
}
```

**Response:**
```json
{
  "nfl_analogy": "Tactical explanation using NFL concepts (2-4 sentences)",
  "nfl_commentary": "Energetic broadcast style (15-35 words)"
}
```

**Rules:**
- Stays faithful to the soccer commentary (no invented events)
- Uses generic NFL terms only (no real team/player/stadium names)
- Uses terms like: offense, defense, quarterback, drive, snap, red zone

### POST `/api/tts`

Convert text to speech using ElevenLabs.

**Request:**
```json
{
  "text": "The offense finds the end zone!"
}
```

**Response:**
- Content-Type: `audio/mpeg`
- Returns playable MP3 audio bytes

### Other Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | POST | Analyze video frame at timestamp |
| `/api/chat` | POST | Interactive Q&A about video |
| `/api/live-commentary` | POST | Real-time commentary generation |
| `/api/captions/{video_id}` | GET | Fetch YouTube captions |
| `/api/video-metadata/{video_id}` | GET | Video metadata |
| `/health` | GET | Health check with service status |

## Usage

1. **Load a Video**: Paste a YouTube URL in the input field at the top
2. **Ask Questions**: Use the AI Coach panel on the right to ask questions like:
   - "Explain what's happening right now"
   - "Who's pressing and why?"
   - "Summarize the last 30 seconds"
3. **Choose Style**: Select your preferred explanation style from the dropdown
4. **View Timeline**: Browse match events in the timeline below the video

## Team

- **Tanvir IA** - Frontend Development, AI Coach UI, Video Integration
- **Ashraf Tutul** - Backend API Development

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with React, Vite, and TypeScript
- UI components from shadcn/ui
- Icons from Lucide React

---

## 🚀 Built with DevSwarm (Sponsor Challenge)

**This project was built and shipped using DevSwarm for NexHacks.**

- DevSwarm was used as the primary development environment for this hackathon project
- An AI coding agent (Claude Code) worked in an isolated `repo-audit` branch, separate from `main`
- Backend services (`/api/nfl-analogy`, `/api/tts`) were implemented without blocking the main branch
- Frontend integration (NFL Commentary UI, Play Voice button) was developed in parallel
- Full documentation was auto-generated alongside code changes
- DevSwarm enabled rapid iteration, safe experimentation, and end-to-end shipping within hackathon time constraints
- Zero merge conflicts — all changes were developed, tested, and committed in isolation

### How DevSwarm Accelerated Development

- **Isolated Branches**: AI agent worked on a dedicated branch, keeping `main` stable and deployable at all times
- **Agent-Driven Workflow**: Comprehensive repo audit + feature implementation handled by Claude Code with full context awareness
- **No Context Switching**: Backend (Python FastAPI), frontend (React/TypeScript), and documentation developed in a single continuous session
- **Safe Parallel Work**: New features were built and verified without risk to existing functionality
