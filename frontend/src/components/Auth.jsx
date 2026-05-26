import { useState } from 'react';
import Button from './Button';

const Auth = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const API_BASE = "";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isLogin ? '/login' : '/register';
    const body = isLogin ? { username, password } : { username, password, email };

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed');

      if (isLogin) {
        onLogin(data.user);
      } else {
        alert('Registration successful! Please log in.');
        setIsLogin(true);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900 px-6">
      <div className="max-w-md w-full glass-panel p-10 rounded-[2.5rem] border border-slate-700/50 shadow-2xl relative overflow-hidden group">
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-brand-500/10 rounded-full blur-3xl group-hover:bg-brand-500/20 transition-all duration-700"></div>
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-all duration-700"></div>

        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center text-white font-black text-2xl mx-auto mb-6 shadow-xl shadow-brand-500/20">
            A
          </div>
          <h2 className="text-3xl font-black text-white tracking-tighter mb-2">
            {isLogin ? 'Welcome Back' : 'Join Intelligence'}
          </h2>
          <p className="text-slate-400 text-sm">
            {isLogin ? 'Access your private legal intelligence dashboard' : 'Create an account to track your legal claims'}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-xs font-bold text-center animate-shake">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-2 block">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-dark-900/50 border border-slate-700 rounded-2xl py-4 px-5 text-white outline-none focus:border-brand-500/50 transition-all placeholder:text-slate-600"
              placeholder="Enter your username"
              required
            />
          </div>

          {!isLogin && (
            <div className="animate-slide-down">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-2 block">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-dark-900/50 border border-slate-700 rounded-2xl py-4 px-5 text-white outline-none focus:border-brand-500/50 transition-all placeholder:text-slate-600"
                placeholder="Enter your email"
                required
              />
            </div>
          )}

          <div>
            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1 mb-2 block">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-dark-900/50 border border-slate-700 rounded-2xl py-4 px-5 text-white outline-none focus:border-brand-500/50 transition-all placeholder:text-slate-600"
              placeholder="••••••••"
              required
            />
          </div>

          <Button
            type="submit"
            isLoading={loading}
            className="w-full py-5 bg-brand-500 hover:bg-brand-400 shadow-xl shadow-brand-500/20 text-sm font-black uppercase tracking-widest rounded-2xl mt-4"
          >
            {isLogin ? 'Login to Dashboard' : 'Create Secure Account'}
          </Button>
        </form>

        <div className="mt-8 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-xs text-slate-500 hover:text-brand-400 transition-colors font-medium"
          >
            {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Auth;
