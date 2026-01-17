# Overshoot Integration Setup

## ✅ What I Built

1. **Node.js Service** (`backend/overshoot-service.js`)
   - Runs on port 3002
   - Uses `@overshoot/sdk` to get frames
   - Exposes HTTP endpoint for Python to call

2. **Python Integration** (`agent/services/frame_window_service.py`)
   - Calls Node.js service via HTTP
   - Falls back to YouTube extractor if Overshoot unavailable

---

## 🚀 Setup Steps

### 1. Install Overshoot SDK

```bash
cd backend
npm install @overshoot/sdk
```

### 2. Start Overshoot Service

```bash
cd backend
npm run overshoot
```

Or run both services:
```bash
npm run dev:all
```

### 3. Verify It's Running

Check health:
```bash
curl http://localhost:3002/health
```

Should return:
```json
{
  "status": "ok",
  "service": "overshoot-service",
  "sdk_installed": true,
  "client_initialized": true,
  "has_api_key": true
}
```

---

## ⚠️ Important: Update Overshoot API Call

The Node.js service has a **placeholder** for the actual Overshoot API call.

**File**: `backend/overshoot-service.js`

**Line ~50-60**: Update this section with actual Overshoot SDK code:

```javascript
// CURRENT (placeholder):
return res.status(501).json({
  error: 'Overshoot SDK integration pending - need actual API documentation'
});

// REPLACE WITH (when you have SDK docs):
const stream = await overshootClient.connectStream(videoUrl);
const frames = await stream.getFrames(startTime, endTime);
// ... actual API call
```

---

## 📋 What You Need

1. **Overshoot SDK Documentation**
   - How to initialize client?
   - How to connect to YouTube video?
   - How to get frames from stream?

2. **Code Example**
   - Sample code showing how to use `@overshoot/sdk`
   - Example: `stream.getFrames()` or similar

3. **Update Node.js Service**
   - Replace placeholder in `overshoot-service.js`
   - Test with: `curl -X POST http://localhost:3002/get-frame-window -d '{"videoUrl":"...","currentTime":10}'`

---

## 🔄 How It Works

```
Python Backend
    ↓
Calls HTTP: POST http://localhost:3002/get-frame-window
    ↓
Node.js Service (overshoot-service.js)
    ↓
Uses @overshoot/sdk to get frames
    ↓
Returns frames to Python
    ↓
Python sends to Gemini Vision
```

---

## 🐛 Troubleshooting

### "SDK not installed"
```bash
cd backend
npm install @overshoot/sdk
```

### "Service not available"
- Check if service is running: `curl http://localhost:3002/health`
- Start it: `npm run overshoot`

### "Client not initialized"
- Check `OVERSHOOT_API_KEY` in `.env`
- Verify API key is correct

### "501 - Integration pending"
- Update `overshoot-service.js` with actual Overshoot API code
- Need SDK documentation to complete

---

## ✅ Status

- ✅ Node.js service created
- ✅ Python integration ready
- ✅ Fallback to YouTube extractor works
- ⏳ Need: Actual Overshoot SDK API code (update `overshoot-service.js`)

**Once you have Overshoot SDK docs, update the placeholder and it's done!**
