import { AnimatePresence, motion } from 'framer-motion';
import {
  ArrowLeft,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Upload,
  Zap
} from 'lucide-react';
import { useEffect, useState } from 'react';
import Button from './Button';

const API_BASE = "";

const SubmitClaim = ({ caseData, onBack }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [trackingId, setTrackingId] = useState(null);

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    state: '',
    zip: '',
    country: 'USA',
    affected: true,
    notification_method: 'Email',
    relationship: 'Customer',
    consent: true,
    problem_description: '',
    evidence_types: []
  });

  const [aiScores, setAiScores] = useState({
    docQuality: 0,
    claimStrength: 0,
    payout: 'Calculating...',
    approvalProb: 0
  });

  const steps = [
    "Qualification",
    "Identity",
    "Evidence",
    "AI Analysis",
    "Review",
    "Finalize"
  ];

  const handleNext = () => setStep(s => Math.min(s + 1, 6));
  const handleBack = () => setStep(s => Math.max(s - 1, 1));

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/submit-claim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, case_id: caseData?.id })
      });
      const data = await response.json();
      if (data.tracking_id) {
        setTrackingId(data.tracking_id);
        setStep(6);
      }
    } catch (err) {
      console.error("Submission failed", err);
    } finally {
      setLoading(false);
    }
  };

  // Simulate AI Analysis during step 4
  useEffect(() => {
    if (step === 4) {
      const timer = setTimeout(() => {
        setAiScores({
          docQuality: 92,
          claimStrength: 88,
          payout: '$1,250 - $4,500',
          approvalProb: 94
        });
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [step]);

  const renderProgress = () => (
    <div className="flex justify-between items-center mb-12">
      {steps.map((s, i) => (
        <div key={i} className="flex flex-col items-center relative flex-1">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-black z-10 transition-all duration-500 ${step > i + 1 ? 'bg-emerald-500 text-white' : step === i + 1 ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/30' : 'bg-slate-800 text-slate-500'
            }`}>
            {step > i + 1 ? <CheckCircle2 size={14} /> : i + 1}
          </div>
          <span className={`text-[9px] mt-2 uppercase tracking-widest font-black transition-colors ${step === i + 1 ? 'text-brand-400' : 'text-slate-600'}`}>{s}</span>
          {i < steps.length - 1 && (
            <div className={`absolute top-4 left-[50%] w-full h-[2px] -z-0 transition-colors duration-500 ${step > i + 1 ? 'bg-emerald-500' : 'bg-slate-800'}`}></div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-dark-950 text-slate-200 py-12 px-6">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-12">

        {/* Left Column: Form Content */}
        <div className="lg:col-span-3">
          <div className="mb-8 flex items-center gap-4">
            <button onClick={onBack} className="p-2 hover:bg-slate-800 rounded-full transition-colors"><ArrowLeft size={20} /></button>
            <div>
              <h1 className="text-4xl font-black text-white tracking-tighter">AI Legal Claim Portal</h1>
              <p className="text-slate-500 text-sm">{caseData?.title || "Official Settlement Submission"}</p>
            </div>
          </div>

          {renderProgress()}

          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4 }}
              className="glass-panel p-10 rounded-[3rem] border border-slate-700/30 min-h-[500px] relative overflow-hidden"
            >
              {/* Step 1: Qualification */}
              {step === 1 && (
                <div className="space-y-8">
                  <div>
                    <h2 className="text-2xl font-black text-white mb-2">AI Claim Qualification</h2>
                    <p className="text-slate-400 text-sm">Verify your legal standing using our automated criteria.</p>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">1. Were you affected by this data breach?</label>
                      <div className="flex gap-4">
                        {['Yes', 'No'].map(opt => (
                          <button key={opt} onClick={() => setFormData({ ...formData, affected: opt === 'Yes' })}
                            className={`px-8 py-4 rounded-2xl border transition-all ${formData.affected === (opt === 'Yes') ? 'bg-brand-500/20 border-brand-500 text-brand-400' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>{opt}</button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">2. How were you notified?</label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {['Email', 'Physical Letter', 'SMS', 'Identity Service', 'Other'].map(opt => (
                          <button key={opt} onClick={() => setFormData({ ...formData, notification_method: opt })}
                            className={`px-4 py-3 rounded-xl border text-xs transition-all ${formData.notification_method === opt ? 'bg-brand-500/20 border-brand-500 text-brand-400' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>{opt}</button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">3. Relationship to organization</label>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {['Customer', 'Employee', 'Vendor', 'Other'].map(opt => (
                          <button key={opt} onClick={() => setFormData({ ...formData, relationship: opt })}
                            className={`px-4 py-3 rounded-xl border text-xs transition-all ${formData.relationship === opt ? 'bg-brand-500/20 border-brand-500 text-brand-400' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>{opt}</button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Identity Verification */}
              {step === 2 && (
                <div className="space-y-8">
                  <div>
                    <h2 className="text-2xl font-black text-white mb-2">Identity Verification</h2>
                    <p className="text-slate-400 text-sm">Our AI utilizes smart validation to prevent fraud and ensure accuracy.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      {['First Name', 'Last Name', 'Phone', 'Email'].map((field, i) => (
                        <div key={i}>
                          <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-2 block">{field}</label>
                          <input
                            type="text"
                            className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 px-4 text-white focus:border-brand-500 outline-none placeholder:text-slate-700"
                            placeholder={`Enter ${field.toLowerCase()}`}
                            value={formData[field.toLowerCase().replace(' ', '_')]}
                            onChange={(e) => setFormData({ ...formData, [field.toLowerCase().replace(' ', '_')]: e.target.value })}
                          />
                        </div>
                      ))}
                    </div>
                    <div className="space-y-4">
                      {['Address', 'City', 'State', 'Zip'].map((field, i) => (
                        <div key={i}>
                          <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-2 block">{field}</label>
                          <input
                            type="text"
                            className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 px-4 text-white focus:border-brand-500 outline-none placeholder:text-slate-700"
                            placeholder={`Enter ${field.toLowerCase()}`}
                            value={formData[field.toLowerCase()]}
                            onChange={(e) => setFormData({ ...formData, [field.toLowerCase()]: e.target.value })}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Evidence Upload */}
              {step === 3 && (
                <div className="space-y-8">
                  <div>
                    <h2 className="text-2xl font-black text-white mb-2">Evidence Upload</h2>
                    <p className="text-slate-400 text-sm">Upload supporting evidence to improve verification confidence.</p>
                  </div>

                  <div className="border-2 border-dashed border-slate-700 rounded-[2rem] p-12 text-center group hover:border-brand-500/50 transition-all cursor-pointer bg-slate-900/20">
                    <div className="w-16 h-16 rounded-full bg-brand-500/10 flex items-center justify-center text-brand-400 mx-auto mb-6 group-hover:scale-110 transition-transform">
                      <Upload size={32} />
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">Drag & drop legal evidence here</h3>
                    <p className="text-slate-500 text-xs mb-6">Supports PDF, JPG, PNG (Max 25MB)</p>
                    <div className="flex flex-wrap justify-center gap-3">
                      {['Official Breach Letter', 'Identity Proof', 'Bank Statements', 'Expense Receipts'].map(tag => (
                        <span key={tag} className="px-3 py-1.5 bg-slate-800 rounded-lg text-[10px] font-bold text-slate-400 border border-slate-700">{tag}</span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-brand-500/5 p-4 rounded-2xl border border-brand-500/20 flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-brand-500/20 flex items-center justify-center text-brand-400"><BrainCircuit size={20} /></div>
                    <div className="flex-1">
                      <p className="text-xs font-bold text-white mb-1">AI Document Analyzer Active</p>
                      <p className="text-[10px] text-slate-500">Documents will be scanned for authenticity and payout impact.</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: AI Analysis Results */}
              {step === 4 && (
                <div className="space-y-8">
                  <div>
                    <h2 className="text-2xl font-black text-white mb-2">AI Analysis Dashboard</h2>
                    <p className="text-slate-400 text-sm">Real-time assessment of your claim strength based on provided data.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-6">
                      <div className="glass-panel p-6 rounded-3xl border border-slate-700/30">
                        <div className="flex justify-between items-center mb-4">
                          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Document Quality</span>
                          <span className="text-emerald-400 font-bold">{aiScores.docQuality}%</span>
                        </div>
                        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                          <motion.div initial={{ width: 0 }} animate={{ width: `${aiScores.docQuality}%` }} className="h-full bg-emerald-500 shadow-lg shadow-emerald-500/30"></motion.div>
                        </div>
                        <div className="mt-4 flex items-center gap-2 text-emerald-400/80 text-[10px] font-bold">
                          <CheckCircle2 size={12} /> High-resolution identity match detected.
                        </div>
                      </div>

                      <div className="glass-panel p-6 rounded-3xl border border-slate-700/30">
                        <div className="flex justify-between items-center mb-4">
                          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Evidence Strength</span>
                          <span className="text-brand-400 font-bold">{aiScores.evidence_strength || "Calculating..."}</span>
                        </div>
                        <p className="text-xs text-slate-400 italic">"Strong correlation found between provided bank statements and breach timeline."</p>
                      </div>
                    </div>

                    <div className="bg-brand-500/10 p-8 rounded-[2.5rem] border border-brand-500/20 text-center flex flex-col justify-center">
                      <span className="text-[10px] font-black text-brand-400 uppercase tracking-[0.2em] mb-4">Est. Payout Impact</span>
                      <div className="text-4xl font-black text-white mb-2">{aiScores.payout}</div>
                      <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Institutional AI Projection</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Final Review */}
              {step === 5 && (
                <div className="space-y-8">
                  <div>
                    <h2 className="text-2xl font-black text-white mb-2">Final Protocol Review</h2>
                    <p className="text-slate-400 text-sm">Review your submission data before official filing.</p>
                  </div>

                  <div className="space-y-4">
                    {[
                      { label: "Full Name", val: `${formData.first_name} ${formData.last_name}` },
                      { label: "Verification Email", val: formData.email },
                      { label: "Notification Path", val: formData.notification_method },
                      { label: "Evidence Status", val: "3 Documents Verified" }
                    ].map((item, i) => (
                      <div key={i} className="flex justify-between p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
                        <span className="text-xs text-slate-500 font-bold uppercase tracking-widest">{item.label}</span>
                        <span className="text-xs font-black text-white">{item.val}</span>
                      </div>
                    ))}
                  </div>

                  <div className="p-6 bg-emerald-500/5 border border-emerald-500/20 rounded-3xl">
                    <div className="flex items-center gap-3 mb-2">
                      <ShieldCheck className="text-emerald-400" size={18} />
                      <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">AI Fraud Shield Active</span>
                    </div>
                    <p className="text-[11px] text-slate-400">Submission meets all regulatory compliance standards for this class action settlement.</p>
                  </div>
                </div>
              )}

              {/* Step 6: Confirmation */}
              {step === 6 && (
                <div className="text-center py-12 animate-fade-in">
                  <div className="w-24 h-24 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 mx-auto mb-8 shadow-2xl shadow-emerald-500/10">
                    <CheckCircle2 size={48} />
                  </div>
                  <h2 className="text-4xl font-black text-white mb-4">Official Claim Submitted</h2>
                  <p className="text-slate-400 mb-12">Your claim is now active in the lead counsel registry.</p>

                  <div className="bg-dark-900 p-8 rounded-[2.5rem] border border-slate-800 max-w-sm mx-auto mb-8 shadow-2xl">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4 block">Tracking Identifier</span>
                    <div className="text-2xl font-black text-brand-400 mb-2">{trackingId || "CLM-EF92X4"}</div>
                    <p className="text-slate-600 text-[10px] font-bold">SAVED TO MONGODB PERMANENTLY</p>
                  </div>

                  <div className="flex justify-center gap-4">
                    <Button onClick={onBack} variant="secondary" className="px-8">Back to Dashboard</Button>
                    <Button className="px-8 bg-brand-500 hover:bg-brand-400">Download Receipt</Button>
                  </div>
                </div>
              )}

              {/* Navigation Footer */}
              {step < 6 && (
                <div className="absolute bottom-10 left-10 right-10 flex justify-between items-center">
                  <button onClick={handleBack} className={`text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-2 hover:text-white transition-colors ${step === 1 ? 'invisible' : ''}`}>
                    <ArrowLeft size={16} /> Back
                  </button>
                  {step === 5 ? (
                    <Button onClick={handleSubmit} isLoading={loading} className="px-12 py-5 bg-emerald-600 hover:bg-emerald-500 shadow-xl shadow-emerald-500/20 text-sm">Submit Official Claim</Button>
                  ) : (
                    <Button onClick={handleNext} className="px-12 py-5 shadow-xl shadow-brand-500/20 flex items-center gap-2 text-sm">Continue <ArrowRight size={18} /></Button>
                  )}
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Right Column: AI Guidance Panel */}
        <div className="space-y-8">
          <section className="glass-panel p-8 rounded-[2.5rem] border border-slate-700/30">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-lg bg-brand-500/20 flex items-center justify-center text-brand-400"><Zap size={18} /></div>
              <h3 className="text-[10px] font-black text-white uppercase tracking-widest">AI Legal Insight</h3>
            </div>
            <div className="space-y-6">
              {[
                { icon: "📄", text: "Users with verified breach letters typically process 3x faster.", color: "text-blue-400" },
                { icon: "💰", text: "Financial loss documentation may increase total compensation potential.", color: "text-emerald-400" },
                { icon: "🆔", text: "Incomplete identity verification can delay approval by several months.", color: "text-rose-400" }
              ].map((tip, i) => (
                <div key={i} className="flex gap-4 group">
                  <div className="text-xl group-hover:scale-125 transition-transform">{tip.icon}</div>
                  <p className="text-[11px] text-slate-400 leading-relaxed font-medium">{tip.text}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="bg-slate-900/40 p-8 rounded-[2.5rem] border border-slate-800/50">
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
              <Clock size={14} /> Critical Deadlines
            </h3>
            <div className="space-y-4">
              {[
                { label: "Submission Deadline", date: "July 23, 2026", color: "text-rose-400" },
                { label: "Opt-Out Date", date: "August 7, 2026", color: "text-slate-400" },
                { label: "Approval Hearing", date: "August 22, 2026", color: "text-slate-400" }
              ].map((item, i) => (
                <div key={i} className="flex justify-between items-center">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">{item.label}</span>
                  <span className={`text-[10px] font-black ${item.color}`}>{item.date}</span>
                </div>
              ))}
            </div>
            <div className="mt-8 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-center">
              <p className="text-[9px] text-rose-400 font-black uppercase tracking-widest animate-pulse">Urgency: 68 Days Remaining</p>
            </div>
          </section>

          <div className="text-center py-4">
            <div className="flex justify-center gap-1 mb-4">
              {[1, 2, 3, 4].map(i => <div key={i} className="w-1 h-1 rounded-full bg-slate-700"></div>)}
            </div>
            <p className="text-[9px] text-slate-600 font-black uppercase tracking-widest">Institutional AI Infrastructure</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubmitClaim;
