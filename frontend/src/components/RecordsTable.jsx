// RecordsTable — searchable, filterable list of CRM requirements.
// Clicking a row calls onSelect(record).

import { useState, useMemo } from 'react'

// Map status strings → badge colour classes
const STATUS_STYLES = {
  'active':                   'text-accent  border-accent/30  bg-accent/10',
  'in progress':               'text-blue-400 border-blue-400/30 bg-blue-400/10',
  'under internal review':     'text-purple-400 border-purple-400/30 bg-purple-400/10',
  'client reviewing profiles': 'text-sky-400 border-sky-400/30 bg-sky-400/10',
  'cvs shared with client':    'text-cyan-400 border-cyan-400/30 bg-cyan-400/10',
  'interview scheduled':       'text-yellow-400 border-yellow-400/30 bg-yellow-400/10',
  'offer made':                'text-orange-400 border-orange-400/30 bg-orange-400/10',
  'candidate mobilized':       'text-green-400 border-green-400/30 bg-green-400/10',
  'done':                      'text-green-400 border-green-400/30 bg-green-400/10',
  'on hold':                   'text-amber-400 border-amber-400/30 bg-amber-400/10',
  'cancelled':                 'text-red-400   border-red-400/30   bg-red-400/10',
}

function badgeClass(status) {
  return STATUS_STYLES[(status ?? '').toLowerCase()] ??
    'text-gray-400 border-gray-600 bg-gray-800'
}

function formatDate(raw) {
  if (!raw) return '—'
  // show first 10 chars: "2026-06-05"
  return String(raw).slice(0, 10)
}

export default function RecordsTable({ records, loading, selectedId, onSelect }) {
  const [search, setSearch]           = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  // Build unique status list for the dropdown
  const statuses = useMemo(() => {
    const seen = new Set()
    records.forEach(r => { if (r.status) seen.add(r.status) })
    return ['all', ...Array.from(seen).sort()]
  }, [records])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return records.filter(r => {
      const matchSearch = !q ||
        (r.req_id        ?? '').toLowerCase().includes(q) ||
        (r.client_name   ?? '').toLowerCase().includes(q) ||
        (r.location      ?? '').toLowerCase().includes(q) ||
        (r.client_country ?? '').toLowerCase().includes(q) ||
        (r.psl_categories ?? '').toLowerCase().includes(q) ||
        (r.designation   ?? '').toLowerCase().includes(q)
      const matchStatus =
        statusFilter === 'all' || r.status === statusFilter
      return matchSearch && matchStatus
    })
  }, [records, search, statusFilter])

  const rowKey = r => r.req_id || r.email_id || r.id

  return (
    <div className="flex flex-col flex-1 min-h-0 px-4 pb-4">

      {/* Search + filter row */}
      <div className="flex gap-2 mb-3 flex-shrink-0">
        <input
          type="text"
          placeholder="Search client, ID, role, location…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 bg-surface border border-border rounded px-3 py-1.5 text-sm
                     text-gray-200 placeholder-gray-600 font-sans
                     focus:outline-none focus:border-accent/50 transition-colors"
        />
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="bg-surface border border-border rounded px-3 py-1.5 text-sm
                     text-gray-300 font-sans focus:outline-none focus:border-accent/50
                     transition-colors cursor-pointer"
        >
          <option value="all">All statuses</option>
          {statuses.slice(1).map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-y-auto rounded-lg border border-border min-h-0">
        <table className="w-full text-sm border-collapse">
          <thead className="sticky top-0 z-10 bg-surface">
            <tr className="border-b border-border">
              {['Req ID', 'Client', 'Role', 'PSL', 'Location', 'Status', 'Received'].map(h => (
                <th
                  key={h}
                  className="text-left px-3 py-2.5 font-mono text-[10px] text-gray-500
                             uppercase tracking-widest whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="text-center py-16 text-gray-600 font-mono text-xs">
                  Fetching records…
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-16 text-gray-600 font-mono text-xs">
                  {records.length === 0 ? 'No records yet — run the pipeline.' : 'No matches.'}
                </td>
              </tr>
            ) : filtered.map(record => {
              const key     = rowKey(record)
              const active  = selectedId === key
              return (
                <tr
                  key={key}
                  onClick={() => onSelect(record)}
                  className={[
                    'border-b border-border/40 cursor-pointer transition-colors',
                    'hover:bg-white/[0.025]',
                    active ? 'bg-accent/[0.06] border-l-2 border-l-accent' : '',
                  ].join(' ')}
                >
                  <td className="px-3 py-2.5 font-mono text-[11px] text-accent whitespace-nowrap">
                    {record.req_id || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-200 whitespace-nowrap max-w-[140px] truncate">
                    {record.client_name || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-300 whitespace-nowrap max-w-[130px] truncate text-xs">
                    {record.designation || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-500 text-xs whitespace-nowrap">
                    {record.psl_categories || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-500 text-xs whitespace-nowrap">
                    {record.location || record.client_country || '—'}
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`inline-block border rounded-full px-2 py-0.5 text-[10px] font-mono whitespace-nowrap ${badgeClass(record.status)}`}>
                      {record.status || 'unknown'}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[11px] text-gray-600 whitespace-nowrap">
                    {formatDate(record.received_date)}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Row count */}
      <div className="text-[10px] text-gray-600 font-mono mt-2 flex-shrink-0">
        {filtered.length} of {records.length} records
      </div>
    </div>
  )
}
