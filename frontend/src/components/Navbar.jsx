import React, { useState } from 'react';

const Navbar = ({ onNavigate, currentView }) => {
  const [showPremium, setShowPremium] = useState(false);

  return (
    <>
      <nav className="border-b border-slate-800 bg-dark-900/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => onNavigate('home')}>
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-brand-500/20">
              A
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent hidden sm:block">
              AI Legal Claim Assistant
            </h1>
          </div>
          
          <div className="flex items-center gap-6">
            <button 
              onClick={() => onNavigate('home')}
              className={`text-sm font-medium transition-colors ${currentView === 'home' ? 'text-brand-400' : 'text-slate-300 hover:text-white'}`}
            >
              Home
            </button>
            <button 
              onClick={() => onNavigate('profile')}
              className={`text-sm font-medium transition-colors ${currentView === 'profile' ? 'text-brand-400' : 'text-slate-300 hover:text-white'}`}
            >
              Digital Twin
            </button>
            <button 
              onClick={() => onNavigate('risk')}
              className={`text-sm font-medium transition-colors ${currentView === 'risk' ? 'text-brand-400' : 'text-slate-300 hover:text-white'}`}
            >
              Privacy Intelligence
            </button>
            <button 
              onClick={() => onNavigate('ml-checker')}
              className={`text-sm font-medium transition-colors ${currentView === 'ml-checker' ? 'text-brand-400' : 'text-slate-300 hover:text-white'}`}
            >
              AI Decision Engine
            </button>
            <button 
              onClick={() => onNavigate('chat')}
              className={`text-sm font-medium transition-colors ${currentView === 'chat' ? 'text-brand-400' : 'text-slate-300 hover:text-white'}`}
            >
              AI Legal Assistant
            </button>
            <button 
              onClick={() => onNavigate('roadmap')}
              className={`text-sm font-medium transition-colors ${currentView === 'roadmap' ? 'text-brand-400' : 'text-slate-300 hover:text-white'}`}
            >
              Platform Roadmap
            </button>
            <div className="h-4 w-px bg-slate-700 mx-1"></div>
            <button 
              onClick={() => setShowPremium(true)}
              className="btn-primary text-sm py-1.5 px-4 shadow-[0_0_15px_rgba(var(--brand-500-rgb),0.3)] bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 transition-all"
            >
              💎 Premium Access
            </button>
          </div>
        </div>
      </nav>

      {/* Premium Modal */}
      {showPremium && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-fade-in" onClick={() => setShowPremium(false)}>
          <div className="bg-dark-800 border border-amber-500/30 rounded-3xl p-8 max-w-md w-full mx-4 shadow-2xl shadow-amber-500/10 animate-slide-up" onClick={(e) => e.stopPropagation()}>
            <div className="text-center mb-8">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-600 flex items-center justify-center text-3xl mx-auto mb-4 shadow-lg shadow-amber-500/30">💎</div>
              <h2 className="text-2xl font-black text-white mb-2">Premium Intelligence</h2>
              <p className="text-slate-400 text-sm">Unlock advanced AI capabilities for your legal claims</p>
            </div>
            
            <div className="space-y-4 mb-8">
              {[
                { icon: "🧠", title: "Deep Legal Reasoning", desc: "GPT-4 level case analysis" },
                { icon: "📊", title: "Advanced Analytics", desc: "Historical case outcome prediction" },
                { icon: "🔔", title: "Real-time Alerts", desc: "Instant notifications for new settlements" },
                { icon: "📄", title: "Document Generator", desc: "AI-generated claim filing documents" },
                { icon: "👨‍⚖️", title: "Attorney Matching", desc: "Connect with verified legal experts" },
              ].map((f, i) => (
                <div key={i} className="flex items-center gap-4 p-3 bg-slate-900/50 rounded-xl border border-slate-700/30 hover:border-amber-500/30 transition-colors">
                  <span className="text-2xl">{f.icon}</span>
                  <div>
                    <p className="text-sm font-bold text-white">{f.title}</p>
                    <p className="text-[11px] text-slate-500">{f.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <button 
              onClick={() => { setShowPremium(false); alert("✅ Premium Access Activated! (Demo Mode)"); }}
              className="w-full py-4 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white font-black text-sm uppercase tracking-widest rounded-2xl shadow-lg shadow-amber-500/20 transition-all"
            >
              Activate Premium — Free Trial
            </button>
            <button 
              onClick={() => setShowPremium(false)}
              className="w-full mt-3 py-2 text-slate-500 text-xs hover:text-white transition-colors"
            >
              Maybe Later
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
