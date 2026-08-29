import React, { useState } from "react";
import { Scale, Lock, User, Sparkles, ShieldCheck, ArrowRight } from "lucide-react";

export default function Login({ onLoginSuccess }) {
  const [officerId, setOfficerId] = useState("LM-OFF-8842");
  const [password, setPassword] = useState("••••••••");

  const handleSubmit = (e) => {
    e.preventDefault();
    onLoginSuccess();
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Graphic Accents */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl"></div>

      <div className="max-w-md w-full relative z-10 space-y-6">
        {/* Department Badge Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex p-3.5 bg-blue-900/80 text-amber-400 rounded-2xl border border-blue-700/60 shadow-xl">
            <Scale className="w-10 h-10" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">Legal Metrology Portal</h1>
            <p className="text-xs text-slate-400 font-medium mt-1">
              Government of India — Package Compliance System (SIH26034)
            </p>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-slate-800/90 rounded-2xl border border-slate-700/80 p-8 shadow-2xl space-y-6 backdrop-blur-md">
          <div className="border-b border-slate-700/80 pb-4">
            <h2 className="text-base font-bold text-white">Inspector Authentication</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Enter official credentials or launch instant demo session
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Officer ID / Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  value={officerId}
                  onChange={(e) => setOfficerId(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-900 text-white rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none text-xs font-medium"
                  placeholder="e.g. LM-OFF-8842"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Security Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-900 text-white rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none text-xs font-medium"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-blue-900/50 transition-all flex items-center justify-center gap-2"
            >
              <span>Sign In to Compliance Portal</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-slate-700 w-full"></div>
            <span className="bg-slate-800 px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider shrink-0">
              OR FOR EVALUATION
            </span>
          </div>

          {/* Instant Demo Login Button */}
          <button
            onClick={onLoginSuccess}
            className="w-full py-3 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 group"
          >
            <Sparkles className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
            <span>Launch Instant Demo Mode</span>
          </button>
        </div>

        {/* Disclaimer Note */}
        <p className="text-[11px] text-center text-slate-500">
          SIH26034 Prototype V1 • Smart Legal Metrology Package Compliance System
        </p>
      </div>
    </div>
  );
}
