import { useEffect, useState } from "react";
import {
  getComplianceRules,
  addComplianceRule,
  updateComplianceRule,
  disableComplianceRule,
} from "../services/api";

const OPERATORS = [
  "REQUIRED",
  "NOT_EMPTY",
  "CONTAINS",
  "MATCH_PATTERN",
  "MIN_VALUE",
  "MAX_VALUE",
];

const emptyForm = {
  rule_id: "",
  rule_name: "",
  description: "",
  category: "",
  field: "",
  operator: "REQUIRED",
  expected_value: "",
  failure_message: "",
  recommendation: "",
};

export default function Settings() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [showAddForm, setShowAddForm] = useState(false);
  const [message, setMessage] = useState("");

  const loadRules = async () => {
    try {
      setLoading(true);
      const data = await getComplianceRules();
      setRules(data.rules || []);
    } catch (error) {
      console.error(error);
      setMessage("Failed to load compliance rules.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const startEdit = (rule) => {
    setEditingId(rule.rule_id);
    setShowAddForm(false);

    setForm({
      rule_id: rule.rule_id || "",
      rule_name: rule.rule_name || "",
      description: rule.description || "",
      category: rule.category || "",
      field: rule.field || "",
      operator: rule.operator || "REQUIRED",
      expected_value: rule.expected_value || "",
      failure_message: rule.failure_message || "",
      recommendation: rule.recommendation || "",
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm(emptyForm);
  };

  const startAdd = () => {
    setEditingId(null);
    setForm(emptyForm);
    setShowAddForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingId) {
        await updateComplianceRule(editingId, form);
        setMessage(`${editingId} updated successfully.`);
      } else {
        await addComplianceRule(form);
        setMessage(`${form.rule_id} added successfully.`);
      }

      cancelEdit();
      setShowAddForm(false);
      await loadRules();
    } catch (error) {
      console.error(error);
      setMessage(
        error?.response?.data?.detail ||
          "Failed to save compliance rule."
      );
    }
  };

  const handleDisable = async (ruleId) => {
    const confirmed = window.confirm(
      `Disable ${ruleId}? The rule will remain in the database but will no longer be evaluated.`
    );

    if (!confirmed) return;

    try {
      await disableComplianceRule(ruleId);
      setMessage(`${ruleId} disabled successfully.`);
      await loadRules();
    } catch (error) {
      console.error(error);
      setMessage(
        error?.response?.data?.detail ||
          "Failed to disable rule."
      );
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold">Compliance Rules</h1>
        <p className="mt-4">Loading rules...</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">
            Legal Metrology Compliance Rules
          </h1>

          <p className="text-gray-600 mt-1">
            All rules are stored locally in SQLite and can be edited.
          </p>
        </div>

        <button
          onClick={startAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Add New Rule
        </button>
      </div>

      {message && (
        <div className="mb-5 p-3 bg-gray-100 rounded-lg">
          {message}
        </div>
      )}

      <div className="mb-6 p-4 border rounded-lg bg-gray-50">
        <div className="font-semibold">
          System Status
        </div>

        <div className="text-sm text-gray-600 mt-1">
          Deterministic • Offline • SQLite Database
        </div>
      </div>

      {(showAddForm || editingId) && (
        <form
          onSubmit={handleSubmit}
          className="mb-8 border rounded-lg p-5 bg-white shadow-sm"
        >
          <h2 className="text-lg font-semibold mb-4">
            {editingId
              ? `Edit ${editingId}`
              : "Add New Compliance Rule"}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              name="rule_id"
              value={form.rule_id}
              onChange={handleChange}
              disabled={!!editingId}
              placeholder="Rule ID (e.g. LM-012)"
              className="border rounded-lg p-2"
              required
            />

            <input
              name="rule_name"
              value={form.rule_name}
              onChange={handleChange}
              placeholder="Rule Name"
              className="border rounded-lg p-2"
              required
            />

            <input
              name="category"
              value={form.category}
              onChange={handleChange}
              placeholder="Category"
              className="border rounded-lg p-2"
            />

            <input
              name="field"
              value={form.field}
              onChange={handleChange}
              placeholder="Field (e.g. custom_fields.batch_number)"
              className="border rounded-lg p-2"
              required
            />

            <select
              name="operator"
              value={form.operator}
              onChange={handleChange}
              className="border rounded-lg p-2"
            >
              {OPERATORS.map((operator) => (
                <option key={operator} value={operator}>
                  {operator}
                </option>
              ))}
            </select>

            <input
              name="expected_value"
              value={form.expected_value}
              onChange={handleChange}
              placeholder="Expected Value"
              className="border rounded-lg p-2"
            />

            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="Description"
              className="border rounded-lg p-2"
            />

            <textarea
              name="failure_message"
              value={form.failure_message}
              onChange={handleChange}
              placeholder="Failure Message"
              className="border rounded-lg p-2"
            />

            <textarea
              name="recommendation"
              value={form.recommendation}
              onChange={handleChange}
              placeholder="Recommendation"
              className="border rounded-lg p-2 md:col-span-2"
            />
          </div>

          <div className="flex gap-3 mt-5">
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded-lg"
            >
              {editingId ? "Save Changes" : "Add Rule"}
            </button>

            <button
              type="button"
              onClick={() => {
                cancelEdit();
                setShowAddForm(false);
              }}
              className="px-4 py-2 bg-gray-300 rounded-lg"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="space-y-4">
        {rules.map((rule) => (
          <div
            key={rule.rule_id}
            className="border rounded-lg p-5 bg-white shadow-sm"
          >
            <div className="flex justify-between items-start gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="font-semibold text-lg">
                    {rule.rule_id} — {rule.rule_name}
                  </h2>

                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      rule.status === "ACTIVE"
                        ? "bg-green-100 text-green-700"
                        : "bg-gray-200 text-gray-600"
                    }`}
                  >
                    {rule.status}
                  </span>
                </div>

                <p className="text-gray-600 mt-2">
                  {rule.description || "No description"}
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => startEdit(rule)}
                  className="px-3 py-1 border rounded-lg hover:bg-gray-50"
                >
                  Edit
                </button>

                {rule.status === "ACTIVE" && (
                  <button
                    onClick={() => handleDisable(rule.rule_id)}
                    className="px-3 py-1 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
                  >
                    Disable
                  </button>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4 text-sm">
              <div>
                <span className="font-medium">Field:</span>{" "}
                {rule.field}
              </div>

              <div>
                <span className="font-medium">Operator:</span>{" "}
                {rule.operator}
              </div>

              <div>
                <span className="font-medium">Expected:</span>{" "}
                {rule.expected_value || "—"}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}