import React from 'react';

const UserRoadmap = () => {
  const steps = [
    {
      step: "01",
      title: "Select Your Case",
      description: "Browse the 'Latest Intelligence' feed or use the search bar to find a data breach or class action settlement that affects you. Look for the company name and settlement amount.",
      icon: "🎯",
      details: ["Search by company", "Filter by breach/case", "Review settlement value"]
    },
    {
      step: "02",
      title: "Verify Eligibility",
      description: "Click on the case card to see AI-driven insights. Check the 'Risk Profile' and 'Required Documents' sections to ensure you have the necessary proof for a valid claim.",
      icon: "🧪",
      details: ["AI confidence score", "Required documents list", "Deadline tracking"]
    },
    {
      step: "03",
      title: "Activate Premium",
      description: "For automated filing support and institutional-grade intelligence, click the '💎 Premium Access' button. Fill out the comprehensive verification form to secure your claim status.",
      icon: "💎",
      details: ["Identity verification", "Account statement upload", "24/7 AI Legal support"]
    },
    {
      step: "04",
      title: "Final Submission",
      description: "Once your data is verified, proceed to the Lead Counsel Registry to file your official claim. This is the final step to secure your spot in the settlement pool.",
      icon: "📜",
      details: ["Official Registry Portal", "Tracking ID generation", "Receipt download"]
    }
  ];

  const faqItems = [
    { q: "What happens after I submit the Premium form?", a: "Our admin team reviews your documents within 10 minutes. You'll receive a system alert once your Premium Intelligence is active." },
    { q: "How do I know if I'm eligible?", a: "The AI Decision Engine uses real-time court data to predict your success probability. A score above 75% is considered high potential." },
    { q: "Is my data secure?", a: "Yes, all uploaded documents are encrypted with AES-256 and stored in a private, audited environment." }
  ];

  return (
    <div className="space-y-16 animate-fade-in max-w-5xl mx-auto">
      {/* Platform Guide Header */}
      <section className="text-center">
        <span className="text-brand-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4 block">Onboarding Guide</span>
        <h2 className="text-5xl font-black text-white mb-6 tracking-tight">How to Claim Your Rights</h2>
        <p className="text-slate-400 max-w-2xl mx-auto text-lg leading-relaxed">
          Follow this professional protocol to discover, validate, and secure your legal compensation using our AI infrastructure.
        </p>
      </section>
      
      {/* Step by Step Protocol */}
      <section className="grid grid-cols-1 gap-12">
        {steps.map((item, idx) => (
          <div key={idx} className="glass-panel p-10 rounded-[2.5rem] border border-slate-700/30 hover:border-brand-500/30 transition-all group flex flex-col md:flex-row gap-10 items-start relative overflow-hidden">
            <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:opacity-10 transition-opacity">
              <span className="text-9xl font-black text-white">{item.step}</span>
            </div>
            
            <div className="w-20 h-20 rounded-3xl bg-dark-900 border border-slate-700 flex items-center justify-center text-4xl shadow-2xl group-hover:border-brand-500/50 transition-all shrink-0">
              {item.icon}
            </div>
            
            <div className="flex-1 space-y-4 relative z-10">
              <div className="flex items-center gap-3">
                <span className="bg-brand-500/10 text-brand-400 text-[10px] font-black px-3 py-1 rounded-full border border-brand-500/20">PHASE {item.step}</span>
                <h3 className="text-2xl font-bold text-white">{item.title}</h3>
              </div>
              <p className="text-slate-400 leading-relaxed text-lg">{item.description}</p>
              
              <div className="flex flex-wrap gap-3 pt-4">
                {item.details.map((detail, dIdx) => (
                  <span key={dIdx} className="text-[10px] font-bold text-slate-300 bg-slate-800/50 px-4 py-2 rounded-xl border border-slate-700/50">
                    ● {detail}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </section>

      {/* FAQ / Understanding Section */}
      <section className="bg-slate-900/40 rounded-[3rem] p-12 border border-slate-800/50 backdrop-blur-xl">
        <h2 className="text-3xl font-black text-white mb-10 text-center">Frequently Asked Questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {faqItems.map((item, idx) => (
            <div key={idx} className="space-y-4">
              <h4 className="text-brand-400 font-bold text-sm">Q: {item.q}</h4>
              <p className="text-slate-400 text-xs leading-relaxed">{item.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Real-World Credibility Footer */}
      <div className="text-center py-8">
        <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">
          Institutional Grade AI Claims Infrastructure • SECURE_ENV_v1.0
        </p>
      </div>
    </div>
  );
};

export default UserRoadmap;
