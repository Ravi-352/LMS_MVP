/*import React, { useState } from 'react'

export default function AuthForm({ mode='signup' }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  return (
    <form onSubmit={e => {
      e.preventDefault()
      fetch(mode === 'signup' ? '/api/auth/signup' : '/api/auth/token', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ email, password })
      }).then(r => r.json()).then(data => alert(JSON.stringify(data)))
    }}>
      <div><input placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} /></div>
      <div><input placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} /></div>
      <button type="submit">{mode==='signup' ? 'Sign up' : 'Login'}</button>
    </form>
  )
}
*/