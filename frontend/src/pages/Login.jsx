import React, { useState } from "react";
import {
  Shield,
  Lock,
  User,
  ArrowRight,
  Building2,
  BadgeCheck,
  AlertCircle,
} from "lucide-react";
import { loginUser } from "../services/api";

export default function Login({ onLogin }) {
  const [role, setRole] = useState("INSPECTOR");
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const user = await loginUser(userId.trim(), password);

      onLogin({
        user_id: user.user_id,
        officer_id: user.user_id,
        name: user.name,
        role: user.role,
        department: user.department,
        status: user.status,
      });
    } catch (err) {
      setError(err.message || "Invalid user ID or password.");
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCredentials = () => {
    if (role === "INSPECTOR") {
      setUserId("LM-INSP-4092");
      setPassword("inspector123");
    } else {
      setUserId("LM-MFG-1001");
      setPassword("manufacturer123");
    }
    setError("");
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
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
          Smart Legal Metrology offline compliance and inspection system.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 sm:px-10 rounded-2xl shadow-xl border border-slate-200">

          {/* Role Selection */}
          <div className="mb-6">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
              Login As
            </label>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => {
                  setRole("INSPECTOR");
                  setError("");
                  setUserId("");
                  setPassword("");
                }}
                className={`flex items-center justify-center gap-2 py-3 rounded-xl border text-sm font-bold transition ${
                  role === "INSPECTOR"
                    ? "bg-[#0F2942] text-white border-[#0F2942]"
                    : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                }`}
              >
                <BadgeCheck size={18} />
                Inspector
              </button>

              <button
                type="button"
                onClick={() => {
                  setRole("MANUFACTURER");
                  setError("");
                  setUserId("");
                  setPassword("");
                }}
                className={`flex items-center justify-center gap-2 py-3 rounded-xl border text-sm font-bold transition ${
                  role === "MANUFACTURER"
                    ? "bg-[#0F2942] text-white border-[#0F2942]"
                    : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                }`}
              >
                <Building2 size={18} />
                Manufacturer
              </button>
            </div>
          </div>

          <form className="space-y-4" onSubmit={handleSignIn}>

            {/* User ID */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                {role === "INSPECTOR"
                  ? "Inspector ID"
                  : "Manufacturer ID"}
              </label>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  {role === "INSPECTOR" ? (
                    <User size={16} />
                  ) : (
                    <Building2 size={16} />
                  )}
                </div>

                <input
                  type="text"
                  required
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  placeholder={
                    role === "INSPECTOR"
                      ? "e.g. LM-INSP-4092"
                      : "e.g. LM-MFG-1001"
                  }
                  className="block w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 font-mono text-slate-900 bg-slate-50/50"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Password
              </label>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock size={16} />
                </div>

                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  className="block w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 text-slate-900 bg-slate-50/50"
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Login */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[#0F2942] hover:bg-[#18395B] shadow-md transition disabled:opacity-60"
              >
                <span>
                  {loading
                    ? "Signing In..."
                    : `Sign In as ${
                        role === "INSPECTOR"
                          ? "Inspector"
                          : "Manufacturer"
                      }`}
                </span>
                {!loading && <ArrowRight size={14} />}
              </button>
            </div>
          </form>

          {/* Local Demo Credentials */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>

            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-3 text-slate-400 font-semibold">
                Local Demo Account
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={fillDemoCredentials}
            className="w-full py-2.5 px-4 rounded-xl text-xs font-bold text-amber-900 bg-amber-50 border border-amber-300 hover:bg-amber-100 transition"
          >
            Fill {role === "INSPECTOR" ? "Inspector" : "Manufacturer"} Demo
            Credentials
          </button>

          <p className="text-[11px] text-center text-slate-500 mt-2">
            Authentication is performed locally using the SQLite database.
          </p>
        </div>

        <div className="mt-6 text-center text-[11px] text-slate-400 space-y-1">
          <p className="font-semibold text-slate-500">
            Smart Legal Metrology Package Compliance System
          </p>
          <p>
            Offline prototype for package declaration inspection and
            compliance evaluation.
          </p>
        </div>
      </div>
    </div>
  );
}