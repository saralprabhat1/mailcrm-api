// App — Zavenir Daubert pipeline dashboard.
// Layout: fixed header / StatsBar / StatusBar on the left pane,
//         RecordsTable in the main pane, DetailPanel slides in on row click.

import { useState, useEffect, useCallback } from 'react'
import { fetchStats, fetchRecords } from './hooks/useApi'
import LoginScreen  from './components/LoginScreen'
import StatsBar     from './components/StatsBar'
import StatusBar    from './components/StatusBar'
import RecordsTable from './components/RecordsTable'
import DetailPanel  from './components/DetailPanel'

const AUTO_REFRESH_MS = 60_000

export default function App() {
  const [authed,   setAuthed]   = useState(false)
  const [stats,    setStats]    = useState(null)
  const [records,  setRecords]  = useState([])
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState(null)
  const [selected, setSelected] = useState(null)
  const [lastSync, setLastSync] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [s, r] = await Promise.all([fetchStats(), fetchRecords()])
      setStats(s)
      setRecords(Array.isArray(r) ? r : (r?.records ?? []))
      setLastSync(new Date())
    } catch (err) {
      setError(err?.message ?? 'Failed to load data.')
    } finally {
      setLoading(false)
    }
  }, [])

  // Load data once after login; then auto-refresh every minute.
  useEffect(() => {
    if (!authed) return
    load()
    const id = setInterval(load, AUTO_REFRESH_MS)
    return () => clearInterval(id)
  }, [authed, load])

  function handleSelect(row) {
    const key = row.req_id || row.id
    setSelected(prev => {
      const prevKey = prev?.req_id || prev?.id
      return prevKey === key ? null : row
    })
  }

  if (!authed) {
    return <LoginScreen onAuth={() => setAuthed(true)} />
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-bg text-gray-200 overflow-hidden">

      {/* ── Top header ── */}
      <header className="flex-shrink-0 flex items-center justify-between
                         px-5 py-3 border-b border-border bg-bg z-20">
        <div className="flex items-center gap-3">
          <span className="font-mono font-semibold text-accent text-base tracking-tight">
            MailCRM
          </span>
          <span className="hidden sm:block text-border text-lg font-thin select-none">/</span>
          <span className="hidden sm:block font-sans text-gray-400 text-sm">
            Zavenir Daubert
          </span>
        </div>

        <div className="flex items-center gap-4">
          {lastSync && (
            <span className="hidden md:block font-mono text-[10px] text-gray-600">
              synced {lastSync.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}

          <button
            onClick={load}
            disabled={loading}
            title="Refresh"
            className="font-mono text-xs text-gray-500 border border-border rounded px-3 py-1
                       hover:text-accent hover:border-accent/40 transition-colors
                       disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading…' : 'Refresh'}
          </button>
        </div>
      </header>

      {/* ── Error banner ── */}
      {error && (
        <div className="flex-shrink-0 bg-red-950/40 border-b border-red-900/40
                        px-5 py-2 font-mono text-xs text-red-400">
          {error}
        </div>
      )}

      {/* ── Main content (fills remaining height) ── */}
      <div className="flex flex-1 min-h-0">

        {/* Left sidebar: StatsBar + StatusBar */}
        <aside className="flex-shrink-0 w-64 flex flex-col border-r border-border overflow-y-auto">
          <div className="pt-4">
            <div className="px-4 mb-1 font-mono text-[10px] text-gray-600 uppercase tracking-widest">
              Overview
            </div>
          </div>

          {/* KPI cards stacked vertically in sidebar */}
          <div className="px-3 pt-2 pb-3 flex flex-col gap-2">
            {[
              { key: 'total_records',        label: 'Total Records',       icon: '◈' },
              { key: 'last_7_days',          label: 'Last 7 Days',         icon: '◷' },
              { key: 'active',               label: 'Active',              icon: '◉' },
              { key: 'top_product_category', label: 'Top Category',        icon: '◆' },
            ].map(({ key, label, icon }) => {
              const val = stats?.[key]
              return (
                <div
                  key={key}
                  className="bg-surface border border-border rounded-md px-3 py-2.5 flex items-center justify-between"
                >
                  <span className="font-mono text-[10px] text-gray-500 uppercase tracking-widest leading-tight">
                    {label}
                  </span>
                  <span className={[
                    'font-semibold font-mono leading-none',
                    typeof val === 'string' && val.length > 10 ? 'text-xs text-gray-300' : 'text-base text-white',
                    loading ? 'text-gray-600' : '',
                  ].join(' ')}>
                    {loading ? '—' : (val !== undefined && val !== null ? String(val) : '—')}
                  </span>
                </div>
              )
            })}
          </div>

          {/* Status breakdown */}
          <div className="px-3 pb-4 mt-1">
            <div className="font-mono text-[10px] text-gray-600 uppercase tracking-widest mb-2 px-1">
              Status Breakdown
            </div>
            {loading ? (
              <div className="text-gray-700 font-mono text-xs px-1">Loading…</div>
            ) : stats?.status_breakdown ? (
              <div className="flex flex-col gap-1.5">
                {Object.entries(stats.status_breakdown)
                  .sort(([, a], [, b]) => b - a)
                  .map(([status, count]) => (
                    <div
                      key={status}
                      className="bg-surface border border-border rounded px-3 py-2
                                 flex items-center justify-between"
                    >
                      <span className="font-mono text-[10px] text-gray-400 capitalize">{status}</span>
                      <span className="font-mono text-sm font-semibold text-accent">{count}</span>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="text-gray-700 font-mono text-[11px] px-1">No data</div>
            )}
          </div>

          {/* Footer note */}
          <div className="mt-auto px-4 pb-4 font-mono text-[9px] text-gray-700 leading-relaxed">
            Pipeline runs locally.<br />
            Dashboard reads Supabase via API.
          </div>
        </aside>

        {/* Main area: records table + detail panel */}
        <div className="flex flex-1 min-w-0 min-h-0">

          {/* Records table */}
          <div className={[
            'flex flex-col min-h-0 transition-all duration-200',
            selected ? 'flex-1' : 'flex-1',
          ].join(' ')}>
            <div className="px-4 pt-4 pb-2 flex-shrink-0 flex items-center justify-between">
              <h1 className="font-sans font-semibold text-white text-base">
                Requirements
              </h1>
              <span className="font-mono text-[10px] text-gray-600">
                {records.length} total
              </span>
            </div>

            <RecordsTable
              records={records}
              loading={loading}
              selectedId={selected?.req_id || selected?.id}
              onSelect={handleSelect}
            />
          </div>

          {/* Detail panel — slides in when a row is selected */}
          {selected && (
            <div className="flex-shrink-0 w-80 xl:w-96 min-h-0 overflow-hidden">
              <DetailPanel
                record={selected}
                onClose={() => setSelected(null)}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
