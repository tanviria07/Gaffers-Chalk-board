# Quick Start - Chatbot Testing

## Step 1: Create `.env` file

Create a file named `.env` in the `agent` folder with your Azure credentials:

```env
AZURE_OPENAI_KEY=YOUR_KEY_HERE
AZURE_OPENAI_ENDPOINT=https://ashra-mk0em67b-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-07-01-preview

PORT=8001
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:8080,http://localhost:5173,http://localhost:8083
```

## Step 2: Start the Backend

Open a **NEW terminal** (keep frontend running in the other one):

```powershell
cd agent
python main.py
```

You should see:
```
Starting Gaffer's Chalkboard Agent on 0.0.0.0:8001
```

## Step 3: Test the Backend

Open your browser and go to:
- **Health check**: http://localhost:8001/health
- **API docs**: http://localhost:8001/docs

You should see JSON response with `"status": "healthy"`

## Step 4: Test the Chatbot

1. Go to your frontend (already running)
2. Load a video
3. Scroll down to the chat widget (below the audio button)
4. Type a question like: "What's happening here?"
5. Press Enter or click Send

The chatbot should respond using Azure OpenAI!

## Troubleshooting

### Backend won't start?
- Make sure you're in the `agent` folder
- Check Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

### Chatbot not responding?
- Check backend is running: http://localhost:8001/health
- Open browser console (F12) and check for errors
- Make sure `.env` file has correct Azure credentials

### Port already in use?
- Change PORT in `.env` to 8002 or another port
- Update `vite.config.ts` proxy target to match
