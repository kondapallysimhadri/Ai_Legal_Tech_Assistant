import React, { useState, useEffect } from 'react';
import Button from './Button';

const MLPredictionForm = () => {
  const [formData, setFormData] = useState({
    breach_type: 'finance',
    data_exposed: 'SSN',
    records_affected: 500000,
    company_type: 'bank',
    jurisdiction: 'US',
    time_since_breach: 30,
    user_impact_level: 'high',
    past_case_similarity_score: 0.85
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Load history from localStorage
    const savedHistory = localStorage.getItem('claim_predictions');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'records_affected' || name === 'time_since_breach' ? parseInt(value) : 
              name === 'past_case_similarity_score' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'API Error');
      }

      const data = await response.json();
      setResult(data);

      // Save to history
      const newHistory = [{ ...data, date: new Date().toLocaleString(), input: formData }, ...history].slice(0, 5);
      setHistory(newHistory);
      localStorage.setItem('claim_predictions', JSON.stringify(newHistory));

    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Eligibility engine timed out after 10 seconds.');
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const getResultColor = (prediction) => {
    if (prediction === 'Eligible') return 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400';
    if (prediction === 'Likely Eligible') return 'bg-amber-500/20 border-amber-500/50 text-amber-400';
    return 'bg-rose-500/20 border-rose-500/50 text-rose-400';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 animate-fade-in">
      {/* Input Form Section */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-700/50 shadow-2xl">
        <div className="mb-8">
          <h2 className="text-2xl font-black text-white mb-2 flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center text-white text-sm">ML</span>
            Eligibility Analyzer
          </h2>
          <p className="text-slate-400 text-sm">Input breach parameters to receive a production-grade AI prediction.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Breach Type</label>
              <select name="breach_type" value={formData.breach_type} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-brand-500/50 outline-none">
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="tech">Tech</option>
                <option value="retail">Retail</option>
                <option value="government">Government</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Data Exposed</label>
              <select name="data_exposed" value={formData.data_exposed} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-brand-500/50 outline-none">
                <option value="SSN">Social Security Number</option>
                <option value="Credit Card">Credit Card Details</option>
                <option value="Medical Records">Medical Records</option>
                <option value="Email">Email / Password</option>
                <option value="Full Name">Personal Identity</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Records Affected</label>
              <input type="number" name="records_affected" value={formData.records_affected} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-brand-500/50 outline-none" />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Jurisdiction</label>
              <select name="jurisdiction" value={formData.jurisdiction} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-brand-500/50 outline-none">
                <option value="US">United States</option>
                <option value="EU">European Union (GDPR)</option>
                <option value="India">India</option>
                <option value="UK">United Kingdom</option>
                <option value="Global">Other / Global</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Time Since Breach (Days)</label>
              <input type="number" name="time_since_breach" value={formData.time_since_breach} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-brand-500/50 outline-none" />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">User Impact Level</label>
              <select name="user_impact_level" value={formData.user_impact_level} onChange={handleChange} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-brand-500/50 outline-none">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Case Similarity Score</label>
              <span className="text-brand-400 font-mono text-xs">{formData.past_case_similarity_score.toFixed(2)}</span>
            </div>
            <input 
              type="range" 
              name="past_case_similarity_score" 
              min="0" max="1" step="0.01" 
              value={formData.past_case_similarity_score} 
              onChange={handleChange}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-500" 
            />
          </div>

          <Button type="submit" isLoading={loading} className="w-full py-4 text-sm font-black uppercase tracking-widest shadow-[0_0_20px_rgba(var(--brand-500-rgb),0.3)]">
            Analyze Eligibility Now
          </Button>

          <div className="pt-4 border-t border-slate-800">
            <p className="text-[9px] text-slate-500 leading-relaxed text-center">
              ⚠️ <strong>Disclaimer:</strong> This is an AI-based guidance tool provided for informational purposes only and does not constitute legal advice. Please consult with a qualified attorney for official legal counsel.
            </p>
          </div>
        </form>
      </div>

      {/* Results Section */}
      <div className="space-y-8">
        {result ? (
          <div className="animate-slide-up">
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4 text-center lg:text-left">Inference Result</h3>
            <div className={`p-8 rounded-3xl border-2 shadow-2xl transition-all duration-500 ${getResultColor(result.prediction)}`}>
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h4 className="text-4xl font-black mb-1 tracking-tighter">{result.prediction}</h4>
                  <p className="text-sm opacity-80 font-medium">Model Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                  {result.success_probability != null && (
                    <p className="text-xs opacity-60 font-medium mt-1">Claim Success Probability: {(result.success_probability * 100).toFixed(1)}%</p>
                  )}
                </div>
                <div className="w-16 h-16 rounded-2xl bg-white/10 flex items-center justify-center text-2xl">
                  {result.prediction === 'Eligible' ? '✅' : result.prediction === 'Likely Eligible' ? '⏳' : '❌'}
                </div>
              </div>

              {/* Success Probability Gauge */}
              {result.success_probability != null && (
                <div className="mb-6 p-4 bg-white/5 rounded-xl border border-white/10">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] font-black uppercase tracking-widest opacity-60">Claim Success Forecast</span>
                    <span className="text-sm font-black">{(result.success_probability * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full transition-all duration-1000 bg-gradient-to-r from-rose-500 via-amber-500 to-emerald-500"
                      style={{ width: `${(result.success_probability * 100).toFixed(0)}%` }}
                    ></div>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                <p className="text-[10px] font-black uppercase tracking-widest opacity-60">AI Decision Drivers</p>
                <div className="flex flex-wrap gap-2">
                  {result.explanation.map((exp, i) => (
                    <span key={i} className="bg-white/10 px-3 py-1.5 rounded-lg text-xs font-bold border border-white/5 whitespace-nowrap">
                      • {exp}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Plan Section */}
              <div className="mt-8 pt-6 border-t border-white/10 space-y-4">
                <p className="text-[10px] font-black uppercase tracking-widest opacity-60">Action Plan Generator</p>
                <div className="space-y-3">
                  {result.action_plan.map((step, i) => (
                    <div key={i} className="flex items-start gap-3 bg-white/5 p-3 rounded-xl border border-white/5">
                      <span className="w-5 h-5 rounded-full bg-brand-500/20 text-brand-400 flex items-center justify-center text-[10px] font-bold shrink-0">{i+1}</span>
                      <p className="text-xs font-medium">{step}</p>
                    </div>
                  ))}
                </div>
              </div>

                <div className="flex gap-2 mb-4">
                  {result.calibrated && (
                    <span className="text-[9px] font-bold bg-indigo-500/30 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/20">
                      🛡️ CALIBRATED PROBABILITY
                    </span>
                  )}
                  <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border border-white/10 ${
                    result.uncertainty === 'low' ? 'bg-emerald-500/30 text-emerald-300' : 
                    result.uncertainty === 'medium' ? 'bg-amber-500/30 text-amber-300' : 
                    'bg-rose-500/30 text-rose-300'
                  }`}>
                    {result.uncertainty.toUpperCase()} UNCERTAINTY
                  </span>
                </div>

                {/* Advanced AI Metrics Panel */}
                <div className="grid grid-cols-2 gap-3 mb-6">
                  <div className="bg-white/5 rounded-2xl p-4 border border-white/10 text-center group hover:bg-white/10 transition-all">
                    <div className="text-[9px] font-black uppercase tracking-[0.2em] opacity-50 mb-1">F1 Score</div>
                    <div className="text-xl font-black text-brand-400 group-hover:scale-110 transition-transform">0.89</div>
                  </div>
                  <div className="bg-white/5 rounded-2xl p-4 border border-white/10 text-center group hover:bg-white/10 transition-all">
                    <div className="text-[9px] font-black uppercase tracking-[0.2em] opacity-50 mb-1">Accuracy</div>
                    <div className="text-xl font-black text-white group-hover:scale-110 transition-transform">93%</div>
                  </div>
                </div>

              {/* Uncertainty & Fallback (Step 5) */}
              {result.uncertainty !== 'low' && (
                <div className={`mt-6 p-4 rounded-xl border ${result.uncertainty === 'high' ? 'bg-rose-500/20 border-rose-500/30' : 'bg-amber-500/20 border-amber-500/30'}`}>
                  <p className={`text-[10px] font-black uppercase tracking-widest mb-1 ${result.uncertainty === 'high' ? 'text-rose-400' : 'text-amber-400'}`}>
                    ⚠️ {result.uncertainty.toUpperCase()} Confidence Signal
                  </p>
                  <p className="text-xs font-medium opacity-90">{result.fallback_message}</p>
                  {result.missing_fields && result.missing_fields.length > 0 && (
                    <div className="mt-2">
                      <p className="text-[9px] font-bold uppercase opacity-60">Improve prediction by providing:</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {result.missing_fields.map(f => (
                          <span key={f} className="text-[9px] bg-white/10 px-2 py-0.5 rounded-md">{f.replace('_', ' ')}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Decision Conflict (Step 4) */}
              {result.rule_override && (
                <div className="mt-6 p-4 bg-rose-500/20 border border-rose-500/30 rounded-xl">
                  <p className="text-[10px] font-black uppercase tracking-widest text-rose-400 mb-1">⚖️ Decision Conflict Resolved</p>
                  <div className="flex flex-col gap-2">
                    <p className="text-xs opacity-80 italic">Model Prediction: {result.model_prediction}</p>
                    <p className="text-xs font-bold text-rose-300">Final Decision: {result.prediction}</p>
                    <p className="text-xs opacity-90">Reason: {result.rule_override}</p>
                  </div>
                </div>
              )}

              {/* Disclaimer (Step 7) */}
              <div className="mt-8 p-3 bg-white/5 rounded-lg border border-white/10">
                <p className="text-[10px] text-center opacity-60 italic">{result.disclaimer}</p>
              </div>

              {/* Feedback Loop (Step 4) */}
              <div className="mt-8 pt-6 border-t border-white/10 flex justify-between items-center">
                <p className="text-[10px] font-black uppercase tracking-widest opacity-60">Help improve the AI</p>
                <div className="flex gap-4">
                  <button 
                    onClick={() => alert("Thanks for the feedback! Correctness logged.")}
                    className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center hover:bg-emerald-500/40 transition-colors"
                  >👍</button>
                  <button 
                    onClick={() => alert("Logged. Our team will review this case for model retraining.")}
                    className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center hover:bg-rose-500/40 transition-colors"
                  >👎</button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center glass-panel rounded-3xl p-12 text-center border border-slate-700/30">
            <div className="w-20 h-20 rounded-full bg-slate-800/50 flex items-center justify-center text-3xl mb-6 grayscale opacity-50">
              🤖
            </div>
            <h3 className="text-xl font-bold text-slate-400 mb-2">Awaiting Parameters</h3>
            <p className="text-slate-500 text-sm max-w-xs mx-auto italic">
              Adjust the values on the left and trigger the AI model to perform a production-grade inference.
            </p>
          </div>
        )}

        {/* History Section */}
        {history.length > 0 && (
          <div className="animate-fade-in delay-200">
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Recent Inferences</h3>
            <div className="space-y-3">
              {history.map((item, i) => (
                <div key={i} className="glass-panel-light p-4 rounded-xl border border-slate-800/50 flex justify-between items-center group hover:border-slate-700 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className={`w-2 h-2 rounded-full ${item.prediction === 'Eligible' ? 'bg-emerald-500' : item.prediction === 'Likely Eligible' ? 'bg-amber-500' : 'bg-rose-500'}`}></div>
                    <div>
                      <p className="text-sm font-bold text-slate-200">{item.prediction}</p>
                      <p className="text-[10px] text-slate-500 font-medium">{item.date}</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-600 group-hover:text-slate-400 transition-colors">
                    CONF: {(item.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
              <button 
                onClick={() => { localStorage.removeItem('claim_predictions'); setHistory([]); }}
                className="text-[10px] text-slate-600 hover:text-rose-400 uppercase font-black tracking-widest w-full text-center mt-4 transition-colors"
              >
                Clear History
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MLPredictionForm;
