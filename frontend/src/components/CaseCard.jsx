import React from 'react';

const CaseCard = ({ caseItem, onClick }) => {
  const getRiskColor = (level) => {
    const l = level?.toLowerCase();
    if (l === 'critical' || l === 'high' || l === 'impact') return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
    if (l === 'medium') return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
  };

  return (
    <div 
      onClick={() => onClick(caseItem)}
      className="glass-panel group p-6 rounded-3xl border border-slate-700/30 hover:border-brand-500/50 transition-all cursor-pointer hover:shadow-2xl hover:shadow-brand-500/10 flex flex-col h-full bg-dark-800/40 backdrop-blur-md overflow-hidden relative animate-fade-in"
    >
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
        <svg className="w-12 h-12 text-brand-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
      </div>

      <div className="flex justify-between items-start mb-4">
        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${getRiskColor(caseItem.risk_level || caseItem.impact_category)}`}>
          {caseItem.risk_level || caseItem.impact_category || 'Active'}
        </span>
        <div className="flex items-center gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse"></div>
          <span className="text-[10px] font-mono text-brand-400/80">CONF: {Math.round((caseItem.confidence > 1 ? caseItem.confidence : (caseItem.confidence || 0.85) * 100))}%</span>
        </div>
      </div>

      <h3 className="text-xl font-bold text-white mb-3 group-hover:text-brand-400 transition-colors line-clamp-2">
        {caseItem.title || caseItem.company || "Legal Case"}
      </h3>
      
      <p className="text-slate-400 text-sm mb-6 line-clamp-3 leading-relaxed">
        {caseItem.summary || caseItem.description || "In-depth analysis of legal proceedings and claim eligibility for affected individuals."}
      </p>

      <div className="mt-auto space-y-4">
        <div className="grid grid-cols-2 gap-4 border-t border-slate-700/50 pt-4">
          <div>
            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Est. Payout</div>
            <div className="text-sm font-bold text-brand-400">{caseItem.estimated_compensation || "$125 - $20,000"}</div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Eligibility</div>
            <div className="text-sm font-bold text-white">{caseItem.eligibility || "High"}</div>
          </div>
        </div>

        <div className="bg-dark-900/50 rounded-2xl p-4 border border-slate-700/30">
          <div className="text-[10px] text-brand-400/60 uppercase font-black tracking-widest mb-2 flex items-center gap-2">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/><path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/></svg>
            AI Insight
          </div>
          <p className="text-[11px] text-slate-300 italic leading-snug">
            {caseItem.ai_insight || `Exposure of ${caseItem.exposed_data || 'sensitive data'} strongly increases claim eligibility patterns.`}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CaseCard;
