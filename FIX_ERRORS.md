# 🔧 Fix: Backend Not Running

## ❌ Error
```
ECONNREFUSED - Cannot connect to http://localhost:8000
/api/live-commentary 500 (Internal Server Error)
```

## ✅ Solution: Start Python Backend

### Step 1: Open New Terminal
Open a **new terminal/PowerShell window**

### Step 2: Start Backend
```bash
cd agent
python main.py
```

### Step 3: Check Output
You should see:
```
Starting Gaffer's Chalkboard Agent on 0.0.0.0:8000
Gemini enabled: True
API Docs available at: http://0.0.0.0:8000/docs
```

---

## 🐛 If Backend Fails to Start

### Error: "ModuleNotFoundError: google.generativeai"
```bash
cd agent
pip install google-generativeai
```

### Error: "ModuleNotFoundError: google"
```bash
cd agent
pip install google-generativeai
```

### Error: Port 8000 already in use
Change port in `agent/.env`:
```env
PORT=8001
```
Then update `vite.config.ts`:
```typescript
target: 'http://localhost:8001'
```

---

## ✅ After Backend Starts

1. **Backend running** on `http://localhost:8000` ✓
2. **Frontend** on `http://localhost:8080` ✓
3. **Refresh browser** - errors should stop!

---

## 📋 Quick Checklist

- [ ] Python backend running (`python main.py`)
- [ ] No import errors
- [ ] Backend shows "Starting on port 8000"
- [ ] Frontend can connect (no ECONNREFUSED)

---

**Start the backend and the errors will stop!**
