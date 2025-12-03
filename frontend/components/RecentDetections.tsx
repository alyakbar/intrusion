'use client'

import { useEffect, useState } from 'react'
import { format } from 'date-fns'
import { AlertCircle, CheckCircle, Clock } from 'lucide-react'

interface Detection {
  id: number
  timestamp: string
  source_ip: string
  dest_ip: string
  source_port: number | null
  dest_port: number | null
  protocol: string
  anomaly_score: number
  is_anomaly: boolean
  severity: string | null
}

export default function RecentDetections() {
  const [detections, setDetections] = useState<Detection[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDetections()
    const interval = setInterval(fetchDetections, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchDetections = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/detections/recent?limit=20')
      const data = await res.json()
      setDetections(Array.isArray(data) ? data : [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching detections:', error)
      setDetections([])
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string | null, isAnomaly: boolean) => {
    if (!isAnomaly) return 'text-green-400 bg-green-500/10 border-green-500/30'
    
    switch (severity) {
      case 'high':
        return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'low':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  // Map destination ports to common service names for clarity
  const getServiceName = (port?: number | null) => {
    if (!port || port <= 0) return ''
    const services: Record<number, string> = {
      20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
      53: 'DNS', 67: 'DHCP-Srv', 68: 'DHCP-Clt', 80: 'HTTP', 110: 'POP3',
      111: 'RPC', 123: 'NTP', 135: 'MSRPC', 139: 'NetBIOS', 143: 'IMAP',
      161: 'SNMP', 162: 'SNMP-Trap', 443: 'HTTPS', 445: 'SMB', 500: 'ISAKMP',
      514: 'Syslog', 993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL', 1521: 'Oracle',
      27017: 'MongoDB', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
      5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
    }
    return services[port] || 'Unknown'
  }

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-800 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-800/50 border-b border-gray-700">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Time
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Source IP
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Destination IP
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Ports
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Protocol
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Score
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {detections.map((detection) => (
              <tr 
                key={detection.id}
                className={`
                  hover:bg-gray-800/30 transition-colors
                  ${detection.is_anomaly ? 'bg-red-500/5' : ''}
                `}
              >
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <Clock className="h-3 w-3 text-gray-500" />
                    <span className="text-sm text-gray-300">
                      {format(new Date(detection.timestamp), 'HH:mm:ss')}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="flex flex-col">
                    <span className="text-sm font-mono text-white">
                      {detection.source_ip || 'N/A'}
                    </span>
                    {(detection as any).source_hostname && (
                      <span className="text-xs text-blue-400 truncate max-w-[180px]">
                        {(detection as any).source_hostname}
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="flex flex-col">
                    <span className="text-sm font-mono text-white">
                      {detection.dest_ip || 'N/A'}
                    </span>
                    {(detection as any).dest_hostname && (
                      <span className="text-xs text-blue-400 truncate max-w-[180px]">
                        {(detection as any).dest_hostname}
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  {detection.protocol === 'ICMP' ? (
                    <span className="text-xs text-gray-500 italic">N/A (ICMP)</span>
                  ) : (
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2 text-xs text-gray-300">
                        {detection.source_port && detection.source_port > 0 ? (
                          <span className="font-mono"><span className="text-gray-500">SRC</span> {detection.source_port}</span>
                        ) : (
                          <span className="text-gray-600">SRC -</span>
                        )}
                        <span className="text-gray-600">→</span>
                        {detection.dest_port && detection.dest_port > 0 ? (
                          <span className="font-mono font-semibold text-orange-400"><span className="text-gray-500">DST</span> {detection.dest_port}</span>
                        ) : (
                          <span className="text-gray-600">DST -</span>
                        )}
                      </div>
                      {detection.dest_port && detection.dest_port > 0 && (
                        <span className="text-[10px] text-gray-500 mt-0.5">
                          {getServiceName(detection.dest_port)}
                        </span>
                      )}
                    </div>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className="text-xs px-2 py-1 rounded bg-blue-500/20 border border-blue-500/40 text-blue-400 font-semibold">
                    {detection.protocol || 'UNKNOWN'}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all ${
                          detection.anomaly_score >= 0.9 ? 'bg-red-500' :
                          detection.anomaly_score >= 0.7 ? 'bg-yellow-500' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${detection.anomaly_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-400">
                      {(detection.anomaly_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`
                    inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border
                    ${getSeverityColor(detection.severity, detection.is_anomaly)}
                  `}>
                    {detection.is_anomaly ? (
                      <>
                        <AlertCircle className="h-3 w-3" />
                        {detection.severity?.toUpperCase() || 'ANOMALY'}
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-3 w-3" />
                        NORMAL
                      </>
                    )}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {detections.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No recent detections</p>
        </div>
      )}
    </div>
  )
}
