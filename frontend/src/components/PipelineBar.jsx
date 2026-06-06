// PipelineBar — horizontal stage count boxes from stats.status_breakdown

// Short display labels for long stage names so boxes don't overflow
const SHORT = {
  'Under Internal Review':    'Internal Review',
  'Client Reviewing Profiles':'Client Review',
  'CVs Shared with Client':   'CVs Shared',
  'Interview Scheduled':      'Interview',
  'Offer Made':               'Offer Made',
  'Candidate Mobilized':      'Mobilized',
  'Cancelled':                'Cancelled',
  'On Hold':                  'On Hold',
  'Done':                     'Done',
}

export default function PipelineBar({ stats, loading }) {
  const breakdown = stats?.status_breakdown ?? {}
  const stages    = Object.entries(breakdown).sort(([, a], [, b]) => b - a)

  return (
    <div className="px-4 pb-3 flex-shrink-0">
      <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-2">
        Pipeline Stages
      </div>

      {loading ? (
        <div className="h-14 flex items-center">
          <span className="text-gray-600 text-xs font-mono">Loading…</span>
        </div>
      ) : stages.length === 0 ? (
        <div className="h-14 flex items-center">
          <span className="text-gray-600 text-xs font-mono">No stage data</span>
        </div>
      ) : (
        <div className="flex gap-2 overflow-x-auto pb-1 hide-scrollbar">
          {stages.map(([stage, count]) => (
            <div
              key={stage}
              className="flex-shrink-0 bg-surface border border-border rounded-md px-3 py-2 text-center min-w-[90px]"
            >
              <div className="text-accent font-mono font-semibold text-xl leading-none">
                {count}
              </div>
              <div className="text-gray-500 text-[10px] font-mono mt-1 leading-tight whitespace-nowrap">
                {SHORT[stage] ?? stage}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
