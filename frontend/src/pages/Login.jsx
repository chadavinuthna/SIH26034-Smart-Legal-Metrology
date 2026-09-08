import React, { useState } from 'react';
import { Shield, Lock, User, ArrowRight, Sparkles, CheckCircle2, FileCheck2 } from 'lucide-react';

export default function Login({ onLogin }) {
  const [officerId, setOfficerId] = useState('LM-INSP-4092');
  const [password, setPassword] = useState('••••••••');
  const [department, setDepartment] = useState('Legal Metrology Enforcement Wing');

  const handleSignIn = (e) => {
    e.preventDefault();
    onLogin({
      officer_id: officerId.trim() || 'LM-INSP-4092',
      name: 'Inspector A. Sharma',
      department: department,
    });
  };

  const handleDemoLogin = () => {
    onLogin({
      officer_id: 'LM-DEMO-2026',
      name: 'Demo Inspection Officer',
      department: 'Legal Metrology Department (Demo Session)',
      is_demo: true,
    });
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Decorative Government Header Accent */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#0F2942] border-2 border-amber-400/40 text-amber-400 shadow-xl mb-4">
          <Shield size={34} className="stroke-[2.2]" />
        </div>
        <div className="text-xs font-black tracking-widest text-amber-700 uppercase">
          Department of Consumer Affairs • Legal Metrology
        </div>
        <h2 className="mt-1 text-2xl font-extrabold text-[#0F2942] tracking-tight">
          Package Compliance Portal
        </h2>
        <p className="mt-1.5 text-xs text-slate-500 max-w-sm mx-auto">
          Smart India Hackathon Prototype (SIH26034) for automated label declaration inspection.
        </p>
      </div>

      {/* Main Login Card */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 sm:px-10 rounded-2xl shadow-xl border border-slate-200">
          <form className="space-y-4" onSubmit={handleSignIn}>
            {/* Officer ID */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Officer / Inspector ID
              </label>
              <div className="relative rounded-lg shadow-2xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <User size={16} />
                </div>
                <input
                  type="text"
                  required
                  value={officerId}
                  onChange={(e) => setOfficerId(e.target.value)}
                  placeholder="e.g. LM-INSP-4092"
                  className="block w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 font-mono text-slate-900 bg-slate-50/50"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Security Passcode
              </label>
              <div className="relative rounded-lg shadow-2xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock size={16} />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="block w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 text-slate-900 bg-slate-50/50"
                />
              </div>
            </div>

            {/* Department */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Designated Wing
              </label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="block w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 text-slate-800 bg-white"
              >
                <option>Legal Metrology Enforcement Wing</option>
                <option>Packaged Commodities Inspection Directorate</option>
                <option>Consumer Protection & Standards Cell</option>
              </select>
            </div>

            {/* Sign In Button */}
            <div className="pt-2">
              <button
                type="submit"
                className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[#0F2942] hover:bg-[#18395B] shadow-md hover:shadow-lg transition-all duration-150 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-blue-600"
              >
                <span>Sign In as Enforcement Officer</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-3 text-slate-400 font-semibold">or instant access</span>
            </div>
          </div>

          {/* Demo Login Button */}
          <div>
            <button
              type="button"
              onClick={handleDemoLogin}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-amber-900 bg-amber-50 border border-amber-300 hover:bg-amber-100 hover:border-amber-400 shadow-2xs transition-all duration-150"
            >
              <Sparkles size={15} className="text-amber-600" />
              <span>Demo Login (Instant Evaluation)</span>
            </button>
            <p className="text-[11px] text-center text-slate-500 mt-2">
              1-click access with pre-loaded mock data and rule engine test scenarios.
            </p>
          </div>
        </div>

        {/* Legal Disclaimer Footer */}
        <div className="mt-6 text-center text-[11px] text-slate-400 space-y-1">
          <p className="font-semibold text-slate-500">Smart Legal Metrology Package Compliance System</p>
          <p>
            Prototype screening result. Final regulatory determination should be verified by an authorized Legal Metrology officer and applicable current regulations.
          </p>
        </div>
      </div>
    </div>
  );
}
