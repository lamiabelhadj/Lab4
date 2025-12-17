import "./loan.css";

const ContractGeneration = ({ loan }) => {
  return (
    <div className="loan-page">
      <div className="loan-card">
        <div className="loan-header">
          <h2>Contract Generation</h2>
          <button className="download-btn">
            ⬇ Download Contract
          </button>
        </div>

        <h3 className="section-title">Loan Contract</h3>

        <div className="info-box">
          <div className="info-row">
            <span>Loan ID:</span>
            <span>{loan.id}</span>
          </div>
          <div className="info-row">
            <span>Principal:</span>
            <span>${loan.amount}</span>
          </div>
          <div className="info-row">
            <span>Duration:</span>
            <span>{loan.duration} months</span>
          </div>
          <div className="info-row">
            <span>Monthly Payment:</span>
            <span>${loan.monthlyPayment}</span>
          </div>
        </div>

        <p className="page-footer">Page 1 of 1</p>
      </div>
    </div>
  );
};

export default ContractGeneration;
