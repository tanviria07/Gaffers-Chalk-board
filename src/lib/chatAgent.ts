export interface ChatInput {
  videoId: string;
  timestamp: number;
  userMessage: string;
  context?: {
    commentary?: string;
    nflAnalogy?: string;
  };
  videoMetadata?: {
    title?: string;
    description?: string;
    uploader?: string;
  };
}

export interface ChatOutput {
  response: string;
  timestamp: number;
}

const API_BASE = '/api';

export async function fetchVideoMetadata(videoId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE}/video-metadata/${encodeURIComponent(videoId)}`);
    if (!response.ok) {
      console.warn('Could not fetch video metadata');
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching video metadata:', error);
    return null;
  }
}

export async function sendChatMessage(input: ChatInput): Promise<ChatOutput> {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        videoId: input.videoId,
        timestamp: input.timestamp,
        userMessage: input.userMessage,
        context: input.context,
        videoMetadata: input.videoMetadata,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    
    return {
      response: data.response || 'Unable to generate response.',
      timestamp: data.timestamp || input.timestamp,
    };
  } catch (error) {
    console.error('Error sending chat message:', error);
    const minutes = Math.floor(input.timestamp / 60);
    const seconds = Math.floor(input.timestamp % 60);
    return {
      response: `At ${minutes}:${seconds.toString().padStart(2, '0')}, I'm having trouble connecting to the chat service. Please try again.`,
      timestamp: input.timestamp,
    };
  }
}
