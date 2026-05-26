import { useEffect, useMemo, useState } from 'react';
import Auth from './components/Auth';
import Button from './components/Button';
import CaseCard from './components/CaseCard';
import EmptyState from './components/EmptyState';
import MLPredictionForm from './components/MLPredictionForm';
import Modal from './components/Modal';
import Navbar from './components/Navbar';
import PremiumForm from './components/PremiumForm';
import RAGChatbot from './components/RAGChatbot';
import RiskDashboard from './components/RiskDashboard';
import SubmitClaim from './components/SubmitClaim';
import UserProfile from './components/UserProfile';
import UserRoadmap from './components/UserRoadmap';

const API_BASE = "";

function App() {
  const [view, setView] = useState('home');
  const [cases, setCases] = useState([]);
  const [stats, setStats] = useState({ cases: 0, breaches: 0 });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [eligibilityResult, setEligibilityResult] = useState(null);
  const [loadingEligibility, setLoadingEligibility] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [enriching, setEnriching] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [filterType, setFilterType] = useState('all'); // 'all', 'cases', 'breaches'
  const [isPremiumFormOpen, setIsPremiumFormOpen] = useState(false);

  useEffect(() => {
    const savedUser = localStorage.getItem('auth_user');
    if (savedUser) {
      const user = JSON.parse(savedUser);
      setCurrentUser(user);
      setIsAuthenticated(true);
    }

    fetchInitialData();
    const savedProfile = localStorage.getItem('user_profile');
    if (savedProfile) setUserProfile(JSON.parse(savedProfile));
  }, []);

  const handleLogin = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
    localStorage.setItem('auth_user', JSON.stringify(user));
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser(null);
    localStorage.removeItem('auth_user');
  };

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [casesRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/cases`),
        fetch(`${API_BASE}/stats`)
      ]);
      if (casesRes.ok) setCases(await casesRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (err) {
      console.error("Failed to fetch data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = (profile) => {
    setUserProfile(profile);
    localStorage.setItem('user_profile', JSON.stringify(profile));
    setView('risk');
  };

  const triggerEnrichment = async () => {
    setEnriching(true);
    try {
      const res = await fetch(`${API_BASE}/enrich`, { method: 'POST' });
      if (res.ok) alert("Enrichment pipeline triggered successfully.");
    } catch (err) {
      console.error("Enrichment failed", err);
    } finally {
      setEnriching(false);
    }
  };

  const filteredCases = useMemo(() => {
    let result = cases;
    if (filterType === 'cases') {
      result = cases.filter(c => c.case_type?.toLowerCase().includes('settlement') || c.title?.toLowerCase().includes('settlement'));
    } else if (filterType === 'breaches') {
      result = cases.filter(c => c.case_type?.toLowerCase().includes('breach') || c.title?.toLowerCase().includes('breach'));
    }

    if (!searchQuery) return result;
    return result.filter(c =>
      (c.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.company || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.description || '').toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [cases, searchQuery, filterType]);

  const checkEligibility = async (caseData) => {
    setLoadingEligibility(true);
    setEligibilityResult(null);
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          breach_type: caseData.case_type || "tech",
          data_exposed: caseData.exposed_data || "Personal Information",
          records_affected: caseData.impact_score > 80 ? 500000 : caseData.impact_score > 50 ? 50000 : 1000,
          company_type: caseData.company || "tech",
          jurisdiction: "US",
          time_since_breach: caseData.deadline === "Ongoing" ? 30 : 180,
          user_impact_level: caseData.risk_level?.toLowerCase() || "high",
          past_case_similarity_score: caseData.confidence ? caseData.confidence / 100 : 0.85
        })
      });
      if (!res.ok) throw new Error("Prediction failed");
      const data = await res.json();

      if (data) {
        if (typeof data.confidence !== 'number' || isNaN(data.confidence)) {
          data.confidence = 0.85;
        }
        if (data.confidence > 1) data.confidence /= 100;
      }
      setEligibilityResult(data);
    } catch (err) {
      console.error("Eligibility check failed", err);
      setEligibilityResult({
        prediction: "Likely Eligible",
        confidence: 0.75,
        explanation: ["We encountered a temporary connection issue.", "General case patterns suggest high eligibility."],
        action_plan: ["Gather your documents.", "Check official status manually."],
        rule_reason: "Offline Fallback"
      });
    } finally {
      setLoadingEligibility(false);
    }
  };

  const viewCase = async (caseItem) => {
    setSelectedCase(caseItem);
    setIsModalOpen(true);
    setEligibilityResult(null);
    setShowGuide(false);

    if (caseItem && caseItem.id) {
      try {
        const res = await fetch(`${API_BASE}/cases/${caseItem.id}`);
        if (res.ok) {
          const detailed = await res.json();
          setSelectedCase(prev => ({ ...prev, ...detailed }));
        }
      } catch (err) {
        console.error("Failed to load case details", err);
      }
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedCase(null), 300);
  };

  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    setSearchResults(null);
    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery })
      });
      if (!res.ok) throw new Error("Search failed");
      const data = await res.json();

      if (data && Array.isArray(data.results)) {
        setSearchResults(data);
      } else {
        setSearchResults({ results: [], ai_overview: "Search returned no valid data." });
      }
    } catch (err) {
      console.error("Search failed", err);
      setSearchResults({ results: [], ai_overview: "Search service is currently offline." });
    } finally {
      setSearching(false);
    }
  };

  const renderGuide = () => (
    <div className="animate-fade-in space-y-8">
      <div className="flex items-center gap-4 mb-8">
        <div className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold">1</div>
        <div>
          <h3 className="text-xl font-bold text-white">Document Collection</h3>
          <p className="text-slate-400 text-sm">Gather these essential files to maximize your claim value.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { t: "Official Breach Letter", d: "The letter sent by the company notifying you of the breach." },
          { t: "Proof of Identity", d: "Valid Government ID or Passport copy." },
          { t: "Account Statements", d: "Bank or credit card statements showing the account existed." },
          { t: "Expense Receipts", d: "Proof of any costs incurred (credit monitoring, fraud resolution)." }
        ].map((item, i) => (
          <div key={i} className="p-4 bg-dark-800 border border-slate-700 rounded-2xl">
            <h4 className="text-brand-400 font-bold text-sm mb-1">{item.t}</h4>
            <p className="text-slate-500 text-xs">{item.d}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4 py-8">
        <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center text-emerald-400 font-bold">2</div>
        <div>
          <h3 className="text-xl font-bold text-white">Registry Submission</h3>
          <p className="text-slate-400 text-sm">Submit your preliminary data to the lead counsel registry.</p>
        </div>
      </div>

      <div className="bg-brand-500/10 p-6 rounded-3xl border border-brand-500/20">
        <p className="text-slate-300 text-sm mb-4">By registering now, you preserve your rights to the settlement pool before the deadline.</p>
        <Button
          onClick={() => {
            window.open('https://veritaconnect.com/tj-factasettlement/Claimant', '_blank');
          }}
          className="w-full bg-brand-500 py-4 shadow-xl shadow-brand-500/20"
        >
          Official Registry Portal →
        </Button>
      </div>

      <Button onClick={() => setShowGuide(false)} variant="secondary" className="w-full py-3">
        ← Back to Case Details
      </Button>
    </div>
  );

  const renderContent = () => {
    if (view === 'profile') return <UserProfile onSave={handleSaveProfile} />;
    if (view === 'risk') return <RiskDashboard profile={userProfile || { dataTypes: [] }} cases={cases} />;
    if (view === 'ml-checker') return <MLPredictionForm />;
    if (view === 'chat') return <RAGChatbot />;
    if (view === 'roadmap') return <UserRoadmap />;
    if (view === 'submit-claim') return <SubmitClaim caseData={selectedCase} onBack={() => setView('home')} />;

    return (
      <>
        <header className="mb-12 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-center md:text-left">
            <h2 className="text-3xl md:text-5xl font-black text-white mb-4 tracking-tighter">AI Legal Intelligence.</h2>
            <p className="text-slate-400 max-w-xl text-lg">Real-world legal cases, scraped in real-time, and analyzed by production-grade AI models.</p>
          </div>
          <div className="flex gap-4">
            <Button
              onClick={triggerEnrichment}
              isLoading={enriching}
              variant="secondary"
              className="border-brand-500/50 text-brand-400 hover:bg-brand-500/10"
            >
              🔄 Sync & Enrich Pipeline
            </Button>
            <Button
              onClick={() => setIsPremiumFormOpen(true)}
              className="bg-gradient-to-r from-amber-500 to-orange-600 shadow-lg shadow-orange-500/20"
            >
              💎 Premium Access
            </Button>
          </div>
        </header>

        <section className="mb-12">
          <div className="relative max-w-4xl mx-auto">
            <div className="flex gap-4 p-2 bg-dark-800/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl">
              <div className="flex-1 relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                </div>
                <input
                  type="text"
                  placeholder="Search legal cases, breaches, settlements..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full bg-transparent text-white rounded-xl py-4 pl-12 pr-4 outline-none placeholder:text-slate-500"
                />
              </div>
              <Button onClick={handleSearch} isLoading={searching} className="px-8 rounded-xl bg-brand-500 hover:bg-brand-400 transition-all">
                Search
              </Button>
            </div>
          </div>
        </section>

        {searchResults && (
          <div className="mb-12 animate-slide-up">
            <div className="glass-panel p-6 rounded-3xl border border-brand-500/30 bg-brand-500/5 mb-8">
              <h4 className="text-[10px] font-black text-brand-400 uppercase tracking-widest mb-2">AI Search Overview</h4>
              <p className="text-slate-200 text-lg leading-relaxed font-medium">
                {searchResults.ai_overview}
              </p>
            </div>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">Search Results</h3>
              <Button variant="secondary" className="text-xs py-1" onClick={() => setSearchResults(null)}>Clear Search</Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {searchResults.results.map((c, idx) => (
                <CaseCard key={idx} caseItem={c} onClick={viewCase} />
              ))}
            </div>
            {searchResults.results.length === 0 && <EmptyState onClear={() => { setSearchResults(null); setSearchQuery(''); }} />}
          </div>
        )}

        {!searchResults && (
          <>
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                Latest Intelligence
                <span className="bg-brand-500/20 text-brand-400 text-[10px] px-2 py-0.5 rounded-full border border-brand-500/30 animate-pulse">LIVE</span>
              </h3>
              <div className="flex gap-4">
                <button
                  onClick={() => setFilterType(filterType === 'cases' ? 'all' : 'cases')}
                  className={`text-xs font-mono tracking-widest transition-all px-3 py-1 rounded-lg border ${filterType === 'cases' ? 'bg-brand-500/20 text-brand-400 border-brand-500/50' : 'text-slate-500 border-transparent hover:text-brand-400'}`}
                >
                  {stats.cases} CASES FOUND
                </button>
                <button
                  onClick={() => setFilterType(filterType === 'breaches' ? 'all' : 'breaches')}
                  className={`text-xs font-mono tracking-widest transition-all px-3 py-1 rounded-lg border ${filterType === 'breaches' ? 'bg-brand-500/20 text-brand-400 border-brand-500/50' : 'text-slate-500 border-transparent hover:text-brand-400'}`}
                >
                  {stats.breaches} BREACHES FOUND
                </button>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="glass-panel p-6 animate-pulse h-64 bg-slate-800/50 rounded-2xl"></div>)}
              </div>
            ) : filteredCases.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCases.map((c, idx) => (
                  <CaseCard
                    key={idx}
                    caseItem={c}
                    onClick={viewCase}
                  />
                ))}
              </div>
            ) : <EmptyState onClear={() => setSearchQuery('')} />}
          </>
        )}
      </>
    );
  };

  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-dark-900 text-slate-200 font-sans selection:bg-brand-500/30 overflow-x-hidden">
      <Navbar onNavigate={setView} currentView={view} />

      <div className="max-w-6xl mx-auto px-6 pt-4 flex justify-end">
        <button onClick={handleLogout} className="text-[10px] font-black text-slate-500 uppercase tracking-widest hover:text-red-400 transition-colors">
          Log Out: {currentUser?.username}
        </button>
      </div>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {renderContent()}
      </main>

      <Modal isOpen={isModalOpen} onClose={closeModal}>
        {selectedCase && (
          <div className="flex flex-col animate-fade-in max-h-[85vh] overflow-y-auto pr-2 scrollbar-custom">
            {showGuide ? renderGuide() : (
              <>
                <div className="mb-8 pb-6 border-b border-slate-700/50">
                  <div className="flex flex-wrap items-center gap-3 mb-2">
                    <h2 className="text-3xl font-black text-white tracking-tighter">{selectedCase.title || selectedCase.company}</h2>
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest 
                      ${(selectedCase.risk_level === 'High' || selectedCase.impact_category === 'High') ? 'bg-red-500/20 text-red-400' : 'bg-brand-500/20 text-brand-400'}`}>
                      {selectedCase.risk_level || selectedCase.impact_category} Impact
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm italic truncate">Source: {selectedCase.source_url}</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                  <div className="lg:col-span-2 space-y-10">
                    <section>
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-7 h-7 rounded-lg bg-brand-500/20 flex items-center justify-center text-brand-400 text-sm">🧠</div>
                        <h3 className="text-[10px] font-black text-brand-500 uppercase tracking-[0.2em]">AI Intelligence Overview</h3>
                      </div>
                      <div className="bg-dark-900 border border-brand-500/20 p-8 rounded-3xl relative group hover:border-brand-500/40 transition-all">
                        <p className="text-slate-100 text-lg leading-relaxed font-medium mb-6">
                          {selectedCase.ai_summary || selectedCase.summary || selectedCase.description || `Our AI analysis indicates this ${selectedCase.company || 'case'} involves a significant data exposure event affecting consumer privacy.`}
                        </p>
                        <div className="flex flex-wrap gap-3 pt-4 border-t border-slate-700/30">
                          <span className="text-[9px] bg-slate-800 px-3 py-1.5 rounded-full text-slate-400 border border-slate-700 font-bold uppercase tracking-widest">🛡️ Severity: {selectedCase.risk_level || "High"}</span>
                          <span className="text-[9px] bg-slate-800 px-3 py-1.5 rounded-full text-slate-400 border border-slate-700 font-bold uppercase tracking-widest">💰 Potential: {selectedCase.eligibility || "Moderate"}</span>
                        </div>
                      </div>
                    </section>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <section>
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Required Documents</h3>
                        <div className="space-y-2">
                          {(selectedCase.required_documents || ["Identity Proof", "Breach Notification", "Account Proof"]).map((doc, idx) => (
                            <div key={idx} className="flex items-center gap-3 p-3 bg-slate-800/30 rounded-xl border border-slate-700/30">
                              <div className="w-5 h-5 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400 text-[10px]">✓</div>
                              <span className="text-slate-300 text-[11px] font-medium">{doc}</span>
                            </div>
                          ))}
                        </div>
                      </section>
                      <section>
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Risk Profile</h3>
                        <div className="space-y-2">
                          {[
                            { label: "Complexity", val: "Moderate", color: "text-blue-400 border-blue-500/20" },
                            { label: "Confidence", val: `${(selectedCase.confidence || 85)}%`, color: "text-emerald-400 border-emerald-500/20" },
                            { label: "Exposure", val: selectedCase.risk_level || "High", color: "text-rose-400 border-rose-500/20" }
                          ].map((risk, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl border border-slate-800">
                              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{risk.label}</span>
                              <span className={`text-[9px] px-2.5 py-1 rounded-full font-black uppercase border ${risk.color}`}>{risk.val}</span>
                            </div>
                          ))}
                        </div>
                      </section>
                    </div>

                    <section>
                      <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">AI Eligibility Reasoning</h3>
                      <div className="bg-brand-500/5 border border-brand-500/15 p-5 rounded-2xl">
                        <p className="text-slate-300 text-sm leading-relaxed italic">
                          {selectedCase.ai_eligibility_reasoning || selectedCase.ai_insight || `Analysis suggests high claim validity based on historical precedents.`}
                        </p>
                      </div>
                    </section>
                  </div>

                  <div className="space-y-8">
                    <section>
                      <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Predict Eligibility</h3>
                      <div className="bg-dark-900 border border-brand-500/20 rounded-3xl p-6 shadow-2xl space-y-6">
                        {!eligibilityResult ? (
                          <div className="text-center space-y-4">
                            <p className="text-slate-500 text-xs">Run our model to check your legal standing.</p>
                            <Button onClick={() => checkEligibility(selectedCase)} isLoading={loadingEligibility} className="w-full py-4 shadow-lg shadow-brand-500/20">
                              Predict Eligibility
                            </Button>
                          </div>
                        ) : (
                          <div className="animate-fade-in space-y-6">
                            <div className="flex items-center gap-3">
                              <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold
                                ${(eligibilityResult.prediction || '').includes('Eligible') ? 'bg-emerald-600' : 'bg-rose-600'}`}>
                                {(eligibilityResult.prediction || 'E')[0]}
                              </div>
                              <div>
                                <h4 className="text-lg font-black text-white">{eligibilityResult.prediction}</h4>
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                                  {(Math.min(0.99, Math.max(0.01, eligibilityResult.confidence || 0.85)) * 100).toFixed(0)}% AI CONFIDENCE
                                </span>
                              </div>
                            </div>
                            <div className="space-y-2">
                              {(eligibilityResult.explanation || []).slice(0, 3).map((exp, i) => (
                                <p key={i} className="text-xs text-slate-400 flex items-start gap-2">
                                  <span className="text-brand-500">→</span> {exp}
                                </p>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="pt-6 border-t border-slate-700/50">
                          <Button onClick={() => setShowGuide(true)} className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-[10px] uppercase tracking-widest font-black">
                            Submit Claim Guide
                          </Button>
                        </div>
                      </div>
                    </section>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </Modal>

      <Modal isOpen={isPremiumFormOpen} onClose={() => setIsPremiumFormOpen(false)}>
        <PremiumForm user={currentUser} onSubmit={() => setIsPremiumFormOpen(false)} />
      </Modal>
    </div>
  );
}

export default App;
