import { ChevronRight, CircleDot, Info, Zap, Trophy } from 'lucide-react';
import { MatchEvent } from '@/data/matchData';
import { motion, AnimatePresence } from 'framer-motion';

interface ExplanationPanelProps {
  event: MatchEvent | null;
}

const ExplanationPanel = ({ event }: ExplanationPanelProps) => {
  if (!event) {
    return (
      <div className="h-full flex items-center justify-center py-12">
        <motion.div 
          className="text-center space-y-4"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="w-16 h-16 rounded-full bg-chalk-white/5 border border-chalk-white/20 flex items-center justify-center mx-auto">
            <CircleDot className="w-8 h-8 text-chalk-white/30" />
          </div>
          <div>
            <p className="text-chalk-white/70 font-body text-lg">
              Select an event from the timeline
            </p>
            <p className="text-chalk-white/40 font-body text-sm mt-1">
              Click any moment to see what happened
            </p>
          </div>
          <motion.div 
            className="flex items-center justify-center gap-2 text-chalk-yellow/60"
            animate={{ x: [0, 5, 0] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          >
            <span className="text-sm font-body">← Look at the timeline</span>
          </motion.div>
        </motion.div>
      </div>
    );
  }

  const renderMarkdown = (text: string) => {
    return text.split('**').map((part, index) => 
      index % 2 === 1 ? (
        <strong key={index} className="text-chalk-yellow font-semibold">{part}</strong>
      ) : (
        <span key={index}>{part}</span>
      )
    );
  };

  const sectionVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.1, duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] as const }
    })
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div 
        key={event.id}
        className="space-y-5"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
      >
        <motion.section
          custom={0}
          variants={sectionVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center">
              <ChevronRight className="w-5 h-5 text-chalk-yellow" />
              <ChevronRight className="w-5 h-5 text-chalk-yellow -ml-3" />
            </div>
            <h3 className="font-chalk text-2xl text-chalk">What Just Happened</h3>
            <Info className="w-4 h-4 text-chalk-white/40 ml-auto" />
          </div>
          <p className="text-chalk-white/90 font-body text-sm leading-relaxed pl-6">
            {renderMarkdown(event.explanation.whatHappened)}
          </p>
        </motion.section>

        <motion.section
          custom={1}
          variants={sectionVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center">
              <ChevronRight className="w-5 h-5 text-chalk-yellow" />
              <ChevronRight className="w-5 h-5 text-chalk-yellow -ml-3" />
            </div>
            <h3 className="font-chalk text-2xl text-chalk">Why It Matters</h3>
            <Zap className="w-4 h-4 text-chalk-white/40 ml-auto" />
          </div>
          <p className="text-chalk-white/90 font-body text-sm leading-relaxed pl-6">
            {renderMarkdown(event.explanation.whyItMatters)}
          </p>
        </motion.section>

        <motion.section 
          className="relative"
          custom={2}
          variants={sectionVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="absolute -inset-3 bg-gradient-to-r from-chalk-yellow/10 to-chalk-yellow/5 rounded-lg border border-chalk-yellow/30" />
          <div className="relative">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-full bg-chalk-yellow/20 border border-chalk-yellow/50 flex items-center justify-center">
                <span className="text-base">🏈</span>
              </div>
              <h3 className="font-chalk text-2xl text-chalk-yellow">NFL Analogy</h3>
              <Trophy className="w-4 h-4 text-chalk-yellow/60 ml-auto" />
            </div>
            <p className="text-chalk-white font-body text-sm leading-relaxed pl-9 italic">
              {renderMarkdown(event.explanation.nflAnalogy)}
            </p>
          </div>
        </motion.section>
      </motion.div>
    </AnimatePresence>
  );
};

export default ExplanationPanel;
