export interface LiveCommentaryInput {
  videoId: string;
  timestamp: number;
  windowSize?: number;
}

export interface LiveCommentaryResponse {
  commentary: string | null;
  rawAction: string | null;
  timestamp: number;
  skipped: boolean;
  error?: string;
}

const API_BASE = '/api';

export async function getLiveCommentary(
  input: LiveCommentaryInput
): Promise<LiveCommentaryResponse> {
  try {
    const response = await fetch(`${API_BASE}/live-commentary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        videoId: input.videoId,
        timestamp: input.timestamp,
        windowSize: input.windowSize || 5.0,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    
    return {
      commentary: data.commentary || null,
      rawAction: data.rawAction || null,
      timestamp: data.timestamp || input.timestamp,
      skipped: data.skipped || false,
      error: data.error || undefined,
    };
  } catch (error) {
    console.error('Error generating live commentary:', error);
    return {
      commentary: null,
      rawAction: null,
      timestamp: input.timestamp,
      skipped: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}
