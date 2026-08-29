import React from "react";
import { Package, Building, Tag, Calendar, PhoneCall, Globe, ListChecks } from "lucide-react";

export default function ExtractedDataPanel({ product }) {
  if (!product) return null;

  const renderValue = (val) => {
    if (val === null || val === undefined || val === "") {
      return <span className="text-slate-400 italic">Not detected</span>;
    }
    if (typeof val === "boolean") {
      return val ? "Yes (Verified)" : "No / Unspecified";
    }
    return <span className="font-semibold text-slate-800">{String(val)}</span>;
  };

  const sections = [
    {
      title: "Product Identification",
      icon: Package,
      items: [
        { label: "Product Name", value: product.product_name },
        { label: "Brand Name", value: product.brand_name },
        { label: "Generic Product Name", value: product.generic_name },
        { label: "Category", value: product.category },
        { label: "Package Type", value: product.package_type },
      ],
    },
    {
      title: "Manufacturer / Packer / Importer",
      icon: Building,
      items: [
        { label: "Role", value: product.manufacturer?.role },
        { label: "Name", value: product.manufacturer?.name },
        { label: "Full Physical Address", value: product.manufacturer?.address },
      ],
    },
    {
      title: "Net Quantity & Price Declarations",
      icon: Tag,
      items: [
        { label: "Quantity Value", value: product.quantity?.value },
        { label: "Quantity Unit", value: product.quantity?.unit },
        { label: "Quantity Label Raw Text", value: product.quantity?.raw_text },
        { label: "Maximum Retail Price (MRP)", value: product.mrp?.value ? `₹${product.mrp.value}` : null },
        { label: "Tax-Inclusive Stated", value: product.mrp?.inclusive_of_taxes },
        { label: "MRP Raw Label Text", value: product.mrp?.raw_text },
      ],
    },
    {
      title: "Manufacture & Expiry Dates",
      icon: Calendar,
      items: [
        { label: "Date Applicability Status", value: product.date_applicability },
        { label: "Manufacture Date", value: product.dates?.manufacture_date },
        { label: "Packing Date", value: product.dates?.packing_date },
        { label: "Best Before Period", value: product.dates?.best_before },
        { label: "Use By Date", value: product.dates?.use_by },
      ],
    },
    {
      title: "Consumer Care & Origin",
      icon: PhoneCall,
      items: [
        { label: "Import Status Classifier", value: product.import_status },
        { label: "Country of Origin", value: product.country_of_origin },
        { label: "Helpline Phone Number", value: product.consumer_care?.phone },
        { label: "Consumer Care Email", value: product.consumer_care?.email },
        { label: "Consumer Care Address", value: product.consumer_care?.address },
      ],
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 className="font-bold text-slate-900 text-base">Extracted Product Information</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Raw structured declarations extracted by AI vision from package label
          </p>
        </div>
        <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-bold rounded-lg border border-slate-200">
          Single Source of Truth
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sections.map((sec, idx) => {
          const Icon = sec.icon;
          return (
            <div key={idx} className="bg-slate-50/70 rounded-xl border border-slate-200/80 p-4 space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200/60 pb-2">
                <Icon className="w-4 h-4 text-blue-700" />
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">{sec.title}</h4>
              </div>
              <div className="space-y-2 text-xs">
                {sec.items.map((item, i) => (
                  <div key={i} className="flex items-start justify-between gap-4 py-1 border-b border-slate-100/60 last:border-0">
                    <span className="text-slate-500 font-medium shrink-0">{item.label}</span>
                    <div className="text-right truncate">{renderValue(item.value)}</div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Raw Evidence List */}
      {product.raw_evidence && product.raw_evidence.length > 0 && (
        <div className="bg-blue-50/40 rounded-xl border border-blue-100 p-4 space-y-2">
          <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wider flex items-center gap-1.5">
            <ListChecks className="w-4 h-4 text-blue-700" />
            <span>Preserved Raw Label Evidence Strings</span>
          </h4>
          <div className="flex flex-wrap gap-2 pt-1">
            {product.raw_evidence.map((text, index) => (
              <span
                key={index}
                className="px-2.5 py-1 bg-white text-blue-950 font-mono text-[11px] font-medium rounded-lg border border-blue-200 shadow-2xs"
              >
                "{text}"
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
