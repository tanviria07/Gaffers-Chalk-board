/**
 * Express Server for Explanation Agent API
 *
 * MVP implementation - STUB-FIRST by default (zero API cost)
 * Set AI_PROVIDER=openai or AI_PROVIDER=claude to use paid APIs
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// AI_PROVIDER: "stub" (default) | "openai" | "claude"
const AI_PROVIDER = (process.env.AI_PROVIDER || 'stub').toLowerCase();

app.use(cors());
app.use(express.json());

/**
 * Generate explanation using configured provider
 */
async function generateExplanation(userMessage, videoContext, style) {
  // Default to stub - only use paid APIs when explicitly enabled
  if (AI_PROVIDER === 'openai') {
    return generateWithOpenAI(userMessage, videoContext, style);
  }
  if (AI_PROVIDER === 'claude') {
    return generateWithClaude(userMessage, videoContext, style);
  }
  // Default: stub (free, fast, predictable)
  return generateStubResponse(userMessage, videoContext, style);
}

/**
 * OpenAI provider (only used when AI_PROVIDER=openai)
 */
async function generateWithOpenAI(userMessage, videoContext, style) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.warn('AI_PROVIDER=openai but OPENAI_API_KEY not set, falling back to stub');
    return generateStubResponse(userMessage, videoContext, style);
  }

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: buildSystemPrompt(videoContext, style) },
          { role: 'user', content: userMessage },
        ],
        temperature: 0.7,
        max_tokens: 500,
      }),
    });

    if (!response.ok) throw new Error(`OpenAI API error: ${response.status}`);
    const data = await response.json();
    const responseText = data.choices[0]?.message?.content || 'Unable to generate explanation.';

    return {
      responseText,
      timestampUsed: videoContext?.currentTime || 0,
      tags: extractTags(responseText),
    };
  } catch (error) {
    console.error('OpenAI error:', error);
    return generateStubResponse(userMessage, videoContext, style);
  }
}

/**
 * Claude/Anthropic provider (only used when AI_PROVIDER=claude)
 */
async function generateWithClaude(userMessage, videoContext, style) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.warn('AI_PROVIDER=claude but ANTHROPIC_API_KEY not set, falling back to stub');
    return generateStubResponse(userMessage, videoContext, style);
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307',
        max_tokens: 500,
        system: buildSystemPrompt(videoContext, style),
        messages: [{ role: 'user', content: userMessage }],
      }),
    });

    if (!response.ok) throw new Error(`Anthropic API error: ${response.status}`);
    const data = await response.json();
    const responseText = data.content[0]?.text || 'Unable to generate explanation.';

    return {
      responseText,
      timestampUsed: videoContext?.currentTime || 0,
      tags: extractTags(responseText),
    };
  } catch (error) {
    console.error('Anthropic error:', error);
    return generateStubResponse(userMessage, videoContext, style);
  }
}

/**
 * Build system prompt for AI providers
 */
function buildSystemPrompt(videoContext, style) {
  return `You are a soccer analyst explaining tactics and plays. The user is watching a soccer video.
Current video time: ${videoContext?.currentTime || 0} seconds.
Video source: ${videoContext?.provider || 'unknown'} (ID: ${videoContext?.videoId || 'N/A'})

Style: ${style}
- If style is "NFL analogies", use American football comparisons
- If style is "Beginner friendly", explain in simple terms
- If style is "Tactical", use technical soccer terminology

Provide concise, insightful explanations.`;
}

/**
 * StubAIProvider - Free, fast, predictable responses for MVP demos
 */
