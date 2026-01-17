# How to Ask Questions - Best Practices

## ✅ Good Ways to Ask

### 1. **Specific Timestamps**

**Best Formats:**
- "What happened at 25 seconds"
- "What happened at 0:25"
- "What happened at 1:15"
- "What happened at 2:30"
- "What happened in 25 second"
- "What happened in 25 seconds"

**Why it works:**
- System parses the timestamp correctly
- Analyzes 10s before + 15s after that moment
- Dense frame sampling after timestamp catches goals

---

### 2. **"What's Happening Now"**

**Best Formats:**
- "What's happening now"
- "What's happening right now"
- "What happened now"
- "What is happening now"

**Why it works:**
- Uses the exact moment you ask (frozen timestamp)
- Analyzes 10s before + 15s after that moment
- Won't change as video plays

---

### 3. **Specific Events**

**Best Formats:**
- "Was there a goal at 25 seconds"
- "Did someone score at 1:30"
- "What was the goal at 2:15"
- "Show me the save at 0:45"

**Why it works:**
- System focuses on that timestamp
- Dense sampling after timestamp catches the event
- AI is instructed to look for goals/saves

---

### 4. **Player-Specific Questions**

**Best Formats:**
- "What did Raphinha do at 25 seconds"
- "What happened with Messi at 1:20"
- "Show me Ronaldo at 2:00"

**Why it works:**
- System analyzes frames at that timestamp
- Object detection identifies players
- Can track specific player actions

---

## ❌ Avoid These Formats

### 1. **Vague Questions**
- ❌ "What happened"
- ❌ "Tell me about this"
- ❌ "What's going on"
- ✅ Better: "What happened at 25 seconds" or "What's happening now"

### 2. **Complex Questions**
- ❌ "What happened at 25 seconds and also at 1:30"
- ✅ Better: Ask separately - "What happened at 25 seconds" then "What happened at 1:30"

### 3. **Future/Past Relative Time**
- ❌ "What happened 5 seconds ago" (system doesn't track relative time)
- ✅ Better: Calculate and ask "What happened at 20 seconds" (if current is 25s)

---

## 📋 Question Templates

### Template 1: Specific Moment
```
"What happened at [timestamp]"
Examples:
- "What happened at 25 seconds"
- "What happened at 1:15"
- "What happened at 0:30"
```

### Template 2: Current Moment
```
"What's happening now"
or
"What happened now"
```

### Template 3: Event Check
```
"Was there a [event] at [timestamp]"
Examples:
- "Was there a goal at 25 seconds"
- "Was there a save at 1:30"
- "Was there a foul at 2:15"
```

### Template 4: Player Action
```
"What did [player] do at [timestamp]"
Examples:
- "What did Raphinha do at 25 seconds"
- "What did Messi do at 1:20"
```

---

## 🎯 Best Practices

### 1. **Be Specific with Timestamps**
- ✅ "What happened at 25 seconds"
- ❌ "What happened around 25 seconds" (still works, but less precise)

### 2. **Use Simple Language**
- ✅ "What happened at 25 seconds"
- ❌ "Can you provide an analysis of the events that transpired at the 25-second mark" (works but unnecessary)

### 3. **Ask One Thing at a Time**
- ✅ "What happened at 25 seconds" (wait for answer)
- ✅ Then: "What happened at 1:30" (ask separately)
- ❌ "What happened at 25 seconds and 1:30" (ask separately)

### 4. **Use Natural Language**
- ✅ "What happened at 25 seconds"
- ✅ "What happened in 25 second"
- ✅ "What happened at 0:25"
- All work the same!

---

## 🔍 How the System Processes Your Question

### Example: "What happened at 25 seconds"

1. **Parse Timestamp**
   - Finds "25" in your message
   - Converts to 25 seconds

2. **Calculate Window**
   - Before: 15s-25s (10 seconds, sparse sampling)
   - At: 25s (exact timestamp)
   - After: 25s-40s (15 seconds, DENSE sampling)

3. **Extract Frames**
   - Before: 15s, 18s, 21s, 24s (4 frames)
   - At: 25s (1 frame)
   - After: 26s, 27s, 28s... 40s (15 frames, DENSE!)

4. **Analyze Frames**
   - YOLOv8: Detects players, ball
   - MediaPipe: Detects actions
   - GPT-4 Vision: Understands what's happening

5. **Generate Response**
   - Combines all frame analyses
   - Focuses on frames AFTER timestamp (where goals happen)
   - Gives accurate answer

---

## 💡 Pro Tips

### Tip 1: Ask About Key Moments
- Goals usually happen quickly (1-3 seconds)
- Dense sampling after timestamp catches them
- Ask: "What happened at [moment before goal]"

### Tip 2: Be Patient
- Analysis takes ~45-60 seconds
- System is analyzing 20 frames with AI
- Wait for the response

### Tip 3: Check Backend Logs
- If question doesn't work, check logs:
  - `[CHAT] Parsed timestamp...` - Did it parse?
  - `[CHAT] Extracted X frames...` - Are frames extracted?
  - `[CHAT] ✓ Vision AI analyzed...` - Did analysis work?

### Tip 4: Try Different Formats
- If "25 second" doesn't work, try "25 seconds"
- If "0:25" doesn't work, try "25 seconds"
- System handles multiple formats

---

## 📝 Examples

### Example 1: Goal Detection
**Question**: "What happened at 25 seconds"
**Expected**: System analyzes 15s-40s, catches goal at 26-30s
**Response**: "At 25 seconds, Raphinha receives the ball. At 26 seconds, he takes a shot. At 27 seconds, the ball enters the goal..."

### Example 2: Current Moment
**Question**: "What's happening now" (video at 1:30)
**Expected**: System analyzes 1:20-1:45, focuses on 1:30-1:45
**Response**: Accurate description of current play

### Example 3: Player Action
**Question**: "What did Raphinha do at 25 seconds"
**Expected**: System analyzes frames, identifies Raphinha, describes his actions
**Response**: "Raphinha received a pass, dribbled past defender, took a shot..."

---

## 🚀 Quick Reference

| Question Type | Best Format | Example |
|--------------|-------------|---------|
| **Specific Time** | "What happened at [time]" | "What happened at 25 seconds" |
| **Current Time** | "What's happening now" | "What's happening now" |
| **Event Check** | "Was there a [event] at [time]" | "Was there a goal at 25 seconds" |
| **Player Action** | "What did [player] do at [time]" | "What did Raphinha do at 25 seconds" |

---

## Summary

✅ **DO:**
- Use specific timestamps: "What happened at 25 seconds"
- Use simple, natural language
- Ask one question at a time
- Be patient (takes 45-60 seconds)

❌ **DON'T:**
- Ask vague questions without timestamps
- Ask multiple things at once
- Use overly complex language
- Expect instant responses

**Best Question Format**: "What happened at [timestamp]"

That's it! Keep it simple and specific. 🎯
