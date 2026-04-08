import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export default function App() {
  const [summary, setSummary] = useState(null)
  const [companies, setCompanies] = useState([])
  const [selected, setSelected] = useState('')
  const [forecast, setForecast] = useState(null)

  useEffect(() => {
    async function load() {
      const [sumRes, compRes] = await Promise.all([axios.get(`${API_URL}/summary`), axios.get(`${API_URL}/companies`)])
      setSummary(sumRes.data)
      setCompanies(compRes.data)
      if (compRes.data.length) setSelected(compRes.data[0].company_id)
    }
    load()
  }, [])

  useEffect(() => {
    async function loadForecast() {
      if (!selected) return
      const res = await axios.get(`${API_URL}/forecast/${selected}?months=12`)
      setForecast(res.data)
    }
    loadForecast()
  }, [selected])

  const chartData = useMemo(() => forecast ? [...forecast.history, ...forecast.forecast] : [], [forecast])

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24, fontFamily: 'Arial, sans-serif' }}>
      <h1>CarbonLens React Dashboard</h1>
      {summary && <p>Companies: {summary.company_count} · Avg ESG: {summary.average_esg_score} · High Risk: {summary.high_risk_companies}</p>}
      <div style={{ marginBottom: 16 }}>
        <select value={selected} onChange={e => setSelected(e.target.value)}>
          {companies.map(c => <option key={c.company_id} value={c.company_id}>{c.company_name}</option>)}
        </select>
      </div>
      <div style={{ background: 'white', padding: 20, borderRadius: 16, boxShadow: '0 8px 24px rgba(0,0,0,0.08)' }}>
        <div style={{ height: 380 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#0f766e" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {forecast && <p>{forecast.commentary}</p>}
      </div>
    </div>
  )
}
