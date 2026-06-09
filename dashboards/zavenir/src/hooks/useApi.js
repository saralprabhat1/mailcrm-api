// useApi.js — API calls for the Zavenir Daubert dashboard.
// Reads from /zavenir/* endpoints on the shared MailCRM Render API.

const API_BASE = 'https://mailcrm-api.onrender.com'

async function _get(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const fetchStats   = () => _get('/zavenir/stats')
export const fetchRecords = () => _get('/zavenir/records')
