'use client'

import { Package, AlertTriangle, Activity, Percent } from 'lucide-react'

interface StatsCardsProps {
  stats: any
}

export default function StatsCards({ stats }: StatsCardsProps) {
  if (!stats) return null

  const cards = [
    {
      title: 'Total Packets',
      value: (stats.total_packets || 0).toLocaleString(),
      icon: Package,
      color: 'blue',
      description: 'Packets processed'
    },
    {
      title: 'Anomalies Detected',
      value: (stats.total_anomalies || 0).toLocaleString(),
      icon: AlertTriangle,
      color: 'red',
      description: 'Suspicious activities'
    },
    {
      title: 'Detection Rate',
      value: `${stats.anomaly_rate || 0}%`,
      icon: Percent,
      color: 'yellow',
      description: 'Anomaly percentage'
    },
    {
      title: 'Recent Activity',
      value: (stats.recent_activity || 0).toLocaleString(),
      icon: Activity,
      color: 'green',
      description: 'Last hour'
    }
  ]

  const colorClasses: Record<string, string> = {
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    red: 'from-red-500/20 to-red-600/10 border-red-500/30',
    yellow: 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30',
    green: 'from-green-500/20 to-green-600/10 border-green-500/30'
  }

  const iconColors: Record<string, string> = {
    blue: 'text-blue-400',
    red: 'text-red-400',
    yellow: 'text-yellow-400',
    green: 'text-green-400'
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <div
            key={idx}
            className={`
              relative overflow-hidden p-6 rounded-lg border
              bg-gradient-to-br ${colorClasses[card.color]}
              hover:shadow-lg transition-all duration-300
            `}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-gray-400 mb-1">{card.title}</p>
                <p className="text-3xl font-bold text-white">{card.value}</p>
              </div>
              <div className={`p-3 rounded-lg bg-gray-900/50`}>
                <Icon className={`h-6 w-6 ${iconColors[card.color]}`} />
              </div>
            </div>
            <p className="text-xs text-gray-500">{card.description}</p>
            
            {/* Severity breakdown for anomalies card */}
            {card.title === 'Anomalies Detected' && stats.severity_counts && (
              <div className="mt-4 pt-4 border-t border-gray-700/50">
                <div className="flex gap-3 text-xs">
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-red-500"></div>
                    <span className="text-gray-400">High: {stats.severity_counts.high}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-yellow-500"></div>
                    <span className="text-gray-400">Med: {stats.severity_counts.medium}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                    <span className="text-gray-400">Low: {stats.severity_counts.low}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
