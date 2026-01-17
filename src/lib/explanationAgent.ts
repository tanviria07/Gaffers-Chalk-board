import { VideoContext } from './videoContext';

export type ExplanationStyle = 'NFL analogies' | 'Beginner friendly' | 'Tactical';

export interface AgentInput {
  userMessage: string;
  videoContext: VideoContext | null;
  style: ExplanationStyle;
}

export interface AgentOutput {
  responseText: string;
  timestampUsed: number;
  tags?: string[];
}

export async function generateExplanation(input: AgentInput): Promise<AgentOutput> {
  try {
    const response = await fetch('/api/explain', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    return generateStubExplanation(input);
  }
}

function generateStubExplanation(input: AgentInput): AgentOutput {
  const { userMessage, videoContext, style } = input;
  const currentTime = videoContext?.currentTime || 0;
  const minutes = Math.floor(currentTime / 60);
  const seconds = Math.floor(currentTime % 60);

  const lowerMessage = userMessage.toLowerCase();
  const tags: string[] = [];

  if (lowerMessage.includes('press') || lowerMessage.includes('pressing')) {
    tags.push('pressing');
  }
  if (lowerMessage.includes('counter') || lowerMessage.includes('counter-attack')) {
    tags.push('counter');
  }
  if (lowerMessage.includes('set-piece') || lowerMessage.includes('corner') || lowerMessage.includes('free kick')) {
    tags.push('set-piece');
  }
  if (lowerMessage.includes('goal')) {
    tags.push('goal');
  }
  if (lowerMessage.includes('defense') || lowerMessage.includes('defensive')) {
    tags.push('defensive');
  }

  let responseText = '';

  if (style === 'NFL analogies') {
    if (lowerMessage.includes('press') || lowerMessage.includes('pressing')) {
      responseText = `At ${minutes}:${seconds.toString().padStart(2, '0')}, the team is applying a **high press**. This is like a **blitz in football** — you're sending extra defenders forward to force a quick decision. The risk? If the press is broken, you're exposed like a cornerback who bites on a double move. The attacking team needs to play out quickly or risk losing possession in a dangerous area.`;
    } else if (lowerMessage.includes('counter') || lowerMessage.includes('counter-attack')) {
      responseText = `This is a **counter-attack** at ${minutes}:${seconds.toString().padStart(2, '0')}. Think of it like a **pick-six in football** — you intercept the ball (or in this case, win it back) and immediately turn defense into offense. The team that just lost possession is caught out of position, like a quarterback who throws into coverage. Speed and numbers are everything here.`;
    } else if (lowerMessage.includes('summarize') || lowerMessage.includes('last')) {
      responseText = `In the last 30 seconds, we saw a **transition moment**. One team was building an attack, but lost possession. The other team quickly switched to offense — like a **two-minute drill** in football. The key is recognizing the moment and capitalizing before the defense can reset.`;
    } else {
      responseText = `At ${minutes}:${seconds.toString().padStart(2, '0')}, we're seeing a **tactical sequence** unfold. This is like a **play call** in football — the team has a plan, but the defense is reading it. The success depends on execution and timing. Watch how the players move off the ball — that's the "route running" of soccer.`;
    }
  } else if (style === 'Beginner friendly') {
    if (lowerMessage.includes('press') || lowerMessage.includes('pressing')) {
      responseText = `Right now (${minutes}:${seconds.toString().padStart(2, '0')}), the team without the ball is **pressing** — meaning they're actively trying to win it back by getting close to the player with the ball. It's like playing defense in basketball where you're trying to force a turnover. The goal is to make the other team make a mistake or pass the ball backward.`;
    } else if (lowerMessage.includes('counter') || lowerMessage.includes('counter-attack')) {
      responseText = `This is a **counter-attack** at ${minutes}:${seconds.toString().padStart(2, '0')}. When one team loses the ball while attacking, the other team quickly tries to score before the first team can get back into defensive positions. It's like a fast break in basketball — speed and having more players forward than the defense can handle.`;
    } else if (lowerMessage.includes('summarize') || lowerMessage.includes('last')) {
      responseText = `In the last 30 seconds, the team in possession was trying to create a scoring chance. They moved the ball around, looking for an opening. The defending team stayed organized, making it hard to find space. It's a chess match — each team is trying to outsmart the other.`;
    } else {
      responseText = `At ${minutes}:${seconds.toString().padStart(2, '0')}, we're watching how the team with the ball is trying to break down the defense. They're passing, moving, and looking for gaps. The defense is trying to stay compact and prevent any clear chances. It's all about patience and finding the right moment to attack.`;
    }
  } else {
    if (lowerMessage.includes('press') || lowerMessage.includes('pressing')) {
      responseText = `At ${minutes}:${seconds.toString().padStart(2, '0')}, we're seeing a **coordinated press**. The front line triggers the press, with midfielders stepping up to cut passing lanes. The key is the **trigger moment** — when the ball goes to a specific player or area, the press activates. The spacing between pressing players is crucial; too wide and there are gaps, too narrow and the press can be bypassed easily.`;
    } else if (lowerMessage.includes('counter') || lowerMessage.includes('counter-attack')) {
      responseText = `This **counter-attack** at ${minutes}:${seconds.toString().padStart(2, '0')} shows the principles of transition play. The team winning the ball immediately looks for **vertical passes** to players in advanced positions. Notice the **width** — players spread out to stretch the recovering defense. The key is speed of thought and execution before the opposition can reorganize.`;
    } else if (lowerMessage.includes('summarize') || lowerMessage.includes('last')) {
      responseText = `In the last 30 seconds, we observed a **possession phase** where the team in control was probing for weaknesses. The defensive block remained compact, forcing play wide. The attacking team attempted to create **overloads** in wide areas, but the defense maintained good **horizontal compactness**, preventing penetration.`;
    } else {
      responseText = `At ${minutes}:${seconds.toString().padStart(2, '0')}, we're analyzing the **phase of play**. The team in possession is in a **build-up phase**, looking to progress through the thirds. The opposition is maintaining a **mid-block**, not pressing too high but also not sitting too deep. The key battle is in the **half-spaces** — the areas between the center and the wings.`;
    }
  }

  return {
    responseText,
    timestampUsed: currentTime,
    tags: tags.length > 0 ? tags : undefined,
  };
}
