import React from 'react';

const BreachCard = ({ breach, onClick, aiResult }) => {
  const isHighRisk = breach.risk_level === 'High';
  
  const eligibility = aiResult?.eligibility;
  const loadingSummary = aiResult?.loadingSummary;
  const loadingEligibility = aiResult?.loadingEligibility;
  
  return (
    <div 
      className="glass-panel p-6 cursor-pointer group flex flex-col h-full animate-fade-in"
      onClick={() => onClick(breach)}
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-white group-hover:text-brand-400 transition-colors">
          {breach.company}
        </h3>
        <div className="flex flex-col items-end gap-1">
          <span className={isHighRisk ? 'badge-high' : 'badge-medium'}>
            {breach.risk_level} Risk
          </span>
          <span className="text-[10px] text-slate-500 font-medium">{breach.date_reported}</span>
        </div>
      </div>
      
      {eligibility && (
        <div className={`mb-4 px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 animate-fade-in
          ${eligibility.status === 'Eligible' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 
            eligibility.status === 'Likely Eligible' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' : 
            'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${eligibility.status === 'Eligible' ? 'bg-green-500' : eligibility.status === 'Likely Eligible' ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
          {eligibility.status.toUpperCase()}
        </div>
      )}
      
      <p className="text-slate-400 text-sm mb-6 flex-grow line-clamp-3">
        {breach.description}
      </p>
      
      <div className="flex flex-wrap gap-2 pt-4 border-t border-slate-700/50 mt-auto">
        <button 
          onClick={(e) => { e.stopPropagation(); onClick(breach, 'summarize'); }}
          disabled={loadingSummary}
          className="flex-1 text-xs py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-600/50 flex items-center justify-center gap-2"
        >
          {loadingSummary && <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>}
          {aiResult?.summary ? 'View Summary' : 'Summarize'}
        </button>
        <button 
          onClick={(e) => { e.stopPropagation(); onClick(breach, 'eligibility'); }}
          disabled={loadingEligibility}
          className="flex-1 text-xs py-2 bg-brand-600/20 hover:bg-brand-600/30 text-brand-400 rounded-lg transition-colors border border-brand-500/30 flex items-center justify-center gap-2"
        >
          {loadingEligibility && <div className="w-3 h-3 border-2 border-brand-400/30 border-t-brand-400 rounded-full animate-spin"></div>}
          {eligibility ? 'Check Again' : 'Check Eligibility'}
        </button>
      </div>
    </div>
  );
};

export default BreachCard;
