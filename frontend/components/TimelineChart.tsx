'use client'

import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function TimelineChart() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTimeline()
    const interval = setInterval(fetchTimeline, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [])

  const fetchTimeline = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/detections/timeline?hours=24')
      const timeline = await res.json()
      
      const formatted = timeline.map((item: any) => ({
        time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        total: item.total,
        anomalies: item.anomalies,
        normal: item.total - item.anomalies
      }))
      
      setData(formatted)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching timeline:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 h-80 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading timeline...</div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1F2937', 
              border: '1px solid #374151',
              borderRadius: '8px'
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="total" 
            stroke="#3B82F6" 
            strokeWidth={2}
            name="Total Packets"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="anomalies" 
            stroke="#EF4444" 
            strokeWidth={2}
            name="Anomalies"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="normal" 
            stroke="#10B981" 
            strokeWidth={2}
            name="Normal"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
