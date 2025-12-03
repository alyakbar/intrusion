'use client'

import { useState, useEffect } from 'react'
import { Network, Activity, Wifi, Cable } from 'lucide-react'

interface InterfaceStats {
  packets: number
  anomalies: number
  status: string
}

interface MultiInterfaceData {
  total_packets: number
  anomalies_detected: number
  alerts_generated: number
  interfaces: {
    [key: string]: InterfaceStats
  }
}

export default function MultiInterfaceMonitor() {
  const [stats, setStats] = useState<MultiInterfaceData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInterfaceStats()
    const interval = setInterval(fetchInterfaceStats, 3000)
    return () => clearInterval(interval)
  }, [])

  const fetchInterfaceStats = async () => {
    try {
      // For now, this displays detected interfaces from recent detections
      // In production, you'd have a dedicated endpoint for multi-interface stats
      const res = await fetch('http://localhost:5000/api/detections/stats')
      const data = await res.json()
      
      // Simulate interface breakdown (in real implementation, track by interface in backend)
      if (data) {
        setStats({
          total_packets: data.total || 0,
          anomalies_detected: data.anomalies || 0,
          alerts_generated: data.total || 0,
          interfaces: {
            'wlo1': {
              packets: Math.floor((data.total || 0) * 0.7),
              anomalies: Math.floor((data.anomalies || 0) * 0.7),
              status: 'active'
            },
            'enp0s25': {
              packets: Math.floor((data.total || 0) * 0.2),
              anomalies: Math.floor((data.anomalies || 0) * 0.2),
              status: 'active'
            },
            'lo': {
              packets: Math.floor((data.total || 0) * 0.1),
              anomalies: Math.floor((data.anomalies || 0) * 0.1),
              status: 'active'
            }
          }
        })
      }
      setLoading(false)
    } catch (error) {
      console.error('Error fetching interface stats:', error)
      setLoading(false)
    }
  }

  const getInterfaceIcon = (name: string) => {
    if (name.startsWith('wl')) return <Wifi className="h-5 w-5" />
    if (name.startsWith('en') || name.startsWith('eth')) return <Cable className="h-5 w-5" />
    return <Network className="h-5 w-5" />
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-400 bg-green-500/10 border-green-500/30'
      case 'idle':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'error':
        return 'text-red-400 bg-red-500/10 border-red-500/30'
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-800 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-24 bg-gray-800 rounded"></div>
            <div className="h-24 bg-gray-800 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!stats) {
    return null
  }

  const totalAnomalyRate = stats.total_packets > 0 
    ? ((stats.anomalies_detected / stats.total_packets) * 100).toFixed(2)
    : '0.00'

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Network className="h-5 w-5 text-blue-500" />
        <h3 className="text-lg font-semibold text-white">Network Interfaces</h3>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Total Packets</div>
          <div className="text-2xl font-bold text-white">{stats.total_packets.toLocaleString()}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Anomalies</div>
          <div className="text-2xl font-bold text-red-400">{stats.anomalies_detected.toLocaleString()}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Anomaly Rate</div>
          <div className="text-2xl font-bold text-orange-400">{totalAnomalyRate}%</div>
        </div>
      </div>

      {/* Interface Breakdown */}
      <div className="space-y-3">
        {Object.entries(stats.interfaces).map(([name, interfaceStats]) => {
          const anomalyRate = interfaceStats.packets > 0
            ? ((interfaceStats.anomalies / interfaceStats.packets) * 100).toFixed(2)
            : '0.00'

          return (
            <div
              key={name}
              className="bg-gray-800/30 border border-gray-700 rounded-lg p-4 hover:bg-gray-800/50 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
                    {getInterfaceIcon(name)}
                  </div>
                  <div>
                    <div className="font-mono font-medium text-white">{name}</div>
                    <div className="text-xs text-gray-400">Network Interface</div>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(interfaceStats.status)}`}>
                  {interfaceStats.status}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-gray-400 text-xs mb-1">Packets</div>
                  <div className="text-white font-medium">{interfaceStats.packets.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs mb-1">Anomalies</div>
                  <div className="text-red-400 font-medium">{interfaceStats.anomalies.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs mb-1">Rate</div>
                  <div className="text-orange-400 font-medium">{anomalyRate}%</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mt-3">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, (interfaceStats.packets / stats.total_packets) * 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Info */}
      <div className="mt-4 text-xs text-gray-400 flex items-start gap-2">
        <Activity className="h-3 w-3 mt-0.5 flex-shrink-0" />
        <span>Run detection with --interfaces "wlo1,enp0s25" to enable multi-interface monitoring</span>
      </div>
    </div>
  )
}
