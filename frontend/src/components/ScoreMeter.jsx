import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

export default function ScoreMeter({ score = 0, status = 'COMPLIANT' }) {
  const norm = (status || '').toUpperCase();
  
  // Color configuration based on score and status
  let strokeColor = '#10B981'; // Emerald
  let bgFill = 'bg-emerald-50';
  let textColor = 'text-emerald-700';
  let Icon = ShieldCheck;

  if (norm.includes('NON') || norm.includes('FAIL') || score < 50) {
    strokeColor = '#EF4444'; // Rose
    bgFill = 'bg-rose-50';
    textColor = 'text-rose-700';
    Icon = ShieldX;
  } else if (norm.includes('REVIEW') || score < 85) {
    strokeColor = '#F59E0B'; // Amber
    bgFill = 'bg-amber-50';
    textColor = 'text-amber-700';
    Icon = ShieldAlert;
  }

  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex items-center gap-5 p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
      {/* Circular Progress Gauge */}
      <div className="relative flex items-center justify-center w-24 h-24">
        <svg className="w-24 h-24 -rotate-90 transform" viewBox="0 0 96 96">
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke="#E2E8F0"
            strokeWidth="8"
            fill="transparent"
          />
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke={strokeColor}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className={`text-2xl font-black ${textColor}`}>{score}%</span>
        </div>
      </div>

      {/* Label and Context */}
      <div className="flex-1">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
          <Icon size={14} className={textColor} />
          <span>Prototype Compliance Score</span>
        </div>
        <div className="text-base font-bold text-slate-800 mt-0.5">
          {score >= 85 ? 'High Compliance Level' : score >= 50 ? 'Moderate Compliance / Needs Review' : 'Critical Violations Detected'}
        </div>
        <p className="text-xs text-slate-500 mt-1 leading-relaxed">
          Weighted evaluation based on mandatory Legal Metrology declaration rules.
        </p>
      </div>
    </div>
  );
}
