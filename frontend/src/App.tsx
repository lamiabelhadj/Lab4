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
    } catch (err) {
      setError("Failed to fetch loans");
    }
  };

  const handleApprove = async (applicationId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`http://localhost:8000/api/loan-application/${applicationId}/approve`);
      const data = res.data;
      // Ouvre les PDFs dans de nouveaux onglets
      window.open(`http://localhost:8000/${data.contract}`, "_blank");
      window.open(`http://localhost:8000/${data.amortization}`, "_blank");
      // Rafraîchir la liste
      fetchLoans();
    } catch (err) {
      setError("Approval failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Loan Applications</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
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
          {loans.map((loan) => (
            <tr key={loan.application_id}>
              <td>{loan.application_id}</td>
              <td>${loan.amount.toLocaleString()}</td>
              <td>{loan.duration} months</td>
              <td>${loan.income.toLocaleString()}</td>
              <td>{loan.status}</td>
              <td>
                {loan.status === "Submitted" && (
                  <button onClick={() => handleApprove(loan.application_id)} disabled={loading}>
                    {loading ? "Processing..." : "Approve & Generate Contract"}
                  </button>
                )}
                {loan.status === "Approved" && (
                  <>
                    <a
                      href={`http://localhost:8000/api/loan-application/${loan.application_id}/contract`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Contract
                    </a>{" "}
                    |{" "}
                    <a
                      href={`http://localhost:8000/api/loan-application/${loan.application_id}/amortization`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Amortization
                    </a>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
