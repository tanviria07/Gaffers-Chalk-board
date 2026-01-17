import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { getSubtitles } from 'youtube-captions-scraper';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

const AI_PROVIDER = (process.env.AI_PROVIDER || 'stub').toLowerCase();

const captionsCache = new Map();
const analogyCache = new Map();

app.use(cors());
app.use(express.json());

async function generateExplanation(userMessage, videoContext, style) {
  if (AI_PROVIDER === 'openai') {
    return generateWithOpenAI(userMessage, videoContext, style);
  }
  if (AI_PROVIDER === 'claude') {
    return generateWithClaude(userMessage, videoContext, style);
  }
  return generateStubResponse(userMessage, videoContext, style);
}

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

function generateStubResponse(userMessage, videoContext, style) {
  const currentTime = videoContext?.currentTime || 0;
  const minutes = Math.floor(currentTime / 60);
  const seconds = Math.floor(currentTime % 60);
  const timestamp = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  const lowerMessage = userMessage.toLowerCase();

  const topic = detectTopic(lowerMessage);
  const tags = topic.tags;

  let responseText = '';

  if (style === 'NFL analogies') {
    responseText = NFL_RESPONSES[topic.key] || NFL_RESPONSES.default;
  } else if (style === 'Beginner friendly') {
    responseText = BEGINNER_RESPONSES[topic.key] || BEGINNER_RESPONSES.default;
  } else {
    responseText = TACTICAL_RESPONSES[topic.key] || TACTICAL_RESPONSES.default;
  }

  responseText = responseText.replace('{timestamp}', timestamp);

  return {
    responseText,
    timestampUsed: currentTime,
    tags: tags.length > 0 ? tags : undefined,
  };
}

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

async function fetchCaptions(videoId) {
  if (captionsCache.has(videoId)) {
    return captionsCache.get(videoId);
  }

  try {
    const captions = await getSubtitles({
      videoID: videoId,
      lang: 'en',
    });
    captionsCache.set(videoId, captions);
    return captions;
  } catch (error) {
    console.error('Error fetching captions:', error.message);
    return [];
  }
}

function getCaptionAtTimestamp(captions, timestamp) {
  if (!captions || captions.length === 0) {
    return null;
  }

  const caption = captions.find(cap => {
    const start = parseFloat(cap.start);
    const duration = parseFloat(cap.dur) || 2;
    return timestamp >= start && timestamp <= start + duration + 2;
  });

  if (caption) {
    return caption.text;
  }

  let nearest = null;
  let nearestDiff = Infinity;
  for (const cap of captions) {
    const start = parseFloat(cap.start);
    const diff = Math.abs(timestamp - start);
    if (diff < nearestDiff && diff <= 5) {
      nearestDiff = diff;
      nearest = cap;
    }
  }

  return nearest ? nearest.text : null;
}

async function generateNFLAnalogy(commentary, videoContext) {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  const prompt = `You are a sports analyst who explains soccer plays using NFL analogies for American football fans.

Convert this soccer commentary into an NFL analogy that American football fans would understand:

"${commentary}"

Instructions:
- Use NFL terminology and concepts
- Compare soccer positions to NFL positions (e.g., striker = receiver making a catch, midfielder = quarterback, defender = linebacker)
- Keep it concise (2-3 sentences max)
- Make it engaging and easy to understand
- Focus on the tactical parallel between the sports

Respond with ONLY the NFL analogy, no preamble.`;

  if (!apiKey) {
    return generateStubNFLAnalogy(commentary);
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
        max_tokens: 200,
        messages: [{ role: 'user', content: prompt }],
      }),
    });

    if (!response.ok) {
      throw new Error(`Anthropic API error: ${response.status}`);
    }

    const data = await response.json();
    return data.content[0]?.text || generateStubNFLAnalogy(commentary);
  } catch (error) {
    console.error('Error generating NFL analogy:', error.message);
    return generateStubNFLAnalogy(commentary);
  }
}

