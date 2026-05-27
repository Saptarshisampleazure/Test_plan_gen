import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

const ENV_API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim()
const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'
const API_BASE_URL = getInitialApiBaseUrl()
const TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY?.trim() || 'qa_testplan_token'
const DEFAULT_USERNAME = import.meta.env.VITE_DEFAULT_USERNAME?.trim() || 'admin'
const DEFAULT_PASSWORD = import.meta.env.VITE_DEFAULT_PASSWORD?.trim() || 'admin123'
const HEALTH_RETRY_DELAYS_MS = [0, 300, 700, 1200]

const sectionTitles = {
  scope: 'Scope',
  objectives: 'Objectives',
  featuresToTest: 'Features to Test',
  featuresNotToTest: 'Features Not to Test',
  testStrategy: 'Test Strategy',
  functionalTesting: 'Functional Testing',
  nonFunctionalTesting: 'Non Functional Testing',
  securityTesting: 'Security Testing',
  apiTesting: 'API Testing',
  uiTesting: 'UI Testing',
  regressionTesting: 'Regression Testing',
  risks: 'Risks',
  deliverables: 'Deliverables',
  testCases: 'Test Cases',
  Summary : 'Summary',
}

const acceptedExtensions = ['pdf', 'docx', 'txt']

function getInitialApiBaseUrl() {
  if (typeof window !== 'undefined' && window.location.port === '8000') {
    return ''
  }

  return ENV_API_BASE_URL || DEFAULT_API_BASE_URL
}

function getBackendLabel(url) {
  return url || window.location.origin
}

function getUrlsToTry(url) {
  if (!url) return ['']
  const alternateUrl = url.includes('127.0.0.1')
    ? url.replace('127.0.0.1', 'localhost')
    : url.replace('localhost', '127.0.0.1')

  return alternateUrl === url ? [url] : [url, alternateUrl]
}

