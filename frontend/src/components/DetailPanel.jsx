// DetailPanel — right panel showing all fields for a selected CRM record.

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
  // Don't render if every child Field returned null
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

function PslTags({ value }) {
  if (isEmpty(value)) return null
  const tags = String(value).split(/[,;|]/).map(t => t.trim()).filter(Boolean)
  if (tags.length === 0) return null
  return (
    <div className="mb-3">
      <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-1.5">
        PSL Categories
      </div>
      <div className="flex flex-wrap gap-1.5">
        {tags.map(tag => (
          <span
            key={tag}
            className="bg-accent/10 border border-accent/30 text-accent text-[10px]
                       font-mono px-2 py-0.5 rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}

function ConfidenceMeter({ value }) {
  if (isEmpty(value)) return null
  const pct = Math.round(parseFloat(value) * 100)
  const color =
    pct >= 80 ? 'text-green-400'  :
    pct >= 60 ? 'text-amber-400'  :
                'text-red-400'
  const barColor =
    pct >= 80 ? 'bg-green-400'   :
    pct >= 60 ? 'bg-amber-400'   :
                'bg-red-400'
  return (
    <div className="mb-4">
      <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-1">
        AI Confidence
      </div>
      <div className="flex items-center gap-3">
        <div className={`text-2xl font-mono font-semibold ${color}`}>{pct}%</div>
        <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${barColor}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  )
}

function StatusBadge({ stage, status, urgency }) {
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {!isEmpty(stage)   && (
        <span className="bg-surface border border-border text-gray-300 text-[10px] font-mono px-2.5 py-1 rounded">
          {stage}
        </span>
      )}
      {!isEmpty(status)  && (
        <span className="bg-accent/10 border border-accent/30 text-accent text-[10px] font-mono px-2.5 py-1 rounded">
          {status}
        </span>
      )}
      {!isEmpty(urgency) && (
        <span className="bg-surface border border-border text-gray-400 text-[10px] font-mono px-2.5 py-1 rounded">
          ⚡ {urgency}
        </span>
      )}
    </div>
  )
}

export default function DetailPanel({ record, onClose }) {
  if (!record) return null

  return (
    <div className="h-full flex flex-col bg-surface border-l border-border overflow-hidden">

      {/* ── Header ── */}
      <div className="flex-shrink-0 px-5 pt-4 pb-3 border-b border-border">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="font-mono text-[10px] text-accent tracking-widest mb-1">
              {record.req_id || 'NO ID'}
            </div>
            <div className="text-white font-semibold text-base leading-snug truncate">
              {record.designation || 'Unknown Role'}
            </div>
            <div className="text-gray-400 text-sm mt-0.5 truncate">
              {record.client_name || 'Unknown Client'}
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close detail panel"
            className="flex-shrink-0 text-gray-600 hover:text-white transition-colors
                       text-base font-mono leading-none mt-0.5"
          >
            ✕
          </button>
        </div>

        <div className="mt-3">
          <StatusBadge
            stage={record.requirement_stage}
            status={record.status}
            urgency={record.urgency}
          />
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div className="flex-1 overflow-y-auto px-5 py-4">

        <Section title="Role Details">
          <Field label="Designation"  value={record.designation} />
          <Field label="Headcount"    value={record.headcount} />
          <Field label="Duration"     value={record.duration} />
          <Field label="Experience"   value={record.experience_years ? `${record.experience_years} yrs` : null} />
          <PslTags value={record.psl_categories} />
        </Section>

        <Section title="Location & Dates">
          <Field label="Location"          value={record.location || record.client_country} />
          <Field label="Mobilisation Date" value={record.mobilization_date} />
          <Field label="Deadline"          value={record.deadline} />
          <Field label="Received"          value={record.received_date} mono />
        </Section>

        <Section title="Client & Contact">
          <Field label="Client"   value={record.client_name} />
          <Field label="Country"  value={record.client_country} />
          <Field label="Contact"  value={record.contact_name} />
          <Field label="Email"    value={record.contact_email} mono />
          <Field label="Phone"    value={record.contact_phone} mono />
          <Field label="Ref No."  value={record.client_ref_number} mono />
        </Section>

        <Section title="Commercial">
          <Field label="Rates"               value={record.rates} />
          <Field label="Contract Type"       value={record.contract_type} />
          <Field label="Work Schedule"       value={record.work_schedule} />
          <Field label="Nationality Pref."   value={record.nationality_preference} />
          <Field label="Certifications"      value={record.certifications} />
          <Field label="Technical Req."      value={record.technical_requirements} />
        </Section>

        <Section title="AI Analysis">
          <ConfidenceMeter value={record.llm_confidence} />
          <Field label="Summary"        value={record.email_summary} />
          <Field label="Next Action"    value={record.next_action} />
          <Field label="Category"       value={record.category} />
          <Field label="Missing Fields" value={record.missing_fields_flag} mono />
        </Section>

        {/* Follow-up fields — only shown if present */}
        {(!isEmpty(record.is_follow_up) || !isEmpty(record.cvs_shared)) && (
          <Section title="Fulfilment">
            <Field label="Is Follow-up"     value={record.is_follow_up} />
            <Field label="CVs Requested"    value={record.cvs_requested} />
            <Field label="CVs Shared"       value={record.cvs_shared} />
            <Field label="Shortlisted"      value={record.profiles_shortlisted} />
            <Field label="Interview Date"   value={record.interview_date} />
            <Field label="Interview Result" value={record.interview_outcome} />
            <Field label="Selected"         value={record.candidate_selected} />
            <Field label="Mobilised"        value={record.candidate_mobilized} />
          </Section>
        )}

        {/* Req ID + sender at the very bottom for reference */}
        <div className="mt-2 pt-3 border-t border-border">
          <Field label="Req ID"       value={record.req_id}       mono />
          <Field label="Sender Email" value={record.sender_email} mono />
          <Field label="AM Owner"     value={record.am_owner} />
        </div>

      </div>
    </div>
  )
}
