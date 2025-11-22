'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, MapPin, TrendingUp } from 'lucide-react'

interface Source {
  ip: string
  count: number
  avg_score: number
}

export default function TopSources() {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSources()
    const interval = setInterval(fetchSources, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchSources = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/detections/top-sources?limit=8')
      const data = await res.json()
      setSources(Array.isArray(data) ? data : [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching sources:', error)
      setSources([])
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 h-80 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading sources...</div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
      <div className="space-y-3">
        {sources.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No threat sources detected</p>
          </div>
        ) : (
          sources.map((source, idx) => {
            const scorePercent = (source.avg_score * 100).toFixed(0)
            const severityColor = 
              source.avg_score >= 0.9 ? 'red' :
              source.avg_score >= 0.7 ? 'yellow' : 'blue'
            
            const colors: Record<string, string> = {
              red: 'bg-red-500',
              yellow: 'bg-yellow-500',
              blue: 'bg-blue-500'
            }

            return (
              <div
                key={source.ip}
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-700 text-xs font-bold text-gray-300">
                    {idx + 1}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <MapPin className="h-3 w-3 text-gray-500" />
                      <span className="text-sm font-mono text-white truncate">
                        {source.ip || 'Unknown'}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-3 text-xs text-gray-400">
                      <span>{source.count} attacks</span>
                      <span className="text-gray-600">•</span>
                      <span>Avg: {scorePercent}%</span>
                    </div>
                  </div>
                </div>

                <div className={`h-2 w-16 bg-gray-700 rounded-full overflow-hidden`}>
                  <div 
                    className={`h-full ${colors[severityColor]} transition-all duration-500`}
                    style={{ width: `${scorePercent}%` }}
                  ></div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
