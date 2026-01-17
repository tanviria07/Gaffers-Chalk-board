import { MatchEvent } from '@/data/matchData';

interface TacticsDiagramProps {
  diagramType: MatchEvent['diagram'] | null;
}

const TacticsDiagram = ({ diagramType }: TacticsDiagramProps) => {
  const renderDiagram = () => {
    switch (diagramType) {
      case 'through-ball':
        return (
          <>
            <text x="60" y="50" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="100" y="45" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="140" y="50" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="180" y="45" className="fill-chalk-white font-bold text-lg">X</text>
            
            <text x="80" y="80" className="fill-chalk-white font-bold text-lg">O</text>
            <text x="160" y="75" className="fill-chalk-white font-bold text-lg">O</text>
            
            <circle cx="120" cy="90" r="4" className="fill-chalk-yellow" />
            
            <path 
              d="M 120 90 Q 145 60 175 40" 
              fill="none" 
              stroke="hsl(45 75% 60%)" 
              strokeWidth="2"
              strokeDasharray="6 3"
              className="animate-chalk-draw"
            />
            <polygon 
              points="175,35 180,45 170,43" 
              className="fill-chalk-yellow"
            />
            
            <path 
              d="M 160 75 L 185 35" 
              fill="none" 
              stroke="hsl(45 30% 90%)" 
              strokeWidth="1.5"
              strokeDasharray="4 2"
            />
          </>
        );
        
      case 'offside-trap':
        return (
          <>
            <line x1="40" y1="55" x2="200" y2="55" stroke="hsl(45 30% 90%)" strokeWidth="1" strokeDasharray="3 3" />
            
            <text x="50" y="50" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="90" y="50" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="130" y="50" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="170" y="50" className="fill-chalk-white font-bold text-lg">X</text>
            
            <path d="M 60 60 L 60 45" stroke="hsl(45 75% 60%)" strokeWidth="2" markerEnd="url(#arrowhead)" />
            <path d="M 100 60 L 100 45" stroke="hsl(45 75% 60%)" strokeWidth="2" />
            <path d="M 140 60 L 140 45" stroke="hsl(45 75% 60%)" strokeWidth="2" />
            <path d="M 180 60 L 180 45" stroke="hsl(45 75% 60%)" strokeWidth="2" />
            
            <text x="150" y="35" className="fill-chalk-white/60 font-bold text-lg">O</text>
            <line x1="145" y1="30" x2="165" y2="40" stroke="hsl(0 70% 60%)" strokeWidth="2" />
          </>
        );
        
      case 'goal':
        return (
          <>
            <rect x="190" y="35" width="8" height="30" fill="none" stroke="hsl(45 30% 90%)" strokeWidth="2" />
            
            <text x="185" y="55" className="fill-chalk-white font-bold text-lg">X</text>
            
            <circle cx="100" cy="60" r="4" className="fill-chalk-yellow" />
            <text x="95" y="75" className="fill-chalk-white font-bold text-lg">O</text>
            
            <path 
              d="M 100 60 Q 140 50 192 40" 
              fill="none" 
              stroke="hsl(45 75% 60%)" 
              strokeWidth="2.5"
            />
            <polygon 
              points="192,38 195,45 188,42" 
              className="fill-chalk-yellow"
            />
            
            <text x="130" y="70" className="fill-chalk-white font-bold text-lg">X</text>
          </>
        );
        
      case 'defensive':
      default:
        return (
          <>
            <text x="80" y="40" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="120" y="40" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="100" y="60" className="fill-chalk-white font-bold text-lg">X</text>
            <text x="140" y="60" className="fill-chalk-white font-bold text-lg">X</text>
            
            <text x="60" y="85" className="fill-chalk-white font-bold text-lg">O</text>
            <text x="100" y="90" className="fill-chalk-white font-bold text-lg">O</text>
            <text x="150" y="85" className="fill-chalk-white font-bold text-lg">O</text>
            
            <circle cx="110" cy="70" r="6" fill="none" stroke="hsl(45 75% 60%)" strokeWidth="2" />
            <line x1="105" y1="65" x2="115" y2="75" stroke="hsl(45 75% 60%)" strokeWidth="2" />
            <line x1="115" y1="65" x2="105" y2="75" stroke="hsl(45 75% 60%)" strokeWidth="2" />
          </>
        );
    }
  };

  return (
    <div className="chalk-border rounded-lg p-2 bg-chalk-green-light/30">
      <svg
        viewBox="0 0 240 100"
        className="w-full h-auto"
        style={{ maxHeight: '100px' }}
      >
        <rect 
          x="10" y="10" 
          width="220" height="80" 
          fill="none" 
          stroke="hsl(45 30% 90% / 0.4)" 
          strokeWidth="1"
        />
        
        <line 
          x1="120" y1="10" x2="120" y2="90" 
          stroke="hsl(45 30% 90% / 0.3)" 
          strokeWidth="1"
        />
        
        <circle 
          cx="120" cy="50" r="15" 
          fill="none" 
          stroke="hsl(45 30% 90% / 0.3)" 
          strokeWidth="1"
        />
        
        <rect x="10" y="25" width="30" height="50" fill="none" stroke="hsl(45 30% 90% / 0.3)" strokeWidth="1" />
        <rect x="200" y="25" width="30" height="50" fill="none" stroke="hsl(45 30% 90% / 0.3)" strokeWidth="1" />
        
        {diagramType && renderDiagram()}
        
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="hsl(45 75% 60%)" />
          </marker>
        </defs>
      </svg>
    </div>
  );
};

export default TacticsDiagram;
