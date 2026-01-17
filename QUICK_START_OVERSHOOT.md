# Quick Start: Overshoot Integration

## ✅ What I Built

1. **Node.js Service** - `backend/overshoot-service.js`
   - Runs on port 3002
   - Uses `@overshoot/sdk` to get frames
   - Python calls it via HTTP

2. **Python Integration** - Updated `frame_window_service.py`
   - Tries Overshoot first
   - Falls back to YouTube extractor if Overshoot fails

---

## 🚀 Setup (3 Steps)

### Step 1: Install Overshoot SDK
```bash
cd backend
npm install @overshoot/sdk
```

### Step 2: Start Overshoot Service
```bash
npm run overshoot
```

### Step 3: Update API Call
Edit `backend/overshoot-service.js` line ~50-60:
- Replace placeholder with actual Overshoot SDK code
- Need: SDK documentation or code example

---

## ⚠️ Important

The Node.js service has a **placeholder** that needs the actual Overshoot API code.

**Get from Overshoot team:**
- How to initialize client?
- How to connect to YouTube video?
- How to get frames?

**Then update `backend/overshoot-service.js`**

---

## ✅ Status

- ✅ Node.js service ready
- ✅ Python integration ready  
- ✅ Fallback works
- ⏳ Need: Actual Overshoot SDK code

**Once you update the placeholder, it's done!**
