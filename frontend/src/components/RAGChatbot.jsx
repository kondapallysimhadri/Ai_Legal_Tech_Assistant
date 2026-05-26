import React, { useState, useRef, useEffect } from 'react';
import Button from './Button';

const RAGChatbot = () => {
  const [messages, setMessages] = useState([
    { 
      role: 'ai', 
      content: 'Hello! I am your AI Legal Assistant. I can search our legal database to answer your questions about data breaches, eligibility, and past cases. How can I help you today?',
      sources: ["Legal Intel DB"]
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(`session_${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question: userMessage,
          session_id: sessionId,
          history: messages.slice(-5).map(m => ({ role: m.role === 'ai' ? 'assistant' : 'user', content: m.content }))
        })
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with RAG engine.');
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: data.answer,
        sources: data.sources || [],
        confidence: data.confidence
      }]);

    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: 'I encountered an error connecting to my knowledge base. Please ensure the API is running.',
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[650px] glass-panel rounded-[2rem] border border-slate-700/30 shadow-2xl overflow-hidden animate-fade-in bg-dark-900/60 backdrop-blur-xl">
      {/* Chat Header */}
      <div className="bg-slate-800/40 p-5 border-b border-slate-700/30 flex justify-between items-center backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center text-2xl shadow-lg shadow-brand-500/20">
              ⚖️
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-2 border-dark-900 rounded-full animate-pulse"></div>
          </div>
          <div>
            <h2 className="text-white font-black text-base tracking-tight">AI Legal Assistant</h2>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-emerald-400 font-black uppercase tracking-widest">System Online</span>
              <span className="text-[10px] text-slate-500 font-mono">• RAG ENGINE ACTIVE</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-slide-up`}>
            <div className={`w-10 h-10 rounded-2xl shrink-0 flex items-center justify-center text-lg shadow-inner ${
              msg.role === 'user' ? 'bg-slate-800' : 'bg-brand-500/20 text-brand-400 border border-brand-500/20'
            }`}>
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            
            <div className={`flex flex-col max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div 
                className={`p-4 rounded-2xl text-sm leading-relaxed shadow-lg ${
                  msg.role === 'user' 
                    ? 'bg-brand-500 text-white rounded-tr-none' 
                    : msg.isError 
                      ? 'bg-rose-500/10 text-rose-200 border border-rose-500/20 rounded-tl-none'
                      : 'bg-dark-800/80 text-slate-200 border border-slate-700/50 rounded-tl-none'
                }`}
              >
                {msg.content}
              </div>
              
              {msg.role === 'ai' && msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {msg.sources.map((source, i) => (
                    <span key={i} className="text-[9px] bg-dark-900/80 text-brand-400/80 px-2.5 py-1 rounded-full border border-brand-500/10 font-black uppercase tracking-widest">
                      SOURCE: {source}
                    </span>
                  ))}
                  {msg.confidence && (
                    <span className="text-[9px] bg-slate-800/50 text-slate-500 px-2.5 py-1 rounded-full border border-slate-700/30 font-black uppercase tracking-widest">
                      CONF: {msg.confidence}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-4 animate-pulse">
            <div className="w-10 h-10 rounded-2xl bg-brand-500/10 flex items-center justify-center text-lg border border-brand-500/10">🤖</div>
            <div className="bg-dark-800/80 p-5 rounded-2xl rounded-tl-none border border-slate-700/50 flex items-center gap-1.5">
               <div className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
               <div className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
               <div className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-slate-900/40 border-t border-slate-700/20 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="relative group">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your legal situation or ask about a case..."
            disabled={isLoading}
            className="w-full bg-dark-800 border border-slate-700/50 rounded-2xl py-4 pl-6 pr-32 text-sm text-white focus:ring-2 focus:ring-brand-500/30 outline-none transition-all placeholder:text-slate-500 group-hover:border-slate-600 disabled:opacity-50"
          />
          <div className="absolute right-2 top-2 bottom-2">
            <Button type="submit" isLoading={isLoading} className="h-full px-8 rounded-xl bg-brand-500 hover:bg-brand-400 transition-all font-black text-xs uppercase tracking-widest">
              Send Query
            </Button>
          </div>
        </form>
        <div className="flex items-center justify-center gap-2 mt-4">
          <div className="w-1 h-1 rounded-full bg-slate-700"></div>
          <p className="text-[9px] text-slate-500 font-bold uppercase tracking-[0.2em]">
            Production-Grade AI Guidance System
          </p>
          <div className="w-1 h-1 rounded-full bg-slate-700"></div>
        </div>
      </div>
    </div>
  );
};

export default RAGChatbot;
