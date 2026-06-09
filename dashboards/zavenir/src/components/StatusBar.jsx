// StatusBar — horizontal status count boxes from stats.status_breakdown.
// Replaces PipelineBar for the Zavenir pipeline (no requirement stages here,
// just commercial statuses: New, Quoted, Won, Lost, On Hold).

export default function StatusBar({ stats, loading }) {
  const breakdown = stats?.status_breakdown ?? {}
  const statuses  = Object.entries(breakdown).sort(([, a], [, b]) => b - a)

  return (
    <div className="px-4 pb-3 flex-shrink-0">
      <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-2">
        Status Breakdown
      </div>

      {loading ? (
        <div className="h-14 flex items-center">
          <span className="text-gray-600 text-xs font-mono">Loading…</span>
        </div>
      ) : statuses.length === 0 ? (
        <div className="h-14 flex items-center">
          <span className="text-gray-600 text-xs font-mono">No status data</span>
        </div>
      ) : (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {statuses.map(([status, count]) => (
            <div
              key={status}
              className="flex-shrink-0 bg-surface border border-border rounded-md px-3 py-2 text-center min-w-[90px]"
            >
              <div className="text-accent font-mono font-semibold text-xl leading-none">
                {count}
              </div>
              <div className="text-gray-500 text-[10px] font-mono mt-1 leading-tight whitespace-nowrap">
                {status}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