function generateStubResponse(userMessage, videoContext, style) {
  const currentTime = videoContext?.currentTime || 0;
  const minutes = Math.floor(currentTime / 60);
  const seconds = Math.floor(currentTime % 60);
  const timestamp = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  const lowerMessage = userMessage.toLowerCase();

  // Detect topic from user message
  const topic = detectTopic(lowerMessage);
  const tags = topic.tags;

  // Select response based on style and topic
  let responseText = '';

  if (style === 'NFL analogies') {
    responseText = NFL_RESPONSES[topic.key] || NFL_RESPONSES.default;
  } else if (style === 'Beginner friendly') {
    responseText = BEGINNER_RESPONSES[topic.key] || BEGINNER_RESPONSES.default;
  } else {
    responseText = TACTICAL_RESPONSES[topic.key] || TACTICAL_RESPONSES.default;
  }

  // Insert timestamp
  responseText = responseText.replace('{timestamp}', timestamp);

  return {
    responseText,
    timestampUsed: currentTime,
    tags: tags.length > 0 ? tags : undefined,
  };
}

/**
 * Detect topic from user message
 */
function detectTopic(message) {
  if (message.includes('press') || message.includes('pressing')) {
    return { key: 'pressing', tags: ['pressing'] };
  }
  if (message.includes('counter') || message.includes('transition') || message.includes('break')) {
    return { key: 'counter', tags: ['counter', 'transition'] };
  }
  if (message.includes('set-piece') || message.includes('corner') || message.includes('free kick')) {
    return { key: 'setpiece', tags: ['set-piece'] };
  }
  if (message.includes('goal') || message.includes('score') || message.includes('finish')) {
    return { key: 'goal', tags: ['goal'] };
  }
  if (message.includes('defend') || message.includes('block') || message.includes('compact')) {
    return { key: 'defensive', tags: ['defensive'] };
  }
  if (message.includes('space') || message.includes('movement') || message.includes('run')) {
    return { key: 'movement', tags: ['movement'] };
  }
  if (message.includes('buildup') || message.includes('build up') || message.includes('possession')) {
    return { key: 'buildup', tags: ['buildup'] };
  }
  return { key: 'default', tags: [] };
}

// NFL-style analogy responses
const NFL_RESPONSES = {
  pressing: `At {timestamp}, the team is running a **high press** — think of it like an all-out blitz in football. They're sending players forward to force a quick decision. If the opponent breaks the press, it's like a QB escaping the pocket with open field ahead.`,
  counter: `At {timestamp}, this is a classic **counter-attack** — like a pick-six! The team just won the ball and is sprinting upfield before the defense can reset. Speed and decision-making are everything here.`,
  setpiece: `At {timestamp}, we've got a **set-piece** situation. This is like a special teams play — everyone has a specific assignment. The attacking team has rehearsed routes, the defense is in zone coverage trying to win the aerial battle.`,
  goal: `At {timestamp}, that's a **touchdown moment**! The buildup created the opening, and the finish was clinical. Like a perfectly executed red zone play — spacing, timing, and execution all came together.`,
  defensive: `At {timestamp}, the defense is in a **compact shape** — similar to a prevent defense. They're protecting the middle, forcing play wide, and making sure no one gets behind the back line.`,
  movement: `At {timestamp}, watch the **off-ball movement** — it's like receivers running routes. The player without the ball is creating space, dragging defenders, and opening passing lanes for teammates.`,
  buildup: `At {timestamp}, the team is in a **buildup phase** — like a methodical drive down the field. Short passes, maintaining possession, waiting for the defense to make a mistake or create an opening.`,
  default: `At {timestamp}, we're seeing a tactical sequence unfold. Think of it like a well-designed play — every player has a role. The team with the ball is probing for weaknesses, while the defense is reading and reacting.`,
};

