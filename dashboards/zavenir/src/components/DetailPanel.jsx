// DetailPanel — right panel showing all fields for a selected Zavenir record.

function isEmpty(v) {
  return v === undefined || v === null || v === '' || v === 'null' || v === 'None' || v === 'N/A'
}

function Field({ label, value, mono = false }) {
  if (isEmpty(value)) return null
  return (
    <div className="mb-3">
      <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-0.5">
        {label}
      </div>
      <div className={`text-sm text-gray-200 leading-snug ${mono ? 'font-mono' : 'font-sans'}`}>
        {String(value)}
      </div>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div className="mb-5">
      <div className="text-[10px] font-mono text-accent uppercase tracking-widest pb-1.5
                      border-b border-border mb-3">
        {title}
      </div>
      {children}
    </div>
  )
}

function ConfidenceMeter({ value }) {
  if (isEmpty(value)) return null
  const pct = Math.round(parseFloat(value) * 100)
  const color    = pct >= 80 ? 'text-green-400' : pct >= 60 ? 'text-amber-400' : 'text-red-400'
  const barColor = pct >= 80 ? 'bg-green-400'   : pct >= 60 ? 'bg-amber-400'   : 'bg-red-400'
  return (
    <div className="mb-4">
      <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-1">
        AI Confidence
      </div>
      <div className="flex items-center gap-3">
        <div className={`text-2xl font-mono font-semibold ${color}`}>{pct}%</div>
        <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all ${barColor}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  )
}

export default function DetailPanel({ record, onClose }) {
  if (!record) return null

  const qtyDisplay = record.quantity
    ? `${record.quantity}${record.quantity_unit ? ' ' + record.quantity_unit : ''}`
    : null

  return (
    <div className="h-full flex flex-col bg-surface border-l border-border overflow-hidden">

      {/* ── Header ── */}
      <div className="flex-shrink-0 px-5 pt-4 pb-3 border-b border-border">

        {/* Back button — mobile only */}
        <button
          onClick={onClose}
          className="md:hidden flex items-center gap-1 font-mono text-xs text-gray-500
                     hover:text-accent transition-colors mb-3"
        >
          &#8592; Back
        </button>

        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="font-mono text-[10px] text-accent tracking-widest mb-1">
              {record.req_id || 'NO ID'}
            </div>
            <div className="text-white font-semibold text-base leading-snug truncate">
              {record.product_category || 'Unknown Product'}
            </div>
            <div className="text-gray-400 text-sm mt-0.5 truncate">
              {record.customer || 'Unknown Customer'}
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close detail panel"
            className="flex-shrink-0 text-gray-600 hover:text-white transition-colors
                       text-base font-mono leading-none mt-0.5"
          >
            &#x2715;
          </button>
        </div>

        {/* Status badge */}
        <div className="mt-3 flex gap-2 flex-wrap">
          {!isEmpty(record.status) && (
            <span className="bg-accent/10 border border-accent/30 text-accent
                             text-[10px] font-mono px-2.5 py-1 rounded">
              {record.status}
            </span>
          )}
          {!isEmpty(record.industry_segment) && (
            <span className="bg-surface border border-border text-gray-300
                             text-[10px] font-mono px-2.5 py-1 rounded">
              {record.industry_segment}
            </span>
          )}
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div className="flex-1 overflow-y-auto px-5 py-4">

        <Section title="Enquiry">
          <Field label="Customer"          value={record.customer} />
          <Field label="Industry Segment"  value={record.industry_segment} />
          <Field label="Email Subject"     value={record.email_subject} />
        </Section>

        <Section title="Product">
          <Field label="Product Category" value={record.product_category} />
          <Field label="Product Brand"    value={record.product_brand} />
          <Field label="Quantity"         value={qtyDisplay} />
        </Section>

        <Section title="Location and Dates">
          <Field label="Location"      value={record.location} />
          <Field label="Delivery Date" value={record.delivery_date} mono />
          <Field label="Received"      value={record.received_date} mono />
        </Section>

        <Section title="AI Analysis">
          <ConfidenceMeter value={record.llm_confidence} />
          <Field label="Summary"     value={record.email_summary} />
          <Field label="Next Action" value={record.next_action} />
        </Section>

        <div className="mt-2 pt-3 border-t border-border">
          <Field label="Req ID"       value={record.req_id}       mono />
          <Field label="Sender Email" value={record.sender_email} mono />
        </div>

      </div>
    </div>
  )
}
