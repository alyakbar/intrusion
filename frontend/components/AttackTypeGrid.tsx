'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Cloud, Scan, Key, Database, Radio, 
  HardDrive, Network, Zap 
} from 'lucide-react'

interface AttackType {
  id: string
  name: string
  description: string
  icon: any
  color: string
  count: number
}

export default function AttackTypeGrid() {
  const router = useRouter()
  const [attackData, setAttackData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAttackTypes()
    const interval = setInterval(fetchAttackTypes, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchAttackTypes = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/detections/by-type')
      const data = await res.json()
      setAttackData(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching attack types:', error)
      setLoading(false)
    }
  }

  const attackTypes: AttackType[] = [
    {
      id: 'dos_ddos',
      name: 'DoS/DDoS Attacks',
      description: 'Flooding servers with traffic to crash them',
      icon: Cloud,
      color: 'red',
      count: attackData?.counts?.dos_ddos || 0
    },
    {
      id: 'port_scan',
      name: 'Port Scanning',
      description: 'Probing network for vulnerabilities',
      icon: Scan,
      color: 'orange',
      count: attackData?.counts?.port_scan || 0
    },
    {
      id: 'brute_force',
      name: 'Brute Force',
      description: 'Multiple failed login attempts',
      icon: Key,
      color: 'yellow',
      count: attackData?.counts?.brute_force || 0
    },
    {
      id: 'sql_xss',
      name: 'SQL Injection & XSS',
      description: 'Malicious database queries & scripts',
      icon: Database,
      color: 'pink',
      count: attackData?.counts?.sql_xss || 0
    },
    {
      id: 'backdoor_botnet',
      name: 'Backdoor & Botnet',
      description: 'C2 communications from compromised devices',
      icon: Radio,
      color: 'purple',
      count: attackData?.counts?.backdoor_botnet || 0
    },
    {
      id: 'data_exfiltration',
      name: 'Data Exfiltration',
      description: 'Unusual large data transfers',
      icon: HardDrive,
      color: 'blue',
      count: attackData?.counts?.data_exfiltration || 0
    },
    {
      id: 'mitm',
      name: 'Man-in-the-Middle',
      description: 'ARP spoofing & DNS hijacking',
      icon: Network,
      color: 'green',
      count: attackData?.counts?.mitm || 0
    },
    {
      id: 'zero_day',
      name: 'Zero-Day Attacks',
      description: 'Unknown attack patterns detected',
      icon: Zap,
      color: 'cyan',
      count: attackData?.counts?.zero_day || 0
    },
  ]

  const colorClasses: Record<string, { bg: string, border: string, text: string, glow: string }> = {
    red: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', glow: 'shadow-red-500/20' },
    orange: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', glow: 'shadow-orange-500/20' },
    yellow: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', glow: 'shadow-yellow-500/20' },
    pink: { bg: 'bg-pink-500/10', border: 'border-pink-500/30', text: 'text-pink-400', glow: 'shadow-pink-500/20' },
    purple: { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400', glow: 'shadow-purple-500/20' },
    blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400', glow: 'shadow-blue-500/20' },
    green: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400', glow: 'shadow-green-500/20' },
    cyan: { bg: 'bg-cyan-500/10', border: 'border-cyan-500/30', text: 'text-cyan-400', glow: 'shadow-cyan-500/20' },
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="animate-pulse bg-gray-800 rounded-lg h-32"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {attackTypes.map((attack) => {
        const Icon = attack.icon
        const colors = colorClasses[attack.color]
        const hasDetections = attack.count > 0

        return (
          <div
            key={attack.id}
            onClick={() => router.push(`/attacks/${attack.id}`)}
            className={`
              relative p-4 rounded-lg border transition-all duration-300
              ${colors.bg} ${colors.border}
              ${hasDetections ? `${colors.glow} shadow-lg` : ''}
              hover:scale-105 hover:shadow-xl cursor-pointer
              ${hasDetections ? 'animate-pulse-slow' : ''}
            `}
          >
            {hasDetections && (
              <div className="absolute -top-2 -right-2">
                <div className={`
                  px-2 py-1 rounded-full text-xs font-bold
                  ${colors.bg} ${colors.border} ${colors.text} border
                  animate-bounce-slow
                `}>
                  {attack.count}
                </div>
              </div>
            )}
            
            <div className="flex items-start justify-between mb-3">
              <div className={`p-2 rounded-lg ${colors.bg}`}>
                <Icon className={`h-6 w-6 ${colors.text}`} />
              </div>
            </div>
            
            <h3 className={`font-semibold mb-1 ${colors.text}`}>
              {attack.name}
            </h3>
            <p className="text-xs text-gray-400 line-clamp-2">
              {attack.description}
            </p>

            {hasDetections && (
              <div className={`mt-3 pt-3 border-t ${colors.border}`}>
                <p className="text-xs text-gray-500">
                  {attack.count} {attack.count === 1 ? 'detection' : 'detections'} identified
                </p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
