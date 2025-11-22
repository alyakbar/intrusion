'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { 
  Shield, ArrowLeft, Clock, TrendingUp, AlertTriangle, 
  Globe, Server, Database, Lock, Eye, Zap, Activity, XCircle 
} from 'lucide-react'

interface Detection {
  id: number
  timestamp: string
  source_ip: string
  dest_ip: string
  source_port?: number
  dest_port?: number
  protocol: string
  anomaly_score: number
  severity: string
}

interface PortScannerInfo {
  source_ip: string
  ports_targeted: number
  total_packets: number
  first_seen: string
  last_seen: string
  scan_type: string
}

const attackTypeConfig: Record<string, {
  title: string
  description: string
  icon: any
  color: string
  bgColor: string
  borderColor: string
  characteristics: string[]
  commonTargets: string[]
  prevention: string[]
}> = {
  dos_ddos: {
    title: 'DoS/DDoS Attacks',
    description: 'Distributed Denial of Service attacks flood servers with traffic to overwhelm and crash them',
    icon: Server,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    characteristics: [
      'High volume of requests from multiple sources',
      'SYN flood or UDP flood patterns',
      'Rapid connection attempts',
      'Bandwidth saturation',
      'Server resource exhaustion'
    ],
    commonTargets: [
      'Web servers (HTTP/HTTPS)',
      'DNS servers',
      'Email servers',
      'Gaming servers',
      'Critical infrastructure'
    ],
    prevention: [
      'Rate limiting and traffic throttling',
      'DDoS mitigation services (Cloudflare, AWS Shield)',
      'Network firewall rules',
      'Load balancing across servers',
      'Anycast network diffusion'
    ]
  },
  port_scan: {
    title: 'Port Scanning',
    description: 'Reconnaissance activity probing network services to identify vulnerabilities and open ports',
    icon: Eye,
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    characteristics: [
      'Sequential port probing',
      'Multiple connection attempts to different ports',
      'SYN packets without completing handshake',
      'ICMP echo requests',
      'Banner grabbing attempts'
    ],
    commonTargets: [
      'Network infrastructure devices',
      'Servers with exposed services',
      'IoT devices',
      'Database servers',
      'Remote access services (SSH, RDP, Telnet)'
    ],
    prevention: [
      'Firewall rules to block unauthorized scanning',
      'Intrusion Detection Systems (IDS)',
      'Port knocking techniques',
      'Minimize exposed services',
      'Network segmentation'
    ]
  },
  brute_force: {
    title: 'Brute Force Attacks',
    description: 'Automated attempts to guess passwords through repeated login attempts',
    icon: Lock,
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    characteristics: [
      'Multiple failed authentication attempts',
      'Dictionary and credential stuffing attacks',
      'Rapid succession of login requests',
      'Same username, different passwords',
      'Distributed sources (credential spraying)'
    ],
    commonTargets: [
      'SSH services (port 22)',
      'RDP connections (port 3389)',
      'Web application login forms',
      'FTP servers',
      'Email servers (SMTP, IMAP, POP3)'
    ],
    prevention: [
      'Account lockout policies',
      'Multi-factor authentication (MFA)',
      'CAPTCHA on login forms',
      'Rate limiting login attempts',
      'Strong password policies'
    ]
  },
  sql_xss: {
    title: 'SQL Injection & XSS',
    description: 'Malicious code injection into web applications to steal data or execute scripts',
    icon: Database,
    color: 'text-pink-400',
    bgColor: 'bg-pink-500/10',
    borderColor: 'border-pink-500/30',
    characteristics: [
      'SQL commands in input fields',
      'JavaScript code in user inputs',
      'Special characters (quotes, semicolons)',
      'UNION-based SQL queries',
      'Script tags in HTTP requests'
    ],
    commonTargets: [
      'Web application forms',
      'URL parameters',
      'Database-driven websites',
      'Content Management Systems (CMS)',
      'E-commerce platforms'
    ],
    prevention: [
      'Input validation and sanitization',
      'Prepared statements and parameterized queries',
      'Content Security Policy (CSP) headers',
      'Web Application Firewall (WAF)',
      'Regular security audits and penetration testing'
    ]
  },
  backdoor_botnet: {
    title: 'Backdoor & Botnet Activity',
    description: 'Command and Control communications from compromised devices in a botnet network',
    icon: Globe,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    characteristics: [
      'Periodic beaconing to C2 servers',
      'Unusual outbound connections',
      'Encrypted command traffic',
      'IRC or HTTP-based C2 protocols',
      'Malware callback patterns'
    ],
    commonTargets: [
      'Compromised IoT devices',
      'Infected workstations',
      'Vulnerable servers',
      'Routers and network devices',
      'Webcams and smart devices'
    ],
    prevention: [
      'Network traffic monitoring and analysis',
      'Endpoint detection and response (EDR)',
      'Block known C2 server IPs',
      'Regular malware scanning',
      'Device firmware updates'
    ]
  },
  data_exfiltration: {
    title: 'Data Exfiltration',
    description: 'Unauthorized large data transfers attempting to steal sensitive information',
    icon: TrendingUp,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    characteristics: [
      'Unusually large outbound data transfers',
      'Data compression before transfer',
      'Off-hours data access patterns',
      'Use of covert channels',
      'Encrypted file transfers'
    ],
    commonTargets: [
      'Database servers',
      'File servers and NAS devices',
      'Cloud storage services',
      'Email systems',
      'Intellectual property repositories'
    ],
    prevention: [
      'Data Loss Prevention (DLP) systems',
      'Outbound traffic monitoring',
      'Encryption at rest and in transit',
      'Access control and least privilege',
      'User behavior analytics (UBA)'
    ]
  },
  mitm: {
    title: 'Man-in-the-Middle Attacks',
    description: 'Intercepting communications through ARP spoofing, DNS hijacking, or session hijacking',
    icon: Activity,
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    characteristics: [
      'ARP cache poisoning',
      'DNS response manipulation',
      'SSL/TLS downgrade attacks',
      'Rogue access points',
      'Session token theft'
    ],
    commonTargets: [
      'Wireless networks',
      'Public Wi-Fi hotspots',
      'Unencrypted HTTP traffic',
      'Email communications',
      'VoIP calls'
    ],
    prevention: [
      'Use HTTPS/TLS everywhere',
      'ARP spoofing detection tools',
      'DNSSEC implementation',
      'VPN for sensitive communications',
      'Certificate pinning'
    ]
  },
  zero_day: {
    title: 'Zero-Day Attacks',
    description: 'Previously unknown attack patterns exploiting undiscovered vulnerabilities',
    icon: Zap,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    characteristics: [
      'Unusual behavior patterns',
      'Exploitation of unknown vulnerabilities',
      'High anomaly scores',
      'Novel attack vectors',
      'No matching signature in threat databases'
    ],
    commonTargets: [
      'Operating systems',
      'Web browsers',
      'Application software',
      'Network protocols',
      'Hardware firmware'
    ],
    prevention: [
      'Machine learning-based anomaly detection',
      'Behavioral analysis systems',
      'Security patches and updates',
      'Application sandboxing',
      'Defense-in-depth strategies'
    ]
  }
}

