// LoginScreen — password gate. Auth lives in React memory only; refresh = re-login.

import { useState, useRef, useEffect } from 'react'

const CORRECT_PASSWORD = 'MailCRM@2026'

export default function LoginScreen({ onAuth }) {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const [shake, setShake] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => { inputRef.current?.focus() }, [])

  function handleSubmit(e) {
    e.preventDefault()
    if (value === CORRECT_PASSWORD) {
      onAuth()
    } else {
      setError('Incorrect password.')
      setValue('')
      setShake(true)
      setTimeout(() => setShake(false), 400)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-bg">

      {/* Subtle grid texture */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            'linear-gradient(#00d4aa 1px, transparent 1px), linear-gradient(90deg, #00d4aa 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
        aria-hidden
      />

      <div className="relative w-full max-w-sm mx-4">
        <div className="bg-surface border border-border rounded-lg px-8 py-10">

          <div className="mb-8 text-center">
            <div className="font-mono text-accent font-semibold text-2xl tracking-tight mb-1">
              MailCRM
            </div>
            <div className="font-mono text-[11px] text-gray-600 uppercase tracking-widest">
              Zavenir Daubert · Sales Pipeline
            </div>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            <label className="block font-mono text-[10px] text-gray-500 uppercase tracking-widest mb-1.5">
              Password
            </label>

            <input
              ref={inputRef}
              type="password"
              value={value}
              onChange={e => { setValue(e.target.value); setError('') }}
              placeholder="Enter password"
              autoComplete="current-password"
              className={[
                'w-full bg-bg border rounded px-3 py-2.5 text-sm font-mono text-gray-200',
                'placeholder-gray-700 outline-none transition-colors',
                shake ? 'border-red-500' : error ? 'border-red-500/60' : 'border-border',
                'focus:border-accent/60',
              ].join(' ')}
            />

            <div className="h-5 mt-2">
              {error && (
                <p className="font-mono text-[11px] text-red-400">{error}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={!value}
              className="mt-3 w-full bg-accent/10 border border-accent/40 text-accent
                         font-mono text-sm py-2.5 rounded
                         hover:bg-accent/20 transition-colors
                         disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Unlock
            </button>
          </form>

          <p className="mt-8 text-center font-mono text-[10px] text-gray-700">
            Access restricted · MailCRM internal
          </p>
        </div>
      </div>
    </div>
  )
}
