import "./loan.css";

const AmortizationGeneration = ({ schedule }) => {
  return (
    <div className="loan-page">
      <div className="loan-card">
        <div className="loan-header">
          <h2>Amortization Schedule Generation</h2>
          <button className="download-btn">
            ⬇ Download PDF
          </button>
        </div>

        <h3 className="section-title">Amortization Schedule</h3>

        <table className="loan-table">
          <thead>
            <tr>
              <th>Month</th>
              <th>Payment</th>
              <th>Principal</th>
              <th>Interest</th>
              <th>Remaining Balance</th>
            </tr>
          </thead>
          <tbody>
            {schedule.map((row, index) => (
              <tr key={index}>
                <td>{row.month}</td>
                <td>${row.payment}</td>
                <td>${row.principal}</td>
                <td>${row.interest}</td>
                <td>${row.balance}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <p className="page-footer">Page 1 of 1</p>
      </div>
    </div>
  );
};

export default AmortizationGeneration;
