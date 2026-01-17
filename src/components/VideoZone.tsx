import { Play, Pause, Volume2, Maximize, RefreshCw } from 'lucide-react';
import { useState, useEffect, useRef, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { videoSourceManager, VideoSource } from '@/lib/videoSources';

interface VideoZoneProps {
  currentMinute: number;
  videoUrl?: string;
  onVideoUrlChange?: (url: string) => void;
  onCurrentTimeChange?: (time: number) => void;
}

declare global {
  interface Window {
    YT: {
      Player: new (
        elementId: string,
        options: {
          videoId: string;
          events: {
            onReady?: (event: { target: YTPlayer }) => void;
            onStateChange?: (event: { data: number; target: YTPlayer }) => void;
          };
          playerVars?: {
            autoplay?: number;
            controls?: number;
            enablejsapi?: number;
          };
        }
      ) => YTPlayer;
      PlayerState: {
        PLAYING: number;
        PAUSED: number;
        ENDED: number;
      };
    };
    onYouTubeIframeAPIReady: () => void;
  }
}

interface YTPlayer {
  getCurrentTime: () => number;
  getPlayerState: () => number;
  destroy: () => void;
  seekTo: (seconds: number, allowSeekAhead: boolean) => void;
}

const VideoZone = ({ currentMinute, videoUrl = '', onVideoUrlChange, onCurrentTimeChange }: VideoZoneProps) => {
  const [isPlaying, setIsPlaying] = useState(true);
  const [inputValue, setInputValue] = useState(videoUrl);
  const [error, setError] = useState<string | null>(null);
  const [videoSource, setVideoSource] = useState<VideoSource | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [isApiReady, setIsApiReady] = useState(false);

  const playerRef = useRef<YTPlayer | null>(null);
  const playerContainerRef = useRef<HTMLDivElement>(null);
  const timeIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (window.YT) {
      setIsApiReady(true);
      return;
    }

    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

    window.onYouTubeIframeAPIReady = () => {
      setIsApiReady(true);
    };

    return () => {
      window.onYouTubeIframeAPIReady = () => {};
    };
  }, []);

  useEffect(() => {
    if (!isApiReady || !videoSource || videoSource.type !== 'youtube') {
      return;
    }

    if (playerRef.current) {
      playerRef.current.destroy();
      playerRef.current = null;
    }

    playerRef.current = new window.YT.Player('youtube-player', {
      videoId: videoSource.videoId,
      playerVars: {
        autoplay: 0,
        controls: 1,
        enablejsapi: 1,
      },
      events: {
        onReady: (event) => {
          console.log('YouTube player ready');
        },
        onStateChange: (event) => {
          if (event.data === window.YT.PlayerState.PLAYING) {
            setIsPlaying(true);
            if (timeIntervalRef.current) {
              clearInterval(timeIntervalRef.current);
            }
            timeIntervalRef.current = window.setInterval(() => {
              if (playerRef.current) {
                const time = playerRef.current.getCurrentTime();
                setCurrentTime(time);
                onCurrentTimeChange?.(time);
              }
            }, 1000);
          } else {
            setIsPlaying(false);
            if (timeIntervalRef.current) {
              clearInterval(timeIntervalRef.current);
              timeIntervalRef.current = null;
            }
            if (playerRef.current) {
              const time = playerRef.current.getCurrentTime();
              setCurrentTime(time);
              onCurrentTimeChange?.(time);
            }
          }
        },
      },
    });

    return () => {
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
      if (playerRef.current) {
        playerRef.current.destroy();
        playerRef.current = null;
      }
    };
  }, [isApiReady, videoSource, onCurrentTimeChange]);

  useEffect(() => {
    if (videoUrl !== inputValue) {
      setInputValue(videoUrl);
      if (videoUrl) {
        const parsed = videoSourceManager.parseUrl(videoUrl);
        if (parsed) {
          setVideoSource(parsed);
          setError(null);
        } else {
          setVideoSource(null);
          setError('Please enter a valid video URL');
        }
      } else {
        setVideoSource(null);
        setError(null);
      }
    }
  }, [videoUrl]);

  const handleUrlChange = (url: string) => {
    setInputValue(url);
    setError(null);

    if (!url.trim()) {
      setVideoSource(null);
      if (onVideoUrlChange) {
        onVideoUrlChange('');
      }
      return;
    }

    const parsed = videoSourceManager.parseUrl(url);
    if (parsed) {
      setVideoSource(parsed);
      setError(null);
      if (onVideoUrlChange) {
        onVideoUrlChange(url);
      }
    } else {
      setVideoSource(null);
      setError('Please enter a valid video URL');
    }
  };

  const handleInputBlur = () => {
    handleUrlChange(inputValue);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleUrlChange(inputValue);
      e.currentTarget.blur();
    }
  };

  const handleAnalyzeNow = useCallback(() => {
    if (playerRef.current) {
      const time = playerRef.current.getCurrentTime();
      setCurrentTime(time);
      onCurrentTimeChange?.(time);
    }
  }, [onCurrentTimeChange]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getVideoSourceLabel = () => {
    if (!videoSource) return 'Enter video URL';
    switch (videoSource.type) {
      case 'youtube':
        return 'YouTube';
      case 'vimeo':
        return 'Vimeo';
      case 'upload':
        return 'Uploaded Video';
      default:
        return 'Video';
    }
  };

  return (
    <div className="h-full flex flex-col min-h-0">
      <div className="space-y-1 flex-shrink-0 mb-2">
        <div className="flex gap-2">
          <Input
            type="text"
            placeholder="Paste any video URL here..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onBlur={handleInputBlur}
            onKeyDown={handleInputKeyDown}
            className="bg-black/40 border-chalk-white/20 text-chalk-white placeholder:text-chalk-white/40 focus-visible:ring-chalk-green focus-visible:border-chalk-green flex-1"
          />
          {videoSource && (
            <Button
              onClick={handleAnalyzeNow}
              variant="outline"
              size="sm"
              className="bg-chalk-yellow/20 border-chalk-yellow/50 text-chalk-yellow hover:bg-chalk-yellow/30 flex-shrink-0"
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Analyze Now
            </Button>
          )}
        </div>
        {error && (
          <p className="text-red-400 text-xs font-body px-1">{error}</p>
        )}
        {videoSource && !error && (
          <p className="text-chalk-white/60 text-xs font-body px-1">
            {getVideoSourceLabel()} video loaded • Current: {formatTime(currentTime)}
          </p>
        )}
      </div>

      <div className="relative rounded-lg overflow-hidden chalk-border bg-black/40 flex-1 min-h-0">
        <div ref={playerContainerRef} className="w-full h-full bg-gradient-to-br from-chalk-green-light/30 to-black/50 relative">
          {videoSource && videoSource.type === 'youtube' && isApiReady ? (
            <div id="youtube-player" className="w-full h-full" />
          ) : videoSource && videoSource.type === 'unknown' ? (
            <iframe
              src={videoSource.url}
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title="Video player"
            />
          ) : (
            <>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-full h-full bg-gradient-to-br from-emerald-900/50 to-black/70 flex items-center justify-center">
                  <div className="relative w-3/4 h-3/4 border border-chalk-white/20 rounded">
                    <div className="absolute top-1/2 left-0 right-0 h-px bg-chalk-white/20" />
                    <div className="absolute top-1/2 left-1/2 w-16 h-16 -translate-x-1/2 -translate-y-1/2 rounded-full border border-chalk-white/20" />
                    <span className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-chalk-white/30 font-chalk text-2xl text-center px-4">
                      {!isApiReady ? 'Loading player...' : videoSource ? 'Video Source Not Supported' : 'Enter a video URL above'}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="absolute inset-0 flex items-center justify-center group"
              >
                <div className="w-16 h-16 rounded-full bg-chalk-white/20 backdrop-blur-sm flex items-center justify-center transition-transform group-hover:scale-110 border border-chalk-white/30">
                  {isPlaying ? (
                    <Pause className="w-6 h-6 text-chalk-white" />
                  ) : (
                    <Play className="w-6 h-6 text-chalk-white ml-1" />
                  )}
                </div>
              </button>
            </>
          )}

          {(!videoSource || videoSource.type !== 'youtube') && (
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="text-chalk-white hover:text-primary transition-colors"
                >
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                </button>

                <button className="text-chalk-white hover:text-primary transition-colors">
                  <Pause className="w-4 h-4" />
                </button>

                <Volume2 className="w-4 h-4 text-chalk-white/70" />

                <div className="flex-1 h-1 bg-chalk-white/20 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-300"
                    style={{ width: `${(currentMinute / 90) * 100}%` }}
                  />
                </div>

                <span className="text-chalk-white text-sm font-mono">
                  {formatTime(currentMinute * 60)}
                </span>

                <button className="text-chalk-white/70 hover:text-chalk-white transition-colors ml-2">
                  <Maximize className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoZone;
