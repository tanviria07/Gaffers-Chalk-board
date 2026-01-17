# 🚨 Fix: Backend Not Running

## ❌ Problem
```
ECONNREFUSED - Cannot connect to http://localhost:8000
/api/live-commentary 500 (Internal Server Error)
```

**The Python backend is NOT running!**

---

## ✅ Solution: Start Backend

### Step 1: Open New Terminal/PowerShell

### Step 2: Install Missing Package
```bash
cd agent
pip install google-generativeai
```

### Step 3: Start Backend
```bash
python main.py
```

### Step 4: Check Output
You should see:
```
Starting Gaffer's Chalkboard Agent on 0.0.0.0:8000
Gemini enabled: True
API Docs available at: http://0.0.0.0:8000/docs
```

---

## ✅ After Backend Starts

1. **Keep terminal open** (don't close it!)
2. **Refresh browser** - errors should stop
3. **Commentary should work**

---

## 🐛 If Backend Fails

### Error: "ModuleNotFoundError: google.generativeai"
```bash
pip install google-generativeai
```

### Error: "Port 8000 already in use"
- Kill process using port 8000
- Or change port in `agent/.env`: `PORT=8001`
- Update `vite.config.ts`: `target: 'http://localhost:8001'`

---

## 📋 Quick Checklist

- [ ] Backend terminal open
- [ ] `python main.py` running
- [ ] No import errors
- [ ] Shows "Starting on port 8000"
- [ ] Browser refreshed

---

**Start the backend and errors will stop!** 🚀
