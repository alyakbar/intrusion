'use client'

import { useEffect, useState } from 'react'
import { Server, Shield, Activity, AlertTriangle, Network, TrendingUp } from 'lucide-react'

interface TargetedPort {
  port: number
  protocol: string
  total_hits: number
  anomaly_hits: number
  avg_anomaly_score: number
  threat_level: string
}

interface PortScanner {
  source_ip: string
  ports_targeted: number
  total_packets: number
  first_seen: string
  last_seen: string
  scan_type: string
}

interface OpenPort {
  port: number
  protocol: string
  confidence: number
  connections: number
  service: string
}

export default function PortActivityDashboard() {
  const [targetedPorts, setTargetedPorts] = useState<TargetedPort[]>([])
  const [scanners, setScanners] = useState<PortScanner[]>([])
  const [openPorts, setOpenPorts] = useState<OpenPort[]>([])
  const [distribution, setDistribution] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [portsRes, scannersRes, openRes, distRes] = await Promise.all([
        fetch('http://localhost:5000/api/ports/targeted?limit=10'),
        fetch('http://localhost:5000/api/ports/scanners'),
        fetch('http://localhost:5000/api/ports/open'),
        fetch('http://localhost:5000/api/ports/distribution')
      ])

      const portsData = await portsRes.json()
      const scannersData = await scannersRes.json()
      const openData = await openRes.json()
      const distData = await distRes.json()

      setTargetedPorts(Array.isArray(portsData) ? portsData : [])
      setScanners(scannersData.suspected_scanners || [])
      setOpenPorts(Array.isArray(openData) ? openData : [])
      setDistribution(distData || {})
      setLoading(false)
    } catch (error) {
      console.error('Error fetching port data:', error)
      setLoading(false)
    }
  }

  const getThreatColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'low': return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-12 bg-gray-800 rounded"></div>
          <div className="h-64 bg-gray-800 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Network className="h-8 w-8 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Port Activity Monitor</h1>
            <p className="text-sm text-gray-400">Network port scanning and traffic analysis</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Targeted Ports</span>
            <AlertTriangle className="h-5 w-5 text-red-400" />
          </div>
          <p className="text-2xl font-bold text-white">{targetedPorts.length}</p>
        </div>
        
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Port Scanners</span>
            <Activity className="h-5 w-5 text-orange-400" />
          </div>
          <p className="text-2xl font-bold text-white">{scanners.length}</p>
        </div>
        
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Likely Open Ports</span>
            <Server className="h-5 w-5 text-green-400" />
          </div>
          <p className="text-2xl font-bold text-white">{openPorts.length}</p>
        </div>
        
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Service Categories</span>
            <TrendingUp className="h-5 w-5 text-blue-400" />
          </div>
          <p className="text-2xl font-bold text-white">{Object.keys(distribution).length}</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Targeted Ports */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Shield className="h-5 w-5 text-red-400" />
            Most Targeted Ports
          </h2>
          
          {targetedPorts.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No targeted ports detected</p>
          ) : (
            <div className="space-y-3">
              {targetedPorts.map((port, idx) => (
                <div key={idx} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl font-bold text-white">{port.port}</span>
                      <span className="text-xs px-2 py-1 rounded bg-blue-500/20 border border-blue-500/40 text-blue-400 font-semibold">
                        {port.protocol}
                      </span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded border font-medium ${getThreatColor(port.threat_level)}`}>
                      {port.threat_level.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="flex gap-4 text-xs text-gray-400">
                    <span>Total: {port.total_hits}</span>
                    <span>•</span>
                    <span className="text-red-400">Anomalies: {port.anomaly_hits}</span>
                    <span>•</span>
                    <span>Avg Score: {(port.avg_anomaly_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Open Ports */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Server className="h-5 w-5 text-green-400" />
            Likely Open Ports
          </h2>
          
          {openPorts.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No open ports detected</p>
          ) : (
            <div className="space-y-2">
              {openPorts.map((port, idx) => (
                <div key={idx} className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-white">{port.port}</span>
                      <span className="text-xs px-2 py-1 rounded bg-blue-500/20 border border-blue-500/40 text-blue-400 font-semibold">
                        {port.protocol}
                      </span>
                      <span className="text-sm text-gray-300">{port.service}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-xs text-gray-400">{port.confidence}%</div>
                      <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-green-500"
                          style={{ width: `${port.confidence}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {port.connections} connections
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Port Scanners */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-orange-400" />
            Suspected Port Scanners
          </h2>
          
          {scanners.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No port scanning activity detected</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800/50 border-b border-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Source IP</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Protocol</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Ports Targeted</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Total Packets</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Scan Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {scanners.map((scanner, idx) => (
                    <tr key={idx} className="hover:bg-gray-800/30">
                      <td className="px-4 py-3 text-sm font-mono text-white">{scanner.source_ip}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-1 rounded bg-blue-500/20 border border-blue-500/40 text-blue-400 font-semibold">
                          TCP
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-orange-400 font-bold">{scanner.ports_targeted}</td>
                      <td className="px-4 py-3 text-sm text-gray-300">{scanner.total_packets}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-1 rounded bg-orange-500/10 border border-orange-500/30 text-orange-400">
                          {scanner.scan_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-400">
                        {new Date(scanner.first_seen).toLocaleTimeString()} - {new Date(scanner.last_seen).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Service Distribution */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-400" />
            Service Distribution
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(distribution).map(([service, count]) => (
              <div key={service} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <div className="text-2xl font-bold text-white mb-1">{count}</div>
                <div className="text-xs text-gray-400">{service}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
