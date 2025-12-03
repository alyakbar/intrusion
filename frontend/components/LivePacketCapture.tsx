'use client'

import { useEffect, useState } from 'react'
import { Activity, Wifi, TrendingUp, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

interface CaptureStats {
  isActive: boolean
  totalPackets: number
  anomaliesDetected: number
  recentPackets: any[]
  anomalyRate: number
  lastUpdate: string
}

export default function LivePacketCapture() {
  const [stats, setStats] = useState<CaptureStats>({
    isActive: false,
    totalPackets: 0,
    anomaliesDetected: 0,
    recentPackets: [],
    anomalyRate: 0,
    lastUpdate: new Date().toISOString()
  })
  const [recentActivity, setRecentActivity] = useState<any[]>([])

  useEffect(() => {
    fetchCaptureStats()
    const interval = setInterval(() => {
      fetchCaptureStats()
    }, 2000) // Update every 2 seconds for real-time feel
    return () => clearInterval(interval)
  }, [])

  const fetchCaptureStats = async () => {
    try {
      // Fetch system status to check if detection is actually running
      const statusRes = await fetch('http://localhost:5000/api/system/status')
      const statusData = await statusRes.json()
      
      // Fetch overall stats
      const statsRes = await fetch('http://localhost:5000/api/detections/stats')
      const statsData = await statsRes.json()
      
      // Fetch recent detections
      const recentRes = await fetch('http://localhost:5000/api/detections/recent?limit=20')
      const recentData = await recentRes.json()
      
      // Use system status to determine if actually capturing
      const isActive = statusData.is_capturing_packets || false;
      
      // Store system status for display
      (window as any).systemStatus = statusData;
      
      setStats({
        isActive,
        totalPackets: statsData.total_packets || 0,
        anomaliesDetected: statsData.total_anomalies || 0,
        recentPackets: recentData.slice(0, 10),
        anomalyRate: statsData.anomaly_rate || 0,
        lastUpdate: new Date().toISOString()
      })
      
      // Update recent activity feed
      setRecentActivity(prev => {
        const newActivity = recentData.slice(0, 5).map((d: any) => ({
          ...d,
          justAdded: !prev.some(p => p.id === d.id)
        }))
        return newActivity
      })
    } catch (error) {
      console.error('Error fetching capture stats:', error)
      setStats(prev => ({ ...prev, isActive: false }))
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'low': return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 1000) return 'Just now'
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    return date.toLocaleTimeString()
  }

  return (
    <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
      {/* Header with Status */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${stats.isActive ? 'bg-green-500/10' : 'bg-gray-500/10'}`}>
            <Wifi className={`h-6 w-6 ${stats.isActive ? 'text-green-500' : 'text-gray-500'}`} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Live Packet Capture</h3>
            <p className="text-sm text-gray-400">
              {(window as any).systemStatus?.process_info?.inject_rate > 0 
                ? `Demo mode (${((window as any).systemStatus.process_info.inject_rate * 100).toFixed(0)}% synthetic anomalies)`
                : 'Real-time network monitoring'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Synthetic Mode Badge */}
          {(window as any).systemStatus?.process_info?.inject_rate > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border bg-amber-500/10 border-amber-500/30 mr-2">
              <AlertCircle className="h-4 w-4 text-amber-400" />
              <span className="text-sm text-amber-400 font-medium">Dummy Data</span>
            </div>
          )}
          
          {/* Status Badge */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${
            stats.isActive 
              ? 'bg-green-500/10 border-green-500/30' 
              : 'bg-gray-500/10 border-gray-500/30'
          }`}>
            {stats.isActive ? (
              <>
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-400 font-medium">Active</span>
              </>
            ) : (
              <>
                <div className="h-2 w-2 bg-gray-500 rounded-full"></div>
                <span className="text-sm text-gray-400 font-medium">
                  {(window as any).systemStatus?.status === 'waiting' ? 'Waiting' : 
                   (window as any).systemStatus?.status === 'stopped' ? 'Stopped' : 'Idle'}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-4 w-4 text-blue-500" />
            <span className="text-xs text-gray-400 uppercase tracking-wide">Total Packets</span>
          </div>
          <p className="text-2xl font-bold text-white">{stats.totalPackets.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">Processed</p>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <span className="text-xs text-gray-400 uppercase tracking-wide">Anomalies</span>
          </div>
          <p className="text-2xl font-bold text-red-400">{stats.anomaliesDetected.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">Detected</p>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-4 w-4 text-purple-500" />
            <span className="text-xs text-gray-400 uppercase tracking-wide">Detection Rate</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">{stats.anomalyRate.toFixed(1)}%</p>
          <p className="text-xs text-gray-500 mt-1">Anomaly ratio</p>
        </div>
      </div>

      {/* Recent Activity Feed */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-gray-300">Recent Activity</h4>
          <span className="text-xs text-gray-500">Last updated: {formatTimestamp(stats.lastUpdate)}</span>
        </div>
        
        <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-800">
          {recentActivity.length > 0 ? (
            recentActivity.map((packet, idx) => (
              <div
                key={packet.id}
                className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${
                  packet.justAdded ? 'bg-blue-500/5 border-blue-500/30 animate-pulse' : 'bg-gray-800/30 border-gray-700/50'
                }`}
              >
                <div className={`p-1.5 rounded ${packet.is_anomaly ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                  {packet.is_anomaly ? (
                    <XCircle className="h-4 w-4 text-red-400" />
                  ) : (
                    <CheckCircle className="h-4 w-4 text-green-400" />
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono text-gray-300 truncate">
                      {packet.source_ip} → {packet.dest_ip}
                    </span>
                    {packet.severity && (
                      <span className={`text-xs px-2 py-0.5 rounded border ${getSeverityColor(packet.severity)}`}>
                        {packet.severity}
                      </span>
                    )}
                  </div>
                  {((packet as any).source_hostname || (packet as any).dest_hostname) && (
                    <div className="text-xs text-blue-400 truncate mt-0.5">
                      {(packet as any).source_hostname && <span>{(packet as any).source_hostname}</span>}
                      {(packet as any).source_hostname && (packet as any).dest_hostname && <span> → </span>}
                      {(packet as any).dest_hostname && <span>{(packet as any).dest_hostname}</span>}
                    </div>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 border border-blue-500/40 text-blue-400 font-semibold">
                      {packet.protocol || 'Unknown'}
                    </span>
                    {packet.dest_port && packet.dest_port > 0 && (
                      <>
                        <span className="text-xs text-gray-600">•</span>
                        <span className="text-xs text-orange-400 font-mono">Port {packet.dest_port}</span>
                      </>
                    )}
                    <span className="text-xs text-gray-600">•</span>
                    <span className="text-xs text-gray-500">Score: {packet.anomaly_score?.toFixed(3) || '0.000'}</span>
                  </div>
                </div>
                
                <span className="text-xs text-gray-500 whitespace-nowrap">
                  {formatTimestamp(packet.timestamp)}
                </span>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <Activity className="h-8 w-8 text-gray-600 mx-auto mb-2" />
              <p className="text-sm text-gray-500">No recent packet activity</p>
              <p className="text-xs text-gray-600 mt-1">Start detection to see live captures</p>
            </div>
          )}
        </div>
      </div>

      {/* Status Message */}
      {!stats.isActive && stats.totalPackets === 0 && (
        <div className="mt-4 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-yellow-400 font-medium">Detection Not Running</p>
              <p className="text-xs text-yellow-300/70 mt-1">
                Start packet capture to see real-time detections. Run: 
                <code className="ml-1 px-1.5 py-0.5 bg-gray-900 rounded text-yellow-400">
                  python anomaly_detection/main.py --mode detect
                </code>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