export default function AttackDetailPage() {
  const params = useParams()
  const router = useRouter()
  const attackType = params.type as string
  
  const [detections, setDetections] = useState<Detection[]>([])
  const [portScanners, setPortScanners] = useState<PortScannerInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ total: 0, high: 0, medium: 0, low: 0 })

  const config = attackTypeConfig[attackType]

  useEffect(() => {
    if (!config) {
      router.push('/')
      return
    }
    fetchDetections()
    if (attackType === 'port_scan') {
      fetchPortScanners()
    }
    const interval = setInterval(() => {
      fetchDetections()
      if (attackType === 'port_scan') {
        fetchPortScanners()
      }
    }, 5000)
    return () => clearInterval(interval)
  }, [attackType])

  const fetchPortScanners = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/ports/scanners')
      const data = await res.json()
      setPortScanners(data.suspected_scanners || [])
    } catch (error) {
      console.error('Error fetching port scanners:', error)
    }
  }

  const fetchDetections = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/detections/by-type')
      const data = await res.json()
      
      const typeDetections = data.detections[attackType] || []
      setDetections(typeDetections)
      
      // Calculate severity stats
      const severityCount = {
        total: typeDetections.length,
        high: typeDetections.filter((d: Detection) => d.severity === 'high').length,
        medium: typeDetections.filter((d: Detection) => d.severity === 'medium').length,
        low: typeDetections.filter((d: Detection) => d.severity === 'low').length
      }
      setStats(severityCount)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching detections:', error)
      setLoading(false)
    }
  }

  if (!config) {
    return null
  }

  const Icon = config.icon

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'low': return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  const getServiceName = (port: number) => {
    const services: Record<number, string> = {
      20: 'FTP Data', 21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
      53: 'DNS', 80: 'HTTP', 110: 'POP3', 111: 'RPC', 135: 'MSRPC',
      139: 'NetBIOS', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 993: 'IMAPS',
      995: 'POP3S', 1433: 'MSSQL', 1521: 'Oracle', 3306: 'MySQL',
      3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
      8080: 'HTTP-Alt', 8443: 'HTTPS-Alt', 27017: 'MongoDB'
    }
    return services[port] || 'Unknown'
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-400" />
            </button>
            <div className={`p-2 ${config.bgColor} rounded-lg`}>
              <Icon className={`h-8 w-8 ${config.color}`} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{config.title}</h1>
              <p className="text-sm text-gray-400">{config.description}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-400 uppercase tracking-wide">Total Detections</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.total}</p>
          </div>

          <div className="bg-gray-900 rounded-lg border border-red-500/30 p-6">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="h-5 w-5 text-red-400" />
              <span className="text-sm text-gray-400 uppercase tracking-wide">High Severity</span>
            </div>
            <p className="text-3xl font-bold text-red-400">{stats.high}</p>
          </div>

          <div className="bg-gray-900 rounded-lg border border-yellow-500/30 p-6">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-5 w-5 text-yellow-400" />
              <span className="text-sm text-gray-400 uppercase tracking-wide">Medium Severity</span>
            </div>
            <p className="text-3xl font-bold text-yellow-400">{stats.medium}</p>
          </div>

          <div className="bg-gray-900 rounded-lg border border-blue-500/30 p-6">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="h-5 w-5 text-blue-400" />
              <span className="text-sm text-gray-400 uppercase tracking-wide">Low Severity</span>
            </div>
            <p className="text-3xl font-bold text-blue-400">{stats.low}</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Attack Characteristics */}
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-400" />
              Attack Characteristics
            </h3>
            <ul className="space-y-2">
              {config.characteristics.map((char, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>{char}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Common Targets */}
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Server className="h-5 w-5 text-orange-400" />
              Common Targets
            </h3>
            <ul className="space-y-2">
              {config.commonTargets.map((target, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-orange-400 mt-1">•</span>
                  <span>{target}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Prevention Methods */}
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Lock className="h-5 w-5 text-green-400" />
              Prevention & Mitigation
            </h3>
            <ul className="space-y-2">
              {config.prevention.map((method, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-green-400 mt-1">•</span>
                  <span>{method}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Port Scanner Detection - Only for port_scan attack type */}
        {attackType === 'port_scan' && portScanners.length > 0 && (
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-6 mb-8">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Eye className="h-5 w-5 text-orange-400" />
              Active Port Scanners Detected
            </h3>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800/50 border-b border-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Source IP</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Ports Scanned</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Total Packets</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Scan Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">First Seen</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Last Seen</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {portScanners.map((scanner, idx) => (
                    <tr key={idx} className="hover:bg-gray-800/30">
                      <td className="px-4 py-3 text-sm font-mono text-white">{scanner.source_ip}</td>
                      <td className="px-4 py-3">
                        <span className="px-3 py-1 bg-orange-500/20 border border-orange-500/40 rounded text-orange-400 text-sm font-bold">
                          {scanner.ports_targeted} ports
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-300">{scanner.total_packets}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-1 rounded bg-orange-500/10 border border-orange-500/30 text-orange-400">
                          {scanner.scan_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-400 font-mono">
                        {new Date(scanner.first_seen).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-400 font-mono">
                        {new Date(scanner.last_seen).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Recent Detections Table */}
        <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Clock className="h-5 w-5 text-purple-400" />
            Recent Detections
          </h3>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-400 mt-4">Loading detections...</p>
            </div>
          ) : detections.length === 0 ? (
            <div className="text-center py-8">
              <AlertTriangle className="h-12 w-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">No detections found for this attack type</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Timestamp</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Source IP</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Destination IP</th>
                    {attackType === 'port_scan' && (
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Target Port</th>
                    )}
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Protocol</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Anomaly Score</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {detections.slice(0, 50).map((detection) => (
                    <tr 
                      key={detection.id} 
                      className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
                    >
                      <td className="py-3 px-4 text-sm text-gray-300 font-mono">
                        {formatTimestamp(detection.timestamp)}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-300 font-mono">
                        {detection.source_ip || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-300 font-mono">
                        {detection.dest_ip || 'N/A'}
                      </td>
                      {attackType === 'port_scan' && (
                        <td className="py-3 px-4 text-sm">
                          <div className="flex flex-col gap-1">
                            <span className="px-2 py-1 bg-orange-500/10 border border-orange-500/30 rounded text-orange-400 text-xs font-bold inline-block w-fit">
                              Port {detection.dest_port || 'N/A'}
                            </span>
                            {detection.dest_port && detection.dest_port > 0 && (
                              <span className="text-xs text-gray-500">
                                {getServiceName(detection.dest_port)}
                              </span>
                            )}
                          </div>
                        </td>
                      )}
                      <td className="py-3 px-4 text-sm">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-1 bg-blue-500/20 border border-blue-500/40 rounded text-blue-400 text-xs font-semibold">
                            {detection.protocol || 'Unknown'}
                          </span>
                          {attackType === 'port_scan' && detection.protocol === 'TCP' && (
                            <span className="text-xs text-cyan-400 font-medium">SYN</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-gray-800 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                detection.anomaly_score > 0.9 ? 'bg-red-500' :
                                detection.anomaly_score > 0.7 ? 'bg-yellow-500' : 'bg-blue-500'
                              }`}
                              style={{ width: `${detection.anomaly_score * 100}%` }}
                            />
                          </div>
                          <span className="text-gray-300 font-mono text-xs">
                            {detection.anomaly_score.toFixed(3)}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <span className={`px-2 py-1 rounded border text-xs font-medium ${getSeverityColor(detection.severity)}`}>
                          {detection.severity?.toUpperCase() || 'UNKNOWN'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
