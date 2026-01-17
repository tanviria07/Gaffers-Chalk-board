import { VideoSource } from './videoSources';

export interface VideoContext {
  currentTime: number;
  videoUrl: string;
  provider: VideoSource['type'];
  videoId: string;
}

export async function getYouTubeCurrentTime(iframe: HTMLIFrameElement | null): Promise<number> {
  if (!iframe || !iframe.contentWindow) {
    return 0;
  }

  try {
    return new Promise((resolve) => {
      resolve(0);
    });
  } catch (error) {
    console.warn('Failed to get YouTube current time:', error);
    return 0;
  }
}

export function createVideoContext(
  videoUrl: string,
  videoSource: VideoSource | null,
  currentTime: number
): VideoContext | null {
  if (!videoSource || !videoUrl) {
    return null;
  }

  return {
    currentTime,
    videoUrl,
    provider: videoSource.type,
    videoId: videoSource.videoId,
  };
}
