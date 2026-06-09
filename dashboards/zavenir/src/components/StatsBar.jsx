// StatsBar — 4 KPI cards for the Zavenir Daubert pipeline.

const CARDS = [
  { key: 'total_records',       label: 'Total Records',       icon: '◈' },
  { key: 'last_7_days',         label: 'Last 7 Days',         icon: '◷' },
  { key: 'active',              label: 'Active',              icon: '◉' },
  { key: 'top_product_category',label: 'Top Product Category',icon: '◆' },
]

export default function StatsBar({ stats, loading }) {
  return (
    <div className="grid grid-cols-4 gap-3 px-4 pt-4 pb-3 flex-shrink-0">
      {CARDS.map(({ key, label, icon }) => {
        const val = stats?.[key]
        return (
          <div
            key={key}
            className="bg-surface border border-border rounded-lg px-4 py-3 flex flex-col gap-1"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">
                {label}
              </span>
              <span className="text-gray-600 text-xs">{icon}</span>
            </div>
            <div className="text-2xl font-semibold text-white leading-none mt-1">
              {loading ? (
                <span className="text-gray-600 text-base">—</span>
              ) : val !== undefined && val !== null ? (
                <span className={typeof val === 'string' && val.length > 12 ? 'text-sm' : ''}>
                  {String(val)}
                </span>
              ) : (
                <span className="text-gray-600 text-base">—</span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
