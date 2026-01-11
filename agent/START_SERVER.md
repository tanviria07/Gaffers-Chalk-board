# How to Start the Backend Server

## Quick Start

### Option 1: Using Environment Variable (Recommended)

```powershell
cd agent
$env:PORT=8001
python main.py
```

### Option 2: Edit .env file

1. Open `agent/.env` file
2. Change `PORT=8000` to `PORT=8001`
3. Save the file
4. Run: `python main.py`

### Option 3: Command Line

```powershell
cd agent
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## Verify Server is Running

Open browser: `http://localhost:8001/health`

You should see:
```json
{
  "status": "healthy",
  "service": "gaffer-agent",
  "version": "1.0.0",
  "has_api_key": false
}
```

## Frontend Configuration

The frontend (`vite.config.ts`) is already configured to proxy `/api` requests to `http://localhost:8001`.

## Troubleshooting

### Port Already in Use
- Port 8000 is already used by another service
- Use port 8001 instead (already configured)

### Server Won't Start
- Make sure you're in the `agent` directory
- Check Python version: `python --version` (should be 3.11+)
- Check dependencies: `pip list | findstr fastapi`

### Frontend Can't Connect
- Make sure backend is running on port 8001
- Check browser console for errors
- Verify `vite.config.ts` has correct port
