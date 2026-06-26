import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "https://eu-ai-act-agent.salmonmeadow-a1fcad59.swedencentral.azurecontainerapps.io";

const RISK_COLORS = {
  UNACCEPTABLE: "#dc2626",
  HIGH: "#ea580c",
  LIMITED: "#d97706",
  MINIMAL: "#16a34a",
};

export default function App() {
  const [systemName, setSystemName] = useState("");
  const [systemDescription, setSystemDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [audits, setAudits] = useState([]);
  const [activeTab, setActiveTab] = useState("scan");
  const [reviewComments, setReviewComments] = useState("");
  const [reviewLoading, setReviewLoading] = useState(null);

  useEffect(() => {
    if (activeTab === "audits") fetchAudits();
  }, [activeTab]);

  const fetchAudits = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/v1/audits`);
      setAudits(res.data);
    } catch {
      setError("Failed to fetch audits");
    }
  };

  const handleScan = async () => {
    if (!systemName || !systemDescription) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/api/v1/scan`, {
        system_name: systemName,
        system_description: systemDescription,
      });
      setResult(res.data);
    } catch {
      setError("Scan failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (auditId, decision) => {
    setReviewLoading(auditId + decision);
    try {
      await axios.post(`${API_BASE}/api/v1/audit/${auditId}/review`, {
        decision,
        comments: reviewComments,
      });
      fetchAudits();
    } catch {
      setError("Review failed.");
    } finally {
      setReviewLoading(null);
      setReviewComments("");
    }
  };

  return (
    <div className="app">
      <header>
        <h1>🇪🇺 EU AI Act Compliance Agent</h1>
        <p>Scan AI systems for EU AI Act compliance and generate audit documentation</p>
        <nav>
          <button className={activeTab === "scan" ? "active" : ""} onClick={() => setActiveTab("scan")}>
            New Scan
          </button>
          <button className={activeTab === "audits" ? "active" : ""} onClick={() => setActiveTab("audits")}>
            Audit History
          </button>
        </nav>
      </header>

      <main>
        {activeTab === "scan" && (
          <div className="scan-panel">
            <div className="form-card">
              <h2>Submit AI System for Compliance Scan</h2>
              <label>System Name</label>
              <input
                type="text"
                placeholder="e.g. HireBot AI"
                value={systemName}
                onChange={(e) => setSystemName(e.target.value)}
              />
              <label>System Description</label>
              <textarea
                placeholder="Describe what the AI system does, how it works, and where it's used..."
                value={systemDescription}
                onChange={(e) => setSystemDescription(e.target.value)}
                rows={5}
              />
              <button className="scan-btn" onClick={handleScan} disabled={loading || !systemName || !systemDescription}>
                {loading ? "Scanning... (this may take 15-30 seconds)" : "Run Compliance Scan"}
              </button>
            </div>

            {error && <div className="error">{error}</div>}

            {result && (
              <div className="result-card">
                <div className="risk-badge" style={{ backgroundColor: RISK_COLORS[result.risk_category] }}>
                  {result.risk_category} RISK
                </div>
                <h3>{result.system_name}</h3>
                <p className="audit-id">Audit ID: {result.audit_id}</p>
                <p className="status">Status: {result.status}</p>

                <h4>Compliance Gaps Identified</h4>
                <ul>
                  {result.compliance_gaps.map((gap, i) => (
                    <li key={i}>{gap}</li>
                  ))}
                </ul>

                <div className="review-section">
                  <h4>Human Review</h4>
                  <textarea
                    placeholder="Add review comments (optional)"
                    value={reviewComments}
                    onChange={(e) => setReviewComments(e.target.value)}
                    rows={3}
                  />
                  <div className="review-buttons">
                    <button
                      className="approve-btn"
                      onClick={() => handleReview(result.audit_id, "APPROVED")}
                      disabled={reviewLoading !== null}
                    >
                      ✓ Approve
                    </button>
                    <button
                      className="reject-btn"
                      onClick={() => handleReview(result.audit_id, "REJECTED")}
                      disabled={reviewLoading !== null}
                    >
                      ✗ Reject
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "audits" && (
          <div className="audits-panel">
            <h2>Audit History</h2>
            {audits.length === 0 ? (
              <p>No audits yet.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>System Name</th>
                    <th>Risk Category</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {audits.map((a) => (
                    <tr key={a.audit_id}>
                      <td>{a.system_name}</td>
                      <td>
                        <span className="risk-tag" style={{ backgroundColor: RISK_COLORS[a.risk_category] }}>
                          {a.risk_category}
                        </span>
                      </td>
                      <td>{a.status}</td>
                      <td>{new Date(a.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </main>
    </div>
  );
}