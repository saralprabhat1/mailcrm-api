import { useState, useEffect } from 'react'
import { fetchStats, fetchRecords, runPipeline } from './hooks/useApi'
import StatsBar      from './components/StatsBar'
import PipelineBar   from './components/PipelineBar'
import RecordsTable  from './components/RecordsTable'
import DetailPanel   from './components/DetailPanel'

export default function App() {
  const [stats,          setStats]          = useState(null)
  const [records,        setRecords]        = useState([])
  const [selectedRecord, setSelectedRecord] = useState(null)
  const [statsLoading,   setStatsLoading]   = useState(true)
  const [recsLoading,    setRecsLoading]    = useState(true)
  const [pipelineRunning, setPipelineRunning] = useState(false)
  const [pipelineMsg,    setPipelineMsg]    = useState('')
  const [apiError,       setApiError]       = useState('')

  // ── Initial data load ──────────────────────────────────────────────────────
  async function loadAll() {
    setStatsLoading(true)
    setRecsLoading(true)
    setApiError('')
    try {
      const [sData, rData] = await Promise.all([fetchStats(), fetchRecords()])
      setStats(sData)
      // API may return plain array or { records: [...] }
      setRecords(Array.isArray(rData) ? rData : (rData.records ?? []))
    } catch {
      setApiError('API unreachable — Render free tier may be waking up (~30 s). Refresh to retry.')
    } finally {
      setStatsLoading(false)
      setRecsLoading(false)
    }
  }

  useEffect(() => { loadAll() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Run pipeline ───────────────────────────────────────────────────────────
  async function handleRunPipeline() {
    setPipelineRunning(true)
    setPipelineMsg('')
    try {
      const res = await runPipeline()
      setPipelineMsg(res?.message ?? 'Pipeline complete')
      await loadAll()             // refresh data after run
    } catch {
      setPipelineMsg('Pipeline call failed — check Render logs')
    } finally {
      setPipelineRunning(false)
    }
  }

  // ── Derived ────────────────────────────────────────────────────────────────
  const selectedId = selectedRecord?.req_id || selectedRecord?.email_id || selectedRecord?.id

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="h-screen flex flex-col bg-bg text-gray-200 font-sans overflow-hidden">

      {/* ── Topbar ── */}
      <header className="flex-shrink-0 flex items-center justify-between
                         px-5 py-3 border-b border-border bg-surface">
        <div className="flex items-center gap-3">
          <span className="font-mono text-accent font-semibold text-sm tracking-tight">
            MailCRM
          </span>
          <span className="text-gray-700 text-xs font-mono hidden sm:block">
            GET Global · BD Pipeline
          </span>
          {apiError && (
            <span className="text-red-400 text-xs font-mono ml-2">{apiError}</span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {pipelineMsg && (
            <span className="text-xs font-mono text-gray-400 hidden md:block">
              {pipelineMsg}
            </span>
          )}
          <button
            onClick={handleRunPipeline}
            disabled={pipelineRunning}
            className="flex items-center gap-1.5 bg-accent/10 border border-accent/40
                       text-accent text-xs font-mono px-4 py-1.5 rounded
                       hover:bg-accent/20 transition-colors
                       disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {pipelineRunning ? '⟳ Running…' : '▶ Run Pipeline'}
          </button>
        </div>
      </header>

      {/* ── Main area: left panel + right detail panel ── */}
      <div className="flex flex-1 min-h-0">

        {/* Left panel — shrinks when detail panel opens */}
        <div
          className={[
            'flex flex-col min-h-0 transition-all duration-300',
            selectedRecord ? 'w-[60%]' : 'w-full',
          ].join(' ')}
        >
          <StatsBar    stats={stats}  loading={statsLoading} />
          <PipelineBar stats={stats}  loading={statsLoading} />
          <RecordsTable
            records={records}
            loading={recsLoading}
            selectedId={selectedId}
            onSelect={setSelectedRecord}
          />
        </div>

        {/* Right panel — slides in when a record is selected */}
        {selectedRecord && (
          <div className="w-[40%] flex-shrink-0 min-h-0 overflow-hidden">
            <DetailPanel
              record={selectedRecord}
              onClose={() => setSelectedRecord(null)}
            />
          </div>
        )}
      </div>
    </div>
  )
}
