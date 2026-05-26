import React, { useState } from 'react';
import Button from './Button';

const UserProfile = ({ onSave }) => {
  const [profile, setProfile] = useState({
    name: '',
    location: '',
    employment: '',
    dataTypes: [],
    financialLoss: false
  });

  const types = ['SSN', 'Credit Card', 'Email', 'Phone', 'Medical Records', 'Driver License'];

  const toggleType = (type) => {
    setProfile(prev => ({
      ...prev,
      dataTypes: prev.dataTypes.includes(type) 
        ? prev.dataTypes.filter(t => t !== type)
        : [...prev.dataTypes, type]
    }));
  };

  return (
    <div className="glass-panel p-8 max-w-2xl mx-auto animate-fade-in">
      <h2 className="text-3xl font-black text-white mb-6 tracking-tighter">Your Digital Twin</h2>
      <p className="text-slate-400 mb-8">Build your risk profile to automatically match against 500+ legal cases.</p>
      
      <div className="space-y-6">
        <div>
          <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Full Name</label>
          <input 
            type="text" 
            value={profile.name}
            onChange={(e) => setProfile({...profile, name: e.target.value})}
            className="w-full bg-dark-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-1 focus:ring-brand-500 outline-none"
            placeholder="John Doe"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Location (State)</label>
            <input 
              type="text" 
              value={profile.location}
              onChange={(e) => setProfile({...profile, location: e.target.value})}
              className="w-full bg-dark-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-1 focus:ring-brand-500 outline-none"
              placeholder="California"
            />
          </div>
          <div>
            <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Employment</label>
            <input 
              type="text" 
              value={profile.employment}
              onChange={(e) => setProfile({...profile, employment: e.target.value})}
              className="w-full bg-dark-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-1 focus:ring-brand-500 outline-none"
              placeholder="Software Engineer"
            />
          </div>
        </div>

        <div>
          <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4">Potentially Exposed Data</label>
          <div className="flex flex-wrap gap-2">
            {types.map(type => (
              <button 
                key={type}
                onClick={() => toggleType(type)}
                className={`px-4 py-2 rounded-full text-xs font-bold transition-all border 
                  ${profile.dataTypes.includes(type) 
                    ? 'bg-brand-500/20 border-brand-500 text-brand-400' 
                    : 'bg-dark-900 border-slate-700 text-slate-500'}`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3 bg-slate-800/20 p-4 rounded-xl border border-slate-700/50">
          <input 
            type="checkbox" 
            checked={profile.financialLoss}
            onChange={(e) => setProfile({...profile, financialLoss: e.target.checked})}
            className="w-5 h-5 rounded border-slate-700 bg-dark-900 text-brand-500"
          />
          <span className="text-sm text-slate-300 font-medium">I have experienced financial loss due to a breach.</span>
        </div>

        <Button onClick={() => onSave(profile)} className="w-full py-4 mt-4">Generate Digital Twin</Button>
      </div>
    </div>
  );
};

export default UserProfile;
