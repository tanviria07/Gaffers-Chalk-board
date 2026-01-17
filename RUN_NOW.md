# 🚀 Run the App - Quick Guide

## ✅ Everything is Integrated!

All components are connected:
- ✅ Gemini services
- ✅ Overshoot integration  
- ✅ Backend endpoint
- ✅ Frontend component

---

## 📋 Run in 3 Steps

### Step 1: Install Dependencies

**Python:**
```bash
cd agent
pip install -r requirements.txt
```

**Node.js:**
```bash
cd backend
npm install
```

### Step 2: Start Services (3 Terminals)

**Terminal 1 - Python Backend:**
```bash
cd agent
python main.py
```
✅ Should see: `Starting Gaffer's Chalkboard Agent on 0.0.0.0:8000`

**Terminal 2 - Overshoot Service (Optional):**
```bash
cd backend
npm run overshoot
```
✅ Should see: `Overshoot Service: http://localhost:3002`

**Terminal 3 - Frontend:**
```bash
npm run dev
```
✅ Should see: `Local: http://localhost:5173/`

### Step 3: Open Browser

Go to: **http://localhost:5173**

---

## 🎬 Test It

1. Paste YouTube URL (any soccer video)
2. Play video
3. Watch **"Live Commentary"** panel update every 2 seconds!

---

## ✅ What Works

- Video loads ✅
- Live commentary updates ✅
- Soccer-focused commentary ✅
- No repetitive lines ✅

---

## 🐛 Quick Fixes

**"ModuleNotFoundError: google.generativeai"**
```bash
cd agent
pip install google-generativeai
```

**"Overshoot service error"**
- App still works! Uses Gemini Vision fallback automatically

**"Port in use"**
- Change `PORT=8001` in `agent/.env`

---

**Ready to test!** 🚀
