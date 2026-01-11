# Python FastAPI Agent Setup Guide

## Quick Start

### 1. Create Virtual Environment

```bash
cd agent
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the `agent` directory:

```env
# AI Provider Configuration
# Set to: "anthropic", "openai", or "stub" (default)
AI_PROVIDER=stub

# Anthropic Claude API Key (required if AI_PROVIDER=anthropic)
ANTHROPIC_API_KEY=your_anthropic_key_here

# OpenAI API Key (required if AI_PROVIDER=openai)
OPENAI_API_KEY=your_openai_key_here

# Server Configuration
PORT=8000
HOST=0.0.0.0

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:8080,http://localhost:5173,http://localhost:8083
```

**Note:** The service works in `stub` mode by default (no API keys needed, zero cost).

### 5. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 6. Test the Server

Open your browser and visit:
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

## Running with Frontend

1. Start Python agent: `cd agent && python main.py` (Terminal 1)
2. Start frontend: `npm run dev` (Terminal 2)
3. Open `http://localhost:8080` in browser

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running from the `agent` directory:
```bash
cd agent
python main.py
```

### Port Already in Use
Change the port in `.env`:
```env
PORT=8001
```

### CORS Errors
Add your frontend URL to `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```
