import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, MinusCircle } from 'lucide-react';

export default function StatusBadge({ status, size = 'md', showIcon = true, className = '' }) {
  const norm = (status || '').toUpperCase();

  const configs = {
    PASS: {
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      icon: CheckCircle2,
      label: 'PASS',
      iconColor: 'text-emerald-600',
    },
    COMPLIANT: {
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      icon: CheckCircle2,
      label: 'COMPLIANT',
      iconColor: 'text-emerald-600',
    },
    FAIL: {
      bg: 'bg-rose-50 text-rose-800 border-rose-200',
      icon: XCircle,
      label: 'FAIL',
      iconColor: 'text-rose-600',
    },
    NON_COMPLIANT: {
      bg: 'bg-rose-50 text-rose-800 border-rose-200',
      icon: XCircle,
      label: 'NON-COMPLIANT',
      iconColor: 'text-rose-600',
    },
    REVIEW: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      icon: AlertTriangle,
      label: 'REVIEW',
      iconColor: 'text-amber-600',
    },
    NEEDS_REVIEW: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      icon: AlertTriangle,
      label: 'NEEDS REVIEW',
      iconColor: 'text-amber-600',
    },
    NA: {
      bg: 'bg-slate-100 text-slate-700 border-slate-200',
      icon: MinusCircle,
      label: 'N/A',
      iconColor: 'text-slate-500',
    },
  };

  const current = configs[norm] || configs.REVIEW;
  const IconComponent = current.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 font-medium',
    md: 'text-xs px-2.5 py-1 font-semibold tracking-wide',
    lg: 'text-sm px-3.5 py-1.5 font-bold tracking-wider',
  };

  const iconSizes = {
    sm: 12,
    md: 14,
    lg: 16,
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${current.bg} ${sizeClasses[size]} ${className}`}
    >
      {showIcon && <IconComponent size={iconSizes[size]} className={current.iconColor} />}
      <span>{current.label}</span>
    </span>
  );
}
