import { Tv, HelpCircle } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const Header = () => {
  return (
    <header className="bg-wood-frame py-3 px-4 md:px-6 border-b-4 border-chalk-wood">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 md:gap-4">
          <div className="w-12 h-12 md:w-14 md:h-14 rounded-full border-2 border-chalk-white/60 flex items-center justify-center bg-chalk-green-light/50 shrink-0">
            <svg viewBox="0 0 40 40" className="w-8 h-8 md:w-10 md:h-10">
              <rect x="5" y="8" width="30" height="24" rx="2" fill="none" stroke="hsl(45 30% 90%)" strokeWidth="1.5" />
              <line x1="10" y1="15" x2="20" y2="15" stroke="hsl(45 75% 60%)" strokeWidth="1.5" />
              <line x1="22" y1="15" x2="30" y2="20" stroke="hsl(45 75% 60%)" strokeWidth="1.5" strokeDasharray="2 2" />
              <circle cx="12" cy="20" r="2" fill="none" stroke="hsl(45 30% 90%)" strokeWidth="1" />
              <circle cx="28" cy="22" r="2" fill="hsl(45 30% 90%)" />
              <text x="17" y="27" fontSize="6" fill="hsl(45 30% 90%)" fontFamily="sans-serif">X</text>
              <text x="23" y="27" fontSize="6" fill="hsl(45 30% 90%)" fontFamily="sans-serif">O</text>
            </svg>
          </div>
          
          <div className="min-w-0">
            <h1 className="font-chalk text-2xl md:text-4xl text-chalk tracking-wide truncate">
              Gaffer's Chalkboard
            </h1>
            <p className="text-chalk-white/70 text-xs md:text-sm font-body truncate">
              Soccer Explained with NFL-Style Analogies
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-3 shrink-0">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-chalk-green-light/50 border border-chalk-white/20">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse-glow" />
            <span className="text-xs text-chalk-white/80 font-body">Live Explanation</span>
            <span className="text-xs text-chalk-yellow">• AI-Powered</span>
          </div>
          
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="w-9 h-9 rounded-full bg-chalk-white/5 border border-chalk-white/20 flex items-center justify-center hover:bg-chalk-white/10 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50">
                <HelpCircle className="w-4 h-4 text-chalk-white/60" />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="bg-card border-chalk-white/20 max-w-xs">
              <p className="text-xs leading-relaxed">
                <strong className="text-chalk-yellow">How to use:</strong> Click events in the timeline to see explanations with NFL analogies. Perfect for watching soccer while learning the game!
              </p>
            </TooltipContent>
          </Tooltip>
          
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="w-9 h-9 rounded-full bg-chalk-white/5 border border-chalk-white/20 flex items-center justify-center hover:bg-chalk-white/10 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50">
                <Tv className="w-4 h-4 text-chalk-white/60" />
              </button>
            </TooltipTrigger>
            <TooltipContent className="bg-card border-chalk-white/20">
              <p className="text-xs">Full screen mode</p>
            </TooltipContent>
          </Tooltip>
        </div>
      </div>
    </header>
  );
};

export default Header;
