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

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tanviria07/gaffer-s-chalkboard.git
   cd gaffer-s-chalkboard
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   npm install
   cd ..
   ```

## Running the Application

You need to run both the frontend and backend servers:

**Terminal 1 - Backend Server:**
```bash
cd backend
npm run dev
```
The backend will run on `http://localhost:3001`

**Terminal 2 - Frontend:**
```bash
npm run dev
```
The frontend will run on `http://localhost:8080`

Open your browser and navigate to `http://localhost:8080`

### Optional: AI API Setup

To use real AI explanations (instead of stub responses), create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=3001
```

**Note**: The app works without an API key using intelligent stub responses for testing.

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
