import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

interface Loan {
  application_id: string;
  amount: number;
  duration: number;
  income: number;
  status: string;
  created_at: string;
}

function App() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLoans();
  }, []);

  const fetchLoans = async () => {
    try {
      const res = await axios.get<Loan[]>("http://localhost:8000/api/loan-applications");
      setLoans(res.data);
    } catch {
      setError("Failed to fetch loans");
    }
  };

  const handleApprove = async (applicationId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`http://localhost:8000/api/loan-application/${applicationId}/approve`);
      const data = res.data;
      window.open(`http://localhost:8000/${data.contract}`, "_blank");
      window.open(`http://localhost:8000/${data.amortization}`, "_blank");
      fetchLoans();
    } catch {
      setError("Approval failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="form-card">
        <h1>Loan Applications</h1>
        {error && <p className="error-message">{error}</p>}
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Amount</th>
              <th>Duration</th>
              <th>Income</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loans.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", padding: "1rem" }}>
                  No loan applications
                </td>
              </tr>
            )}
            {loans.map((loan) => (
              <tr key={loan.application_id}>
                <td>{loan.application_id}</td>
                <td>${loan.amount.toLocaleString()}</td>
                <td>{loan.duration} months</td>
                <td>${loan.income.toLocaleString()}</td>
                <td>
                  <span className={`status-badge ${loan.status.toLowerCase()}`}>
                    {loan.status === "Submitted" ? "Re-Approved" : loan.status}
                  </span>
                </td>
                <td>
                  {loan.status === "Submitted" && (
                    <button
                      className="submit-btn"
                      onClick={() => handleApprove(loan.application_id)}
                      disabled={loading}
                    >
                      {loading ? "Processing..." : "Approve & Generate Contract"}
                    </button>
                  )}
                  {loan.status === "Approved" && (
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <a
                        className="pdf-link"
                        href={`http://localhost:8000/api/loan-application/${loan.application_id}/contract`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Contract
                      </a>
                      <a
                        className="pdf-link"
                        href={`http://localhost:8000/api/loan-application/${loan.application_id}/amortization`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Amortization
                      </a>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
