export type VideoSourceType = 'youtube' | 'vimeo' | 'upload' | 'unknown';

export interface VideoSource {
  type: VideoSourceType;
  videoId: string;
  url: string;
}

export interface VideoSourceProvider {
  canHandle(url: string): boolean;
  extractVideoId(url: string): string | null;
  getType(): VideoSourceType;
  validate(url: string): boolean;
}

class YouTubeProvider implements VideoSourceProvider {
  getType(): VideoSourceType {
    return 'youtube';
  }

  canHandle(url: string): boolean {
    return this.validate(url);
  }

  validate(url: string): boolean {
    if (!url || typeof url !== 'string') {
      return false;
    }

    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)/;
    return youtubeRegex.test(url);
  }

  extractVideoId(url: string): string | null {
    if (!this.validate(url)) {
      return null;
    }

    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)/,
      /youtube\.com\/watch\?.*&v=([^&\n?#]+)/,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }

    return null;
  }
}

class GenericVideoProvider implements VideoSourceProvider {
  getType(): VideoSourceType {
    return 'unknown';
  }

  canHandle(url: string): boolean {
    return this.validate(url);
  }

  validate(url: string): boolean {
    if (!url || typeof url !== 'string') {
      return false;
    }

    try {
      const urlObj = new URL(url.trim());
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  }

  extractVideoId(url: string): string | null {
    if (this.validate(url)) {
      return url.trim();
    }
    return null;
  }
}

class VideoSourceManager {
  private providers: VideoSourceProvider[] = [];

  constructor() {
    this.registerProvider(new YouTubeProvider());
    this.registerProvider(new GenericVideoProvider());
  }

  registerProvider(provider: VideoSourceProvider): void {
    this.providers.push(provider);
  }

  parseUrl(url: string): VideoSource | null {
    if (!url || !url.trim()) {
      return null;
    }

    const trimmedUrl = url.trim();

    for (const provider of this.providers) {
      if (provider.canHandle(trimmedUrl)) {
        const videoId = provider.extractVideoId(trimmedUrl);
        if (videoId) {
          return {
            type: provider.getType(),
            videoId,
            url: trimmedUrl,
          };
        }
      }
    }

    return null;
  }

  isValidUrl(url: string): boolean {
    return this.parseUrl(url) !== null;
  }
}

export const videoSourceManager = new VideoSourceManager();

export { YouTubeProvider, GenericVideoProvider };
