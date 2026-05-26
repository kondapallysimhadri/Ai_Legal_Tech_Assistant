import React from 'react';

const Timeline = ({ events }) => {
  if (!events || events.length === 0) return null;

  return (
    <div className="relative pl-8 border-l border-slate-700/50 space-y-8">
      {events.map((e, idx) => (
        <div key={idx} className="relative">
          <div className="absolute -left-[41px] top-1 w-5 h-5 rounded-full bg-dark-900 border-2 border-brand-500 shadow-[0_0_10px_rgba(var(--brand-500-rgb),0.5)]"></div>
          <div>
            <span className="text-[10px] font-bold text-brand-400 uppercase tracking-tighter">{e.date || 'TBD'}</span>
            <h4 className="text-white font-semibold text-sm">{e.event}</h4>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Timeline;
