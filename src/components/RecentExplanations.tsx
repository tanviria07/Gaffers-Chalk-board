import { Clock, ChevronDown } from 'lucide-react';
import { forwardRef, useState } from 'react';
import { recentExplanations } from '@/data/matchData';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const RecentExplanations = forwardRef<HTMLDivElement>((props, ref) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div ref={ref} className="relative" {...props}>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="w-full chalk-border rounded-lg px-4 py-3 bg-chalk-green-light/30 hover:bg-chalk-green-light/50 transition-all duration-200 flex items-center justify-between group focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-chalk-yellow/70" />
              <span className="font-body text-sm text-chalk-white/80">Recent Explanations</span>
              <span className="text-xs text-chalk-white/40 font-body">({recentExplanations.length})</span>
            </div>
            <ChevronDown className={cn(
              "w-5 h-5 text-chalk-white/60 transition-transform duration-200",
              isOpen && "rotate-180"
            )} />
          </button>
        </TooltipTrigger>
        <TooltipContent className="bg-card border-chalk-white/20">
          <p className="text-xs">View your recently viewed explanations</p>
        </TooltipContent>
      </Tooltip>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            className="absolute bottom-full left-0 right-0 mb-2 bg-card rounded-lg chalk-border overflow-hidden shadow-card-chalk"
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <div className="p-3 space-y-1">
              {recentExplanations.map((item, index) => (
                <motion.button
                  key={item.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-chalk-white/10 transition-all flex items-center justify-between group focus:outline-none focus:ring-2 focus:ring-primary/30"
                >
                  <span className="text-chalk-white/90 text-sm font-body group-hover:text-chalk-yellow transition-colors">{item.title}</span>
                  <span className="text-chalk-white/40 text-xs font-body">{item.time}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

RecentExplanations.displayName = 'RecentExplanations';

export default RecentExplanations;
