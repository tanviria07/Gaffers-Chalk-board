# Chat Feature Setup

The chatbot feature uses Azure OpenAI to answer questions about video plays.

## Quick Setup

1. **Create `.env` file** in the `agent` directory (copy from `.env.example`)

2. **Add your Azure OpenAI credentials**:

```env
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-07-01-preview
```

3. **Restart the Python backend**:
```bash
cd agent
python main.py
```

## How It Works

1. User asks a question in the chat widget
2. Frontend sends request to `/api/chat` with:
   - `videoId`: Current video ID
   - `timestamp`: Current playback time
   - `userMessage`: User's question
   - `context`: Current analysis (commentary + NFL analogy)

3. Backend uses Azure OpenAI GPT-4o-mini to generate intelligent response
4. Response is displayed in the chat widget

## Features

- **Context-aware**: Uses current play analysis for better answers
- **Timestamp-aware**: References specific moments in the video
- **NFL analogies**: Can explain using American football comparisons
- **Fallback**: Uses stub responses if Azure OpenAI is not configured

## Testing

1. Start the backend: `cd agent && python main.py`
2. Load a video in the frontend
3. Ask questions like:
   - "What's happening here?"
   - "Why did that player move there?"
   - "Explain this tactic"
   - "What's the NFL equivalent?"

## Troubleshooting

### Chat not working
- Check that `.env` file has correct Azure credentials
- Verify backend is running: `http://localhost:8000/health`
- Check browser console for errors

### Getting stub responses
- Verify `AZURE_OPENAI_KEY` is set correctly
- Check that `AZURE_OPENAI_ENDPOINT` includes the full URL
- Ensure deployment name matches your Azure deployment

### API errors
- Verify your Azure OpenAI resource is active
- Check that the deployment name is correct
- Ensure API version matches your Azure setup