function App() {
  const [file, setFile] = useState(null)
  const [testPlan, setTestPlan] = useState(null)
  const [status, setStatus] = useState('Select a document to begin.')
  const [error, setError] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [isWorking, setIsWorking] = useState(false)
  const [isExporting, setIsExporting] = useState('')
  const [backendAlert, setBackendAlert] = useState(null)
  const [backendUrl, setBackendUrl] = useState(API_BASE_URL)
  const abortRef = useRef(null)
  const inputRef = useRef(null)

  const canSubmit = useMemo(() => Boolean(file) && !isWorking, [file, isWorking])

  const clearDocument = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    setFile(null)
    setTestPlan(null)
    setError('')
    setIsWorking(false)
    setIsExporting('')
    setStatus('Select a document to begin.')

    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }, [])

  const showBackendAlert = useCallback((details = '') => {
    setBackendAlert({
      title: 'Python backend is not responding',
      message: `Start or restart the Python backend at ${getBackendLabel(backendUrl)}, then try again.${details ? ` (${details})` : ''}`,
    })
  }, [backendUrl])

  const checkBackend = useCallback(async () => {
    const urlsToTry = getUrlsToTry(backendUrl)
    let lastError = null

    for (const delay of HEALTH_RETRY_DELAYS_MS) {
      if (delay) {
        await sleep(delay)
      }

      for (const url of urlsToTry) {
        try {
          const response = await fetch(`${url}/health`, {
            cache: 'no-store',
          })

          if (response.ok) {
            if (url !== backendUrl) {
              setBackendUrl(url)
            }
            setBackendAlert(null)
            return true
          }

          lastError = new Error(`Health check failed: ${response.status}`)
        } catch (error) {
          lastError = error
        }
      }
    }

    showBackendAlert(lastError?.message ?? 'Failed to fetch')
    return false
  }, [backendUrl, showBackendAlert])

  useEffect(() => {
    clearDocument()

    const handlePageShow = (event) => {
      if (event.persisted) {
        clearDocument()
      }
    }

    window.addEventListener('pageshow', handlePageShow)
    return () => window.removeEventListener('pageshow', handlePageShow)
  }, [clearDocument])

  const request = async (path, options = {}, shouldRetryAuth = true) => {
    const headers = new Headers(options.headers || {})
    const token = await ensureToken()

    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }

    const response = await fetch(`${backendUrl}${path}`, {
      ...options,
      headers,
      signal: abortRef.current?.signal,
    })

    if (response.status === 401 && shouldRetryAuth) {
      localStorage.removeItem(TOKEN_KEY)
      return request(path, options, false)
    }

    return response
  }

  const ensureToken = async () => {
    const existingToken = localStorage.getItem(TOKEN_KEY)
    if (existingToken) return existingToken

    const response = await fetch(`${backendUrl}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: DEFAULT_USERNAME,
        password: DEFAULT_PASSWORD,
      }),
      signal: abortRef.current?.signal,
    })

    if (!response.ok) {
      throw new Error('Could not authenticate with the Python backend.')
    }

    const data = await response.json()
    localStorage.setItem(TOKEN_KEY, data.token)
    return data.token
  }

  const validateFile = (candidate) => {
    if (!candidate) return

    const extension = candidate.name.split('.').pop()?.toLowerCase()
    if (!acceptedExtensions.includes(extension)) {
      setError('Upload a PDF, DOCX, or TXT document.')
      return
    }

    setFile(candidate)
    setError('')
    setStatus('Document ready.')
    setTestPlan(null)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    validateFile(event.dataTransfer.files?.[0])
  }

  const handleSubmit = async () => {
    if (!file) return

    const backendReady = await checkBackend()
    if (!backendReady) return

    abortRef.current = new AbortController()
    setIsWorking(true)
    setError('')
    setTestPlan(null)

    try {
      setStatus('Uploading document...')
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await request('/upload', {
        method: 'POST',
        body: formData,
      })

      if (!uploadResponse.ok) {
        throw new Error(await readError(uploadResponse, 'Upload failed.'))
      }

      const uploadedFile = await uploadResponse.json()

      setStatus('Generating document...')
      const generateResponse = await request('/generate-testplan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files: [uploadedFile] }),
      })

      if (!generateResponse.ok) {
        throw new Error(await readError(generateResponse, 'Generation failed.'))
      }

      const generatedPlan = await generateResponse.json()
      setTestPlan(generatedPlan)
      setStatus('Document generated.')
    } catch (caughtError) {
      if (caughtError.name === 'AbortError') {
        setStatus('Stopped.')
      } else {
        if (isBackendError(caughtError)) {
          showBackendAlert()
        }
        setError(caughtError.message || 'Something went wrong.')
        setStatus('Ready.')
      }
    } finally {
      setIsWorking(false)
      abortRef.current = null
    }
  }

  const stopWork = () => {
    abortRef.current?.abort()
  }

  const download = async (format) => {
    if (!testPlan) return

    const backendReady = await checkBackend()
    if (!backendReady) return

    abortRef.current = new AbortController()
    setIsExporting(format)
    setError('')

    try {
      const response = await request(`/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPlan),
      })

      if (!response.ok) {
        throw new Error(await readError(response, 'Export failed.'))
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `generated-test-plan.${format === 'docx' ? 'docx' : 'pdf'}`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (caughtError) {
      if (caughtError.name !== 'AbortError') {
        if (isBackendError(caughtError)) {
          showBackendAlert()
        }
        setError(caughtError.message || 'Could not download the file.')
      }
    } finally {
      setIsExporting('')
      abortRef.current = null
    }
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        {backendAlert ? (
          <BackendAlert
            alert={backendAlert}
            onClose={() => setBackendAlert(null)}
            onRetry={checkBackend}
          />
        ) : null}

        <header className="page-header">
          <div>
            <h1>VeriMind AI</h1>
          </div>
          <span className="status-pill">{status}</span>
        </header>

        <div className="tool-grid">
          <section className="upload-panel" aria-label="Document upload">
            <div
              className={`drop-zone${isDragging ? ' is-dragging' : ''}`}
              onDragEnter={(event) => {
                event.preventDefault()
                setIsDragging(true)
              }}
              onDragOver={(event) => event.preventDefault()}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              role="button"
              tabIndex={0}
              onClick={() => inputRef.current?.click()}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  inputRef.current?.click()
                }
              }}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(event) => validateFile(event.target.files?.[0])}
                hidden
              />
              <div className="upload-mark">+</div>
              <h2>Drop or attach your document here</h2>
              <p>PDF/DOCX</p>
            </div>

            {file ? (
              <div className="file-row">
                <div>
                  <strong>{file.name}</strong>
                  <span>{formatBytes(file.size)}</span>
                </div>
                <button
                  className="ghost-button"
                  type="button"
                  onClick={clearDocument}
                  disabled={isWorking}
                >
                  Clear
                </button>
              </div>
            ) : null}

            {error ? <p className="error-text">{error}</p> : null}

            <div className="action-row">
              <button
                className="secondary-button"
                type="button"
                onClick={stopWork}
                disabled={!isWorking}
              >
                Stop
              </button>
              <button
                className="primary-button"
                type="button"
                onClick={handleSubmit}
                disabled={!canSubmit}
              >
                {isWorking ? 'Working...' : 'Submit'}
              </button>
            </div>
          </section>

          <section className="preview-panel" aria-label="Generated document preview">
            <div className="preview-header">
              <div>
                <p className="eyebrow">Preview</p>
                <h2>Generated Document</h2>
              </div>
              <div className="download-row">
                <button
                  className="ghost-button"
                  type="button"
                  onClick={() => download('docx')}
                  disabled={!testPlan || Boolean(isExporting)}
                >
                  {isExporting === 'docx' ? 'Preparing...' : 'Download DOCX'}
                </button>
                <button
                  className="ghost-button"
                  type="button"
                  onClick={() => download('pdf')}
                  disabled={!testPlan || Boolean(isExporting)}
                >
                  {isExporting === 'pdf' ? 'Preparing...' : 'Download PDF'}
                </button>
              </div>
            </div>

            {testPlan ? <TestPlanPreview testPlan={testPlan} /> : <EmptyPreview />}
          </section>
        </div>
      </section>
    </main>
  )
}

