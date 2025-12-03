'use client'

import { useEffect, useState } from 'react'
import { Shield, Activity, AlertTriangle, TrendingUp, Network } from 'lucide-react'
import { useRouter } from 'next/navigation'
import AttackTypeGrid from '@/components/AttackTypeGrid'
import RecentDetections from '@/components/RecentDetections'
import TimelineChart from '@/components/TimelineChart'
import StatsCards from '@/components/StatsCards'
import TopSources from '@/components/TopSources'
import LivePacketCapture from '@/components/LivePacketCapture'

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/detections/stats')
      const data = await res.json()
      setStats(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching stats:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading detection data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Shield className="h-8 w-8 text-blue-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Network Anomaly Detection</h1>
                <p className="text-sm text-gray-400">Real-time Threat Intelligence & Monitoring</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/advanced')}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 rounded-lg transition-colors"
              >
                <Shield className="h-4 w-4 text-purple-400" />
                <span className="text-sm text-purple-400 font-medium">Advanced Features</span>
              </button>
              <button
                onClick={() => router.push('/ports')}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 rounded-lg transition-colors"
              >
                <Network className="h-4 w-4 text-blue-400" />
                <span className="text-sm text-blue-400 font-medium">Port Monitor</span>
              </button>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 rounded-lg border border-green-500/30">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-400 font-medium">System Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <StatsCards stats={stats} />

        {/* Live Packet Capture Monitor */}
        <section className="mb-8">
          <LivePacketCapture />
        </section>

        {/* Attack Types Grid */}
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-6">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <h2 className="text-xl font-bold text-white">Attack Classification</h2>
          </div>
          <AttackTypeGrid />
        </section>

        {/* Timeline & Activity */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-5 w-5 text-blue-500" />
              <h2 className="text-xl font-bold text-white">Detection Timeline</h2>
            </div>
            <TimelineChart />
          </div>
          
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Activity className="h-5 w-5 text-purple-500" />
              <h2 className="text-xl font-bold text-white">Top Threat Sources</h2>
            </div>
            <TopSources />
          </div>
        </div>

        {/* Recent Detections */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Activity className="h-5 w-5 text-yellow-500" />
            <h2 className="text-xl font-bold text-white">Recent Detections</h2>
          </div>
          <RecentDetections />
        </section>
      </div>
    </div>
  )
}
