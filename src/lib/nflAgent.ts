/**
 * NFL Analogy and TTS API client
 */

const API_BASE = '/api';

export interface NFLAnalogyInput {
  soccer_commentary: string;
}

export interface NFLAnalogyOutput {
  nfl_analogy: string;
  nfl_commentary: string;
}

/**
 * Generate NFL analogy and broadcast commentary from soccer commentary.
 */
export async function generateNFLAnalogy(soccerCommentary: string): Promise<NFLAnalogyOutput> {
  if (!soccerCommentary || !soccerCommentary.trim()) {
    return { nfl_analogy: '', nfl_commentary: '' };
  }

  try {
    const response = await fetch(`${API_BASE}/nfl-analogy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ soccer_commentary: soccerCommentary }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      nfl_analogy: data.nfl_analogy || '',
      nfl_commentary: data.nfl_commentary || '',
    };
  } catch (error) {
    console.error('Error generating NFL analogy:', error);
    return {
      nfl_analogy: 'The offense methodically moves the chains, using a balanced attack to keep the defense guessing.',
      nfl_commentary: 'Steady progress on the drive as the offense continues to move the chains efficiently.',
    };
  }
}

/**
 * Convert text to speech using ElevenLabs API.
 * Returns an audio Blob that can be played in the browser.
 */
export async function synthesizeSpeech(text: string): Promise<Blob | null> {
  if (!text || !text.trim()) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE}/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`TTS API error: ${response.status} - ${errorText}`);
    }

    const audioBlob = await response.blob();
    return audioBlob;
  } catch (error) {
    console.error('Error synthesizing speech:', error);
    return null;
  }
}

/**
 * Play audio from a Blob in the browser.
 * Returns a promise that resolves when playback is complete.
 */
export function playAudioBlob(audioBlob: Blob): Promise<void> {
  return new Promise((resolve, reject) => {
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      resolve();
    };

    audio.onerror = (event) => {
      URL.revokeObjectURL(audioUrl);
      reject(new Error('Audio playback failed'));
    };

    audio.play().catch((error) => {
      URL.revokeObjectURL(audioUrl);
      reject(error);
    });
  });
}

/**
 * Synthesize and play text as speech.
 * Convenience function that combines synthesizeSpeech and playAudioBlob.
 */
export async function speakWithElevenLabs(text: string): Promise<boolean> {
  const audioBlob = await synthesizeSpeech(text);
  if (!audioBlob) {
    return false;
  }

  try {
    await playAudioBlob(audioBlob);
    return true;
  } catch (error) {
    console.error('Error playing audio:', error);
    return false;
  }
}
