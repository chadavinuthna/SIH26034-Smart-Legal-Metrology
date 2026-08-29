const HISTORY_KEY = "sih26034_inspection_history";

export const getStoredHistory = () => {
  try {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error("Failed to read history from localStorage:", e);
    return [];
  }
};

export const saveInspectionToHistory = (inspection) => {
  try {
    const current = getStoredHistory();
    // Prepend new inspection, avoid duplicates
    const filtered = current.filter((item) => item.inspection_id !== inspection.inspection_id);
    const updated = [inspection, ...filtered];
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    return updated;
  } catch (e) {
    console.error("Failed to save inspection to localStorage:", e);
    return [];
  }
};

export const getInspectionById = (inspectionId) => {
  const history = getStoredHistory();
  return history.find((item) => item.inspection_id === inspectionId) || null;
};
