import { useState, type FormEvent, type ChangeEvent } from 'react'
import './App.css'

interface LoanFormData {
  amount: string
  duration: string
  income: string
}

interface SubmissionResult {
  application_id: string
  amount: number
  duration: number
  income: number
  status: string
  created_at: string
}

function App() {
  const [formData, setFormData] = useState<LoanFormData>({
    amount: '',
    duration: '',
    income: ''
  })
  const [idDocument, setIdDocument] = useState<File | null>(null)
  const [salarySlip, setSalarySlip] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<SubmissionResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>, type: 'id' | 'salary') => {
    const file = e.target.files?.[0] || null
    if (file && file.type !== 'application/pdf') {
      setError('Only PDF files are allowed')
      return
    }
    setError(null)
    if (type === 'id') {
      setIdDocument(file)
    } else {
      setSalarySlip(file)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setResult(null)

    if (!idDocument || !salarySlip) {
      setError('Please upload both documents')
      return
    }

    setIsLoading(true)

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('amount', formData.amount)
      formDataToSend.append('duration', formData.duration)
      formDataToSend.append('income', formData.income)
      formDataToSend.append('id_document', idDocument)
      formDataToSend.append('salary_slip', salarySlip)

      const response = await fetch('http://localhost:8000/api/loan-application', {
        method: 'POST',
        body: formDataToSend
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Submission failed')
      }

      const data: SubmissionResult = await response.json()
      setResult(data)
      
      // Reset form
      setFormData({ amount: '', duration: '', income: '' })
      setIdDocument(null)
      setSalarySlip(null)
      
      // Reset file inputs
      const fileInputs = document.querySelectorAll<HTMLInputElement>('input[type="file"]')
      fileInputs.forEach(input => input.value = '')
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <div className="form-card">
        <h1>Loan Application</h1>
        <p className="subtitle">Fill in your details and upload required documents</p>

        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h2>Loan Details</h2>
            
            <div className="form-group">
              <label htmlFor="amount">Loan Amount ($)</label>
              <input
                type="number"
                id="amount"
                name="amount"
                value={formData.amount}
                onChange={handleInputChange}
                placeholder="Enter loan amount"
                min="1"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="duration">Duration (months)</label>
              <input
                type="number"
                id="duration"
                name="duration"
                value={formData.duration}
                onChange={handleInputChange}
                placeholder="Enter duration in months"
                min="1"
                max="360"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="income">Monthly Income ($)</label>
              <input
                type="number"
                id="income"
                name="income"
                value={formData.income}
                onChange={handleInputChange}
                placeholder="Enter your monthly income"
                min="1"
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h2>Required Documents</h2>
            
            <div className="form-group">
              <label htmlFor="idDocument">ID Document (PDF)</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="idDocument"
                  accept=".pdf"
                  onChange={(e) => handleFileChange(e, 'id')}
                  required
                />
                {idDocument && <span className="file-name">✓ {idDocument.name}</span>}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="salarySlip">Salary Slip (PDF)</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="salarySlip"
                  accept=".pdf"
                  onChange={(e) => handleFileChange(e, 'salary')}
                  required
                />
                {salarySlip && <span className="file-name">✓ {salarySlip.name}</span>}
              </div>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn" disabled={isLoading}>
            {isLoading ? 'Submitting...' : 'Submit Application'}
          </button>
        </form>

        {result && (
          <div className="success-card">
            <h2>✓ Application Submitted Successfully!</h2>
            <div className="result-details">
              <p><strong>Application ID:</strong> {result.application_id}</p>
              <p><strong>Amount:</strong> ${result.amount.toLocaleString()}</p>
              <p><strong>Duration:</strong> {result.duration} months</p>
              <p><strong>Income:</strong> ${result.income.toLocaleString()}</p>
              <p><strong>Status:</strong> <span className="status-badge">{result.status}</span></p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