// Beginner-friendly responses
const BEGINNER_RESPONSES = {
  pressing: `At {timestamp}, the defending team is **pressing** — they're running toward the player with the ball to try to win it back quickly. It's aggressive but risky; if they don't win the ball, they leave space behind.`,
  counter: `At {timestamp}, this is a **counter-attack**! One team just lost the ball, and now the other team is racing forward while the defense is out of position. It's all about speed right now.`,
  setpiece: `At {timestamp}, we have a **set-piece** — a corner, free kick, or throw-in. The game stops and both teams set up in specific positions. It's a great chance to score from a rehearsed play.`,
  goal: `At {timestamp}, **GOAL!** The attacking team found an opening and took their chance. Watch the buildup — the passes, the movement — everything led to that moment.`,
  defensive: `At {timestamp}, the team without the ball is **defending deep**. They're staying close together, not letting attackers get behind them, and waiting for a chance to win the ball back.`,
  movement: `At {timestamp}, notice the **movement** — players running into space even without the ball. This creates confusion for defenders and opens up passing options.`,
  buildup: `At {timestamp}, the team is **building up slowly** — short passes, keeping the ball safe, looking for an opening. Patience is key here; they're waiting for the right moment to attack.`,
  default: `At {timestamp}, the team with the ball is trying to create a chance. They're passing, moving, and looking for gaps. The defense is organized and trying to block any clear opportunities.`,
};

// Tactical responses
const TACTICAL_RESPONSES = {
  pressing: `At {timestamp}, we're seeing a **coordinated press** with clear trigger points. The front line initiates when the ball goes to a specific zone, midfielders step up to cut passing lanes. The defensive line pushes high to compress space — classic gegenpressing principles.`,
  counter: `At {timestamp}, the team is executing a **vertical transition**. Upon winning possession, they immediately look for the forward pass into space. Notice the wide players stretching the recovering defensive line — this is transition football at its best.`,
  setpiece: `At {timestamp}, this **set-piece** shows interesting structural choices. The attacking team is using near-post runners to disrupt zonal markers, with late runners targeting the back post. The defensive setup appears to be a hybrid man-zonal system.`,
  goal: `At {timestamp}, the **goal sequence** demonstrates key principles: width to stretch the defense, patient buildup through the thirds, and clinical finishing. The final ball exploited the gap between the center-backs created by the striker's movement.`,
  defensive: `At {timestamp}, the team is in a **mid-to-low block**, maintaining horizontal compactness of about 35 meters. They're denying central access, forcing play wide, and the back four is holding a disciplined line.`,
  movement: `At {timestamp}, the **off-ball movement** is creating overloads in the half-spaces. The #10 is dropping to receive between lines while the #8 makes a blind-side run. This rotation is pulling the defensive structure apart.`,
  buildup: `At {timestamp}, classic **positional play** in the buildup phase. The center-backs split wide, the #6 drops to create a back-three, and the fullbacks push high. They're looking to progress through the thirds with controlled possession.`,
  default: `At {timestamp}, we're in a **phase of play** transition. The team in possession is probing the defensive block, looking for gaps between the lines. The key battle is in the half-spaces — the channels between the center and the flanks.`,
};

/**
 * Extract tags from response text
 */
function extractTags(text) {
  const tagKeywords = {
    pressing: ['press', 'pressing', 'high press', 'counter-press'],
    counter: ['counter', 'counter-attack', 'transition', 'break'],
    'set-piece': ['set-piece', 'corner', 'free kick', 'throw-in'],
    goal: ['goal', 'score', 'finish'],
    defensive: ['defense', 'defensive', 'block', 'compact'],
  };

  const lowerText = text.toLowerCase();
  const foundTags = [];

  for (const [tag, keywords] of Object.entries(tagKeywords)) {
    if (keywords.some(keyword => lowerText.includes(keyword))) {
      foundTags.push(tag);
    }
  }

  return foundTags;
}

/**
 * POST /api/explain
 * Generate explanation for a video moment
 */
app.post('/api/explain', async (req, res) => {
  try {
    const { userMessage, videoContext, style } = req.body;

    if (!userMessage) {
      return res.status(400).json({ error: 'userMessage is required' });
    }

    const result = await generateExplanation(userMessage, videoContext, style);
    res.json(result);
  } catch (error) {
    console.error('Error in /api/explain:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    provider: AI_PROVIDER,
    hasOpenAIKey: !!process.env.OPENAI_API_KEY,
    hasAnthropicKey: !!process.env.ANTHROPIC_API_KEY,
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`AI Provider: ${AI_PROVIDER} (set AI_PROVIDER env to change)`);
});
