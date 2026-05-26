import React, { useState } from 'react';
import Button from './Button';

const PremiumForm = ({ user, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: user?.username || '',
    email: user?.email || '',
    password: '',
    citizen_type: 'Resident',
    state: '',
    district: '',
    village_town: '',
    identity_type: 'Adhar',
    identity_number: '',
    identity_file: null,
    statement_file: null,
    exposed_data: [],
    expense_receipts: null,
    problem_statement: ''
  });

  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  const exposedDataOptions = [
    'SSN', 'Credit Card', 'Email', 'Phone', 'Medical Records', 'Driver\'s License'
  ];

  const handleExposedDataChange = (option) => {
    const updated = formData.exposed_data.includes(option)
      ? formData.exposed_data.filter(i => i !== option)
      : [...formData.exposed_data, option];
    setFormData({ ...formData, exposed_data: updated });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Mock backend delay
    setTimeout(async () => {
      try {
        const response = await fetch('http://localhost:8000/premium-apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
        
        if (response.ok) {
          alert("Application Submitted! Please wait 10 minutes for admin verification. You will be alerted once accepted.");
          onSubmit();
        } else {
          alert("Error submitting application. Please try again.");
        }
      } catch (err) {
        console.error(err);
        alert("Network error. Please try again.");
      } finally {
        setLoading(false);
      }
    }, 1500);
  };

  return (
    <div className="flex flex-col max-h-[80vh] overflow-y-auto pr-4 scrollbar-custom animate-fade-in">
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-black text-white tracking-tighter mb-2">💎 Premium Intelligence Activation</h2>
        <p className="text-slate-400 text-sm">Securely submit your details for institutional-grade claim processing.</p>
      </div>

      <div className="flex gap-2 mb-8 justify-center">
        {[1, 2, 3].map(i => (
          <div key={i} className={`h-1 w-12 rounded-full transition-all ${step >= i ? 'bg-brand-500' : 'bg-slate-700'}`}></div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {step === 1 && (
          <div className="space-y-4 animate-slide-right">
            <h3 className="text-[10px] font-black text-brand-500 uppercase tracking-widest mb-4">Step 1: Personal & Location</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Full Name</label>
                <input 
                  type="text" 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-brand-500 outline-none"
                  placeholder="Enter full name" required
                />
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Citizen Type</label>
                <select 
                  value={formData.citizen_type}
                  onChange={(e) => setFormData({...formData, citizen_type: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-brand-500 outline-none"
                >
                  <option>Resident</option>
                  <option>Non-Resident</option>
                  <option>Expat</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">State</label>
                <input 
                  type="text" 
                  value={formData.state}
                  onChange={(e) => setFormData({...formData, state: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-brand-500 outline-none"
                  placeholder="State" required
                />
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">District</label>
                <input 
                  type="text" 
                  value={formData.district}
                  onChange={(e) => setFormData({...formData, district: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-brand-500 outline-none"
                  placeholder="District" required
                />
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Village/Town</label>
                <input 
                  type="text" 
                  value={formData.village_town}
                  onChange={(e) => setFormData({...formData, village_town: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-brand-500 outline-none"
                  placeholder="Village/Town" required
                />
              </div>
            </div>
            <div className="flex justify-end pt-4">
              <Button type="button" onClick={() => setStep(2)} className="px-8">Next Step</Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4 animate-slide-right">
            <h3 className="text-[10px] font-black text-brand-500 uppercase tracking-widest mb-4">Step 2: Proof & Identity</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Identity Type</label>
                <select 
                  value={formData.identity_type}
                  onChange={(e) => setFormData({...formData, identity_type: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-brand-500 outline-none"
                >
                  <option>Adhar</option>
                  <option>PAN</option>
                  <option>Passport</option>
                  <option>Government ID</option>
                </select>
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">ID Number</label>
                <input 
                  type="text" 
                  value={formData.identity_number}
                  onChange={(e) => setFormData({...formData, identity_number: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-brand-500 outline-none"
                  placeholder="Enter ID Number" required
                />
              </div>
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Upload ID Photo / Copy</label>
              <input type="file" className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:bg-brand-500/20 file:text-brand-400 hover:file:bg-brand-500/30 cursor-pointer" />
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Account Statements (Bank/CC)</label>
              <input type="file" className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:bg-brand-500/20 file:text-brand-400 hover:file:bg-brand-500/30 cursor-pointer" />
            </div>
            <div className="flex justify-between pt-4">
              <Button type="button" onClick={() => setStep(1)} variant="secondary">Back</Button>
              <Button type="button" onClick={() => setStep(3)}>Next Step</Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4 animate-slide-right">
            <h3 className="text-[10px] font-black text-brand-500 uppercase tracking-widest mb-4">Step 3: Data & Problem</h3>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase mb-3 block">Potentially Exposed Data</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {exposedDataOptions.map(option => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => handleExposedDataChange(option)}
                    className={`px-3 py-2 rounded-xl text-[10px] font-bold border transition-all ${
                      formData.exposed_data.includes(option)
                        ? 'bg-brand-500/20 border-brand-500 text-brand-400'
                        : 'bg-slate-900 border-slate-700 text-slate-500 hover:border-slate-500'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Expense Receipts (Credit monitoring, etc.)</label>
              <input type="file" className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:bg-brand-500/20 file:text-brand-400 hover:file:bg-brand-500/30 cursor-pointer" />
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Problem Statement (Max 1000 words)</label>
              <textarea 
                value={formData.problem_statement}
                onChange={(e) => setFormData({...formData, problem_statement: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-4 text-white focus:border-brand-500 outline-none h-32 resize-none text-sm"
                placeholder="Describe your legal problem or data exposure concerns..."
                required
              ></textarea>
            </div>
            <div className="flex justify-between pt-4">
              <Button type="button" onClick={() => setStep(2)} variant="secondary">Back</Button>
              <Button type="submit" isLoading={loading} className="px-10 bg-emerald-600 hover:bg-emerald-500">Submit Activation</Button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default PremiumForm;
