# 🚀 How to Run the Web App

## ✅ Integration Check

Everything is integrated:
- ✅ Gemini Vision + Text services
- ✅ Overshoot integration (Node.js service)
- ✅ Commentary orchestrator
- ✅ Backend endpoint `/api/live-commentary`
- ✅ Frontend `LiveCommentary` component
- ✅ All imports and connections verified

---

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** installed
3. **Gemini API Key** in `agent/.env`
4. **Overshoot API Key** in `agent/.env` (optional - fallback works)

---

## 🚀 Step-by-Step Run Instructions

### Step 1: Install Python Dependencies

```bash
cd agent
pip install -r requirements.txt
```

**Important:** Make sure `google-generativeai` is installed:
```bash
pip install google-generativeai
```

### Step 2: Install Node.js Dependencies

```bash
cd backend
npm install
```

This installs:
- `@overshoot/sdk` (already in package.json)
- `express`, `cors`, `dotenv`

### Step 3: Verify Environment Variables

Check `agent/.env` has:
```env
GEMINI_API_KEY=AIzaSyAGRRq39y5c3MtyePBebK7-DVIHOQ4gUd4
OVERSHOOT_API_KEY=ovs_5caef01157a3d7b22c20155eb04a5fef
```

### Step 4: Start Backend Services

**Terminal 1 - Python Backend:**
```bash
cd agent
python main.py
```

Should see:
```
Starting Gaffer's Chalkboard Agent on 0.0.0.0:8000
Gemini enabled: True
```

**Terminal 2 - Overshoot Service (Optional):**
```bash
cd backend
npm run overshoot
```

Should see:
```
Overshoot Service: http://localhost:3002
API Key: Set ✓
```

**Note:** If Overshoot service fails, the app will use Gemini Vision fallback automatically.

### Step 5: Start Frontend

**Terminal 3 - Frontend:**
```bash
npm run dev
```

Should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

---

## 🌐 Access the App

Open browser: **http://localhost:5173**

---

## 🎬 How to Test

1. **Paste YouTube URL** in the input field
2. **Play the video**
3. **Watch "Live Commentary" panel** (top of right column)
4. **Commentary updates every 2 seconds** automatically

---

## ✅ What Should Work

- ✅ Video loads and plays
- ✅ "Live Commentary" panel appears
- ✅ Commentary updates every 2 seconds
- ✅ Commentary is soccer-focused (no NFL)
- ✅ Natural, broadcast-style commentary
- ✅ No repetitive commentary (deduplication)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: google.generativeai"
```bash
cd agent
pip install google-generativeai
```

### "Overshoot service not available"
- Check if `npm run overshoot` is running
- If not, app uses Gemini Vision fallback (still works!)

### "No commentary appearing"
- Check browser console for errors
- Check Python backend logs
- Verify Gemini API key is correct

### "Port already in use"
- Change port in `agent/.env`: `PORT=8001`
- Or kill process using port 8000

---

## 📊 Services Running

When everything is running, you should have:

1. **Python Backend** - `http://localhost:8000`
   - FastAPI server
   - `/api/live-commentary` endpoint

2. **Overshoot Service** (optional) - `http://localhost:3002`
   - Node.js service
   - Uses `@overshoot/sdk`

3. **Frontend** - `http://localhost:5173`
   - React app
   - Calls Python backend

---

## 🎯 Quick Test

1. Start all services (3 terminals)
2. Open `http://localhost:5173`
3. Paste: `https://www.youtube.com/watch?v=dQw4w9WgXcQ` (or any soccer video)
4. Play video
5. Watch "Live Commentary" update!

---

**Everything is integrated and ready to test!** 🚀
