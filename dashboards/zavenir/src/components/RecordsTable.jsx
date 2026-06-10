// RecordsTable — searchable, filterable table of Zavenir CRM records.
// Columns: Req ID, Customer, Industry Segment, Product Category, Product Brand,
//          Quantity, Location, Delivery Date, Status, Received.
// Filters: search text, Status, Product Category, Industry Segment.

import { useState, useMemo } from 'react'

const STATUS_STYLES = {
  'new':         'text-accent  border-accent/30  bg-accent/10',
  'quoted':      'text-blue-400 border-blue-400/30 bg-blue-400/10',
  'won':         'text-green-400 border-green-400/30 bg-green-400/10',
  'lost':        'text-red-400  border-red-400/30  bg-red-400/10',
  'on hold':     'text-amber-400 border-amber-400/30 bg-amber-400/10',
  'in progress': 'text-sky-400  border-sky-400/30  bg-sky-400/10',
  'done':        'text-green-400 border-green-400/30 bg-green-400/10',
}

function badgeClass(status) {
  return STATUS_STYLES[(status ?? '').toLowerCase()] ??
    'text-gray-400 border-gray-600 bg-gray-800'
}

function fmt(raw) {
  return raw ? String(raw).slice(0, 10) : '—'
}

function uniq(records, key) {
  const seen = new Set()
  records.forEach(r => { if (r[key]) seen.add(r[key]) })
  return ['all', ...Array.from(seen).sort()]
}

const SELECT_CLS = `bg-surface border border-border rounded px-2.5 py-1.5 text-xs
                    text-gray-300 font-sans focus:outline-none focus:border-accent/50
                    transition-colors cursor-pointer`

export default function RecordsTable({ records, loading, selectedId, onSelect }) {
  const [search,   setSearch]   = useState('')
  const [statusF,  setStatusF]  = useState('all')
  const [categoryF,setCategoryF]= useState('all')
  const [segmentF, setSegmentF] = useState('all')

  const statuses   = useMemo(() => uniq(records, 'status'),           [records])
  const categories = useMemo(() => uniq(records, 'product_category'), [records])
  const segments   = useMemo(() => uniq(records, 'industry_segment'), [records])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return records.filter(r => {
      const matchSearch = !q ||
        (r.req_id           ?? '').toLowerCase().includes(q) ||
        (r.customer         ?? '').toLowerCase().includes(q) ||
        (r.product_brand    ?? '').toLowerCase().includes(q) ||
        (r.location         ?? '').toLowerCase().includes(q) ||
        (r.product_category ?? '').toLowerCase().includes(q) ||
        (r.industry_segment ?? '').toLowerCase().includes(q)
      const matchStatus   = statusF   === 'all' || r.status           === statusF
      const matchCategory = categoryF === 'all' || r.product_category === categoryF
      const matchSegment  = segmentF  === 'all' || r.industry_segment === segmentF
      return matchSearch && matchStatus && matchCategory && matchSegment
    })
  }, [records, search, statusF, categoryF, segmentF])

  const rowKey = r => r.req_id || r.id

  const COLS = [
    'Req ID', 'Customer', 'Segment', 'Product Category',
    'Brand', 'Qty', 'Location', 'Delivery', 'Status', 'Received',
  ]

  return (
    <div className="flex flex-col flex-1 min-h-0 min-w-0 px-4 pb-4">

      {/* ── Filter row ── */}
      <div className="flex gap-2 mb-3 flex-shrink-0 flex-wrap">
        <input
          type="text"
          placeholder="Search customer, brand, ID, location…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 min-w-[160px] bg-surface border border-border rounded px-3 py-1.5
                     text-sm text-gray-200 placeholder-gray-600 font-sans
                     focus:outline-none focus:border-accent/50 transition-colors"
        />

        {/* Status filter */}
        <select value={statusF} onChange={e => setStatusF(e.target.value)} className={SELECT_CLS}>
          <option value="all">All statuses</option>
          {statuses.slice(1).map(s => <option key={s} value={s}>{s}</option>)}
        </select>

        {/* Product Category filter */}
        <select value={categoryF} onChange={e => setCategoryF(e.target.value)} className={SELECT_CLS}>
          <option value="all">All categories</option>
          {categories.slice(1).map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        {/* Industry Segment filter */}
        <select value={segmentF} onChange={e => setSegmentF(e.target.value)} className={SELECT_CLS}>
          <option value="all">All segments</option>
          {segments.slice(1).map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {/* ── Table ── */}
      <div className="flex-1 overflow-auto rounded-lg border border-border min-h-0">
        <table className="w-full text-sm border-collapse">
          <thead className="sticky top-0 z-10 bg-surface">
            <tr className="border-b border-border">
              {COLS.map(h => (
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
                <td colSpan={COLS.length} className="text-center py-16 text-gray-600 font-mono text-xs">
                  Fetching records…
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={COLS.length} className="text-center py-16 text-gray-600 font-mono text-xs">
                  {records.length === 0 ? 'No records yet — run the pipeline.' : 'No matches.'}
                </td>
              </tr>
            ) : filtered.map(r => {
              const key    = rowKey(r)
              const active = selectedId === key
              return (
                <tr
                  key={key}
                  onClick={() => onSelect(r)}
                  className={[
                    'border-b border-border/40 cursor-pointer transition-colors hover:bg-white/[0.025]',
                    active ? 'bg-accent/[0.06] border-l-2 border-l-accent' : '',
                  ].join(' ')}
                >
                  <td className="px-3 py-2.5 font-mono text-[11px] text-accent whitespace-nowrap">
                    {r.req_id || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-200 whitespace-nowrap max-w-[130px] truncate">
                    {r.customer || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-400 text-xs whitespace-nowrap max-w-[110px] truncate">
                    {r.industry_segment || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-300 text-xs whitespace-nowrap max-w-[140px] truncate">
                    {r.product_category || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-400 text-xs whitespace-nowrap max-w-[100px] truncate">
                    {r.product_brand || '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-400 text-xs whitespace-nowrap">
                    {r.quantity ? `${r.quantity} ${r.quantity_unit || ''}`.trim() : '—'}
                  </td>
                  <td className="px-3 py-2.5 text-gray-500 text-xs whitespace-nowrap">
                    {r.location || '—'}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[11px] text-gray-500 whitespace-nowrap">
                    {fmt(r.delivery_date)}
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`inline-block border rounded-full px-2 py-0.5 text-[10px] font-mono whitespace-nowrap ${badgeClass(r.status)}`}>
                      {r.status || 'unknown'}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[11px] text-gray-600 whitespace-nowrap">
                    {fmt(r.received_date)}
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
