import React from "react";
import { CheckCircle2, XCircle, AlertTriangle, MinusCircle, ShieldCheck, ShieldAlert } from "lucide-react";

export default function StatusBadge({ status, size = "md", showIcon = true }) {
  const normalized = (status || "").toUpperCase();

  const configs = {
    PASS: {
      bg: "bg-emerald-50 text-emerald-700 border-emerald-200",
      icon: CheckCircle2,
      label: "PASS",
    },
    COMPLIANT: {
      bg: "bg-emerald-600 text-white border-emerald-700",
      icon: ShieldCheck,
      label: "COMPLIANT",
    },
    FAIL: {
      bg: "bg-rose-50 text-rose-700 border-rose-200",
      icon: XCircle,
      label: "FAIL",
    },
    NON_COMPLIANT: {
      bg: "bg-rose-600 text-white border-rose-700",
      icon: ShieldAlert,
      label: "NON-COMPLIANT",
    },
    REVIEW: {
      bg: "bg-amber-50 text-amber-700 border-amber-200",
      icon: AlertTriangle,
      label: "REVIEW",
    },
    NEEDS_REVIEW: {
      bg: "bg-amber-500 text-white border-amber-600",
      icon: AlertTriangle,
      label: "NEEDS REVIEW",
    },
    NA: {
      bg: "bg-slate-100 text-slate-600 border-slate-200",
      icon: MinusCircle,
      label: "N/A",
    },
  };

  const config = configs[normalized] || {
    bg: "bg-slate-100 text-slate-700 border-slate-200",
    icon: MinusCircle,
    label: normalized,
  };

  const IconComponent = config.icon;

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs font-semibold rounded-md border",
    md: "px-2.5 py-1 text-xs font-bold rounded-lg border tracking-wide",
    lg: "px-4 py-1.5 text-sm font-extrabold rounded-lg border shadow-sm tracking-wider uppercase",
  };

  return (
    <span className={`inline-flex items-center gap-1.5 ${config.bg} ${sizeClasses[size]}`}>
      {showIcon && <IconComponent className={size === "lg" ? "w-4 h-4" : "w-3.5 h-3.5"} />}
      <span>{config.label}</span>
    </span>
  );
}
