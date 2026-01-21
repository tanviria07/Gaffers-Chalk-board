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

**Rules:**
- Stays faithful to the soccer commentary (no invented events)
- Uses generic NFL terms only (no real team/player/stadium names)
- Uses terms like: offense, defense, quarterback, drive, snap, red zone


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
