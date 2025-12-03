'use client'

import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, Globe, Server, TrendingUp } from 'lucide-react'

interface ThreatData {
  abuseipdb?: {
    abuse_confidence_score: number
    country_code: string
    total_reports: number
    is_whitelisted: boolean
  }
  virustotal?: {
    malicious: number
    suspicious: number
    harmless: number
    reputation: number
  }
}

interface Detection {
  id: number
  timestamp: string
  source_ip: string
  threat_score?: number
  threat_intel?: {
    src_threat_intel?: ThreatData
    dst_threat_intel?: ThreatData
  }
}

export default function ThreatIntelligence() {
  const [detections, setDetections] = useState<Detection[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchThreatData()
    const interval = setInterval(fetchThreatData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchThreatData = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/detections/recent?limit=20')
      const data = await res.json()
      
      // Filter detections that have threat intelligence data
      const withThreatIntel = data.detections?.filter((d: Detection) => 
        d.threat_score !== undefined && d.threat_score > 0
      ) || []
      
      setDetections(withThreatIntel)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching threat data:', error)
      setLoading(false)
    }
  }

  const getThreatLevel = (score: number) => {
    if (score >= 75) return { label: 'Critical', color: 'text-red-500', bg: 'bg-red-500/10', border: 'border-red-500/30' }
    if (score >= 50) return { label: 'High', color: 'text-orange-500', bg: 'bg-orange-500/10', border: 'border-orange-500/30' }
    if (score >= 25) return { label: 'Medium', color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' }
    return { label: 'Low', color: 'text-blue-500', bg: 'bg-blue-500/10', border: 'border-blue-500/30' }
  }

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-800 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-800 rounded"></div>
            <div className="h-20 bg-gray-800 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (detections.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Shield className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-white">Threat Intelligence</h3>
        </div>
        <div className="text-center py-8 text-gray-400">
          <Globe className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No threat intelligence data available</p>
          <p className="text-sm mt-2">Enable threat intel in config.yaml to see reputation data</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-white">Threat Intelligence</h3>
        </div>
        <div className="text-sm text-gray-400">
          {detections.length} threats detected
        </div>
      </div>

      <div className="space-y-4 max-h-[500px] overflow-y-auto">
        {detections.map((detection) => {
          const threatLevel = getThreatLevel(detection.threat_score || 0)
          const srcIntel = detection.threat_intel?.src_threat_intel

          return (
            <div
              key={detection.id}
              className={`border ${threatLevel.border} ${threatLevel.bg} rounded-lg p-4 hover:bg-opacity-20 transition-all`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Server className="h-4 w-4 text-gray-400" />
                    <span className="font-mono text-white font-medium">{detection.source_ip}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${threatLevel.color} ${threatLevel.bg} border ${threatLevel.border}`}>
                      {threatLevel.label}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400">
                    {new Date(detection.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">
                    {detection.threat_score?.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-400">Threat Score</div>
                </div>
              </div>

              {/* AbuseIPDB Data */}
              {srcIntel?.abuseipdb && (
                <div className="bg-gray-800/50 rounded-lg p-3 mb-2">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-3.5 w-3.5 text-orange-400" />
                    <span className="text-xs font-semibold text-orange-400">AbuseIPDB</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <div className="text-gray-400">Confidence</div>
                      <div className="text-white font-medium">
                        {srcIntel.abuseipdb.abuse_confidence_score}%
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400">Reports</div>
                      <div className="text-white font-medium">
                        {srcIntel.abuseipdb.total_reports}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400">Country</div>
                      <div className="text-white font-medium">
                        {srcIntel.abuseipdb.country_code}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* VirusTotal Data */}
              {srcIntel?.virustotal && (
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-3.5 w-3.5 text-red-400" />
                    <span className="text-xs font-semibold text-red-400">VirusTotal</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <div className="text-gray-400">Malicious</div>
                      <div className="text-red-400 font-medium">
                        {srcIntel.virustotal.malicious}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400">Suspicious</div>
                      <div className="text-yellow-400 font-medium">
                        {srcIntel.virustotal.suspicious}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400">Reputation</div>
                      <div className="text-white font-medium">
                        {srcIntel.virustotal.reputation}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
