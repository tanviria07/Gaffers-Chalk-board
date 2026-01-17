import { ChevronRight, Swords, MousePointerClick } from 'lucide-react';
import { MatchEvent } from '@/data/matchData';
import { cn } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface EventTimelineProps {
  events: MatchEvent[];
  selectedEventId: string | null;
  onSelectEvent: (event: MatchEvent) => void;
}

const EventTimeline = ({ events, selectedEventId, onSelectEvent }: EventTimelineProps) => {
  const getEventIcon = (type: MatchEvent['type']) => {
    switch (type) {
      case 'goal':
        return '⚽';
      case 'yellow-card':
        return '🟨';
      case 'through-ball':
        return '➡️';
      case 'offside-trap':
        return '🚩';
      default:
        return '•';
    }
  };

  const getEventDescription = (type: MatchEvent['type']) => {
    switch (type) {
      case 'goal':
        return 'A goal was scored!';
      case 'yellow-card':
        return 'Player received a warning';
      case 'through-ball':
        return 'A pass splitting the defense';
      case 'offside-trap':
        return 'Defensive tactical move';
      default:
        return 'Match event';
    }
  };

  return (
    <div className="h-full flex flex-col min-h-0">
      <div className="flex items-center justify-between flex-shrink-0 mb-2">
        <div className="flex items-center gap-2">
          <Swords className="w-5 h-5 text-chalk-yellow" />
          <h2 className="font-chalk text-2xl text-chalk">Event Timeline</h2>
        </div>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-chalk-white/5 border border-chalk-white/10 cursor-help">
              <MousePointerClick className="w-3.5 h-3.5 text-chalk-yellow/70" />
              <span className="text-[10px] text-chalk-white/50 font-body">Click to explore</span>
            </div>
          </TooltipTrigger>
          <TooltipContent side="top" className="bg-card border-chalk-white/20">
            <p className="text-xs">Click any event to see the explanation and NFL analogy</p>
          </TooltipContent>
        </Tooltip>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto space-y-1">
        {events.map((event, index) => {
          const isSelected = selectedEventId === event.id;
          
          return (
            <Tooltip key={event.id}>
              <TooltipTrigger asChild>
                <button
                  onClick={() => onSelectEvent(event)}
                  className={cn(
                    "w-full text-left px-3 py-3 rounded-lg transition-all duration-200",
                    "hover:bg-chalk-white/10 group flex items-center justify-between",
                    "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-chalkboard",
                    "active:scale-[0.98]",
                    isSelected && "event-highlight bg-chalk-yellow/10",
                    !isSelected && "animate-fade-in"
                  )}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{getEventIcon(event.type)}</span>
                    
                    <span className={cn(
                      "font-chalk text-xl min-w-[40px]",
                      isSelected ? "text-chalk-yellow" : "text-chalk-white/80"
                    )}>
                      {event.minute}'
                    </span>
                    
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        "font-body text-sm",
                        isSelected ? "text-chalk-yellow font-semibold" : "text-chalk-white/90"
                      )}>
                        {event.title}
                      </span>
                      {event.type === 'goal' && (
                        <span className="text-chalk-white/60 text-xs font-body">
                          ({event.description})
                        </span>
                      )}
                    </div>
                  </div>

                  <ChevronRight className={cn(
                    "w-5 h-5 transition-all duration-200",
                    isSelected 
                      ? "text-chalk-yellow translate-x-0" 
                      : "text-chalk-white/40 -translate-x-1 group-hover:translate-x-0 group-hover:text-chalk-white/70"
                  )} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right" className="bg-card border-chalk-white/20">
                <p className="text-xs">{getEventDescription(event.type)}</p>
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>

    </div>
  );
};

export default EventTimeline;
