import { saveInspectionToHistory } from "./storage";

const API_BASE_URL = "/api/inspection";

export async function analyzePackageImage({ file, category, demoSample }) {
  const formData = new FormData();
  if (file) {
    formData.append("image", file);
  }
  if (category) {
    formData.append("category", category);
  }
  if (demoSample) {
    formData.append("demo_sample", demoSample);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || "Inspection analysis request failed");
    }

    const data = await response.json();
    saveInspectionToHistory(data);
    return data;
  } catch (error) {
    console.warn("Backend API request error, fallback to mock demo processing:", error);
    return simulateDemoInspection(demoSample || "compliant", category);
  }
}

export async function fetchInspectionHistory() {
  try {
    const response = await fetch(`${API_BASE_URL}/history`);
    if (response.ok) {
      return await response.json();
    }
  } catch (e) {
    console.warn("Using local storage history fallback:", e);
  }
  return null;
}

export async function fetchInspectionById(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/${id}`);
    if (response.ok) {
      return await response.json();
    }
  } catch (e) {
    console.warn("Fetch by id error:", e);
  }
  return null;
}

function simulateDemoInspection(sampleType = "compliant", categoryHint = "Food") {
  const isCompliant = sampleType === "compliant";
  const now = new Date();
  const timestamp = now.toISOString().replace("T", " ").substring(0, 19);
  const inspection_id = `LM-${now.getFullYear()}-${Math.floor(10000 + Math.random() * 90000)}`;

  let product, checks, overall_status, score, summary;

  if (isCompliant) {
    product = {
      product_name: "Golden Harvest Crunchy Butter Biscuits",
      brand_name: "Golden Harvest",
      generic_name: "Biscuits",
      category: categoryHint || "Food",
      manufacturer: {
        role: "Manufacturer",
        name: "ABC Foods Pvt Ltd",
        address: "Plot No. 42, Industrial Area, Uppal, Hyderabad, Telangana - 500039",
      },
      quantity: {
        value: "200",
        unit: "g",
        raw_text: "NET QUANTITY: 200 g",
      },
      mrp: {
        value: "80",
        currency: "INR",
        inclusive_of_taxes: true,
        raw_text: "M.R.P. ₹ 80.00 (Inclusive of all taxes)",
      },
      dates: {
        manufacture_date: "07/2026",
        packing_date: "07/2026",
        best_before: "6 Months from Manufacture",
        use_by: null,
      },
      consumer_care: {
        phone: "1800-123-4567",
        email: "care@abcfoods.com",
        address: "Consumer Care Cell, ABC Foods Pvt Ltd, Uppal, Hyderabad",
      },
      country_of_origin: "India",
      import_status: "DOMESTIC",
      is_imported: false,
      date_applicability: "APPLICABLE",
      package_type: "normal",
      raw_evidence: [
        "Golden Harvest Butter Biscuits",
        "Mfd by: ABC Foods Pvt Ltd, Uppal, Hyderabad",
        "NET QUANTITY: 200 g",
        "M.R.P. ₹ 80.00 (Inclusive of all taxes)",
        "Mfg Date: 07/2026",
        "Best Before 6 Months from Manufacture",
        "Customer Care: 1800-123-4567 | care@abcfoods.com",
        "Made in India",
      ],
    };

    checks = [
      {
        rule_id: "LM-001",
        rule_name: "Manufacturer / Packer / Importer Details",
        field: "manufacturer",
        status: "PASS",
        detected_value: "ABC Foods Pvt Ltd, Uppal, Hyderabad",
        evidence: "Manufacturer: ABC Foods Pvt Ltd, Address: Uppal, Hyderabad - 500039",
        reason: "Both manufacturer name and physical address were verified on the label.",
        recommendation: null,
      },
      {
        rule_id: "LM-002",
        rule_name: "Country of Origin",
        field: "country_of_origin",
        status: "NA",
        detected_value: "India (Domestic)",
        evidence: "Domestic product indicator / Country: India",
        reason: "Country of origin rule is Not Applicable for domestic (Indian) manufactured products unless required.",
        recommendation: null,
      },
      {
        rule_id: "LM-003",
        rule_name: "Generic Product Name",
        field: "generic_name",
        status: "PASS",
        detected_value: "Biscuits",
        evidence: "Generic Name: Biscuits (Brand: Golden Harvest)",
        reason: "Generic/common name of commodity ('Biscuits') is clearly stated.",
        recommendation: null,
      },
      {
        rule_id: "LM-004",
        rule_name: "Net Quantity",
        field: "quantity",
        status: "PASS",
        detected_value: "200 g",
        evidence: "NET QUANTITY: 200 g",
        reason: "Net quantity ('200 g') declared with valid standard units.",
        recommendation: null,
      },
      {
        rule_id: "LM-005",
        rule_name: "Manufacture / Packing Date",
        field: "dates",
        status: "PASS",
        detected_value: "Manufacture Date: 07/2026",
        evidence: "Manufacture Date: 07/2026",
        reason: "Manufacture Date declaration ('07/2026') is present on package label.",
        recommendation: null,
      },
      {
        rule_id: "LM-006",
        rule_name: "Best Before / Use By",
        field: "dates",
        status: "PASS",
        detected_value: "Best Before: 6 Months from Manufacture",
        evidence: "Best Before: 6 Months from Manufacture",
        reason: "Expiry / Best Before declaration ('6 Months from Manufacture') is present.",
        recommendation: null,
      },
      {
        rule_id: "LM-007",
        rule_name: "Maximum Retail Price (MRP)",
        field: "mrp",
        status: "PASS",
        detected_value: "₹80",
        evidence: "M.R.P. ₹ 80.00 (Inclusive of all taxes)",
        reason: "Maximum Retail Price ('₹80') detected.",
        recommendation: null,
      },
      {
        rule_id: "LM-008",
        rule_name: "MRP Tax-Inclusive Indication",
        field: "mrp",
        status: "PASS",
        detected_value: "Tax Inclusive Verified",
        evidence: "M.R.P. ₹ 80.00 (Inclusive of all taxes)",
        reason: "Evidence of tax-inclusive wording ('Inclusive of all taxes' or equivalent) was detected.",
        recommendation: null,
      },
      {
        rule_id: "LM-009",
        rule_name: "Consumer Care Details",
        field: "consumer_care",
        status: "PASS",
        detected_value: "Tel: 1800-123-4567; Email: care@abcfoods.com",
        evidence: "Tel: 1800-123-4567, Email: care@abcfoods.com",
        reason: "At least one consumer care contact (phone/email/address) is declared on the label.",
        recommendation: null,
      },
    ];

    overall_status = "COMPLIANT";
    score = 100;
    summary = { pass_count: 8, fail_count: 0, review_count: 0, na_count: 1 };
  } else {
    // V1.1 Non-compliant demo sample: Spicy Crunchy Bites by XYZ Snacks
    product = {
      product_name: "Spicy Crunchy Bites",
      brand_name: "XYZ Snacks",
      generic_name: null,
      category: categoryHint || "Food",
      manufacturer: {
        role: "Packer",
        name: "XYZ Foods & Beverages",
        address: null,
      },
      quantity: {
        value: "500",
        unit: "g",
        raw_text: "500 g",
      },
      mrp: {
        value: "120",
        currency: "INR",
        inclusive_of_taxes: null,
        raw_text: "MRP ₹120",
      },
      dates: {
        manufacture_date: null,
        packing_date: null,
        best_before: null,
        use_by: null,
      },
      consumer_care: {
        phone: null,
        email: null,
        address: null,
      },
      country_of_origin: null,
      import_status: "UNCERTAIN",
      is_imported: null,
      date_applicability: "APPLICABLE",
      package_type: "normal",
      raw_evidence: [
        "XYZ Snacks",
        "Spicy Crunchy Bites",
        "Packed by: XYZ Foods & Beverages",
        "500 g",
        "MRP ₹120",
      ],
    };

    checks = [
      {
        rule_id: "LM-001",
        rule_name: "Manufacturer / Packer / Importer Details",
        field: "manufacturer",
        status: "FAIL",
        detected_value: "XYZ Foods & Beverages (Address missing)",
        evidence: "Packer: XYZ Foods & Beverages, Address: Not found",
        reason: "Manufacturer/Packer name is present, but complete physical address is missing.",
        recommendation: "Package label must declare full address of manufacturer/packer.",
      },
      {
        rule_id: "LM-002",
        rule_name: "Country of Origin",
        field: "country_of_origin",
        status: "REVIEW",
        detected_value: "Not detected",
        evidence: "Evidence not available.",
        reason: "Import status and Country of Origin could not be conclusively verified from the available label information.",
        recommendation: "Officer review required to verify whether package is imported.",
      },
      {
        rule_id: "LM-003",
        rule_name: "Generic Product Name",
        field: "generic_name",
        status: "FAIL",
        detected_value: 'Brand found: "XYZ Snacks"; generic name not detected',
        evidence: "Brand Name: XYZ Snacks",
        reason: "Brand name was detected, but a distinct generic/common name of the commodity was not detected.",
        recommendation: "Ensure the common or generic name of the commodity is clearly declared alongside the brand name.",
      },
      {
        rule_id: "LM-004",
        rule_name: "Net Quantity",
        field: "quantity",
        status: "PASS",
        detected_value: "500 g",
        evidence: "500 g",
        reason: "Net quantity ('500 g') declared with valid standard units.",
        recommendation: null,
      },
      {
        rule_id: "LM-005",
        rule_name: "Manufacture / Packing Date",
        field: "dates",
        status: "FAIL",
        detected_value: "Not detected",
        evidence: "Evidence not available.",
        reason: "Neither month and year of manufacture nor packing date was detected.",
        recommendation: "Month and year of manufacture or packing must be declared on package.",
      },
      {
        rule_id: "LM-006",
        rule_name: "Best Before / Use By",
        field: "dates",
        status: "FAIL",
        detected_value: "Not detected",
        evidence: "Evidence not available.",
        reason: "Best before / expiry date is missing for perishable category 'Food'.",
        recommendation: "Perishable items must declare Best Before period or Use By date.",
      },
      {
        rule_id: "LM-007",
        rule_name: "Maximum Retail Price (MRP)",
        field: "mrp",
        status: "PASS",
        detected_value: "₹120",
        evidence: "MRP ₹120",
        reason: "Maximum Retail Price ('₹120') detected.",
        recommendation: null,
      },
      {
        rule_id: "LM-008",
        rule_name: "MRP Tax-Inclusive Indication",
        field: "mrp",
        status: "REVIEW",
        detected_value: "Uncertain",
        evidence: "MRP ₹120",
        reason: "Image or label text is unclear; tax-inclusive indication could not be determined with certainty.",
        recommendation: "Verify that the package's MRP declaration indicates that applicable taxes are included.",
      },
      {
        rule_id: "LM-009",
        rule_name: "Consumer Care Details",
        field: "consumer_care",
        status: "FAIL",
        detected_value: "Not detected",
        evidence: "Evidence not available.",
        reason: "No consumer care helpline phone, email, or address was detected.",
        recommendation: "Package must state consumer care contact details for consumer complaints.",
      },
    ];

    overall_status = "NON_COMPLIANT";
    score = 33; // 2 PASS, 5 FAIL, 2 REVIEW -> (2 + 1.0) / 9 = 33%
    summary = { pass_count: 2, fail_count: 5, review_count: 2, na_count: 0 };
  }

  const resultObj = {
    inspection_id,
    status: overall_status,
    score,
    product,
    checks,
    summary,
    timestamp,
    is_demo: true,
    disclaimer:
      "Prototype screening result. Final regulatory determination should be verified by an authorized Legal Metrology officer and applicable current regulations.",
  };

  saveInspectionToHistory(resultObj);
  return resultObj;
}