function generateStubNFLAnalogy(commentary) {
  const lowerCommentary = commentary.toLowerCase();

  if (lowerCommentary.includes('goal') || lowerCommentary.includes('score')) {
    return "That's a touchdown moment! The striker hit the back of the net like a receiver catching a fade route in the end zone — perfect timing, perfect execution.";
  }
  if (lowerCommentary.includes('pass') || lowerCommentary.includes('through')) {
    return "Think of that pass like a QB threading a seam route between the linebackers and safeties. The timing window was tiny, and the midfielder hit it perfectly.";
  }
  if (lowerCommentary.includes('defend') || lowerCommentary.includes('block') || lowerCommentary.includes('tackle')) {
    return "That defensive play is like a linebacker reading the quarterback's eyes and jumping the route. Great anticipation to cut off the attacking lane.";
  }
  if (lowerCommentary.includes('save') || lowerCommentary.includes('keeper') || lowerCommentary.includes('goalkeeper')) {
    return "The goalkeeper made a save like a safety coming over the top to break up a deep ball. Last line of defense doing their job perfectly.";
  }
  if (lowerCommentary.includes('foul') || lowerCommentary.includes('card')) {
    return "That's a professional foul — like an intentional holding penalty when you're beat. Take the flag instead of giving up the big play.";
  }
  if (lowerCommentary.includes('corner') || lowerCommentary.includes('set piece')) {
    return "This set piece is like a goal-line package play. Everyone has an assignment, and it's all about execution and winning the one-on-one battles.";
  }

  return "This play is like a well-designed offensive scheme — every player has a role, creating space and options. The team with the ball is probing for weaknesses while the defense reads and reacts.";
}

function determineDiagramType(commentary) {
  const lowerCommentary = commentary.toLowerCase();

  if (lowerCommentary.includes('goal') || lowerCommentary.includes('score') || lowerCommentary.includes('finish')) {
    return 'goal';
  }
  if (lowerCommentary.includes('through') || lowerCommentary.includes('pass')) {
    return 'through-ball';
  }
  if (lowerCommentary.includes('offside') || lowerCommentary.includes('trap')) {
    return 'offside-trap';
  }
  return 'defensive';
}

app.post('/api/generate-analogy', async (req, res) => {
  try {
    const { videoId, timestamp, caption: providedCaption } = req.body;

    if (!videoId) {
      return res.status(400).json({ error: 'videoId is required' });
    }

    const ts = parseFloat(timestamp) || 0;
    const cacheKey = `${videoId}-${Math.floor(ts / 5) * 5}`;

    if (analogyCache.has(cacheKey)) {
      console.log(`Cache hit for ${cacheKey}`);
      return res.json(analogyCache.get(cacheKey));
    }

    let commentary = providedCaption;
    if (!commentary) {
      const captions = await fetchCaptions(videoId);
      commentary = getCaptionAtTimestamp(captions, ts);
    }

    if (!commentary) {
      commentary = `Soccer action at ${Math.floor(ts / 60)}:${Math.floor(ts % 60).toString().padStart(2, '0')}`;
    }

    const nflAnalogy = await generateNFLAnalogy(commentary, { videoId, timestamp: ts });
    const fieldDiagram = determineDiagramType(commentary);

    const result = {
      originalCommentary: commentary,
      nflAnalogy,
      fieldDiagram,
      timestamp: ts,
      videoId,
      cached: false,
    };

    analogyCache.set(cacheKey, { ...result, cached: true });

    res.json(result);
  } catch (error) {
    console.error('Error in /api/generate-analogy:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/captions/:videoId', async (req, res) => {
  try {
    const { videoId } = req.params;
    const captions = await fetchCaptions(videoId);
    res.json({ videoId, captions, count: captions.length });
  } catch (error) {
    console.error('Error fetching captions:', error);
    res.status(500).json({ error: 'Failed to fetch captions' });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    provider: AI_PROVIDER,
    hasOpenAIKey: !!process.env.OPENAI_API_KEY,
    hasAnthropicKey: !!process.env.ANTHROPIC_API_KEY,
    captionsCacheSize: captionsCache.size,
    analogyCacheSize: analogyCache.size,
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`AI Provider: ${AI_PROVIDER} (set AI_PROVIDER env to change)`);
});
