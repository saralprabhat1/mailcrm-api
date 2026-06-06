// useApi.js — all API calls for the MailCRM dashboard
// Functions are module-level so they are stable references (safe in useEffect deps).

const API_BASE = 'https://mailcrm-api.onrender.com'

async function _get(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function _post(path) {
  const res = await fetch(`${API_BASE}${path}`, { method: 'POST' })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const fetchStats    = () => _get('/stats')
export const fetchRecords  = () => _get('/records')
export const fetchRecord   = (emailId) => _get(`/records/${emailId}`)
export const runPipeline   = () => _post('/run-pipeline')

// Hook wrapper — returns the stable function refs.
// Consume as: const { fetchStats, fetchRecords, runPipeline } = useApi()
export function useApi() {
  return { fetchStats, fetchRecords, fetchRecord, runPipeline }
}
