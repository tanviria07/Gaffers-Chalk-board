export interface AnalogyInput {
  videoId: string;
  timestamp: number;
}

export interface AnalogyOutput {
  originalCommentary: string;
  nflAnalogy: string;
  fieldDiagram: 'through-ball' | 'offside-trap' | 'goal' | 'defensive' | any;
  timestamp: number;
  videoId: string;
  cached: boolean;
}

const API_BASE = '/api';

export async function generateAnalogyFromText(commentary: string): Promise<string> {
  try {
    const response = await fetch(`${API_BASE}/generate-analogy-from-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ commentary }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data.nflAnalogy || "This is like a well-designed offensive scheme — every player has a role, creating space and options.";
  } catch (error) {
    console.error('Error generating analogy from text:', error);
    return "This is like a well-designed offensive scheme — every player has a role, creating space and options.";
  }
}

export async function generateAnalogy(input: AnalogyInput): Promise<AnalogyOutput> {
  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        videoId: input.videoId,
        timestamp: input.timestamp,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    
    return {
      originalCommentary: data.originalCommentary || `Soccer action at ${formatTime(input.timestamp)}`,
      nflAnalogy: data.nflAnalogy || "This play is like a well-designed offensive scheme — every player has a role, creating space and options.",
      fieldDiagram: data.fieldDiagram?.diagramType || 'defensive',
      timestamp: data.timestamp || input.timestamp,
      videoId: input.videoId,
      cached: data.cached || false,
    };
  } catch (error) {
    console.error('Error generating analogy:', error);
    return {
      originalCommentary: `Soccer action at ${formatTime(input.timestamp)}`,
      nflAnalogy: "This play is like a well-designed offensive scheme — every player has a role, creating space and options.",
      fieldDiagram: 'defensive',
      timestamp: input.timestamp,
      videoId: input.videoId,
      cached: false,
    };
  }
}

export async function fetchCaptions(videoId: string): Promise<{ text: string; start: number; dur: number }[]> {
  try {
    const response = await fetch(`${API_BASE}/captions/${videoId}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    const data = await response.json();
    const captions = (data.captions || []).map((cap: any) => ({
      text: cap.text || '',
      start: cap.start || 0,
      dur: cap.duration || cap.dur || 0,
    }));
    return captions;
  } catch (error) {
    console.error('Error fetching captions:', error);
    return [];
  }
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function speakText(text: string, options?: { rate?: number; pitch?: number }): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!('speechSynthesis' in window)) {
      reject(new Error('Text-to-speech not supported'));
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options?.rate || 1.0;
    utterance.pitch = options?.pitch || 1.0;
    utterance.lang = 'en-US';

    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(
      v => v.lang === 'en-US' && (v.name.includes('Male') || v.name.includes('David') || v.name.includes('Alex'))
    ) || voices.find(v => v.lang === 'en-US') || voices[0];

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onend = () => resolve();
    utterance.onerror = (event) => reject(new Error(event.error));

    window.speechSynthesis.speak(utterance);
  });
}

export function stopSpeaking(): void {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}
