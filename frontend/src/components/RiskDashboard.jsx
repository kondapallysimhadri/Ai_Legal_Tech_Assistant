import React, { useState, useEffect } from 'react';
import Button from './Button';

const RiskDashboard = ({ profile, cases }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 seconds for Gemini API
      try {
        const response = await fetch('/api/privacy/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profile),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        const data = await response.json();
        setAnalysis(data);
      } catch (err) {
        if (err.name === 'AbortError') {
          console.error("Privacy analysis timed out");
        } else {
          console.error("Failed to fetch privacy analysis", err);
        }
        // Set fallback analysis to prevent hanging forever
        setAnalysis({
          matched_cases: 0,
          identity_theft_risk: "Unknown (Timeout)",
          risk_score: 50,
          analysis_details: "The AI Engine is currently experiencing high latency. Please check back later.",
          recommended_action: "Monitor your accounts manually in the meantime."
        });
      } finally {
        setLoading(false);
      }
    };

    if (profile) {
      fetchAnalysis();
    }
  }, [profile]);

  if (loading) {
    return <div className="text-center p-12 text-slate-400 animate-pulse">Running AI Privacy Analysis...</div>;
  }

  if (!analysis) return null;

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 border-brand-500/30 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-2 text-4xl opacity-10">🔍</div>
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Matched Legal Cases</span>
          <div className="text-4xl font-black text-white mt-2">{analysis.matched_cases}</div>
        </div>
        <div className="glass-panel p-6 border-red-500/30 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-2 text-4xl opacity-10">⚠️</div>
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Identity Theft Risk</span>
          <div className={`text-4xl font-black mt-2 ${analysis.identity_theft_risk.includes('High') || analysis.identity_theft_risk.includes('Critical') ? 'text-red-400' : 'text-yellow-400'}`}>
            {analysis.identity_theft_risk}
          </div>
        </div>
        <div className="glass-panel p-6 border-orange-500/30 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-2 text-4xl opacity-10">📊</div>
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Risk Exposure Score</span>
          <div className="text-4xl font-black text-orange-400 mt-2">{analysis.risk_score}%</div>
        </div>
      </div>

      <div className="glass-panel p-8">
        <div className="flex items-center gap-3 mb-6">
          <h3 className="text-xl font-bold text-white">AI Privacy Intelligence</h3>
          <span className="bg-brand-500/20 text-brand-400 text-[10px] px-2 py-0.5 rounded-full border border-brand-500/30 animate-pulse">LIVE</span>
        </div>
        
        <div className="space-y-6">
          <div className="bg-slate-800/30 p-6 rounded-2xl border border-slate-700/50">
            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Analysis Details</h4>
            <p className="text-slate-300 text-sm leading-relaxed">{analysis.analysis_details}</p>
          </div>
          
          <div className="bg-brand-500/10 p-6 rounded-2xl border border-brand-500/30">
            <h4 className="text-[10px] font-black text-brand-500 uppercase tracking-widest mb-2">Recommended Action</h4>
            <p className="text-white text-lg font-bold">{analysis.recommended_action}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskDashboard;
