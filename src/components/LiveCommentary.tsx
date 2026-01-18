import { useEffect, useState, useRef } from 'react';
import { getLiveCommentary } from '@/lib/commentaryAgent';

interface LiveCommentaryProps {
  videoId: string | null;
  currentTime: number;
  isPlaying: boolean;
  updateInterval?: number;
}

interface CommentaryItem {
  text: string;
  timestamp: number;
  rawAction?: string | null;
}

const LiveCommentary = ({
  videoId,
  currentTime,
  isPlaying,
  updateInterval = 5.0, // <- slower by default (Gemini needs time)
}: LiveCommentaryProps) => {
  const [currentCommentary, setCurrentCommentary] = useState<CommentaryItem | null>(null);
  const [history, setHistory] = useState<CommentaryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const lastUpdateTime = useRef<number>(0);
  const updateTimerRef = useRef<number | null>(null);

  // ✅ REAL lock (state is not a reliable lock)
  const inFlightRef = useRef(false);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const fetchCommentary = async (timestamp: number) => {
    if (!videoId) return;
    if (inFlightRef.current) return;

    inFlightRef.current = true;
    setIsLoading(true);

    try {
      const res = await getLiveCommentary({
        videoId,
        timestamp,
        windowSize: 5.0,
      });

      // ✅ Only update if backend actually produced a result
      if (res?.commentary && !res.skipped) {
        const newCommentary: CommentaryItem = {
          text: res.commentary,
          timestamp,
          rawAction: res.rawAction,
        };

        setCurrentCommentary(newCommentary);
        setHistory(prev => [newCommentary, ...prev].slice(0, 10));
      }

      // ✅ If skipped/empty: keep old commentary on screen (don’t wipe)
    } catch (error) {
      console.error('Error fetching live commentary:', error);
    } finally {
      setIsLoading(false);
      inFlightRef.current = false;
    }
  };

  useEffect(() => {
    // Stop polling if no video or not playing
    if (!videoId || !isPlaying) {
      if (updateTimerRef.current) {
        clearInterval(updateTimerRef.current);
        updateTimerRef.current = null;
      }
      return;
    }

    const shouldUpdate = () => {
      const now = Date.now();
      const timeSinceLastUpdate = (now - lastUpdateTime.current) / 1000;

      // ✅ Don’t schedule a new run while one is running
      if (inFlightRef.current) return;

      if (timeSinceLastUpdate >= updateInterval) {
        lastUpdateTime.current = now;
        fetchCommentary(currentTime);
      }
    };

    // Fire once immediately, then poll
    shouldUpdate();

    updateTimerRef.current = window.setInterval(() => {
      shouldUpdate();
    }, updateInterval * 1000);

    return () => {
      if (updateTimerRef.current) {
        clearInterval(updateTimerRef.current);
        updateTimerRef.current = null;
      }
    };
  }, [videoId, isPlaying, currentTime, updateInterval]);

  useEffect(() => {
    // Reset when video changes
    setCurrentCommentary(null);
    setHistory([]);
    lastUpdateTime.current = 0;
    inFlightRef.current = false;
    setIsLoading(false);
  }, [videoId]);

  if (!videoId) return null;

  return (
    <div className="bg-card/50 rounded-lg p-3 chalk-border">
      <div className="flex items-center gap-2 mb-2">
        <span className="w-2 h-2 rounded-full bg-chalk-green animate-pulse" />
        <h3 className="font-chalk text-base text-chalk-yellow">Live Commentary</h3>
        {isLoading && <span className="text-xs text-chalk-white/50">Generating...</span>}
      </div>

      {currentCommentary ? (
        <div className="space-y-2">
          <p className="text-chalk-white/90 font-body text-sm leading-relaxed">
            {currentCommentary.text}
          </p>
          <div className="flex items-center justify-between text-xs text-chalk-white/50">
            <span>{formatTime(currentCommentary.timestamp)}</span>
            {currentCommentary.rawAction && (
              <span className="italic">Raw: {currentCommentary.rawAction.substring(0, 40)}...</span>
            )}
          </div>
        </div>
      ) : (
        <p className="text-chalk-white/50 font-body text-sm italic">
          Commentary will appear here as the video plays...
        </p>
      )}

      {history.length > 1 && (
        <details className="mt-3">
          <summary className="text-xs text-chalk-white/40 cursor-pointer hover:text-chalk-white/60">
            Recent commentary ({history.length - 1})
          </summary>
          <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
            {history.slice(1).map((item, idx) => (
              <div
                key={idx}
                className="text-xs text-chalk-white/60 border-l-2 border-chalk-white/20 pl-2"
              >
                <span className="text-chalk-white/40">{formatTime(item.timestamp)}:</span>{' '}
                <span>{item.text.substring(0, 60)}...</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
};

export default LiveCommentary;