function EmptyPreview() {
  return (
    <div className="empty-preview">
     <h3></h3>
      <p>Preview the generated test plan here.</p>
    </div>
  )
}

function BackendAlert({ alert, onClose, onRetry }) {
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="backend-alert-title">
      <div className="modal-panel">
        <h2 id="backend-alert-title">{alert.title}</h2>
        <p>{alert.message}</p>
        <div className="modal-actions">
          <button className="ghost-button" type="button" onClick={onClose}>
            Close
          </button>
          <button className="primary-button" type="button" onClick={onRetry}>
            Retry
          </button>
        </div>
      </div>
    </div>
  )
}

function TestPlanPreview({ testPlan }) {
  const sections = testPlan.sections || {}

  return (
    <article className="document-preview">
      <header>
        <h3>Software Test Plan</h3>
        <p>
          {testPlan.sourceFiles?.join(', ') || 'Uploaded document'} -{' '}
          {formatDate(testPlan.createdAt)}
        </p>
      </header>

      {Object.entries(sectionTitles).map(([key, title]) => {
        const value = sections[key]
        if (!value || (Array.isArray(value) && value.length === 0)) return null

        return (
          <section className="doc-section" key={key}>
            <h4>{title}</h4>
            <SectionContent value={value} />
          </section>
        )
      })}
    </article>
  )
}

function SectionContent({ value }) {
  if (Array.isArray(value)) {
    const isTestCaseList = value.every((item) => item && typeof item === 'object')

    if (isTestCaseList) {
      return (
        <div className="testcase-list">
          {value.map((item) => (
            <div className="testcase-row" key={item.id || item.title}>
              <strong>{item.id}</strong>
              <span>{item.title}</span>
              <em>{item.priority}</em>
              <p>{item.expected}</p>
            </div>
          ))}
        </div>
      )
    }

    return (
      <ul>
        {value.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    )
  }

  return <p>{value}</p>
}

async function readError(response, fallback) {
  try {
    const data = await response.json()
    return data.detail || fallback
  } catch {
    return fallback
  }
}

function sleep(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

function isBackendError(error) {
  const message = error.message || ''
  return (
    message.includes('Failed to fetch') ||
    message.includes('Backend URL is not configured') ||
    message.includes('Could not authenticate')
  )
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`
}

function formatDate(value) {
  if (!value) return 'Generated now'
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export default App
