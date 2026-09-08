import React from 'react';
import { Check, X, HelpCircle, Package, Building2, Calendar, Phone, DollarSign, Globe, Scale } from 'lucide-react';

export default function ExtractedInfoTable({ product }) {
  if (!product) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        No extracted product information available.
      </div>
    );
  }

  const renderVal = (val, prefix = '') => {
    if (val === null || val === undefined || val === '') {
      return <span className="text-slate-400 italic font-sans text-xs">Not detected</span>;
    }
    return <span className="font-mono text-slate-900 font-medium text-xs sm:text-sm">{prefix}{String(val)}</span>;
  };

  const sections = [
    {
      title: 'Identity & Classification',
      icon: Package,
      items: [
        { label: 'Product Name', value: product.product_name },
        { label: 'Brand Name', value: product.brand_name },
        { label: 'Generic Commodity Name', value: product.generic_name },
        { label: 'Product Category', value: product.category },
        { label: 'Package Type', value: product.package_type || 'Normal' },
      ],
    },
    {
      title: 'Manufacturer / Packer Declarations',
      icon: Building2,
      items: [
        { label: 'Entity Role', value: product.manufacturer?.role },
        { label: 'Entity / Company Name', value: product.manufacturer?.name },
        { label: 'Complete Operational Address', value: product.manufacturer?.address },
        { label: 'Country of Origin', value: product.country_of_origin },
      ],
    },
    {
      title: 'Measurement & Pricing',
      icon: Scale,
      items: [
        { label: 'Net Quantity (Parsed)', value: product.quantity?.value ? `${product.quantity.value} ${product.quantity.unit || ''}` : null },
        { label: 'Quantity Raw Snippet', value: product.quantity?.raw_text },
        { label: 'Maximum Retail Price (MRP)', value: product.mrp?.value ? `₹${product.mrp.value}` : null },
        { 
          label: 'Tax-Inclusive Status', 
          value: product.mrp?.inclusive_of_taxes === true ? 'Inclusive of all taxes' : product.mrp?.inclusive_of_taxes === false ? 'Not declared inclusive' : null 
        },
        { label: 'MRP Raw Snippet', value: product.mrp?.raw_text },
      ],
    },
    {
      title: 'Timeline & Validity',
      icon: Calendar,
      items: [
        { label: 'Date of Manufacture', value: product.dates?.manufacture_date },
        { label: 'Date of Packing', value: product.dates?.packing_date },
        { label: 'Best Before Period', value: product.dates?.best_before },
        { label: 'Use By / Expiry Date', value: product.dates?.use_by },
      ],
    },
    {
      title: 'Consumer Grievance Redressal',
      icon: Phone,
      items: [
        { label: 'Consumer Care Phone', value: product.consumer_care?.phone },
        { label: 'Consumer Care Email', value: product.consumer_care?.email },
        { label: 'Redressal Postal Address / Web', value: product.consumer_care?.address },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      {sections.map((sec, idx) => {
        const Icon = sec.icon;
        return (
          <div key={idx} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
            <div className="flex items-center gap-2 px-4 py-3 bg-slate-50 border-b border-slate-200">
              <Icon size={16} className="text-blue-900" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                {sec.title}
              </h4>
            </div>

            <div className="divide-y divide-slate-100">
              {sec.items.map((item, iIdx) => (
                <div key={iIdx} className="grid grid-cols-1 sm:grid-cols-3 p-3.5 hover:bg-slate-50/50 transition-colors">
                  <div className="text-xs font-semibold text-slate-600 sm:col-span-1">
                    {item.label}
                  </div>
                  <div className="sm:col-span-2 mt-1 sm:mt-0">
                    {renderVal(item.value)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
