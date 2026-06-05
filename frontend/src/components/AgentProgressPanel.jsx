import { useEffect, useMemo, useRef, useState } from 'react'

const AGENT_META = {
  planner: { icon: '🧠', label: 'Planner' },
  search: { icon: '🔍', label: 'Search' },
  reader: { icon: '📄', label: 'Reader' },
  synthesis: { icon: '✍️', label: 'Synthesis' },
  critic: { icon: '✅', label: 'Critic' },
}

const STATUS_META = {
  running: {
    label: 'Running',
    className: 'bg-amber-400/20 text-amber-200 border border-amber-400/40 animate-pulse',
  },
  done: {
    label: 'Done',
    className: 'bg-emerald-500/20 text-emerald-200 border border-emerald-400/40',
  },
  error: {
    label: 'Error',
    className: 'bg-rose-500/20 text-rose-200 border border-rose-400/40',
  },
}

function formatElapsed(totalSeconds) {
  const safeSeconds = Math.max(0, totalSeconds)
  const minutes = Math.floor(safeSeconds / 60)
  const seconds = safeSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

export default function AgentProgressPanel({
  entries,
  startedAt,
  isRunning,
  collapsed,
  onToggle,
}) {
  const [now, setNow] = useState(Date.now())
  const listRef = useRef(null)

  useEffect(() => {
    if (!startedAt) return undefined

    if (!isRunning) {
      setNow(Date.now())
      return undefined
    }

    const intervalId = setInterval(() => {
      setNow(Date.now())
    }, 1000)

    return () => clearInterval(intervalId)
  }, [isRunning, startedAt])

  useEffect(() => {
    if (!listRef.current || collapsed) return
    listRef.current.scrollTop = listRef.current.scrollHeight
  }, [collapsed, entries])

  const elapsedSeconds = useMemo(() => {
    if (!startedAt) return 0
    return Math.floor((now - startedAt) / 1000)
  }, [now, startedAt])

  if (collapsed) {
    return (
      <button
        type="button"
        onClick={onToggle}
        className="inline-flex items-center gap-2 self-start rounded-full border border-cyan-500/40 bg-slate-900/90 px-4 py-2 text-sm font-medium text-cyan-100 shadow-[0_10px_30px_rgba(8,145,178,0.18)] transition hover:border-cyan-400/70 hover:bg-slate-800"
      >
        <span className="text-base">🛰️</span>
        <span>View Swarm Logs</span>
        <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">{entries.length}</span>
      </button>
    )
  }

  return (
    <aside className="flex h-full min-h-[18rem] flex-col overflow-hidden rounded-3xl border border-slate-800 bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.12),_transparent_28%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.98))] shadow-[0_24px_80px_rgba(2,6,23,0.5)]">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-4 sm:px-5">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-300/80">
            Live Swarm Feed
          </p>
          <h2 className="mt-1 text-lg font-semibold text-slate-100">Agent Activity</h2>
        </div>
        <div className="text-right">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Elapsed</p>
          <p className="font-mono text-lg text-slate-100">{formatElapsed(elapsedSeconds)}</p>
        </div>
      </div>

      <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-3 py-3 sm:px-4">
        {entries.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/70 px-4 py-6 text-sm text-slate-400">
            Waiting for agent activity...
          </div>
        ) : (
          entries.map((entry) => {
            const agentMeta = AGENT_META[entry.agent] ?? { icon: '•', label: entry.agent }
            const statusMeta = STATUS_META[entry.status] ?? STATUS_META.running

            return (
              <div
                key={entry.id}
                className="animate-log-in rounded-2xl border border-slate-800 bg-slate-900/90 px-4 py-3 backdrop-blur-sm"
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 text-2xl leading-none">{agentMeta.icon}</div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-100">{agentMeta.label}</p>
                        <p className="mt-1 text-sm text-slate-300">{entry.detail || 'Processing'}</p>
                      </div>
                      <p className="shrink-0 font-mono text-xs text-slate-500">+{entry.timestamp}s</p>
                    </div>
                    <div className="mt-3 flex items-center justify-between gap-3">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${statusMeta.className}`}>
                        {statusMeta.label}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {!isRunning && entries.length > 0 && (
        <div className="border-t border-slate-800 px-4 py-3 sm:px-5">
          <button
            type="button"
            onClick={onToggle}
            className="text-sm font-medium text-cyan-200 transition hover:text-cyan-100"
          >
            Hide Swarm Logs
          </button>
        </div>
      )}
    </aside>
  )
}