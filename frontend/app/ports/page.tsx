'use client'

import { useRouter } from 'next/navigation'
import { ArrowLeft, Shield } from 'lucide-react'
import PortActivityDashboard from '@/components/PortActivityDashboard'

export default function PortMonitorPage() {
  const router = useRouter()

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
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Shield className="h-8 w-8 text-blue-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Port Activity Monitor</h1>
                <p className="text-sm text-gray-400">Comprehensive network port analysis and scanning detection</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <PortActivityDashboard />
      </div>
    </div>
  )
}
