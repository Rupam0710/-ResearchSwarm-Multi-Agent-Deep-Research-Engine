import { useEffect, useState } from 'react'
import AgentProgressPanel from '../components/AgentProgressPanel'
import InputPanel from '../components/InputPanel'
import SwarmVisualizer from '../components/SwarmVisualizer'
import ReportViewer from '../components/ReportViewer'

const REQUEST_TIMEOUT_MS = 300000 // 5 minutes total for the entire stream
const HEALTH_CHECK_TIMEOUT_MS = 5000
const HEALTH_POLL_INTERVAL_MS = 5000
const WARMUP_PROGRESS_DURATION_MS = 40000
const WARMUP_READY_MESSAGE_MS = 1000
const BASE_URL = import.meta.env.VITE_API_URL || ''

const AGENT_STEP_INDEX = {
  planner: 0,
  search: 1,
  reader: 2,
  synthesis: 3,
  critic: 4,
}

function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [activeStep, setActiveStep] = useState(-1)
  const [report, setReport] = useState(null)
  const [critique, setCritique] = useState(null)
  const [criticReviewing, setCriticReviewing] = useState(false)
  const [error, setError] = useState('')
  const [progressEntries, setProgressEntries] = useState([])
  const [startedAt, setStartedAt] = useState(null)
  const [logsCollapsed, setLogsCollapsed] = useState(false)
  const [backendStatus, setBackendStatus] = useState('sleeping')
  const [warmupBannerVisible, setWarmupBannerVisible] = useState(false)
  const [warmupPhase, setWarmupPhase] = useState('idle')
  const [warmupStartedAt, setWarmupStartedAt] = useState(null)
  const [warmupProgress, setWarmupProgress] = useState(0)

  useEffect(() => {
    if (warmupPhase !== 'waking' || !warmupStartedAt) {
      setWarmupProgress(0)
      return undefined
    }

    const intervalId = window.setInterval(() => {
      const elapsed = Date.now() - warmupStartedAt
      const nextProgress = Math.min((elapsed / WARMUP_PROGRESS_DURATION_MS) * 100, 100)
      setWarmupProgress(nextProgress)
    }, 200)

    return () => window.clearInterval(intervalId)
  }, [warmupPhase, warmupStartedAt])

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms))

  const checkBackend = async () => {
    try {
      const res = await fetch(`${BASE_URL}/health`, {
        signal: AbortSignal.timeout(HEALTH_CHECK_TIMEOUT_MS),
      })
      return res.ok
    } catch {
      return false
    }
  }

  const executeResearchRequest = async (question, researchStartedAt) => {
    const controller = new AbortController()
    const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

    try {
      const response = await fetch(`${BASE_URL}/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        throw new Error(payload?.detail || `HTTP error: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let streamError = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        const frames = buffer.split('\n\n')
        buffer = frames.pop() || ''

        for (const frame of frames) {
          const dataLines = frame
            .split('\n')
            .filter((line) => line.startsWith('data:'))
            .map((line) => line.slice(5).trimStart())

          if (dataLines.length === 0) {
            continue
          }

          let event
          try {
            event = JSON.parse(dataLines.join('\n'))
          } catch (parseError) {
            console.error('Error parsing SSE event:', parseError)
            continue
          }

          if (event.type === 'progress') {
            const timestamp = Math.floor((Date.now() - researchStartedAt) / 1000)
            setProgressEntries((prev) => [
              ...prev,
              {
                id: `${Date.now()}-${prev.length}`,
                agent: event.agent,
                status: event.status,
                detail: event.detail || '',
                timestamp,
              },
            ])

            const nextStep = AGENT_STEP_INDEX[event.agent]
            if (typeof nextStep === 'number') {
              setActiveStep((prev) => Math.max(prev, nextStep))
            }
          } else if (event.type === 'report') {
            setReport(event.report)
            setCriticReviewing(true)
            setLogsCollapsed(true)
          } else if (event.type === 'critique') {
            setCritique(event.critique)
            setCriticReviewing(false)
          } else if (event.type === 'error') {
            streamError = new Error(event.error || 'Research failed.')
            break
          }
        }

        if (streamError) {
          throw streamError
        }
      }

      if (buffer.trim()) {
        const maybeData = buffer
          .split('\n')
          .find((line) => line.startsWith('data:'))
        if (maybeData) {
          try {
            const event = JSON.parse(maybeData.slice(5).trimStart())
            if (event.type === 'report') {
              setReport(event.report)
              setCriticReviewing(true)
              setLogsCollapsed(true)
            } else if (event.type === 'critique') {
              setCritique(event.critique)
              setCriticReviewing(false)
            }
          } catch (parseError) {
            console.error('Error parsing trailing SSE event:', parseError)
          }
        }
      }
    } finally {
      window.clearTimeout(timeoutId)
    }
  }

  const handleSubmit = async (question) => {
    const researchStartedAt = Date.now()

    setError('')
    setReport(null)
    setCritique(null)
    setCriticReviewing(false)
    setProgressEntries([])
    setStartedAt(researchStartedAt)
    setLogsCollapsed(false)
    setIsLoading(true)
    setActiveStep(-1)
    setBackendStatus('sleeping')
    setWarmupBannerVisible(false)
    setWarmupPhase('idle')
    setWarmupStartedAt(null)
    setWarmupProgress(0)

    try {
      const backendAwake = await checkBackend()

      if (!backendAwake) {
        setBackendStatus('waking')
        setWarmupPhase('waking')
        setWarmupBannerVisible(true)
        setWarmupStartedAt(Date.now())

        let backendReady = false
        while (!backendReady) {
          await sleep(HEALTH_POLL_INTERVAL_MS)
          backendReady = await checkBackend()
        }

        setBackendStatus('ready')
        setWarmupPhase('ready')
        setWarmupProgress(100)
        await sleep(WARMUP_READY_MESSAGE_MS)
        setWarmupBannerVisible(false)
        await sleep(250)
      } else {
        setBackendStatus('ready')
      }

      setWarmupPhase('idle')
      setWarmupStartedAt(null)
      setWarmupProgress(0)

      await executeResearchRequest(question, researchStartedAt)
    } catch (submitError) {
      if (submitError.name === 'AbortError') {
        setError('Research request timed out. Please retry or reduce the question scope.')
      } else {
        setError(submitError.message || 'Research failed. Please try again.')
      }
    } finally {
      setWarmupBannerVisible(false)
      setWarmupPhase('idle')
      setWarmupStartedAt(null)
      setWarmupProgress(0)
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setReport(null)
    setCritique(null)
    setError('')
    setIsLoading(false)
    setActiveStep(-1)
    setCriticReviewing(false)
    setProgressEntries([])
    setStartedAt(null)
    setLogsCollapsed(false)
    setBackendStatus('sleeping')
    setWarmupBannerVisible(false)
    setWarmupPhase('idle')
    setWarmupStartedAt(null)
    setWarmupProgress(0)
  }

  const hasResult = report !== null

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 px-3 py-6 sm:px-4 sm:py-10">
      <div className="max-w-5xl mx-auto flex flex-col gap-6 sm:gap-8">
        <header className="text-center animate-fade-in transition-all duration-500">
          <h1 className="text-3xl sm:text-5xl font-bold mb-2 sm:mb-3 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            ResearchSwarm
          </h1>
          <p className="text-sm sm:text-lg text-slate-300">Multi-Agent Deep Research Engine</p>
        </header>

        {!hasResult && (
          <div className="flex flex-col gap-4 sm:gap-6 animate-fade-in transition-all duration-500">
            <InputPanel
              onSubmit={handleSubmit}
              isLoading={isLoading}
              isPreparingBackend={warmupPhase !== 'idle'}
              warmupBanner={{
                visible: warmupBannerVisible,
                phase: warmupPhase,
                progress: warmupProgress,
              }}
            />
            {error && (
              <div className="bg-red-950/60 border border-red-500/50 rounded-xl px-4 py-3 text-red-200 transition-opacity duration-500">
                {error}
              </div>
            )}
            {isLoading && (
              <div className="grid gap-4 lg:grid-cols-[minmax(0,22rem)_minmax(0,1fr)] animate-fade-in transition-all duration-500">
                <AgentProgressPanel
                  entries={progressEntries}
                  startedAt={startedAt}
                  isRunning={isLoading}
                  collapsed={false}
                  onToggle={() => {}}
                />
                <div className="bg-slate-900 border border-slate-700 rounded-2xl px-3 sm:px-6 py-3 sm:py-4 transition-all duration-500">
                  <SwarmVisualizer activeStep={activeStep} backendStatus={backendStatus} />
                </div>
              </div>
            )}
          </div>
        )}

        {hasResult && (
          <div className="flex flex-col gap-4 sm:gap-5 animate-fade-in transition-all duration-500">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <AgentProgressPanel
                entries={progressEntries}
                startedAt={startedAt}
                isRunning={isLoading}
                collapsed={logsCollapsed}
                onToggle={() => setLogsCollapsed((prev) => !prev)}
              />
              <button
                onClick={handleReset}
                className="w-full sm:w-auto bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-100 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                New Research
              </button>
            </div>

            {criticReviewing && (
              <div className="flex items-center gap-2 px-4 py-2 bg-amber-900/30 border border-amber-700/50 rounded-lg">
                <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-amber-200">Critic reviewing...</span>
              </div>
            )}

            <ReportViewer report={report} critique={critique} />
          </div>
        )}

        {!hasResult && !isLoading && !error && (
          <p className="text-center text-slate-500 text-xs sm:text-sm animate-fade-in transition-opacity duration-500">
            Submit a question to start the multi-agent research pipeline.
          </p>
        )}
      </div>
    </div>
  )
}

export default Home
