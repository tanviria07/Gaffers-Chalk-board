export interface MatchEvent {
  id: string;
  minute: number;
  type: 'through-ball' | 'offside-trap' | 'goal' | 'yellow-card' | 'save' | 'corner';
  title: string;
  description: string;
  videoTimestamp: number;
  explanation: {
    whatHappened: string;
    whyItMatters: string;
    nflAnalogy: string;
  };
  diagram: 'through-ball' | 'offside-trap' | 'goal' | 'defensive';
}

export interface Match {
  id: string;
  homeTeam: string;
  awayTeam: string;
  competition: string;
  date: string;
  youtubeId: string;
  events: MatchEvent[];
}

export const mockMatch: Match = {
  id: 'match-001',
  homeTeam: 'Chelsea',
  awayTeam: 'Manchester United',
  competition: 'Premier League',
  date: '2024-01-15',
  youtubeId: 'dQw4w9WgXcQ',
  events: [
    {
      id: 'event-1',
      minute: 12,
      type: 'through-ball',
      title: 'Through Ball',
      description: 'Brilliant pass splits the defense',
      videoTimestamp: 720,
      explanation: {
        whatHappened: "The midfielder slipped a **through ball** between the center-backs. The striker timed his run perfectly and finished near-post.",
        whyItMatters: "This breaks the defensive shape and forces a mistake deep in their defensive third. The defense was caught flat and couldn't recover.",
        nflAnalogy: "That's like a QB threading a **seam pass** between linebackers — the timing window is tiny and closes fast. One split-second late and it's picked off."
      },
      diagram: 'through-ball'
    },
    {
      id: 'event-2',
      minute: 27,
      type: 'offside-trap',
      title: 'Offside Trap',
      description: 'High defensive line catches striker',
      videoTimestamp: 1620,
      explanation: {
        whatHappened: "The defensive line stepped up **in unison** just as the pass was played. The striker was caught a half-step offside.",
        whyItMatters: "A well-executed offside trap is high-risk, high-reward. It nullifies dangerous attacks but requires perfect timing from all four defenders.",
        nflAnalogy: "Think of it like a **zone blitz** where the linebackers drop into coverage at the snap — if everyone reads the play correctly, you create confusion and force a turnover."
      },
      diagram: 'offside-trap'
    },
    {
      id: 'event-3',
      minute: 35,
      type: 'goal',
      title: 'Goal!',
      description: 'Near-post finish',
      videoTimestamp: 2100,
      explanation: {
        whatHappened: "The winger cut inside and drove a low shot at the **near post**. The keeper was beaten at his near side — a goalkeeper's nightmare.",
        whyItMatters: "Near-post goals are often seen as keeper errors. The goalkeeper should have that angle covered. This shifts momentum completely.",
        nflAnalogy: "It's like a running back hitting an **A-gap** hole that the linebacker should have filled. When you beat someone at their strongest point, it's demoralizing."
      },
      diagram: 'goal'
    },
    {
      id: 'event-4',
      minute: 42,
      type: 'yellow-card',
      title: 'Yellow Card',
      description: 'Tactical foul to stop counter-attack',
      videoTimestamp: 2520,
      explanation: {
        whatHappened: "The midfielder made a **cynical foul** to stop a dangerous counter-attack. He accepted the yellow card to prevent a 3-on-2 break.",
        whyItMatters: "This is a 'professional foul' — trading a booking for preventing a high-quality scoring chance. The math usually works out.",
        nflAnalogy: "Exactly like an **intentional holding** penalty when a defender is beat. You take the 10 yards instead of giving up the touchdown."
      },
      diagram: 'defensive'
    }
  ]
};

export const recentExplanations = [
  { id: 1, title: "False 9 Movement", time: "2 min ago" },
  { id: 2, title: "Gegenpressing Trigger", time: "5 min ago" },
  { id: 3, title: "Inverted Fullback", time: "8 min ago" },
];
