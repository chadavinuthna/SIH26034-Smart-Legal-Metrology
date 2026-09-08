/**
 * Demo product samples with pre-configured mock labels and SVG mock images.
 */

// SVG Image for Compliant Biscuit Pack
const COMPLIANT_BISCUIT_SVG = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <rect width="600" height="400" fill="%230F2942" rx="12"/>
  <rect x="20" y="20" width="560" height="360" fill="%23FFFFFF" rx="8" stroke="%23D97706" stroke-width="4"/>
  <rect x="30" y="30" width="540" height="60" fill="%231E3A8A" rx="4"/>
  <text x="50" y="70" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="%23FFFFFF">ROYAL TREATS</text>
  <text x="360" y="68" font-family="Arial, sans-serif" font-size="16" fill="%23FCD34D">★ PREMIUM QUALITY ★</text>
  
  <text x="50" y="125" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="%230F172A">Butter Delight Biscuits</text>
  <text x="50" y="150" font-family="Arial, sans-serif" font-size="14" fill="%23475569">Generic Name: Biscuits | 100% Vegetarian</text>
  
  <line x1="50" y1="165" x2="550" y2="165" stroke="%23E2E8F0" stroke-width="2"/>
  
  <!-- Left Column: Declarations -->
  <text x="50" y="195" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="%231E293B">Net Quantity: <tspan font-weight="normal">200 g (7.05 oz)</tspan></text>
  <text x="50" y="220" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="%231E293B">MRP: <tspan font-weight="normal">Rs. 80.00 (Inclusive of all taxes)</tspan></text>
  <text x="50" y="245" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="%231E293B">Mfg Date: <tspan font-weight="normal">07/2026</tspan> | Best Before: <tspan font-weight="normal">6 months from pkd</tspan></text>
  <text x="50" y="270" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="%231E293B">Country of Origin: <tspan font-weight="normal">India</tspan></text>
  
  <!-- Right Column: Manufacturer & Care -->
  <text x="50" y="305" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="%230F172A">Manufactured by:</text>
  <text x="50" y="325" font-family="Arial, sans-serif" font-size="11" fill="%23475569">ABC Foods &amp; Confectioneries Pvt Ltd, Plot 45, Industrial Park, Nacharam, Hyderabad, TS - 500076</text>
  
  <text x="50" y="355" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="%230F172A">Consumer Care: <tspan font-weight="normal">Toll-Free 1800-123-4567 | care@abcfoods.example.in</tspan></text>
</svg>`;

// SVG Image for Non-Compliant Snack Pack
const NON_COMPLIANT_SNACK_SVG = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <rect width="600" height="400" fill="%237F1D1D" rx="12"/>
  <rect x="20" y="20" width="560" height="360" fill="%23FFF1F2" rx="8" stroke="%23EF4444" stroke-width="4"/>
  
  <rect x="30" y="30" width="540" height="60" fill="%23991B1B" rx="4"/>
  <text x="50" y="70" font-family="Arial, sans-serif" font-size="26" font-weight="bold" fill="%23FFFFFF">CRUNCHY BITES</text>
  <text x="370" y="68" font-family="Arial, sans-serif" font-size="14" fill="%23FECACA">TASTY SNACK</text>
  
  <text x="50" y="130" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="%23991B1B">Masala Flavoured Bites</text>
  <text x="50" y="155" font-family="Arial, sans-serif" font-size="13" fill="%239CA3AF">[MISSING GENERIC COMMODITY NAME]</text>
  
  <line x1="50" y1="170" x2="550" y2="170" stroke="%23FECACA" stroke-width="2"/>
  
  <text x="50" y="205" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="%231F2937">Net Qty: <tspan font-weight="normal">500g</tspan></text>
  <text x="50" y="235" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="%231F2937">Price: <tspan font-weight="normal">Rs. 120 (Taxes not specified)</tspan></text>
  
  <!-- Missing Elements Callout -->
  <rect x="50" y="260" width="500" height="90" fill="%23FEE2E2" rx="6" stroke="%23F87171" stroke-dasharray="4"/>
  <text x="65" y="285" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="%23B91C1C">DEFECTS PRESENT (FOR COMPLIANCE DEMONSTRATION):</text>
  <text x="65" y="305" font-family="Arial, sans-serif" font-size="11" fill="%23991B1B">• Missing complete Manufacturer Address (Only "XYZ Snack Hub")</text>
  <text x="65" y="325" font-family="Arial, sans-serif" font-size="11" fill="%23991B1B">• Missing Date of Manufacture / Packing Date and Best Before Period</text>
  <text x="65" y="342" font-family="Arial, sans-serif" font-size="11" fill="%23991B1B">• Missing Mandatory Consumer Care Helpline / Grievance Redressal</text>
</svg>`;

export const DEMO_PRODUCTS = [
  {
    id: "sample_compliant",
    name: "Sample Biscuits (Compliant Package)",
    product_name: "Royal Butter Delight Biscuits",
    brand_name: "Royal Treats",
    category: "Food",
    expected_status: "COMPLIANT",
    score_estimate: "100%",
    image_url: COMPLIANT_BISCUIT_SVG,
    description: "Fully compliant packaged commodity adhering to all 9 Legal Metrology mandatory declarations.",
    highlights: [
      "Full manufacturer address with PIN code",
      "Standard SI unit (200 g)",
      "MRP declared with explicit 'Inclusive of all taxes'",
      "Clear Mfg Date & Best Before period",
      "Consumer care helpline & email provided"
    ]
  },
  {
    id: "sample_non_compliant",
    name: "Sample Snack (Non-Compliant Package)",
    product_name: "Crunchy Masala Bites",
    brand_name: "Crunchy Bites",
    category: "Food",
    expected_status: "NON_COMPLIANT",
    score_estimate: "39%",
    image_url: NON_COMPLIANT_SNACK_SVG,
    description: "Deliberately defective sample designed to demonstrate non-compliance detection and violation flags.",
    highlights: [
      "Missing complete manufacturer address",
      "Missing generic commodity declaration",
      "Missing date of manufacture & best-before",
      "Missing consumer care helpline & email",
      "Unspecified tax inclusivity clause"
    ]
  }
];
