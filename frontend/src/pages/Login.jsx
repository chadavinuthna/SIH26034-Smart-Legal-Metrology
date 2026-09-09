import React, { useState } from "react";
import { Scale, Lock, User, Sparkles, ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import { loginUser } from "../services/auth";

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState("inspector");
  const [password, setPassword] = useState("Insp#LM8842$Secure2026!");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const user = await loginUser(username, password);
      onLoginSuccess(user);
    } catch (err) {
      setError(err.message || "Invalid username or password");
    } finally {
      setIsLoading(false);
    }
  };

  const handleInstantDemo = async () => {
    setUsername("inspector");
    setPassword("Insp#LM8842$Secure2026!");
    setError(null);
    setIsLoading(true);

    try {
      const user = await loginUser("inspector", "Insp#LM8842$Secure2026!");
      onLoginSuccess(user);
    } catch (err) {
      setError(err.message || "Failed to launch demo session");
    } finally {
      setIsLoading(false);
    }
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
            <h2 className="text-base font-bold text-white">Portal Authentication</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Sign in with your Inspector or Manufacturer credentials
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-950/60 border border-red-500/50 rounded-xl text-red-300 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Username / Officer ID
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-900 text-white rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none text-xs font-medium"
                  placeholder="e.g. inspector or manufacturer"
                  disabled={isLoading}
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
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold text-xs rounded-xl shadow-lg shadow-blue-900/50 transition-all flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In to Compliance Portal</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials Guide */}
          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-700/50 space-y-1.5 text-[11px] text-slate-400">
            <span className="font-semibold text-slate-300 block uppercase tracking-wider text-[10px]">
              Available Demo Credentials:
            </span>
            <div className="flex justify-between items-center text-slate-300">
              <span>Inspector: <code className="text-blue-400">inspector</code> / <code className="text-blue-400">Insp#LM8842$Secure2026!</code></span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span>Manufacturer: <code className="text-amber-400">manufacturer</code> / <code className="text-amber-400">Mfr#QA7135$Secure2026!</code></span>
            </div>
          </div>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-slate-700 w-full"></div>
            <span className="bg-slate-800 px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider shrink-0">
              OR FOR QUICK EVALUATION
            </span>
          </div>

          {/* Instant Demo Login Button */}
          <button
            onClick={handleInstantDemo}
            disabled={isLoading}
            className="w-full py-3 bg-amber-500/10 hover:bg-amber-500/20 disabled:opacity-50 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 group"
          >
            <Sparkles className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
            <span>Launch Instant Demo (Inspector)</span>
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

