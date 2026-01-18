import { useState, useEffect, useCallback, useRef } from 'react';
import Header from '@/components/Header';
import VideoZone from '@/components/VideoZone';
import TacticsDiagram from '@/components/TacticsDiagram';
import AudioButton from '@/components/AudioButton';
import ChatBot from '@/components/ChatBot';
import LiveCommentary from '@/components/LiveCommentary';
import { videoSourceManager } from '@/lib/videoSources';
import { fetchVideoMetadata } from '@/lib/chatAgent';
import { generateAnalogy, generateAnalogyFromText, AnalogyOutput, fetchCaptions, speakText, stopSpeaking } from '@/lib/analogyAgent';
import { getLiveCommentary } from '@/lib/commentaryAgent';
import { generateNFLAnalogy, speakWithElevenLabs } from '@/lib/nflAgent';
import { MatchEvent } from '@/data/matchData';

interface AnalysisState {
  commentary: string;
  nflAnalogy: string;
  nflCommentary: string;
  fieldDiagram: MatchEvent['diagram'];
  isLoading: boolean;
  timestamp: number;
}

const Index = () => {
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [videoId, setVideoId] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [isVideoPlaying, setIsVideoPlaying] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [videoMetadata, setVideoMetadata] = useState<any>(null);
  const lastFetchedTime = useRef<number>(-1);
  const [analysis, setAnalysis] = useState<AnalysisState>({
    commentary: "Paste a video URL to see real-time soccer analysis with NFL analogies.",
    nflAnalogy: "NFL analogies will appear here as you watch the video.",
    nflCommentary: "",
    fieldDiagram: 'defensive',
    isLoading: false,
    timestamp: 0,
  });
  const [isPlayingVoice, setIsPlayingVoice] = useState(false);

  useEffect(() => {
    if (videoUrl) {
      const parsed = videoSourceManager.parseUrl(videoUrl);
      if (parsed) {
        if (parsed.type === 'youtube') {
          setVideoId(parsed.videoId);
        } else {
          setVideoId(parsed.url);
        }
      } else {
        setVideoId(null);
      }
    } else {
      setVideoId(null);
    }
  }, [videoUrl]);

  useEffect(() => {
    if (videoId) {
      fetchVideoMetadata(videoId).then(metadata => {
        if (metadata) {
          setVideoMetadata(metadata);
          console.log('Video metadata loaded:', metadata.title);
        }
      });
      
    } else {
      setVideoMetadata(null);
    }
  }, [videoId]);

  const updateLiveAnalysis = useCallback(async (timestamp: number) => {
    if (!videoId) return;

    setAnalysis(prev => ({ ...prev, timestamp }));

    const roundedTime = Math.floor(timestamp / 5) * 5;
    if (Math.abs(roundedTime - lastFetchedTime.current) < 5) {
      return;
    }
    
    lastFetchedTime.current = roundedTime;
    setAnalysis(prev => ({ ...prev, isLoading: true }));
    
    try {
      console.log(`[What's Happening] Fetching for videoId=${videoId}, timestamp=${timestamp.toFixed(1)}s`);
      const liveCommentaryResult = await getLiveCommentary({
        videoId,
        timestamp,
        windowSize: 5.0,
      });
      
      console.log(`[What's Happening] Result: commentary=${liveCommentaryResult.commentary?.substring(0, 50)}..., skipped=${liveCommentaryResult.skipped}`);
      
      if (liveCommentaryResult.commentary && !liveCommentaryResult.skipped) {
        const visionCommentary = liveCommentaryResult.commentary;

        setAnalysis(prev => ({
          ...prev,
          commentary: visionCommentary,
        }));

        try {
          const nflResult = await generateNFLAnalogy(visionCommentary);
          setAnalysis(prev => ({
            ...prev,
            nflAnalogy: nflResult.nfl_analogy,
            nflCommentary: nflResult.nfl_commentary,
            isLoading: false,
          }));
        } catch (error) {
          console.error('Error generating NFL analogy from vision commentary:', error);
          setAnalysis(prev => ({ ...prev, isLoading: false }));
        }
      } else {
        const result: AnalogyOutput = await generateAnalogy({
          videoId,
          timestamp,
        });
        
        setAnalysis(prev => ({
          ...prev,
          commentary: result.originalCommentary,
          nflAnalogy: result.nflAnalogy,
          fieldDiagram: result.fieldDiagram,
          isLoading: false,
          timestamp: result.timestamp,
        }));
      }
    } catch (error) {
      console.error('Error fetching live commentary or analogy:', error);
      setAnalysis(prev => ({ ...prev, isLoading: false }));
    }
  }, [videoId]);

  const handleTimeChange = useCallback((time: number) => {
    setCurrentTime(time);
    updateLiveAnalysis(time);
  }, [updateLiveAnalysis]);

  useEffect(() => {
    const checkPlaying = () => {
      const wasPlaying = isVideoPlaying;
      setIsVideoPlaying(videoId !== null && currentTime > 0);
    };
    checkPlaying();
  }, [currentTime, videoId]);

  const handleAudioClick = async () => {
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
      return;
    }

    setIsSpeaking(true);
    try {
      const fullText = `${analysis.commentary}. And here's the NFL comparison: ${analysis.nflAnalogy}`;
      await speakText(fullText, { rate: 0.95, pitch: 1.0 });
    } catch (error) {
      console.error('Speech error:', error);
    } finally {
      setIsSpeaking(false);
    }
  };

  const handlePlayVoice = async () => {
    if (isPlayingVoice || !analysis.nflCommentary) {
      return;
    }

    setIsPlayingVoice(true);
    try {
      const success = await speakWithElevenLabs(analysis.nflCommentary);
      if (!success) {
        console.warn('ElevenLabs TTS failed, falling back to browser TTS');
        await speakText(analysis.nflCommentary, { rate: 1.0, pitch: 1.0 });
      }
    } catch (error) {
      console.error('Voice playback error:', error);
    } finally {
      setIsPlayingVoice(false);
    }
  };

  const renderMarkdown = (text: string) => {
    return text.split('**').map((part, index) =>
      index % 2 === 1 ? (
        <strong key={index} className="text-chalk-yellow font-semibold">{part}</strong>
      ) : (
        <span key={index}>{part}</span>
      )
    );
  };

  const formatTime = (seconds: number) => {
    return `${Math.floor(seconds)}s`;
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-chalkboard chalk-texture">
      <Header />

      <main className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-10 gap-4 p-4 lg:p-6">
        <div className="lg:col-span-7 flex flex-col min-h-0">
          <VideoZone
            currentMinute={Math.floor(currentTime / 60)}
            videoUrl={videoUrl}
            onVideoUrlChange={setVideoUrl}
            onCurrentTimeChange={handleTimeChange}
          />
        </div>

        <div className="lg:col-span-3 flex flex-col min-h-0 gap-3">
          {videoId && (
            <div className="text-xs text-chalk-white/50 font-body flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-chalk-green animate-pulse" />
              Live analysis at {formatTime(analysis.timestamp)}
              {analysis.isLoading && <span className="ml-2 text-chalk-yellow">Loading...</span>}
            </div>
          )}

          <LiveCommentary
            videoId={videoId}
            currentTime={currentTime}
            isPlaying={isVideoPlaying}
            updateInterval={2.0}
          />

          <div className="bg-card/50 rounded-lg p-3 chalk-border">
            <h3 className="font-chalk text-base text-chalk-yellow mb-1">What's Happening</h3>
            <p className={`text-chalk-white/90 font-body text-sm leading-snug ${analysis.isLoading ? 'opacity-50' : ''}`}>
              {renderMarkdown(analysis.commentary)}
            </p>
          </div>

          <div className="bg-gradient-to-r from-chalk-yellow/10 to-chalk-yellow/5 rounded-lg p-3 border border-chalk-yellow/30">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-base">🏈</span>
              <h3 className="font-chalk text-base text-chalk-yellow">NFL Analogy</h3>
            </div>
            <p className={`text-chalk-white font-body text-sm leading-snug italic ${analysis.isLoading ? 'opacity-50' : ''}`}>
              {renderMarkdown(analysis.nflAnalogy)}
            </p>
          </div>

          {analysis.nflCommentary && (
            <div className="bg-gradient-to-r from-orange-500/10 to-orange-500/5 rounded-lg p-3 border border-orange-500/30">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-base">📢</span>
                  <h3 className="font-chalk text-base text-orange-400">NFL Commentary</h3>
                </div>
                <button
                  onClick={handlePlayVoice}
                  disabled={isPlayingVoice || !analysis.nflCommentary}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-body transition-colors ${
                    isPlayingVoice
                      ? 'bg-orange-500/30 text-orange-300 cursor-wait'
                      : 'bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 hover:text-orange-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {isPlayingVoice ? (
                    <>
                      <span className="w-3 h-3 border-2 border-orange-400 border-t-transparent rounded-full animate-spin" />
                      Playing...
                    </>
                  ) : (
                    <>
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                      </svg>
                      Play Voice
                    </>
                  )}
                </button>
              </div>
              <p className={`text-chalk-white font-body text-sm leading-snug font-medium ${analysis.isLoading ? 'opacity-50' : ''}`}>
                {renderMarkdown(analysis.nflCommentary)}
              </p>
            </div>
          )}

          <div className="flex-shrink-0">
            <TacticsDiagram diagramType={analysis.fieldDiagram} />
          </div>

          <div className="flex-shrink-0 mt-auto">
            <AudioButton onClick={handleAudioClick} isSpeaking={isSpeaking} />
          </div>

          <div className="flex-shrink-0">
            <ChatBot 
              videoId={videoId} 
              currentTime={currentTime}
              context={{
                commentary: analysis.commentary,
                nflAnalogy: analysis.nflAnalogy,
              }}
              videoMetadata={videoMetadata}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
