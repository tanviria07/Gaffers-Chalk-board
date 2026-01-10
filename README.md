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
- **Backend**: Express.js (Node.js)
- **AI Integration**: OpenAI API (optional, falls back to smart stubs)

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
